-- ============================================================
-- 医疗诊断智能问答系统 - 数据库表结构
-- 数据库: medical_qa
-- 字符集: utf8mb4
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS medical_qa 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE medical_qa;

-- ============================================================
-- 1. raw_spider_data 表 - 原始爬虫数据存储
-- ============================================================
-- 此表用于存储爬虫采集的原始医疗数据
-- data 字段存储 JSON 格式的原始数据，包含：
--   - basic_info: 基本信息（name, desc, category, attributes）
--   - symptom_info: 症状信息
--   - inspect_info: 检查项目信息
--   - drug_info: 药品信息
--   - food_info: 食物信息（good, bad, recommand）
--   - prevent_info: 预防措施
--   - cause_info: 成因
--   - type: 数据类型（disease/inspect）
CREATE TABLE IF NOT EXISTS raw_spider_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    page INT NOT NULL COMMENT '爬取的页码',
    data JSON NOT NULL COMMENT '原始JSON数据',
    status ENUM('pending', 'processed', 'failed') DEFAULT 'pending' COMMENT '处理状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_page (page) COMMENT '页码索引',
    INDEX idx_status (status) COMMENT '状态索引',
    INDEX idx_data_type ((JSON_EXTRACT(data, '$.type'))) COMMENT '数据类型索引'
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='原始爬虫数据表';

-- ============================================================
-- 2. users 表 - 用户信息表
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    user_type ENUM('doctor', 'patient', 'admin') DEFAULT 'patient' COMMENT '用户类型',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    INDEX idx_username (username) COMMENT '用户名索引',
    INDEX idx_email (email) COMMENT '邮箱索引',
    INDEX idx_user_type (user_type) COMMENT '用户类型索引'
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='用户信息表';

-- ============================================================
-- 3. conversation_history 表 - 对话历史表
-- ============================================================
CREATE TABLE IF NOT EXISTS conversation_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    session_id VARCHAR(100) NOT NULL COMMENT '会话ID',
    question TEXT NOT NULL COMMENT '用户问题',
    answer TEXT COMMENT '系统回答',
    related_entities JSON COMMENT '相关实体（疾病、症状、药品等）',
    citations JSON COMMENT '引用来源',
    response_time INT COMMENT '响应时间（毫秒）',
    model_version VARCHAR(50) COMMENT '使用的模型版本',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id) COMMENT '用户ID索引',
    INDEX idx_session_id (session_id) COMMENT '会话ID索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引'
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='对话历史表';

-- ============================================================
-- 4. feedback 表 - 用户反馈表
-- ============================================================
CREATE TABLE IF NOT EXISTS feedback (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    conversation_id INT NOT NULL COMMENT '对话ID',
    rating INT CHECK (rating >= 1 AND rating <= 5) COMMENT '评分（1-5）',
    feedback_type ENUM('helpful', 'incorrect', 'unclear', 'other') COMMENT '反馈类型',
    comment TEXT COMMENT '反馈内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversation_history(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id) COMMENT '用户ID索引',
    INDEX idx_conversation_id (conversation_id) COMMENT '对话ID索引',
    INDEX idx_rating (rating) COMMENT '评分索引'
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='用户反馈表';

-- ============================================================
-- 初始化完成提示
-- ============================================================
SELECT '数据库表结构创建完成！' AS message;
SELECT '表列表：' AS info;
SHOW TABLES;

