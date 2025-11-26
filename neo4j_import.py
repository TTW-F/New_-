#!/usr/bin/env python3
# coding: utf-8
# File: neo4j_import.py
# Description: 将 data/medical.json 数据导入 Neo4j 知识图谱

import os
import json
import logging
from typing import Dict, List, Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Neo4jImporter:
    """Neo4j 数据导入工具"""
    
    def __init__(self):
        """初始化 Neo4j 连接"""
        # 从环境变量读取配置，支持多种配置方式
        neo4j_host = os.getenv("NEO4J_HOST", "localhost")
        neo4j_port = os.getenv("NEO4J_PORT", "7687")
        self.uri = os.getenv("NEO4J_URI", f"bolt://{neo4j_host}:{neo4j_port}")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "12345678")
        
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            self.driver.verify_connectivity()
            logger.info(f"Neo4j 连接成功: {self.uri}")
        except Exception as e:
            logger.error(f"Neo4j 连接失败: {e}")
            raise
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j 连接已关闭")
    
    def create_constraints(self):
        """创建唯一性约束和索引"""
        constraints = [
            "CREATE CONSTRAINT disease_name IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE",
            "CREATE CONSTRAINT symptom_name IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT drug_name IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE",
            "CREATE CONSTRAINT check_name IF NOT EXISTS FOR (c:Check) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT department_name IF NOT EXISTS FOR (d:Department) REQUIRE d.name IS UNIQUE",
            "CREATE CONSTRAINT food_name IF NOT EXISTS FOR (f:Food) REQUIRE f.name IS UNIQUE"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"约束创建成功: {constraint}")
                except Exception as e:
                    logger.warning(f"约束创建失败（可能已存在）: {e}")
    
    def clear_database(self):
        """清空数据库（谨慎使用）"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("数据库已清空")
    
    def import_disease(self, disease_data: Dict) -> bool:
        """导入单个疾病及其关系"""
        try:
            # 跳过没有名称的数据
            disease_name = disease_data.get('name', '')
            if not disease_name:
                return False
            
            with self.driver.session() as session:
                # 1. 创建疾病节点
                disease_query = """
                MERGE (d:Disease {name: $name})
                SET d.desc = $desc,
                    d.category = $category,
                    d.yibao_status = $yibao_status,
                    d.get_prob = $get_prob,
                    d.easy_get = $easy_get,
                    d.get_way = $get_way,
                    d.cure_department = $cure_department,
                    d.cure_way = $cure_way,
                    d.cure_lasttime = $cure_lasttime,
                    d.cured_prob = $cured_prob,
                    d.cost_money = $cost_money,
                    d.cause = $cause,
                    d.prevent = $prevent
                RETURN d
                """
                
                session.run(disease_query, {
                    'name': disease_data.get('name', ''),
                    'desc': disease_data.get('desc', ''),
                    'category': disease_data.get('category', []),
                    'yibao_status': disease_data.get('yibao_status', ''),
                    'get_prob': disease_data.get('get_prob', ''),
                    'easy_get': disease_data.get('easy_get', ''),
                    'get_way': disease_data.get('get_way', ''),
                    'cure_department': disease_data.get('cure_department', []),
                    'cure_way': disease_data.get('cure_way', []),
                    'cure_lasttime': disease_data.get('cure_lasttime', ''),
                    'cured_prob': disease_data.get('cured_prob', ''),
                    'cost_money': disease_data.get('cost_money', ''),
                    'cause': disease_data.get('cause', ''),
                    'prevent': disease_data.get('prevent', '')
                })
                
                disease_name = disease_data.get('name', '')
                
                # 2. 创建症状节点和关系
                symptoms = disease_data.get('symptom', [])
                if symptoms:
                    for symptom in symptoms:
                        if symptom:
                            session.run("""
                                MATCH (d:Disease {name: $disease_name})
                                MERGE (s:Symptom {name: $symptom_name})
                                MERGE (d)-[:HAS_SYMPTOM {weight: 0.8}]->(s)
                            """, {'disease_name': disease_name, 'symptom_name': symptom})
                
                # 3. 创建药品节点和关系
                drugs = disease_data.get('recommand_drug', [])
                if drugs:
                    for drug in drugs:
                        if drug:
                            session.run("""
                                MATCH (d:Disease {name: $disease_name})
                                MERGE (dr:Drug {name: $drug_name})
                                MERGE (d)-[:RECOMMAND_DRUG]->(dr)
                            """, {'disease_name': disease_name, 'drug_name': drug})
                
                # 4. 创建检查项节点和关系
                checks = disease_data.get('check', [])
                if checks:
                    for check in checks:
                        if check:
                            session.run("""
                                MATCH (d:Disease {name: $disease_name})
                                MERGE (c:Check {name: $check_name})
                                MERGE (d)-[:NEED_CHECK]->(c)
                            """, {'disease_name': disease_name, 'check_name': check})
                
                # 5. 创建科室节点和关系
                departments = disease_data.get('cure_department', [])
                if isinstance(departments, list):
                    for dept in departments:
                        if dept:
                            session.run("""
                                MATCH (d:Disease {name: $disease_name})
                                MERGE (dep:Department {name: $dept_name})
                                MERGE (d)-[:BELONGS_DEPARTMENT]->(dep)
                            """, {'disease_name': disease_name, 'dept_name': dept})
                
                # 6. 创建食物节点和关系（宜食）
                do_eat = disease_data.get('do_eat', [])
                if do_eat:
                    for food in do_eat:
                        if food:
                            session.run("""
                                MATCH (d:Disease {name: $disease_name})
                                MERGE (f:Food {name: $food_name})
                                MERGE (d)-[:SHOULD_EAT]->(f)
                            """, {'disease_name': disease_name, 'food_name': food})
                
                # 7. 创建食物节点和关系（忌食）
                not_eat = disease_data.get('not_eat', [])
                if not_eat:
                    for food in not_eat:
                        if food:
                            session.run("""
                                MATCH (d:Disease {name: $disease_name})
                                MERGE (f:Food {name: $food_name})
                                MERGE (d)-[:SHOULD_AVOID]->(f)
                            """, {'disease_name': disease_name, 'food_name': food})
                
                # 8. 创建并发症关系
                acompany = disease_data.get('acompany', [])
                if acompany:
                    for comp in acompany:
                        if comp:
                            session.run("""
                                MATCH (d1:Disease {name: $disease_name})
                                MERGE (d2:Disease {name: $comp_name})
                                MERGE (d1)-[:COMPLICATION]->(d2)
                            """, {'disease_name': disease_name, 'comp_name': comp})
                
                return True
                
        except Exception as e:
            logger.error(f"导入疾病失败 [{disease_data.get('name', 'Unknown')}]: {e}")
            return False
    
    def import_disease_batch(self, disease_batch: List[Dict]) -> bool:
        """批量导入疾病数据（大幅提升性能）"""
        try:
            with self.driver.session() as session:
                # 使用事务批量处理
                with session.begin_transaction() as tx:
                    for disease_data in disease_batch:
                        disease_name = disease_data.get('name', '')
                        if not disease_name:
                            continue
                        
                        # 1. 创建疾病节点
                        tx.run("""
                            MERGE (d:Disease {name: $name})
                            SET d.desc = $desc,
                                d.category = $category,
                                d.yibao_status = $yibao_status,
                                d.get_prob = $get_prob,
                                d.easy_get = $easy_get,
                                d.get_way = $get_way,
                                d.cure_department = $cure_department,
                                d.cure_way = $cure_way,
                                d.cure_lasttime = $cure_lasttime,
                                d.cured_prob = $cured_prob,
                                d.cost_money = $cost_money,
                                d.cause = $cause,
                                d.prevent = $prevent
                        """, {
                            'name': disease_name,
                            'desc': disease_data.get('desc', ''),
                            'category': disease_data.get('category', []),
                            'yibao_status': disease_data.get('yibao_status', ''),
                            'get_prob': disease_data.get('get_prob', ''),
                            'easy_get': disease_data.get('easy_get', ''),
                            'get_way': disease_data.get('get_way', ''),
                            'cure_department': disease_data.get('cure_department', []),
                            'cure_way': disease_data.get('cure_way', []),
                            'cure_lasttime': disease_data.get('cure_lasttime', ''),
                            'cured_prob': disease_data.get('cured_prob', ''),
                            'cost_money': disease_data.get('cost_money', ''),
                            'cause': disease_data.get('cause', ''),
                            'prevent': disease_data.get('prevent', '')
                        })
                        
                        # 2. 创建症状节点和关系
                        symptoms = disease_data.get('symptom', [])
                        if symptoms and isinstance(symptoms, list):
                            for symptom in symptoms:
                                if symptom and isinstance(symptom, str):
                                    tx.run("""
                                        MERGE (d:Disease {name: $disease_name})
                                        MERGE (s:Symptom {name: $symptom_name})
                                        MERGE (d)-[:HAS_SYMPTOM {weight: 0.8}]->(s)
                                    """, {
                                        'disease_name': disease_name, 
                                        'symptom_name': symptom.strip()
                                    })
                        
                        # 3. 创建药品节点和关系
                        drugs = disease_data.get('recommand_drug', [])
                        if drugs and isinstance(drugs, list):
                            for drug in drugs:
                                if drug and isinstance(drug, str):
                                    tx.run("""
                                        MERGE (d:Disease {name: $disease_name})
                                        MERGE (dr:Drug {name: $drug_name})
                                        MERGE (d)-[:RECOMMAND_DRUG]->(dr)
                                    """, {
                                        'disease_name': disease_name, 
                                        'drug_name': drug.strip()
                                    })
                        
                        # 4. 创建检查项节点和关系
                        checks = disease_data.get('check', [])
                        if checks and isinstance(checks, list):
                            for check in checks:
                                if check and isinstance(check, str):
                                    tx.run("""
                                        MERGE (d:Disease {name: $disease_name})
                                        MERGE (c:Check {name: $check_name})
                                        MERGE (d)-[:NEED_CHECK]->(c)
                                    """, {
                                        'disease_name': disease_name, 
                                        'check_name': check.strip()
                                    })
                        
                        # 5. 创建科室节点和关系
                        departments = disease_data.get('cure_department', [])
                        if departments and isinstance(departments, list):
                            for dept in departments:
                                if dept and isinstance(dept, str):
                                    tx.run("""
                                        MERGE (d:Disease {name: $disease_name})
                                        MERGE (dep:Department {name: $dept_name})
                                        MERGE (d)-[:BELONGS_DEPARTMENT]->(dep)
                                    """, {
                                        'disease_name': disease_name, 
                                        'dept_name': dept.strip()
                                    })
                        
                        # 6. 创建食物节点和关系（宜食）
                        do_eat = disease_data.get('do_eat', [])
                        if do_eat and isinstance(do_eat, list):
                            for food in do_eat:
                                if food and isinstance(food, str):
                                    tx.run("""
                                        MERGE (d:Disease {name: $disease_name})
                                        MERGE (f:Food {name: $food_name})
                                        MERGE (d)-[:SHOULD_EAT]->(f)
                                    """, {
                                        'disease_name': disease_name, 
                                        'food_name': food.strip()
                                    })
                        
                        # 6.5. 创建食物节点和关系（推荐食物）
                        recommand_eat = disease_data.get('recommand_eat', [])
                        if recommand_eat and isinstance(recommand_eat, list):
                            for food in recommand_eat:
                                if food and isinstance(food, str):
                                    tx.run("""
                                        MERGE (d:Disease {name: $disease_name})
                                        MERGE (f:Food {name: $food_name})
                                        MERGE (d)-[:SHOULD_EAT {recommend: true}]->(f)
                                    """, {
                                        'disease_name': disease_name, 
                                        'food_name': food.strip()
                                    })
                        
                        # 7. 创建食物节点和关系（忌食）
                        not_eat = disease_data.get('not_eat', [])
                        if not_eat and isinstance(not_eat, list):
                            for food in not_eat:
                                if food and isinstance(food, str):
                                    tx.run("""
                                        MERGE (d:Disease {name: $disease_name})
                                        MERGE (f:Food {name: $food_name})
                                        MERGE (d)-[:SHOULD_AVOID]->(f)
                                    """, {
                                        'disease_name': disease_name, 
                                        'food_name': food.strip()
                                    })
                        
                        # 8. 创建并发症关系
                        acompany = disease_data.get('acompany', [])
                        if acompany and isinstance(acompany, list):
                            for comp in acompany:
                                if comp and isinstance(comp, str):
                                    tx.run("""
                                        MERGE (d1:Disease {name: $disease_name})
                                        MERGE (d2:Disease {name: $comp_name})
                                        MERGE (d1)-[:COMPLICATION]->(d2)
                                    """, {
                                        'disease_name': disease_name, 
                                        'comp_name': comp.strip()
                                    })
                    
                    # 提交事务
                    tx.commit()
            return True
        except Exception as e:
            logger.error(f"批量导入失败: {e}")
            return False
    
    def _clean_disease_data(self, disease_data: Dict) -> Optional[Dict]:
        """
        清洗疾病数据，移除不需要的字段（如 MongoDB _id）
        
        Args:
            disease_data: 原始疾病数据字典
            
        Returns:
            清洗后的数据字典，如果数据无效则返回 None
        """
        if not isinstance(disease_data, dict):
            return None
        
        cleaned = disease_data.copy()
        
        # 移除 MongoDB _id 字段
        if '_id' in cleaned:
            del cleaned['_id']
        
        # 确保关键字段存在且格式正确
        if 'name' not in cleaned or not cleaned['name']:
            logger.warning(f"跳过无效数据：缺少 name 字段")
            return None
        
        # 确保 name 是字符串
        if not isinstance(cleaned['name'], str):
            cleaned['name'] = str(cleaned['name'])
        
        # 处理字符串字段，去除前后空格
        for key in ['desc', 'yibao_status', 'get_prob', 'easy_get', 'get_way', 
                    'cure_lasttime', 'cured_prob', 'cost_money', 'cause', 'prevent']:
            if key in cleaned:
                if cleaned[key] is None:
                    cleaned[key] = ''
                elif not isinstance(cleaned[key], str):
                    cleaned[key] = str(cleaned[key])
                else:
                    cleaned[key] = cleaned[key].strip()
        
        # 处理列表字段，确保是列表类型并过滤空值
        for key in ['category', 'symptom', 'recommand_drug', 'check', 'cure_department', 
                    'cure_way', 'acompany', 'do_eat', 'not_eat', 'recommand_eat', 'drug_detail']:
            if key in cleaned:
                if cleaned[key] is None:
                    cleaned[key] = []
                elif not isinstance(cleaned[key], list):
                    if isinstance(cleaned[key], str) and cleaned[key]:
                        # 尝试分割字符串（使用逗号或空格）
                        cleaned[key] = [i.strip() for i in cleaned[key].replace(',', ' ').split() if i.strip()]
                    else:
                        cleaned[key] = []
                else:
                    # 过滤空值和非字符串值
                    cleaned[key] = [item.strip() if isinstance(item, str) else str(item).strip() 
                                   for item in cleaned[key] if item]
        
        return cleaned
    
    def import_from_json(self, json_file: str, batch_size: int = 100):
        """
        从 JSON 文件批量导入数据
        
        支持两种格式：
        1. JSONL 格式（每行一个 JSON 对象）
        2. 标准 JSON 数组格式
        
        Args:
            json_file: JSON 文件路径
            batch_size: 批处理大小（默认 100，避免事务过大）
        """
        if not os.path.exists(json_file):
            logger.error(f"文件不存在: {json_file}")
            return
        
        logger.info(f"开始从 {json_file} 导入数据...")
        
        # 尝试读取数据（支持两种格式）
        data = []
        try:
            # 先尝试作为标准 JSON 数组读取
            with open(json_file, 'r', encoding='utf-8') as f:
                file_content = f.read().strip()
                
                # 判断文件格式
                if file_content.startswith('['):
                    # 标准 JSON 数组格式
                    logger.info("检测到标准 JSON 数组格式")
                    data = json.loads(file_content)
                else:
                    # JSONL 格式（每行一个 JSON 对象）
                    logger.info("检测到 JSONL 格式（每行一个 JSON 对象）")
                    f.seek(0)  # 重置文件指针
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            item = json.loads(line)
                            cleaned = self._clean_disease_data(item)
                            if cleaned:
                                data.append(cleaned)
                        except json.JSONDecodeError as e:
                            logger.warning(f"第 {line_num} 行 JSON 解析失败: {e}")
                            continue
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            return
        
        if not data:
            logger.warning("未找到有效数据")
            return
        
        total = len(data)
        success_count = 0
        fail_count = 0
        
        logger.info(f"总计 {total} 条数据待导入，批处理大小: {batch_size}")
        
        # 使用进度条
        with tqdm(total=total, desc="导入进度", unit="条") as pbar:
            # 分批处理
            for i in range(0, total, batch_size):
                batch = data[i:i + batch_size]
                # 再次清洗批次数据
                cleaned_batch = []
                for item in batch:
                    cleaned = self._clean_disease_data(item)
                    if cleaned:
                        cleaned_batch.append(cleaned)
                
                if cleaned_batch:
                    if self.import_disease_batch(cleaned_batch):
                        success_count += len(cleaned_batch)
                        pbar.update(len(cleaned_batch))
                    else:
                        fail_count += len(cleaned_batch)
                        pbar.update(len(cleaned_batch))
                        logger.warning(f"批次 {i//batch_size + 1} 导入失败")
        
        logger.info("=" * 60)
        logger.info(f"导入完成！成功: {success_count}, 失败: {fail_count}, 总计: {total}")
        logger.info("=" * 60)
    
    def verify_import(self):
        """验证导入结果"""
        with self.driver.session() as session:
            # 统计各类节点数量
            stats_queries = {
                'Disease': "MATCH (d:Disease) RETURN COUNT(d) as count",
                'Symptom': "MATCH (s:Symptom) RETURN COUNT(s) as count",
                'Drug': "MATCH (d:Drug) RETURN COUNT(d) as count",
                'Check': "MATCH (c:Check) RETURN COUNT(c) as count",
                'Department': "MATCH (d:Department) RETURN COUNT(d) as count",
                'Food': "MATCH (f:Food) RETURN COUNT(f) as count"
            }
            
            logger.info("=" * 60)
            logger.info("数据导入统计：")
            logger.info("-" * 60)
            for label, query in stats_queries.items():
                result = session.run(query)
                count = result.single()['count']
                logger.info(f"  {label:15s}: {count:>8d} 个节点")
            
            # 统计关系数量
            rel_count = session.run("MATCH ()-[r]->() RETURN COUNT(r) as count").single()['count']
            logger.info(f"  {'总关系数':15s}: {rel_count:>8d} 条关系")
            
            # 统计各类关系数量
            rel_types = {
                'HAS_SYMPTOM': '症状关系',
                'RECOMMAND_DRUG': '药品关系',
                'NEED_CHECK': '检查关系',
                'BELONGS_DEPARTMENT': '科室关系',
                'SHOULD_EAT': '宜食关系',
                'SHOULD_AVOID': '忌食关系',
                'COMPLICATION': '并发症关系'
            }
            logger.info("-" * 60)
            logger.info("关系类型统计：")
            for rel_type, desc in rel_types.items():
                result = session.run(
                    f"MATCH ()-[r:{rel_type}]->() RETURN COUNT(r) as count"
                )
                count = result.single()['count']
                if count > 0:
                    logger.info(f"  {desc:15s} ({rel_type:20s}): {count:>6d} 条")
            logger.info("=" * 60)


def main():
    """主函数"""
    importer = Neo4jImporter()
    
    try:
        # 1. 创建约束
        logger.info("步骤 1/4: 创建约束和索引...")
        importer.create_constraints()
        
        # 2. 清空数据库（可选，谨慎使用）
        # logger.warning("步骤 2/4: 清空现有数据...")
        # importer.clear_database()
        
        # 3. 导入数据
        logger.info("步骤 2/4: 导入数据...")
        json_file = os.path.join(
            os.path.dirname(__file__),
            'data',
            'medical_data.json'  # 修正：使用 build_data.py 输出的文件名
        )
        importer.import_from_json(json_file)
        
        # 4. 验证导入
        logger.info("步骤 3/4: 验证导入结果...")
        importer.verify_import()
        
        logger.info("全部完成！")
        
    except Exception as e:
        logger.error(f"导入过程出错: {e}")
    finally:
        importer.close()


if __name__ == '__main__':
    main()
