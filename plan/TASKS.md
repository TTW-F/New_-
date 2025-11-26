# 医疗诊断智能问答系统 - 任务清单 (TASKS)

基于 `spec.md` 和 `plan.md`，本文档将项目分解为具体的、可执行的开发任务。

---

## 📋 任务总体结构

```
Phase 1: 环境和基础设施准备
Phase 2: 数据管道（采集、清洗、导入）
Phase 3: LangChain RAG 核心实现
Phase 4: API 服务实现
Phase 5: 测试和验证
Phase 6: 部署和优化
```

---

## Phase 1: 环境和基础设施准备

### Task 1.1: Python 环境配置
**目标**：确保 Python 环境和依赖安装完整
**步骤**：
1. [ ] 检查 Python 版本 >= 3.8
2. [ ] 创建虚拟环境（可选但推荐）
3. [ ] 安装 requirements.txt 中的所有依赖
4. [ ] 验证关键包安装成功（langchain, sentence-transformers, faiss-cpu）

**验证命令**：
```bash
python --version
pip list | grep langchain
pip list | grep faiss
```

**预期输出**：
- Python 3.8+
- langchain >= 0.1.0
- faiss-cpu >= 1.7.4
- sentence-transformers >= 2.2.0

---

### Task 1.2: 数据库初始化
**目标**：初始化 MySQL 和 Neo4j 数据库
**步骤**：
1. [ ] 创建 MySQL 数据库 `medical_qa`
2. [ ] 创建以下 MySQL 表：
   - `users` - 用户表
   - `raw_spider_data` - 原始爬虫数据
   - `conversation_history` - 对话历史
   - `feedback` - 用户反馈

3. [ ] 验证 Neo4j 连接可用
4. [ ] 在 Neo4j 中创建约束和索引

**SQL 脚本**（保存为 `db/schema.sql`）：
```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS medical_qa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE medical_qa;

-- users 表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('doctor', 'patient', 'admin') DEFAULT 'patient',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
) CHARACTER SET utf8mb4;

-- raw_spider_data 表
CREATE TABLE raw_spider_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    page INT NOT NULL,
    data JSON NOT NULL,
    status ENUM('pending', 'processed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_page (page),
    INDEX idx_status (status)
) CHARACTER SET utf8mb4;

-- conversation_history 表
CREATE TABLE conversation_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT,
    related_entities JSON,
    citations JSON,
    response_time INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id)
) CHARACTER SET utf8mb4;

-- feedback 表
CREATE TABLE feedback (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    conversation_id INT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    feedback_type ENUM('helpful', 'incorrect', 'unclear', 'other'),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (conversation_id) REFERENCES conversation_history(id),
    INDEX idx_user_id (user_id)
) CHARACTER SET utf8mb4;
```

---

### Task 1.3: 环境变量配置
**目标**：完成 `.env` 文件配置
**步骤**：
1. [ ] 编辑 `.env` 文件
2. [ ] 填入 DeepSeek API Key
3. [ ] 填入数据库连接信息
4. [ ] 填入嵌入模型路径

**关键变量**：
```
DEEPSEEK_API_KEY=your_key_here
EMBEDDING_MODEL_PATH=D:\Qwen3-Embedding-8B
DB_HOST=localhost
DB_USER=root
NEO4J_HOST=localhost
```

---

## Phase 2: 数据管道（采集、清洗、导入）

### Task 2.1: 完善数据爬虫 (`data_spider.py`)
**目标**：优化爬虫，确保能稳定采集医疗数据
**步骤**：
1. [x] 审查现有 `data_spider.py` 代码
2. [x] 完善错误处理和重试机制
3. [x] 实现断点续传（记录采集进度）
4. [x] 添加日志记录
5. [x] 优化采集效率（降低延迟、添加速率统计）
6. [x] 添加无效页面检测和处理
7. [ ] 测试爬虫能否正常运行

**关键检查点**：
- [x] 爬虫能否连接到 `https://jib.xywy.com`（已更新为 HTTPS）
- [x] 能否正确解析页面内容（已优化错误处理）
- [x] 是否正确存储到 MySQL `raw_spider_data` 表
- [x] 能否从断点恢复（已实现进度保存）
- [x] 采集效率优化（延迟从 2-4 秒降低到 0.5-1.5 秒）

**完成情况**：
- ✅ 添加可配置延迟参数（默认 0.5-1.5 秒，提升 2-4 倍速度）
- ✅ 添加采集速率统计和 ETA 估算
- ✅ 优化错误处理，支持无效页面检测
- ✅ 统一延迟控制到所有采集方法
- ✅ 支持症状站点采集（zzk.xywy.com）

**测试命令**：
```bash
python prepare_data/data_spider.py
# 查看 MySQL 中是否有数据
mysql medical_qa -e "SELECT COUNT(*) FROM raw_spider_data;"
```

---

