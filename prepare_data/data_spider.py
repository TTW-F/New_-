#!/usr/bin/env python3
# coding: utf-8
# File: data_spider.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-3


import urllib.request
import urllib.parse
from urllib.parse import urljoin
from lxml import etree
import pymysql
from pymysql.cursors import DictCursor
import re
import time
import logging
import json
import os
import random
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
import threading

load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 进度文件配置
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), 'spider_progress.json')
PROGRESS_INTERVAL = 10  # 每采集10页保存一次进度

# 采集效率配置
DEFAULT_DELAY_MIN = 0.3  # 默认最小延迟（秒）
DEFAULT_DELAY_MAX = 0.8  # 默认最大延迟（秒）
DEFAULT_MAX_WORKERS = 8  # 默认并发线程数（每个页面的子URL并发数）
DEFAULT_PAGE_WORKERS = 3  # 默认页面级并发数（同时处理多个页面）

class MedicalSpider:
    """基于寻医问药网采集（MySQL 存储原始数据）"""
    
    def __init__(self, progress_file=PROGRESS_FILE, delay_min=DEFAULT_DELAY_MIN, delay_max=DEFAULT_DELAY_MAX, 
                 max_workers=DEFAULT_MAX_WORKERS, page_workers=DEFAULT_PAGE_WORKERS):
        try:
            # 从环境变量读取数据库配置
            self.db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', '3306')),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'medical_qa'),
                'charset': 'utf8mb4',
                'cursorclass': DictCursor
            }
            self.conn = pymysql.connect(**self.db_config)
            self.conn.ping(reconnect=True)
            logger.info("MySQL 连接成功")
            self._init_table()
        except Exception as e:
            logger.error(f"MySQL 连接失败: {e}")
            raise
        
        self.progress_file = progress_file
        self.progress = self._load_progress()
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.max_workers = max_workers  # 每个页面的子URL并发数
        self.page_workers = page_workers  # 页面级并发数
        self.start_time = None  # 用于统计采集速率
        self._success_count_lock = threading.Lock()  # 线程安全计数器
        self._fail_count_lock = threading.Lock()
    
    def _init_table(self):
        """初始化数据表"""
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS raw_spider_data (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        page INT NOT NULL,
                        data JSON NOT NULL,
                        status ENUM('pending', 'processed', 'failed') DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_page (page),
                        INDEX idx_status (status)
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                self.conn.commit()
                logger.info("raw_spider_data 表初始化完成")
            except Exception as e:
                logger.error(f"初始化表失败: {e}")
                self.conn.rollback()
                raise

    def _load_progress(self) -> Dict:
        """加载采集进度"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                logger.info(f"已加载采集进度: {progress}")
                return progress
            except Exception as e:
                logger.warning(f"加载进度文件失败: {e}")
        return {"spider_main": 0, "inspect_crawl": 0, "last_update": None}
    
    def _save_progress(self, task_name: str, page: int):
        """保存采集进度"""
        try:
            self.progress[task_name] = page
            self.progress["last_update"] = datetime.now().isoformat()
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存进度失败: {e}")
    
    '''根据url，请求html'''
    def get_html(self, url, retry=3, timeout=10):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/120.0.0.0 Safari/537.36'
        }
        
        for attempt in range(retry):
            try:
                req = urllib.request.Request(url=url, headers=headers)
                res = urllib.request.urlopen(req, timeout=timeout)
                html = res.read().decode('gbk')
                return html
            except UnicodeDecodeError as decode_error:
                try:
                    html = res.read().decode('utf-8')
                    return html
                except Exception as e:
                    logger.warning(f"解码失败: {url}, 错误: {e}")
                    raise decode_error
            except Exception as e:
                logger.warning(f"第{attempt + 1}次请求失败 {url}: {e}")
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    raise
        return None

    '''url解析'''
    def url_parser(self, content):
        selector = etree.HTML(content)
        urls = ['http://www.anliguan.com' + i for i in  selector.xpath('//h2[@class="item-title"]/a/@href')]
        return urls
    
    def _fetch_page_data_concurrent(self, data: Dict, url_tasks: Dict):
        """
        并发请求同一页面的多个子URL，提升采集速度
        
        Args:
            data: 数据字典，用于存储结果
            url_tasks: 任务字典，格式为 {'key': (spider_method, url), ...}
        """
        def fetch_single(spider_method, url, key):
            """单个URL的请求任务"""
            try:
                result = spider_method(url)
                return key, result, None
            except Exception as e:
                logger.warning(f"并发请求失败 [{key}]: {url}, 错误: {e}")
                return key, None, str(e)
        
        # 使用线程池并发请求
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            futures = {
                executor.submit(fetch_single, spider_method, url, key): key
                for key, (spider_method, url) in url_tasks.items()
            }
            
            # 收集结果
            for future in as_completed(futures):
                key = futures[future]
                try:
                    result_key, result, error = future.result()
                    if error:
                        # 请求失败，设置默认值
                        data[result_key] = [] if result_key in ['symptom_info', 'inspect_info', 'drug_info'] else ''
                    else:
                        data[result_key] = result
                except Exception as e:
                    logger.error(f"获取任务结果失败 [{key}]: {e}")
                    # 设置默认值
                    default_value = [] if key in ['symptom_info', 'inspect_info', 'drug_info'] else ''
                    data[key] = default_value

    def _crawl_single_page(self, page: int) -> tuple:
        """
        采集单个页面的所有数据（线程安全）
        
        Args:
            page: 页面编号
            
        Returns:
            (page, success, disease_name) - 页面号、是否成功、疾病名称
        """
        try:
            # 每个线程使用独立的数据库连接（线程安全）
            thread_conn = pymysql.connect(**self.db_config)
            
            # 更新为新网站 HTTPS 地址
            basic_url = 'https://jib.xywy.com/il_sii/gaishu/%s.htm' % page
            cause_url = 'https://jib.xywy.com/il_sii/cause/%s.htm' % page
            prevent_url = 'https://jib.xywy.com/il_sii/prevent/%s.htm' % page
            symptom_url = 'https://jib.xywy.com/il_sii/symptom/%s.htm' % page
            inspect_url = 'https://jib.xywy.com/il_sii/inspect/%s.htm' % page
            treat_url = 'https://jib.xywy.com/il_sii/treat/%s.htm' % page
            food_url = 'https://jib.xywy.com/il_sii/food/%s.htm' % page
            drug_url = 'https://jib.xywy.com/il_sii/drug/%s.htm' % page
            
            data = {}
            data['url'] = basic_url
            data['page'] = page
            data['timestamp'] = datetime.now().isoformat()
            
            # 先获取基本信息，判断页面是否有效
            data['basic_info'] = self.basicinfo_spider(basic_url)
            disease_name = data['basic_info'].get('name', '').strip()
            
            if not disease_name:
                # 页面可能不存在或无效
                error_msg = data['basic_info'].get('error', 'unknown')
                logger.warning(f"第{page}页: 疾病名称为空，可能是无效页面")
                
                # 并发请求其他子页面
                self._fetch_page_data_concurrent(data, {
                    'cause_info': (self.common_spider, cause_url),
                    'prevent_info': (self.common_spider, prevent_url),
                    'symptom_info': (self.symptom_spider, symptom_url),
                    'inspect_info': (self.inspect_spider, inspect_url),
                    'treat_info': (self.treat_spider, treat_url),
                    'food_info': (self.food_spider, food_url),
                    'drug_info': (self.drug_spider, drug_url)
                })
                
                # 保存数据
                with thread_conn.cursor() as cursor:
                    cursor.execute("SELECT id FROM raw_spider_data WHERE page = %s", (page,))
                    existing = cursor.fetchone()
                    status = 'failed' if error_msg in ['invalid_page', 'empty_name', 'no_title'] else 'pending'
                    if existing:
                        cursor.execute(
                            "UPDATE raw_spider_data SET data = %s, status = %s WHERE page = %s",
                            (json.dumps(data, ensure_ascii=False), status, page)
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO raw_spider_data (page, data, status) VALUES (%s, %s, %s)",
                            (page, json.dumps(data, ensure_ascii=False), status)
                        )
                    thread_conn.commit()
                
                thread_conn.close()
                logger.info(f"第{page}页采集完成: [无效页面] {error_msg}")
                return (page, False, '')
            
            # 正常采集其他信息 - 使用并发请求加速
            self._fetch_page_data_concurrent(data, {
                'cause_info': (self.common_spider, cause_url),
                'prevent_info': (self.common_spider, prevent_url),
                'symptom_info': (self.symptom_spider, symptom_url),
                'inspect_info': (self.inspect_spider, inspect_url),
                'treat_info': (self.treat_spider, treat_url),
                'food_info': (self.food_spider, food_url),
                'drug_info': (self.drug_spider, drug_url)
            })
            
            # 保存数据
            with thread_conn.cursor() as cursor:
                cursor.execute("SELECT id FROM raw_spider_data WHERE page = %s", (page,))
                existing = cursor.fetchone()
                if existing:
                    cursor.execute(
                        "UPDATE raw_spider_data SET data = %s, status = %s WHERE page = %s",
                        (json.dumps(data, ensure_ascii=False), 'pending', page)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO raw_spider_data (page, data, status) VALUES (%s, %s, %s)",
                        (page, json.dumps(data, ensure_ascii=False), 'pending')
                    )
                thread_conn.commit()
            
            thread_conn.close()
            logger.info(f"第{page}页采集完成: {disease_name}")
            return (page, True, disease_name)
            
        except Exception as e:
            logger.error(f"第{page}页采集失败: {e}")
            if 'thread_conn' in locals():
                thread_conn.rollback()
                thread_conn.close()
            return (page, False, '')
    
    '''主爬虫函数'''
    def spider_main(self, start_page=None, end_page=11000):
        """
        采集疾病数据（支持多页面并发）
        :param start_page: 起始页数（默认读取进度）
        :param end_page: 结束页数
        """
        # 如果未指定起始页，使用上次进度
        if start_page is None:
            start_page = self.progress.get('spider_main', 0)
            if start_page > 0:
                logger.info(f"恢复采集进度至第 {start_page} 页")
        else:
            # 如果明确指定了起始页，使用指定的值（不取最大值）
            logger.info(f"使用指定的起始页：第 {start_page} 页")
        
        self.start_time = time.time()
        success_count = 0
        fail_count = 0
        total_pages = end_page - start_page
        logger.info(f"开始采集，预计采集 {total_pages} 页")
        logger.info(f"效率配置：页面级并发 {self.page_workers} 个页面 | 每个页面 {self.max_workers} 个线程并发子URL")
        
        # 使用线程池并发处理多个页面
        with ThreadPoolExecutor(max_workers=self.page_workers) as executor:
            # 提交所有页面任务（带延迟控制，避免一次性提交太多）
            future_to_page = {}
            submitted = 0
            
            for page in range(start_page, end_page):
                # 控制提交速率：每提交一个页面后延迟
                if submitted > 0 and submitted % self.page_workers == 0:
                    time.sleep(random.uniform(self.delay_min, self.delay_max))
                
                future = executor.submit(self._crawl_single_page, page)
                future_to_page[future] = page
                submitted += 1
            
            # 收集结果并统计
            completed_pages = set()
            for future in as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    result_page, success, disease_name = future.result()
                    completed_pages.add(result_page)
                    
                    if success:
                        with self._success_count_lock:
                            success_count += 1
                    else:
                        with self._fail_count_lock:
                            fail_count += 1
                    
                    # 每完成10页保存一次进度并显示速率
                    if len(completed_pages) % PROGRESS_INTERVAL == 0:
                        max_completed = max(completed_pages) if completed_pages else start_page
                        self._save_progress('spider_main', max_completed)
                        elapsed = time.time() - self.start_time
                        rate = len(completed_pages) / elapsed if elapsed > 0 else 0
                        remaining = total_pages - len(completed_pages)
                        eta_seconds = remaining / rate if rate > 0 else 0
                        eta_minutes = eta_seconds / 60
                        logger.info(f"进度：已完成 {len(completed_pages)}/{total_pages} 页 | 成功 {success_count} | 失败 {fail_count} | "
                                  f"速率 {rate:.2f} 页/秒 | 预计剩余 {eta_minutes:.1f} 分钟")
                    
                except Exception as e:
                    logger.error(f"处理页面 {page} 结果失败: {e}")
                    with self._fail_count_lock:
                        fail_count += 1
        
        # 最后保存进度
        max_completed = max(completed_pages) if completed_pages else end_page - 1
        self._save_progress('spider_main', max_completed)
        elapsed = time.time() - self.start_time
        total_elapsed_minutes = elapsed / 60
        avg_rate = len(completed_pages) / elapsed if elapsed > 0 else 0
        logger.info(f"采集完成！总计成功 {success_count} 条，失败 {fail_count} 条 | "
                   f"总耗时 {total_elapsed_minutes:.1f} 分钟 | 平均速率 {avg_rate:.2f} 页/秒")
        return

    '''基本信息解析'''
    def basicinfo_spider(self, url):
        try:
            html = self.get_html(url)
            if not html:
                logger.warning(f"[basicinfo] 无法获取页面内容: {url}")
                return {'name': '', 'category': [], 'desc': [], 'attributes': [], 'error': 'empty_html'}
            
            selector = etree.HTML(html)
            title_elements = selector.xpath('//title/text()')
            if not title_elements:
                logger.warning(f"[basicinfo] 无法解析标题: {url}")
                return {'name': '', 'category': [], 'desc': [], 'attributes': [], 'error': 'no_title'}
            
            title = title_elements[0].strip()
            if not title or title in ['这是什么情况', '404', '页面不存在']:
                logger.warning(f"[basicinfo] 页面无效或不存在: {url}, title={title}")
                return {'name': '', 'category': [], 'desc': [], 'attributes': [], 'error': 'invalid_page', 'title': title}
            
            # 提取疾病名称（从标题中移除"的简介"等后缀）
            disease_name = title
            for suffix in ['的简介', ' - 好大夫在线', ' - 寻医问药', '简介']:
                if suffix in disease_name:
                    disease_name = disease_name.split(suffix)[0].strip()
                    break
            
            if not disease_name:
                logger.warning(f"[basicinfo] 疾病名称为空: {url}, title={title}")
                return {'name': '', 'category': [], 'desc': [], 'attributes': [], 'error': 'empty_name', 'title': title}
            
            category = selector.xpath('//div[@class="wrap mt10 nav-bar"]/a/text()')
            desc = selector.xpath('//div[@class="jib-articl-con jib-lh-articl"]/p/text()')
            ps = selector.xpath('//div[@class="mt20 articl-know"]/p')
            infobox = []
            for p in ps:
                info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
                if info.strip():
                    infobox.append(info)
            
            basic_data = {
                'name': disease_name,
                'category': category if category else [],
                'desc': desc if desc else [],
                'attributes': infobox,
                'original_title': title
            }
            return basic_data
            
        except Exception as e:
            logger.error(f"[basicinfo] 解析失败 {url}: {e}")
            return {'name': '', 'category': [], 'desc': [], 'attributes': [], 'error': str(e)}

    '''treat_infobox治疗解析'''
    def treat_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        ps = selector.xpath('//div[starts-with(@class,"mt20 articl-know")]/p')
        infobox = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
            infobox.append(info)
        return infobox

    '''treat_infobox治疗解析'''
    def drug_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        drugs = [i.replace('\n','').replace('\t', '').replace(' ','') for i in selector.xpath('//div[@class="fl drug-pic-rec mr30"]/p/a/text()')]
        return drugs

    '''food食物信息解析'''
    def food_spider(self, url):
        try:
            html = self.get_html(url)
            selector = etree.HTML(html)
            divs = selector.xpath('//div[@class="diet-img clearfix mt20"]')
            
            food_data = {}
            if len(divs) > 0:
                food_data['good'] = divs[0].xpath('./div/p/text()') if len(divs) > 0 else []
            if len(divs) > 1:
                food_data['bad'] = divs[1].xpath('./div/p/text()') if len(divs) > 1 else []
            if len(divs) > 2:
                food_data['recommand'] = divs[2].xpath('./div/p/text()') if len(divs) > 2 else []
            
            return food_data
        except Exception as e:
            logger.warning(f"食物信息解析失败 {url}: {e}")
            return {}

    '''症状信息解析'''
    def symptom_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        symptoms = selector.xpath('//a[@class="gre" ]/text()')
        ps = selector.xpath('//p')
        detail = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
            detail.append(info)
        symptoms_data = {}
        symptoms_data['symptoms'] = symptoms
        symptoms_data['symptoms_detail'] = detail
        return symptoms_data

    '''检查信息解析'''
    def inspect_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        inspects  = selector.xpath('//li[@class="check-item"]/a/@href')
        return inspects

    '''通用解析模块'''
    def common_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        ps = selector.xpath('//p')
        infobox = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ','').replace('\t', '')
            if info:
                infobox.append(info)
        return '\n'.join(infobox)
    '''检查项抓取模块'''
    def inspect_crawl(self, start_page=None, end_page=3685):
        """
        采集检查项抓取模块（使用 MySQL 存储）
        :param start_page: 起始页数（默认读取进度）
        :param end_page: 结束页数
        """
        # 如果未指定起始页，使用上次进度
        if start_page is None:
            start_page = self.progress.get('inspect_crawl', 0)
            if start_page > 0:
                logger.info(f"恢复检查项采集进度至第 {start_page} 页")
        else:
            # 如果明确指定了起始页，使用指定的值（不取最大值）
            logger.info(f"使用指定的起始页：第 {start_page} 页")
        
        self.start_time = time.time()
        success_count = 0
        fail_count = 0
        total_pages = end_page - start_page
        logger.info(f"开始检查项采集，预计采集 {total_pages} 页，延迟范围：{self.delay_min}-{self.delay_max}秒")
            
        for page in range(start_page, end_page):
            try:
                # 更新为新网站 HTTPS 地址
                url = 'https://jck.xywy.com/jc_%s.html' % page
                html = self.get_html(url)
                data = {
                    'url': url,
                    'html': html,
                    'page': page,
                    'type': 'inspect',
                    'timestamp': datetime.now().isoformat()
                }
                    
                # 使用 MySQL 存储
                with self.conn.cursor() as cursor:
                    # 检查是否已存在（通过 page 查询，避免重复）
                    cursor.execute(
                        "SELECT id FROM raw_spider_data WHERE page = %s AND JSON_EXTRACT(data, '$.type') = 'inspect'",
                        (page,)
                    )
                    existing = cursor.fetchone()
                    
                    if existing:
                        # 更新现有数据
                        cursor.execute(
                            "UPDATE raw_spider_data SET data = %s, status = %s WHERE page = %s AND JSON_EXTRACT(data, '$.type') = 'inspect'",
                            (json.dumps(data, ensure_ascii=False), 'pending', page)
                        )
                        logger.debug(f"检查项第{page}页数据已更新")
                    else:
                        # 插入新数据
                        cursor.execute(
                            "INSERT INTO raw_spider_data (page, data, status) VALUES (%s, %s, %s)",
                            (page, json.dumps(data, ensure_ascii=False), 'pending')
                        )
                        success_count += 1
                    
                    self.conn.commit()
                    
                logger.info(f"检查项采集: {url}")
                    
                # 每采集10页保存一次进度并显示速率
                if page % PROGRESS_INTERVAL == 0:
                    self._save_progress('inspect_crawl', page)
                    elapsed = time.time() - self.start_time
                    rate = (page - start_page + 1) / elapsed if elapsed > 0 else 0
                    eta_seconds = (total_pages - (page - start_page + 1)) / rate if rate > 0 else 0
                    eta_minutes = eta_seconds / 60
                    logger.info(f"进度：第 {page}/{end_page-1} 页 | 成功 {success_count} | 失败 {fail_count} | "
                              f"速率 {rate:.2f} 页/秒 | 预计剩余 {eta_minutes:.1f} 分钟")
                    
                # 添加随机延迟
                time.sleep(random.uniform(self.delay_min, self.delay_max))
                
            except Exception as e:
                fail_count += 1
                logger.error(f"检查项采集失败 {url}: {e}")
                self.conn.rollback()
                continue
            
        # 最后保存进度
        self._save_progress('inspect_crawl', end_page - 1)
        elapsed = time.time() - self.start_time
        total_elapsed_minutes = elapsed / 60
        avg_rate = (end_page - start_page) / elapsed if elapsed > 0 else 0
        logger.info(f"检查项采集完成！总计成功 {success_count} 条，失败 {fail_count} 条 | "
                   f"总耗时 {total_elapsed_minutes:.1f} 分钟 | 平均速率 {avg_rate:.2f} 页/秒")

    # ------------------------------------------------------------------
    # zzk.xywy.com 症状站点采集
    # ------------------------------------------------------------------

    def zzk_symptom_spider(self, categories: Optional[List[str]] = None,
                           limit: Optional[int] = None):
        """
        采集 https://zzk.xywy.com/ 症状站点
        :param categories: 指定分类链接（默认自动获取）
        :param limit: 最多采集的症状数量
        """
        base_url = 'https://zzk.xywy.com'
        if categories is None:
            categories = self._get_zzk_category_links(base_url)

        if not categories:
            logger.warning("[zzk] 未获取到分类链接，采集终止")
            return

        self.start_time = time.time()
        visited = set()
        total_success = 0
        total_fail = 0
        logger.info(f"[zzk] 开始症状采集，延迟范围：{self.delay_min}-{self.delay_max}秒")

        for category_url in categories:
            try:
                symptom_entries = self._get_zzk_symptom_links(category_url)
            except Exception as exc:
                logger.error(f"[zzk] 获取分类 {category_url} 失败: {exc}")
                total_fail += 1
                continue

            logger.info(f"[zzk] 分类 {category_url} 包含 {len(symptom_entries)} 个症状候选")

            for entry in symptom_entries:
                detail_url = entry['url']
                if detail_url in visited:
                    continue
                visited.add(detail_url)

                try:
                    symptom_data = self._parse_zzk_symptom_detail(detail_url)
                    if not symptom_data:
                        total_fail += 1
                        continue

                    symptom_data['category'] = entry.get('category')
                    symptom_data['category_url'] = entry.get('category_url')
                    symptom_data['source'] = 'zzk.xywy.com'
                    symptom_data['type'] = 'symptom'

                    if self._save_symptom_record(symptom_data):
                        total_success += 1
                    else:
                        total_fail += 1

                    # 每采集10条显示一次速率
                    if total_success % 10 == 0:
                        elapsed = time.time() - self.start_time
                        rate = total_success / elapsed if elapsed > 0 else 0
                        logger.info(f"[zzk] 进度：成功 {total_success} | 失败 {total_fail} | "
                                  f"速率 {rate:.2f} 条/秒")

                    if limit and total_success >= limit:
                        logger.info(f"[zzk] 达到采集限制 {limit} 条，提前结束")
                        elapsed = time.time() - self.start_time
                        total_elapsed_minutes = elapsed / 60
                        avg_rate = total_success / elapsed if elapsed > 0 else 0
                        logger.info(f"[zzk] 症状采集完成！成功 {total_success} 条，失败 {total_fail} 条 | "
                                   f"总耗时 {total_elapsed_minutes:.1f} 分钟 | 平均速率 {avg_rate:.2f} 条/秒")
                        return

                    # 添加延迟控制，避免请求过快被封IP
                    time.sleep(random.uniform(self.delay_min, self.delay_max))

                except Exception as exc:
                    total_fail += 1
                    logger.error(f"[zzk] 采集 {detail_url} 失败: {exc}", exc_info=True)

        elapsed = time.time() - self.start_time
        total_elapsed_minutes = elapsed / 60
        avg_rate = total_success / elapsed if elapsed > 0 else 0
        logger.info(f"[zzk] 症状采集完成！成功 {total_success} 条，失败 {total_fail} 条 | "
                   f"总耗时 {total_elapsed_minutes:.1f} 分钟 | 平均速率 {avg_rate:.2f} 条/秒")

    def _get_zzk_category_links(self, base_url: str) -> List[str]:
        """获取 zzk 站点的科室/分类链接"""
        seeds = [
            urljoin(base_url, '/p/neike.html'),
            urljoin(base_url, '/p/toubu.html'),
            urljoin(base_url, '/p/a.html'),
        ]
        seen = set()
        results = []
        queue = list(seeds)

        while queue:
            current = queue.pop(0)
            if current in seen:
                continue
            seen.add(current)
            html = self.get_html(current)
            if not html:
                continue
            results.append(current)
            selector = etree.HTML(html)
            links = selector.xpath('//div[contains(@class,"jblist-nav")]//a/@href')
            for href in links:
                if not href or not href.startswith('/p/'):
                    continue
                full_url = urljoin(base_url, href)
                if full_url not in seen and full_url not in queue:
                    queue.append(full_url)

        logger.info(f"[zzk] 获取到 {len(results)} 个分类链接")
        return results

    def _get_zzk_symptom_links(self, category_url: str) -> List[Dict]:
        """解析分类页面下的症状链接"""
        html = self.get_html(category_url)
        if not html:
            return []
        selector = etree.HTML(html)
        entries: List[Dict] = []
        base = 'https://zzk.xywy.com'

        boxes = selector.xpath('//div[contains(@class, "ks-ill-box")]')
        for box in boxes:
            title = box.xpath('.//strong[contains(@class,"fb")]/a/text() | '
                              './/strong[contains(@class,"fb")]/text()')
            category_name = ''.join(title).strip()
            for a in box.xpath('.//ul[contains(@class,"ks-ill-list")]//a'):
                href = a.get('href')
                name = (a.get('title') or (a.text or '')).strip()
                if not href or not name:
                    continue
                detail_url = urljoin(base, href)
                entries.append({
                    'url': detail_url,
                    'name': name,
                    'category': category_name,
                    'category_url': category_url
                })
        return entries

    def _clean_text(self, text: str) -> str:
        """清理文本：移除换行符、制表符、多余空格、详情链接文本等"""
        if not text:
            return ''
        # 移除换行符、制表符、回车符
        text = text.replace('\r', '').replace('\n', ' ').replace('\t', ' ')
        # 移除HTML实体
        text = text.replace('&ldquo;', '"').replace('&rdquo;', '"').replace('&nbsp;', ' ')
        # 移除"详情>"或"详情"或"更多>"等链接文本
        text = re.sub(r'详情\s*>?\s*$', '', text)
        text = re.sub(r'更多\s*>?\s*$', '', text)
        # 合并多个空格为单个空格
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_detail_content(self, detail_url: str) -> str:
        """从详情页面提取完整内容"""
        try:
            html = self.get_html(detail_url)
            if not html:
                return ''
            selector = etree.HTML(html)
            # 提取主要内容区域的文本（尝试多种选择器）
            paragraphs = selector.xpath('//div[contains(@class,"jib-articl-con")]//p//text() | '
                                       '//div[contains(@class,"jib-articl-con")]//text() | '
                                       '//div[contains(@class,"articl-know")]//p//text() | '
                                       '//div[contains(@class,"articl-know")]//text()')
            content = ' '.join(t.strip() for t in paragraphs if t.strip())
            return self._clean_text(content)
        except Exception as e:
            logger.warning(f"[zzk] 提取详情内容失败 {detail_url}: {e}")
            return ''

    def _parse_zzk_symptom_detail(self, detail_url: str) -> Optional[Dict]:
        """解析症状详情页面"""
        html = self.get_html(detail_url)
        if not html:
            return None
        selector = etree.HTML(html)

        name = ''.join(selector.xpath('//div[contains(@class,"jb-name")]/text()')).strip()
        if not name:
            return None

        match = re.search(r'/(\d+)_', detail_url)
        symptom_id = int(match.group(1)) if match else None
        base_url = 'https://zzk.xywy.com'

        breadcrumb = [t.strip() for t in selector.xpath('//div[contains(@class,"nav-bar")]//a/text()')
                      if t.strip()]
        summary = ''.join(selector.xpath('//div[contains(@class,"jib-rec-hd")]//p//text()')).strip()
        summary = self._clean_text(summary)

        # 提取详情链接并获取完整内容
        sections = selector.xpath('//div[contains(@class,"zz-know")]//div[contains(@class,"jib-")]')
        section_data = {}
        detail_links = {}
        
        for block in sections:
            title = ''.join(block.xpath('.//strong/text()')).strip()
            if not title:
                continue
            
            # 提取详情链接（查找包含"详情"或"更多"的链接）
            detail_link = block.xpath('.//a[contains(@class,"gre") and (contains(text(),"详情") or contains(text(),"更多"))]/@href')
            if not detail_link:
                # 尝试其他可能的链接选择器
                detail_link = block.xpath('.//a[contains(text(),"详情") or contains(text(),"更多")]/@href')
            
            if detail_link:
                full_link = urljoin(base_url, detail_link[0])
                detail_links[title] = full_link
                # 获取完整内容
                full_content = self._extract_detail_content(full_link)
                if full_content:
                    section_data[title] = full_content
                    logger.debug(f"[zzk] 已获取 {title} 的完整内容，长度: {len(full_content)}")
                else:
                    # 如果详情页面获取失败，使用概览页面的内容（清理后）
                    content = ''.join(block.xpath('.//p//text()'))
                    section_data[title] = self._clean_text(content)
            else:
                # 没有详情链接，直接使用概览页面的内容
                content = ''.join(block.xpath('.//p//text()'))
                section_data[title] = self._clean_text(content)

        possible_diseases = []
        disease_rows = selector.xpath('//ul[contains(@class,"loop-tag") and contains(@class,"bor-dash")]')
        for row in disease_rows:
            disease_name = ''.join(row.xpath('.//li[contains(@class,"loop-tag-name")]//text()')).strip()
            disease_link = ''.join(row.xpath('.//li[contains(@class,"loop-tag-name")]//a/@href')).strip()
            typical = ' '.join(t.strip() for t in row.xpath('.//li[contains(@class,"loop-tag-ill")]//text()')
                               if t.strip())
            departments = [t.strip() for t in row.xpath('.//li[contains(@class,"loop-tag-other")]//span/text()')
                           if t.strip()]
            # 跳过表头行（名称、典型症状、就诊科室）
            table_headers = {'名称', '典型症状', '就诊科室'}
            if disease_name and disease_name not in table_headers and len(disease_name) >= 2:
                # 处理相对链接
                if disease_link and not disease_link.startswith('http'):
                    disease_link = urljoin('https://jib.xywy.com', disease_link)
                
                possible_diseases.append({
                    'name': disease_name,
                    'link': disease_link,
                    'typical_symptoms': typical,
                    'departments': departments
                })

        related_symptoms = [t.strip() for t in selector.xpath('//div[contains(@class,"about-zz")]//a/text()') if t.strip()]
        related_symptom_links = [urljoin('https://zzk.xywy.com', href)
                                 for href in selector.xpath('//div[contains(@class,"about-zz")]//a/@href')]

        warning_rows = selector.xpath('//div[contains(@class,"warm-notice")]//p')
        notice = {}
        for row in warning_rows:
            label = ''.join(row.xpath('.//span[contains(@class,"notice-left")]/text()')).strip().rstrip('：:')
            value = ' '.join(t.strip() for t in row.xpath('.//span[contains(@class,"notice-right")]//text()')
                             if t.strip())
            if label:
                notice[label] = value

        image_url = ''.join(selector.xpath('//div[@class="rec-imgbox"]//img/@src')).strip()

        symptom_data = {
            'symptom_id': symptom_id,
            'name': name,
            'url': detail_url,
            'breadcrumb': breadcrumb,
            'summary': summary,
            'cause': section_data.get('病因', ''),
            'prevent': section_data.get('预防', ''),
            'check': section_data.get('检查', ''),
            'identify': section_data.get('鉴别', ''),
            'possible_diseases': possible_diseases,
            'related_symptoms': related_symptoms,
            'related_symptom_links': related_symptom_links,
            'notice': notice,
            'image': image_url,
            'detail_links': detail_links  # 保存详情链接，便于调试
        }
        return symptom_data

    def _save_symptom_record(self, symptom_data: Dict) -> bool:
        """将症状数据写入 raw_spider_data"""
        symptom_id = symptom_data.get('symptom_id')
        if symptom_id is None:
            logger.warning("[zzk] 缺少症状 ID，跳过")
            return False

        storage_page = 2000000 + symptom_id
        serialized = json.dumps(symptom_data, ensure_ascii=False)

        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT id FROM raw_spider_data WHERE page = %s", (storage_page,))
                existing = cursor.fetchone()
                if existing:
                    cursor.execute(
                        "UPDATE raw_spider_data SET data = %s, status = %s WHERE page = %s",
                        (serialized, 'pending', storage_page)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO raw_spider_data (page, data, status) VALUES (%s, %s, %s)",
                        (storage_page, serialized, 'pending')
                    )
                self.conn.commit()
            logger.info(f"[zzk] 保存症状 {symptom_data.get('name')} (ID: {symptom_id}) 成功")
            return True
        except Exception as exc:
            logger.error(f"[zzk] 保存症状 {symptom_data.get('name')} 失败: {exc}")
            self.conn.rollback()
            return False

if __name__ == '__main__':
    # 效率配置（已优化）：
    # - delay_min/delay_max: 每个页面完成后的延迟（秒），默认 0.3-0.8 秒
    # - max_workers: 每个页面的8个子URL并发线程数，默认 8
    # - page_workers: 页面级并发数（同时处理多个页面），默认 3
    # - 双重并发：页面级并发 + 子URL并发，速度提升约 10-20 倍
    # - 建议：如果被封IP，降低 page_workers 到 1-2，或提高延迟
    handler = MedicalSpider(
        delay_min=0.3,      # 页面间延迟：0.3-0.8秒
        delay_max=0.8,
        max_workers=8,      # 每个页面8个子URL并发请求
        page_workers=3      # 同时处理3个页面（新增：多页面并发）
    )
    
    # ========== 从第一页开始爬取的方法 ==========
    # 方法1: 直接指定起始页为1（最简单，推荐）
    handler.spider_main(start_page=1, end_page=10300)  # 从第1页开始，采集到10300页
    
    # 方法2: 删除进度文件后运行（会自动从第1页开始）
    # 删除 prepare_data/spider_progress.json 文件，然后运行：
    # handler.spider_main()
    
    # 方法3: 修改进度文件中的值
    # 将 spider_progress.json 中的 "spider_main": 1210 改为 "spider_main": 0，然后运行：
    # handler.spider_main()
    
    # ========== 其他采集方案 ==========
    # 方案A: 从上次中断的采集进度继续（默认行为）
    #handler.spider_main()  # 自动从上次进度继续
    
    # 方案B: 指定起始页数（会覆盖进度文件中的值）
    # handler.spider_main(start_page=100, end_page=200)  # 从第100页到200页
    
    # 方案C: 采集検查项
    # handler.inspect_crawl()  # 从上次进度继续采集
    # handler.inspect_crawl(start_page=1, end_page=100)  # 正常测试

    # 方案D: 采集症状（zzk.xywy.com）
    # handler.zzk_symptom_spider(limit=100)  # 测试采集前 100 个症状