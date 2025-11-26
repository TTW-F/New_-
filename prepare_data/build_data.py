#!/usr/bin/env python3
# coding: utf-8
# File: build_data.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-3
import pymysql
from pymysql.cursors import DictCursor
from lxml import etree
import os
from max_cut import CutWords
import logging
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MedicalGraph:
    def __init__(self, output_format='json'):
        """
        初始化医疗知识图谱数据处理器（使用 MySQL）
        :param output_format: 输出格式，'json' 或 'neo4j'
        """
        try:
            # 从环境变量读取 MySQL 配置
            self.conn = pymysql.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', '3306')),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'medical_qa'),
                charset='utf8mb4',
                cursorclass=DictCursor
            )
            self.conn.ping(reconnect=True)
            logger.info("MySQL 连接成功")
        except Exception as e:
            logger.error(f"MySQL 连接失败: {e}")
            raise
        
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_format = output_format
        
        # 加载停用词
        first_name_path = os.path.join(cur_dir, 'first_name.txt')
        if os.path.exists(first_name_path):
            with open(first_name_path, encoding='utf-8') as f:
                first_words = [i.strip() for i in f if i.strip()]
        else:
            logger.warning(f"first_name.txt 不存在，使用默认停用词")
            first_words = []
        
        alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                     't', 'u', 'v', 'w', 'x', 'y', 'z']
        nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        self.stop_words = first_words + alphabets + nums
        self.key_dict = {
            '医保疾病': 'yibao_status',
            "患病比例": "get_prob",
            "易感人群": "easy_get",
            "传染方式": "get_way",
            "就诊科室": "cure_department",
            "治疗方式": "cure_way",
            "治疗周期": "cure_lasttime",
            "治愈率": "cured_prob",
            '药品明细': 'drug_detail',
            '药品推荐': 'recommand_drug',
            '推荐': 'recommand_eat',
            '忌食': 'not_eat',
            '宜食': 'do_eat',
            '症状': 'symptom',
            '检查': 'check',
            '成因': 'cause',
            '预防措施': 'prevent',
            '所属类别': 'category',
            '简介': 'desc',
            '名称': 'name',
            '常用药品': 'common_drug',
            '治疗费用': 'cost_money',
            '并发症': 'acompany'
        }
        
        # 初始化分词器
        disease_dict_path = os.path.join(cur_dir, 'disease.txt')
        if os.path.exists(disease_dict_path):
            self.cuter = CutWords(disease_dict_path)
        else:
            logger.warning(f"disease.txt 不存在，分词功能可能不可用")
            self.cuter = None

    def collect_medical(self, output_file=None):
        """
        从 MySQL 采集医疗数据并输出
        :param output_file: 输出文件路径
        """
        if output_file is None:
            cur_dir = os.path.dirname(os.path.abspath(__file__))
            output_file = os.path.join(os.path.dirname(cur_dir), 'data', 'medical_data.json')
        
        cates = []
        inspects = []
        count = 0
        all_data = []
        
        # 从 MySQL 读取爬虫采集的数据
        # 修改：处理所有状态的数据（不限制 status），只要包含 basic_info 且疾病名称不为空即可
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT data FROM raw_spider_data 
                WHERE JSON_EXTRACT(data, '$.basic_info') IS NOT NULL
                AND JSON_EXTRACT(data, '$.basic_info.name') IS NOT NULL
                AND JSON_EXTRACT(data, '$.basic_info.name') != ''
                AND JSON_EXTRACT(data, '$.basic_info.name') != 'null'
                """
            )
            rows = cursor.fetchall()
            total_docs = len(rows)
            logger.info(f"开始处理，总计 {total_docs} 条数据（包含所有状态的有效数据）")
        
        for row in rows:
            # 解析 JSON 数据
            item = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
            try:
                data = {}
                basic_info = item.get('basic_info', {})
                name = basic_info.get('name', '')
                
                if not name:
                    continue
                
                # 基本信息
                data['名称'] = name
                desc_text = '\n'.join(basic_info.get('desc', [])) if basic_info.get('desc') else ''
                data['简介'] = desc_text.replace('\r\n\t', '').replace('\r\n\n\n', '').replace(' ', '').replace(
                    '\r\n', '\n')
                
                category = basic_info.get('category', [])
                data['所属类别'] = category
                cates += category
                
                inspect = item.get('inspect_info', [])
                inspects += inspect
                
                attributes = basic_info.get('attributes', [])
                
                # 成因及预防
                data['预防措施'] = item.get('prevent_info', '')
                data['成因'] = item.get('cause_info', '')
                
                # 症状 - 修复格式适配问题：symptom_info 是字典格式 {'symptoms': [...], 'symptoms_detail': [...]}
                symptom_info = item.get('symptom_info', {})
                if symptom_info and isinstance(symptom_info, dict):
                    symptoms = symptom_info.get('symptoms', [])
                    data['症状'] = list(set([i for i in symptoms if len(i) > 0 and i[0] not in self.stop_words]))
                elif symptom_info and isinstance(symptom_info, list) and len(symptom_info) > 0:
                    # 兼容旧格式（列表格式）
                    data['症状'] = list(set([i for i in symptom_info[0] if len(i) > 0 and i[0] not in self.stop_words]))
                else:
                    data['症状'] = []
                
                # 处理属性
                for attr in attributes:
                    attr_pair = attr.split('：')
                    if len(attr_pair) == 2:
                        key = attr_pair[0]
                        value = attr_pair[1]
                        data[key] = value
                
                # 检查
                inspects = item.get('inspect_info', [])
                jcs = []
                for inspect in inspects:
                    jc_name = self.get_inspect(inspect)
                    if jc_name:
                        jcs.append(jc_name)
                data['检查'] = jcs
                
                # 食物
                food_info = item.get('food_info', {})
                if food_info:
                    data['宜食'] = food_info.get('good', [])
                    data['忌食'] = food_info.get('bad', [])
                    data['推荐'] = food_info.get('recommand', [])
                
                # 药品
                drug_info = item.get('drug_info', [])
                if drug_info:
                    data['药品推荐'] = list(set([i.split('(')[-1].replace(')', '') for i in drug_info]))
                    data['药品明细'] = drug_info
                else:
                    data['药品推荐'] = []
                    data['药品明细'] = []
                
                # 转换为英文key
                data_modify = {}
                for attr, value in data.items():
                    attr_en = self.key_dict.get(attr)
                    if attr_en:
                        data_modify[attr_en] = value
                        
                        # 处理特定字段
                        if attr_en in ['yibao_status', 'get_prob', 'easy_get', 'get_way', "cure_lasttime",
                                       "cured_prob"]:
                            if isinstance(value, str):
                                data_modify[attr_en] = value.replace(' ', '').replace('\t', '')
                        elif attr_en in ['cure_department', 'cure_way', 'common_drug']:
                            if isinstance(value, str):
                                data_modify[attr_en] = [i for i in value.split(' ') if i]
                            else:
                                data_modify[attr_en] = value if isinstance(value, list) else []
                        elif attr_en == 'acompany' and self.cuter:
                            if isinstance(value, str) and value:
                                acompany = [i for i in self.cuter.max_biward_cut(value) if len(i) > 1]
                                data_modify[attr_en] = acompany
                
                all_data.append(data_modify)
                count += 1
                
                if count % 100 == 0:
                    logger.info(f"已处理 {count} 条数据")
                
            except Exception as e:
                logger.error(f"处理数据失败: {e}, 疾病名称: {name if 'name' in locals() else 'Unknown'}")
                continue
        
        # 输出数据
        if self.output_format == 'json':
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已保存到: {output_file}, 总计 {count} 条")
        
        elif self.output_format == 'neo4j':
            # 如果需要直接写入Neo4j，可以在这里添加逻辑
            logger.info("待实现: 直接写入Neo4j")
            # TODO: 实现Neo4j导入逻辑
        
        return all_data


    def get_inspect(self, url):
        """获取检查项名称（从 MySQL）"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT JSON_EXTRACT(data, '$.name') as name FROM raw_spider_data WHERE JSON_EXTRACT(data, '$.url') = %s AND JSON_EXTRACT(data, '$.type') = 'inspect' LIMIT 1",
                    (url,)
                )
                result = cursor.fetchone()
                if result and result.get('name'):
                    # JSON_EXTRACT 返回带引号的字符串，需要去除
                    name = result['name']
                    if isinstance(name, str):
                        name = name.strip('"')
                    return name
                return ''
        except Exception as e:
            logger.warning(f"获取检查项失败 {url}: {e}")
            return ''

    def modify_jc(self):
        """修正检查项数据（使用 MySQL）"""
        count = 0
        
        with self.conn.cursor() as cursor:
            # 查询所有检查项数据
            cursor.execute(
                "SELECT id, data FROM raw_spider_data WHERE JSON_EXTRACT(data, '$.type') = 'inspect'"
            )
            items = cursor.fetchall()
            
            logger.info(f"开始修正检查项数据，总计 {len(items)} 条")
        
        for item in items:
            try:
                data = json.loads(item['data']) if isinstance(item['data'], str) else item['data']
                url = data.get('url', '')
                content = data.get('html', '')
                
                if not content:
                    continue
                
                selector = etree.HTML(content)
                
                title_list = selector.xpath('//title/text()')
                if not title_list:
                    continue
                    
                name = title_list[0].split('结果分析')[0]
                
                desc_list = selector.xpath('//meta[@name="description"]/@content')
                desc = desc_list[0].replace('\r\n\t', '') if desc_list else ''
                
                # 更新数据
                data['name'] = name
                data['desc'] = desc
                
                with self.conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE raw_spider_data SET data = %s WHERE id = %s",
                        (json.dumps(data, ensure_ascii=False), item['id'])
                    )
                    self.conn.commit()
                
                count += 1
                
                if count % 100 == 0:
                    logger.info(f"已修正 {count} 条检查项数据")
                    
            except Exception as e:
                logger.error(f"修正检查项失败: {e}")
                self.conn.rollback()
                continue
        
        logger.info(f"检查项数据修正完成，总计 {count} 条")


if __name__ == '__main__':
    # 示例用法
    handler = MedicalGraph(output_format='json')
    
    # 1. 采集数据并输出为JSON
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'medical_data.json')
    handler.collect_medical(output_file=output_file)
    
    # 2. 修正检查项数据（如果需要）
    # handler.modify_jc()
    
    logger.info("数据处理完成")
    handler.conn.close()