### Task 2.2: 数据清洗和规范化 (`build_data.py`)
**目标**：从原始数据中提取结构化的医学实体
**步骤**：
1. [x] 审查 `build_data.py` 代码
2. [x] 实现从 JSON 数据中提取：
   - [x] 疾病名称、描述
   - [x] 症状列表（修复格式适配问题）
   - [x] 推荐药物
   - [x] 所属科室
3. [x] 实现数据验证（去重、格式检查）
4. [x] 输出结构化数据格式
5. [x] 修复症状数据格式不匹配问题

**完成情况**：
- ✅ 修复症状数据格式适配：支持字典格式 `{'symptoms': [...], 'symptoms_detail': [...]}`
- ✅ 兼容旧格式（列表格式）
- ✅ 数据流程验证：`data_spider.py` → `build_data.py` → `neo4j_import.py` 完全适配

**输出格式示例**：
```json
{
  "name": "感冒",
  "desc": "由病毒引起的呼吸道感染",
  "category": ["呼吸科"],
  "symptom": ["发热", "咳嗽"],
  "recommand_drug": ["退烧药"],
  "cure_department": ["呼吸科"]
}
```

**测试命令**：
```bash
python prepare_data/build_data.py
# 验证输出数据结构
# 输出文件：data/medical_data.json
```

---

### Task 2.3: Neo4j 数据导入 (`neo4j_import.py`)
**目标**：将清洗后的数据导入 Neo4j 知识图谱
**步骤**：
1. [ ] 创建 Neo4j 连接模块
2. [ ] 创建节点创建函数：
   - Disease（疾病）
   - Symptom（症状）
   - Drug（药品）
   - Department（科室）
3. [ ] 创建关系创建函数：
   - Disease -[:HAS_SYMPTOM]-> Symptom
   - Disease -[:RECOMMAND_DRUG]-> Drug
   - Disease -[:BELONGS_DEPARTMENT]-> Department
4. [ ] 实现批量导入和去重逻辑
5. [ ] 添加索引和约束

**关键 Cypher 查询**：
```cypher
-- 创建约束
CREATE CONSTRAINT disease_name IF NOT EXISTS
FOR (d:Disease) REQUIRE d.name IS UNIQUE;

-- 创建节点
MERGE (d:Disease {name: "感冒"})
SET d.description = "由病毒引起的呼吸道感染"
RETURN d;

-- 创建关系
MATCH (d:Disease {name: "感冒"})
MATCH (s:Symptom {name: "发热"})
MERGE (d)-[:HAS_SYMPTOM {weight: 0.8}]->(s);
```

**验证命令**：
```bash
python neo4j_import.py
# 在 Neo4j 中验证
neo4j> MATCH (d:Disease) RETURN COUNT(d);
```

---

## Phase 3: LangChain RAG 核心实现

### Task 3.1: 完成 `graphrag_service.py` 实现
**目标**：完成 LangChainRAGService 类的所有方法
**步骤**：
1. [ ] 验证 `__init__` 方法能正确加载本地嵌入模型
2. [ ] 实现 `build_index()` 方法：
   - 文本分割
   - 向量化
   - FAISS 索引创建和保存
3. [ ] 实现 `_build_qa_chain()` 方法：
   - 创建医疗提示词
   - 初始化 RetrievalQA 链
4. [ ] 实现 `query_knowledge_graph()` 方法
5. [ ] 实现 `load_index()` 和 `save_index()`

**测试代码**（在 `if __name__ == "__main__"` 中运行）：
```python
# 测试服务初始化
service = get_langchain_rag_service()

# 测试文档索引
docs = [
    {"id": "1", "source": "kb", "text": "感冒是由病毒引起的呼吸道感染..."},
    {"id": "2", "source": "kb", "text": "头痛是常见的神经症状..."}
]
success = service.build_index(docs)
assert success, "索引构建失败"

# 测试查询
result = service.query_knowledge_graph("我头痛了怎么办？")
assert result["status"] == "success"
print(result["answer"])
```

---

### Task 3.2: 完善 `qa_service.py`
**目标**：完成问答服务与数据库的集成
**步骤**：
1. [ ] 验证 `process_question()` 方法能正确调用 LangChain RAG
2. [ ] 完善 `_extract_entities()` 方法（从答案中提取医学实体）
3. [ ] 完善 `_format_citations()` 方法（格式化引用信息）
4. [ ] 验证 `_save_conversation()` 能正确保存到 MySQL
5. [ ] 实现 `get_conversation_history()` 查询
6. [ ] 实现 `save_feedback()` 反馈保存

**集成测试**：
```python
service = get_qa_service()
result = service.process_question(
    user_id=1,
    question="我有头痛和发热，应该怎么办？",
    session_id="test_session",
    user_type="patient"
)
assert result["status"] == "success"
assert "answer" in result
```

---

## Phase 4: API 服务实现

### Task 4.1: 完善 FastAPI 应用 (`main.py`)
**目标**：完成所有 API 端点实现
**步骤**：
1. [ ] 测试 `/api/v1/auth/register` 端点
2. [ ] 测试 `/api/v1/auth/login` 端点
3. [ ] 测试 `/api/v1/qa` 端点（核心问答）
4. [ ] 测试 `/api/v1/qa/history` 端点
5. [ ] 测试 `/api/v1/search` 端点
6. [ ] 测试 `/api/v1/feedback` 端点
7. [ ] 添加全局异常处理
8. [ ] 添加请求日志

