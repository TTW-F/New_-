# 数据库架构文档

**最后更新**: 2026-03-25  
**数据库**: Neo4j 5.0+ (知识图谱) + SQLite 3.0+ (用户数据)  
**服务文件**: `neo4j_service.py`

---

## 📋 目录

- [架构概览](#架构概览)
- [Neo4j知识图谱](#neo4j知识图谱)
- [SQLite关系数据库](#sqlite关系数据库)
- [数据模型](#数据模型)
- [查询接口](#查询接口)
- [数据导入](#数据导入)
- [性能优化](#性能优化)
- [备份恢复](#备份恢复)

---

## 🏗️ 架构概览

系统采用双数据库架构：

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层 (Application)                      │
│  FastAPI + MedicalAgent                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌──────────────────────┐            ┌──────────────────────┐
│   Neo4j 知识图谱      │            │   SQLite 用户数据     │
│  (医疗知识)           │            │  (用户/对话)          │
│                      │            │                      │
│  • Disease (疾病)    │            │  • users (用户)      │
│  • Symptom (症状)    │            │  • conversations     │
│  • Drug (药品)       │            │    (对话记录)        │
│  • Check (检查)      │            │  • feedback (反馈)   │
│  • Department (科室) │            │                      │
│  • Food (食物)       │            │                      │
│                      │            │                      │
│  关系:               │            │                      │
│  • HAS_SYMPTOM      │            │                      │
│  • RECOMMAND_DRUG   │            │                      │
│  • NEED_CHECK       │            │                      │
│  • COMPLICATION     │            │                      │
│  • SHOULD_EAT       │            │                      │
│  • SHOULD_AVOID     │            │                      │
└──────────────────────┘            └──────────────────────┘
```

**设计理念**:
- **Neo4j**: 存储医疗知识图谱，支持复杂关系查询和推理
- **SQLite**: 存储用户数据和对话历史，简单高效

---

## 🕸️ Neo4j知识图谱

### 节点类型 (Node Labels)

#### 1. Disease (疾病)
**属性**:
```cypher
{
  name: String,           // 疾病名称 (唯一)
  desc: String,           // 疾病描述
  cause: String,          // 病因
  prevent: String,        // 预防措施
  cure_lasttime: String,  // 治疗周期
  cure_way: String,       // 治疗方式
  cured_prob: String,     // 治愈概率
  easy_get: String,       // 易感人群
  get_prob: String,       // 患病概率
  get_way: String         // 传播途径
}
```

**索引**:
```cypher
CREATE INDEX disease_name_index FOR (d:Disease) ON (d.name)
```

**统计**: ~8,000个节点

#### 2. Symptom (症状)
**属性**:
```cypher
{
  name: String,    // 症状名称 (唯一)
  desc: String     // 症状描述
}
```

**统计**: ~5,000个节点

#### 3. Drug (药品)
**属性**:
```cypher
{
  name: String,           // 药品名称 (唯一)
  desc: String,           // 药品描述
  producer: String,       // 生产厂家
  drug_type: String,      // 药品类型
  sale_place: String,     // 销售地点
  approval_number: String // 批准文号
}
```

**统计**: ~3,000个节点

#### 4. Check (检查项目)
**属性**:
```cypher
{
  name: String,    // 检查名称 (唯一)
  desc: String     // 检查描述
}
```

**统计**: ~500个节点

#### 5. Department (科室)
**属性**:
```cypher
{
  name: String,    // 科室名称 (唯一)
  desc: String     // 科室描述
}
```

**统计**: ~50个节点

#### 6. Food (食物)
**属性**:
```cypher
{
  name: String,    // 食物名称 (唯一)
  desc: String     // 食物描述
}
```

**统计**: ~1,000个节点

---

### 关系类型 (Relationship Types)

#### 1. HAS_SYMPTOM (疾病-症状)
```cypher
(Disease)-[r:HAS_SYMPTOM {weight: Float}]->(Symptom)
```
**属性**:
- `weight`: 症状权重 (0.0-1.0)，表示该症状对疾病的重要程度

**统计**: ~50,000条关系

**示例查询**:
```cypher
// 查找糖尿病的所有症状
MATCH (d:Disease {name: "糖尿病"})-[r:HAS_SYMPTOM]->(s:Symptom)
RETURN s.name, r.weight
ORDER BY r.weight DESC
```

#### 2. RECOMMAND_DRUG (疾病-药品)
```cypher
(Disease)-[r:RECOMMAND_DRUG {usage: String, frequency: String}]->(Drug)
```
**属性**:
- `usage`: 用法用量
- `frequency`: 服用频率

**统计**: ~30,000条关系

#### 3. NEED_CHECK (疾病-检查)
```cypher
(Disease)-[r:NEED_CHECK {priority: String}]->(Check)
```
**属性**:
- `priority`: 优先级 (高/中/低)

**统计**: ~10,000条关系

#### 4. BELONGS_DEPARTMENT (疾病-科室)
```cypher
(Disease)-[:BELONGS_DEPARTMENT]->(Department)
```

**统计**: ~8,000条关系

#### 5. SHOULD_EAT (疾病-宜食)
```cypher
(Disease)-[r:SHOULD_EAT {reason: String}]->(Food)
```
**属性**:
- `reason`: 推荐原因

**统计**: ~5,000条关系

#### 6. SHOULD_AVOID (疾病-忌食)
```cypher
(Disease)-[r:SHOULD_AVOID {reason: String}]->(Food)
```
**属性**:
- `reason`: 禁忌原因

**统计**: ~5,000条关系

#### 7. COMPLICATION (疾病-并发症)
```cypher
(Disease)-[r:COMPLICATION {probability: String}]->(Disease)
```
**属性**:
- `probability`: 发生概率

**统计**: ~2,000条关系

---

### 图谱统计

| 类型 | 数量 |
|------|------|
| 总节点数 | ~17,550 |
| 总关系数 | ~110,000 |
| Disease节点 | ~8,000 |
| Symptom节点 | ~5,000 |
| Drug节点 | ~3,000 |
| Check节点 | ~500 |
| Department节点 | ~50 |
| Food节点 | ~1,000 |

---

## 💾 SQLite关系数据库

### 表结构

#### 1. users (用户表)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

**字段说明**:
- `id`: 用户ID (主键)
- `username`: 用户名 (唯一)
- `email`: 邮箱 (唯一)
- `hashed_password`: 密码哈希 (bcrypt)
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `is_active`: 是否激活

#### 2. conversations (对话表)
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    tool_calls JSON,
    entities JSON,
    response_time_ms INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
```

**字段说明**:
- `id`: 对话ID (主键)
- `user_id`: 用户ID (外键)
- `session_id`: 会话ID
- `question`: 用户问题
- `answer`: 助手回答
- `tool_calls`: 工具调用记录 (JSON)
- `entities`: 提取的实体 (JSON)
- `response_time_ms`: 响应时间 (毫秒)
- `created_at`: 创建时间

#### 3. feedback (反馈表)
```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_feedback_conversation_id ON feedback(conversation_id);
CREATE INDEX idx_feedback_user_id ON feedback(user_id);
```

**字段说明**:
- `id`: 反馈ID (主键)
- `conversation_id`: 对话ID (外键)
- `user_id`: 用户ID (外键)
- `rating`: 评分 (1-5)
- `comment`: 评论内容
- `created_at`: 创建时间

---

## 🔍 查询接口

### Neo4jService类 (neo4j_service.py)

#### 1. search_disease_by_name()
**功能**: 根据疾病名称精确查询疾病信息

**参数**:
```python
disease_name: str  # 疾病名称
```

**返回**:
```python
{
  "name": "糖尿病",
  "desc": "...",
  "cause": "...",
  "prevent": "...",
  ...
}
```

**Cypher查询**:
```cypher
MATCH (d:Disease {name: $name})
RETURN d
```

#### 2. find_diseases_by_symptoms()
**功能**: 根据症状列表查找可能的疾病

**参数**:
```python
symptoms: List[str]  # 症状列表
top_k: int = 5       # 返回前k个结果
```

**返回**:
```python
[
  {
    "name": "感冒",
    "description": "...",
    "match_score": 0.85,
    "matched_symptoms": 3
  }
]
```

**Cypher查询**:
```cypher
MATCH (s:Symptom)<-[r:HAS_SYMPTOM]-(d:Disease)
WHERE s.name IN $symptoms
WITH d, SUM(r.weight) as total_weight, COUNT(s) as matched_symptoms
RETURN d.name, d.desc, total_weight, matched_symptoms
ORDER BY total_weight DESC, matched_symptoms DESC
LIMIT $top_k
```

**算法说明**:
- 计算症状权重总和作为匹配分数
- 同时考虑匹配的症状数量
- 按分数和数量降序排序

#### 3. get_disease_full_context()
**功能**: 获取疾病的完整上下文信息

**参数**:
```python
disease_name: str  # 疾病名称
```

**返回**:
```python
{
  "disease": {...},
  "symptoms": [...],
  "drugs": [...],
  "checks": [...],
  "departments": [...],
  "dietary_advice": {
    "should_eat": [...],
    "should_avoid": [...]
  },
  "complications": [...]
}
```

**Cypher查询**:
```cypher
MATCH (d:Disease {name: $name})

// 获取症状
OPTIONAL MATCH (d)-[hs:HAS_SYMPTOM]->(s:Symptom)

// 获取药品
OPTIONAL MATCH (d)-[rd:RECOMMAND_DRUG]->(drug:Drug)

// 获取检查
OPTIONAL MATCH (d)-[nc:NEED_CHECK]->(check:Check)

// 获取科室
OPTIONAL MATCH (d)-[bd:BELONGS_DEPARTMENT]->(dept:Department)

// 获取宜食食物
OPTIONAL MATCH (d)-[se:SHOULD_EAT]->(food_good:Food)

// 获取忌食食物
OPTIONAL MATCH (d)-[sa:SHOULD_AVOID]->(food_bad:Food)

// 获取并发症
OPTIONAL MATCH (d)-[comp:COMPLICATION]->(comp_disease:Disease)

RETURN d,
       collect(DISTINCT {name: s.name, weight: hs.weight}) as symptoms,
       collect(DISTINCT {name: drug.name, usage: rd.usage}) as drugs,
       collect(DISTINCT {name: check.name, priority: nc.priority}) as checks,
       collect(DISTINCT dept.name) as departments,
       collect(DISTINCT {name: food_good.name, reason: se.reason}) as good_foods,
       collect(DISTINCT {name: food_bad.name, reason: sa.reason}) as bad_foods,
       collect(DISTINCT {name: comp_disease.name, probability: comp.probability}) as complications
```

#### 4. search_drug_by_name()
**功能**: 根据药品名称查询药品详细信息

**参数**:
```python
drug_name: str  # 药品名称
```

**返回**:
```python
{
  "name": "阿司匹林",
  "desc": "...",
  "producer": "...",
  "drug_type": "...",
  ...
}
```

#### 5. search_drugs_by_disease()
**功能**: 查询疾病相关的药品

**参数**:
```python
disease_name: str  # 疾病名称
```

**返回**:
```python
[
  {
    "name": "二甲双胍",
    "description": "...",
    "usage": "口服",
    "frequency": "一日三次"
  }
]
```

#### 6. fuzzy_search_entity()
**功能**: 模糊搜索医疗实体

**参数**:
```python
keyword: str              # 搜索关键词
entity_type: str = None   # 实体类型 (Disease/Symptom/Drug/Check)
limit: int = 10           # 返回数量
```

**返回**:
```python
[
  {
    "name": "糖尿病",
    "type": "Disease",
    "description": "..."
  }
]
```

**Cypher查询**:
```cypher
// 指定类型
MATCH (n:Disease)
WHERE n.name CONTAINS $keyword
RETURN n.name, n.desc, 'Disease' as type
LIMIT $limit

// 所有类型
MATCH (n)
WHERE n.name CONTAINS $keyword
RETURN n.name, n.desc, labels(n)[0] as type
LIMIT $limit
```

---

## 📥 数据导入

### 导入脚本 (neo4j_import.py)

**数据源**: `data/medical_data.json`

**导入流程**:
```python
1. 读取JSON数据文件
2. 创建节点索引
3. 批量创建节点
   - Disease节点
   - Symptom节点
   - Drug节点
   - Check节点
   - Department节点
   - Food节点
4. 批量创建关系
   - HAS_SYMPTOM关系
   - RECOMMAND_DRUG关系
   - NEED_CHECK关系
   - BELONGS_DEPARTMENT关系
   - SHOULD_EAT关系
   - SHOULD_AVOID关系
   - COMPLICATION关系
5. 验证数据完整性
```

**执行命令**:
```bash
python neo4j_import.py
```

**批量导入优化**:
```python
# 使用UNWIND批量创建节点
query = """
UNWIND $batch as row
CREATE (d:Disease)
SET d = row
"""

# 批量大小: 1000条/批
batch_size = 1000
```

---

## 🚀 性能优化

### 1. 索引优化

**创建索引**:
```cypher
// 疾病名称索引
CREATE INDEX disease_name_index FOR (d:Disease) ON (d.name)

// 症状名称索引
CREATE INDEX symptom_name_index FOR (s:Symptom) ON (s.name)

// 药品名称索引
CREATE INDEX drug_name_index FOR (dr:Drug) ON (dr.name)
```

**查看索引**:
```cypher
SHOW INDEXES
```

### 2. 查询优化

**使用参数化查询**:
```python
# 好的做法
session.run("MATCH (d:Disease {name: $name}) RETURN d", name="糖尿病")

# 避免字符串拼接
# session.run(f"MATCH (d:Disease {{name: '{name}'}}) RETURN d")
```

**限制返回结果**:
```cypher
MATCH (d:Disease)
RETURN d
LIMIT 100  // 始终使用LIMIT
```

**使用EXPLAIN分析查询**:
```cypher
EXPLAIN MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
WHERE s.name IN ["头痛", "发热"]
RETURN d
```

### 3. 连接池管理

```python
class Neo4jService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            max_connection_pool_size=50,
            connection_acquisition_timeout=60
        )
```

### 4. 缓存策略

**应用层缓存**:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_disease_info(disease_name: str):
    return neo4j_service.search_disease_by_name(disease_name)
```

---

## 💾 备份恢复

### Neo4j备份

**方式1: 数据库导出**
```bash
# 导出数据库
neo4j-admin dump --database=neo4j --to=backup.dump

# 恢复数据库
neo4j-admin load --from=backup.dump --database=neo4j --force
```

**方式2: Cypher导出**
```cypher
// 导出所有节点和关系
CALL apoc.export.cypher.all("backup.cypher", {})
```

### SQLite备份

**备份命令**:
```bash
# 备份数据库
sqlite3 medical_qa.db ".backup backup.db"

# 或使用文件复制
copy medical_qa.db medical_qa_backup.db
```

**恢复命令**:
```bash
# 恢复数据库
copy medical_qa_backup.db medical_qa.db
```

---

## 📊 数据统计查询

### Neo4j统计

```cypher
// 节点统计
MATCH (n)
RETURN labels(n)[0] as type, count(n) as count
ORDER BY count DESC

// 关系统计
MATCH ()-[r]->()
RETURN type(r) as type, count(r) as count
ORDER BY count DESC

// 疾病症状统计
MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
RETURN d.name, count(s) as symptom_count
ORDER BY symptom_count DESC
LIMIT 10
```

### SQLite统计

```sql
-- 用户统计
SELECT COUNT(*) as total_users FROM users;

-- 对话统计
SELECT COUNT(*) as total_conversations FROM conversations;

-- 每日对话量
SELECT DATE(created_at) as date, COUNT(*) as count
FROM conversations
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## 📝 最佳实践

1. **始终使用参数化查询**: 防止Cypher注入
2. **合理使用索引**: 提高查询性能
3. **控制返回数据量**: 使用LIMIT限制结果
4. **定期备份数据**: 防止数据丢失
5. **监控数据库性能**: 使用Neo4j Browser查看查询计划
6. **使用连接池**: 避免频繁创建连接

---

*本文档由 doc-updater agent 生成 @ 2026-03-25*
