#!/usr/bin/env python3
# coding: utf-8
# File: verify_tables.py
# Description: 验证 MySQL 数据库表结构是否正确

import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_tables():
    """验证数据库表结构"""
    try:
        # 连接数据库
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '3306')),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'medical_qa'),
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        
        logger.info("=" * 60)
        logger.info("数据库表结构验证")
        logger.info("=" * 60)
        
        with conn.cursor() as cursor:
            # 1. 检查数据库
            cursor.execute("SELECT DATABASE() as db")
            db_name = cursor.fetchone()['db']
            logger.info(f"当前数据库: {db_name}")
            logger.info("")
            
            # 2. 列出所有表
            cursor.execute("SHOW TABLES")
            tables = [list(row.values())[0] for row in cursor.fetchall()]
            logger.info(f"已创建的表 ({len(tables)} 个):")
            for table in tables:
                logger.info(f"  ✓ {table}")
            logger.info("")
            
            # 3. 验证必需的表是否存在
            required_tables = [
                'raw_spider_data',
                'users',
                'conversation_history',
                'feedback'
            ]
            
            missing_tables = [t for t in required_tables if t not in tables]
            if missing_tables:
                logger.error(f"缺失的表: {', '.join(missing_tables)}")
            else:
                logger.info("✓ 所有必需的表都已创建")
            logger.info("")
            
            # 4. 检查每个表的结构
            for table in required_tables:
                if table in tables:
                    logger.info(f"表 '{table}' 结构:")
                    cursor.execute(f"DESCRIBE {table}")
                    columns = cursor.fetchall()
                    for col in columns:
                        nullable = "NULL" if col['Null'] == 'YES' else "NOT NULL"
                        default = f" DEFAULT {col['Default']}" if col['Default'] else ""
                        extra = f" {col['Extra']}" if col['Extra'] else ""
                        logger.info(f"  - {col['Field']:20s} {col['Type']:20s} {nullable}{default}{extra}")
                    
                    # 检查索引
                    cursor.execute(f"SHOW INDEX FROM {table}")
                    indexes = cursor.fetchall()
                    if indexes:
                        logger.info(f"  索引:")
                        unique_indexes = {}
                        for idx in indexes:
                            idx_name = idx['Key_name']
                            if idx_name not in unique_indexes:
                                unique_indexes[idx_name] = []
                            unique_indexes[idx_name].append(idx['Column_name'])
                        
                        for idx_name, columns in unique_indexes.items():
                            unique = "UNIQUE" if idx['Non_unique'] == 0 and idx_name != 'PRIMARY' else ""
                            logger.info(f"    - {idx_name} {unique}: ({', '.join(columns)})")
                    logger.info("")
            
            # 5. 检查 raw_spider_data 表的 JSON 支持
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'raw_spider_data' 
                AND COLUMN_NAME = 'data'
            """, (db_name,))
            json_col = cursor.fetchone()
            if json_col:
                logger.info("✓ raw_spider_data.data 字段类型: JSON")
                if 'json' in json_col['DATA_TYPE'].lower():
                    logger.info("  ✓ MySQL JSON 类型支持正常")
                else:
                    logger.warning(f"  ⚠ 数据类型: {json_col['DATA_TYPE']} (建议使用 JSON 类型)")
            logger.info("")
            
            # 6. 检查表记录数
            logger.info("表记录统计:")
            for table in required_tables:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    count = cursor.fetchone()['count']
                    logger.info(f"  {table:25s}: {count:>6d} 条记录")
            logger.info("")
            
        logger.info("=" * 60)
        logger.info("验证完成！")
        logger.info("=" * 60)
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"验证失败: {e}")
        return False


if __name__ == '__main__':
    verify_tables()