**本地测试**：
```bash
# 启动 API 服务
python main.py

# 在另一个终端测试
curl -X POST "http://127.0.0.1:8000/api/v1/qa" \
  -H "Content-Type: application/json" \
  -d '{"question": "我头痛了怎么办？"}'

# 或访问 Swagger UI
# http://127.0.0.1:8000/docs
```

---

### Task 4.2: 添加认证和授权
**目标**：实现 JWT token 认证（可选升级）
**步骤**：
1. [ ] 安装 `python-jose` 和 `passlib`
2. [ ] 实现密码加密
3. [ ] 实现 JWT token 生成和验证
4. [ ] 添加依赖注入的当前用户获取

**简单版本**（当前已有）：
- 用户注册/登录保存到内存
- 返回简单 token

**升级版本**（可选）：
- 密码使用 bcrypt 加密
- JWT token 签名验证
- token 过期时间设置

---

## Phase 5: 测试和验证

### Task 5.1: 单元测试
**目标**：为核心模块编写单元测试
**步骤**：
1. [ ] 为 `graphrag_service.py` 编写测试（创建 `tests/test_graphrag_service.py`）
2. [ ] 为 `qa_service.py` 编写测试（创建 `tests/test_qa_service.py`）
3. [ ] 为 `main.py` API 端点编写集成测试（创建 `tests/test_api.py`）

**测试框架**：使用 `pytest`
```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

**示例测试代码**：
```python
# tests/test_graphrag_service.py
import pytest
from graphrag_service import get_langchain_rag_service

def test_service_initialization():
    service = get_langchain_rag_service()
    assert service is not None

def test_build_index():
    service = get_langchain_rag_service()
    docs = [{"id": "1", "source": "kb", "text": "test document"}]
    success = service.build_index(docs)
    assert success is True

def test_query():
    service = get_langchain_rag_service()
    result = service.query_knowledge_graph("test question")
    assert "status" in result
    assert "answer" in result
```

---

### Task 5.2: 集成测试
**目标**：测试完整的端到端流程
**步骤**：
1. [ ] 准备测试数据
2. [ ] 执行完整的数据管道：采集 → 清洗 → 导入
3. [ ] 构建 RAG 索引
4. [ ] 测试 API 调用和响应
5. [ ] 验证数据库记录

**测试场景**：
- 新用户注册和登录
- 提交医疗问题
- 获取对话历史
- 提交反馈

---

## Phase 6: 部署和优化

### Task 6.1: 性能优化
**目标**：优化系统性能
**步骤**：
1. [ ] 添加 Redis 缓存（热门问题缓存）
2. [ ] 添加数据库连接池
3. [ ] 优化向量检索 top_k 参数
4. [ ] 添加请求超时设置

---

### Task 6.2: 部署准备
**目标**：为生产部署做准备
**步骤**：
1. [ ] 编写 requirements.txt（已完成）
2. [ ] 编写启动脚本 `run.sh` 或 `run.bat`
3. [ ] 编写配置文件管理
4. [ ] 准备日志路径和日志轮转

**启动脚本示例** (`run.sh`)：
```bash
#!/bin/bash
set -e

# 激活虚拟环境（如果使用）
# source venv/bin/activate

# 启动 FastAPI 应用
python main.py --host 0.0.0.0 --port 8000
```

---

## 📊 任务依赖关系

```
Task 1.1 (环境)
    ↓
Task 1.2 (数据库) → Task 1.3 (配置)
    ↓
Task 2.1 (爬虫) → Task 2.2 (清洗) → Task 2.3 (导入)
    ↓
Task 3.1 (RAG) → Task 3.2 (QA)
    ↓
Task 4.1 (API) → Task 4.2 (认证)
    ↓
Task 5.1 (单元) → Task 5.2 (集成)
    ↓
Task 6.1 (优化) → Task 6.2 (部署)
```

---

## ✅ 完成检查清单

完成每个任务后，请检查：
- [ ] 代码已测试
- [ ] 错误处理完善
- [ ] 日志已添加
- [ ] 单元测试通过
- [ ] 文档已更新

---

## 🎯 关键里程碑

| 里程碑 | 目标 | 预期时间 |
|-------|------|---------|
| 环境准备完成 | Task 1.1-1.3 | Day 1 |
| 数据管道运行 | Task 2.1-2.3 | Day 2-3 |
| RAG 服务可用 | Task 3.1-3.2 | Day 4 |
| API 基本可用 | Task 4.1-4.2 | Day 5 |
| 测试覆盖完成 | Task 5.1-5.2 | Day 6 |
| 系统部署就绪 | Task 6.1-6.2 | Day 7 |

---

**提示**：
- 每完成一个任务，请确保代码能正常运行
- 遇到问题可随时向我咨询
- 保持代码整洁和注释完善
