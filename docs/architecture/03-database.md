# 数据库架构决策记录 (ADR-03)

## 决策背景

本项目采用**双数据库架构**：MySQL 用于结构化数据存储，Neo4j 用于知识图谱存储。本文档记录数据格式、数据流程和字段映射的关键决策。

---

## 1. 数据库选型

### 1.1 MySQL（关系数据库）
**用途**：
- 存储原始爬虫采集数据（`raw_spider_data` 表）
- 用户数据、对话历史、反馈记录
- 作为数据清洗和转换的中间存储

**版本要求**：MySQL 8.0+

**字符集**：`utf8mb4`（支持完整 Unicode，包括 emoji）

### 1.2 Neo4j（图数据库）
**用途**：
- 存储医疗知识图谱（疾病、症状、药品、检查项等实体）
- 存储实体间关系（HAS_SYMPTOM, RECOMMAND_DRUG 等）
- 支持图查询和关系推理

**版本要求**：Neo4j 5.0+

---

## 2. 数据流程设计

### 2.1 数据管道架构

```
[数据采集] data_spider.py
    ↓ 存储 JSON 数据
[MySQL] raw_spider_data 表
    ↓ 读取并转换
[数据清洗] build_data.py
    ↓ 输出结构化 JSON
[文件] data/medical_data.json
    ↓ 批量导入
[Neo4j] 知识图谱节点和关系
```

### 2.2 数据存储格式

#### 2.2.1 MySQL - 原始数据表 (`raw_spider_data`)

**表结构**：
```sql
CREATE TABLE raw_spider_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    page INT NOT NULL,                    -- 页面编号（用于疾病：1-11000，症状：2000000+症状ID）
    data JSON NOT NULL,                    -- JSON 格式的原始数据
    status ENUM('pending', 'processed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_page (page),
    INDEX idx_status (status)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**原始数据 JSON 格式**（`data_spider.py` 采集）：
```json
{
  "url": "https://jib.xywy.com/il_sii/gaishu/123.htm",
  "page": 123,
  "timestamp": "2025-01-20T12:00:00",
  "basic_info": {
    "name": "疾病名称",
    "category": ["分类1", "分类2"],
    "desc": ["描述文本"],
    "attributes": ["医保疾病：否", "患病比例：0.5%", ...]
  },
  "cause_info": "成因文本",
  "prevent_info": "预防文本",
  "symptom_info": {
    "symptoms": ["症状1", "症状2"],
    "symptoms_detail": ["详情1", "详情2"]
  },
  "inspect_info": ["检查URL1", "检查URL2"],
  "treat_info": ["治疗文本"],
  "food_info": {
    "good": ["宜食1", "宜食2"],
    "bad": ["忌食1", "忌食2"],
    "recommand": ["推荐1", "推荐2"]
  },
  "drug_info": ["药品1", "药品2"]
}
```

#### 2.2.2 中间格式（`build_data.py` 输出）

**文件路径**：`data/medical_data.json`

**数据格式**（扁平化英文 key）：
```json
{
  "name": "疾病名称",
  "desc": "描述",
  "category": ["分类"],
  "yibao_status": "否",
  "get_prob": "0.5%",
  "easy_get": "小儿",
  "get_way": "呼吸道传播",
  "cure_department": ["儿科"],
  "cure_way": ["药物治疗"],
  "cure_lasttime": "1-2个月",
  "cured_prob": "98%",
  "cost_money": "1000-4000元",
  "cause": "成因文本",
  "prevent": "预防文本",
  "symptom": ["症状1", "症状2"],
  "check": ["检查项1"],
  "do_eat": ["宜食1"],
  "not_eat": ["忌食1"],
  "recommand_eat": ["推荐1"],
  "recommand_drug": ["药品1"],
  "drug_detail": ["药品明细"],
  "acompany": ["并发症"]
}
```

#### 2.2.3 Neo4j - 节点和关系

**节点类型**：
- `Disease`（疾病）
- `Symptom`（症状）
- `Drug`（药品）
- `Check`（检查项）
- `Department`（科室）
- `Food`（食物）

**关系类型**：
- `(Disease)-[:HAS_SYMPTOM {weight: 0.8}]->(Symptom)`
- `(Disease)-[:RECOMMAND_DRUG]->(Drug)`
- `(Disease)-[:NEED_CHECK]->(Check)`
- `(Disease)-[:BELONGS_DEPARTMENT]->(Department)`
- `(Disease)-[:SHOULD_EAT]->(Food)`
- `(Disease)-[:SHOULD_AVOID]->(Food)`
- `(Disease)-[:COMPLICATION]->(Disease)`

---

## 3. 字段映射规范

### 3.1 采集到清洗的字段映射

| 采集字段 (data_spider.py) | 中文键 (build_data.py) | 英文键 (输出) | Neo4j 字段 |
|---------------------------|----------------------|--------------|-----------|
| `basic_info.name` | `名称` | `name` | `Disease.name` |
| `basic_info.desc` | `简介` | `desc` | `Disease.desc` |
| `basic_info.category` | `所属类别` | `category` | `Disease.category` |
| `basic_info.attributes["医保疾病"]` | `医保疾病` | `yibao_status` | `Disease.yibao_status` |
| `basic_info.attributes["患病比例"]` | `患病比例` | `get_prob` | `Disease.get_prob` |
| `basic_info.attributes["易感人群"]` | `易感人群` | `easy_get` | `Disease.easy_get` |
| `basic_info.attributes["传染方式"]` | `传染方式` | `get_way` | `Disease.get_way` |
| `basic_info.attributes["就诊科室"]` | `就诊科室` | `cure_department` | `Disease.cure_department` |
| `basic_info.attributes["治疗方式"]` | `治疗方式` | `cure_way` | `Disease.cure_way` |
| `basic_info.attributes["治疗周期"]` | `治疗周期` | `cure_lasttime` | `Disease.cure_lasttime` |
| `basic_info.attributes["治愈率"]` | `治愈率` | `cured_prob` | `Disease.cured_prob` |
| `basic_info.attributes["治疗费用"]` | `治疗费用` | `cost_money` | `Disease.cost_money` |
| `basic_info.attributes["并发症"]` | `并发症` | `acompany` | `COMPLICATION` 关系 |
| `cause_info` | `成因` | `cause` | `Disease.cause` |
| `prevent_info` | `预防措施` | `prevent` | `Disease.prevent` |
| `symptom_info.symptoms` | `症状` | `symptom` | `HAS_SYMPTOM` 关系 |
| `inspect_info` | `检查` | `check` | `NEED_CHECK` 关系 |
| `food_info.good` | `宜食` | `do_eat` | `SHOULD_EAT` 关系 |
| `food_info.bad` | `忌食` | `not_eat` | `SHOULD_AVOID` 关系 |
| `food_info.recommand` | `推荐` | `recommand_eat` | `SHOULD_EAT` 关系 |
| `drug_info` | `药品推荐` | `recommand_drug` | `RECOMMAND_DRUG` 关系 |

### 3.2 关键格式决策

#### 决策 1: 症状数据格式统一 ✅
**问题**：`data_spider.py` 返回字典格式，`build_data.py` 需要适配
**决策**：`build_data.py` 支持字典格式 `{'symptoms': [...], 'symptoms_detail': [...]}`
**实现**：修改 `build_data.py` 第 151-159 行，支持字典格式并兼容列表格式

#### 决策 2: 页面编号分配策略
**疾病数据**：使用原始页面编号（1-11000）
**症状数据**：使用 `2000000 + symptom_id`（避免冲突）
**检查项数据**：使用原始页面编号，通过 `type` 字段区分

---

## 4. 数据清洗规则

### 4.1 数据验证规则

1. **名称验证**：疾病名称不能为空，空名称记录标记为 `status='failed'`
2. **列表去重**：所有列表字段（symptoms, drugs, checks 等）自动去重
3. **文本清理**：移除多余空格、换行符、制表符
4. **类型转换**：确保字符串字段为字符串，列表字段为列表

### 4.2 错误处理策略

- **无效页面**：标记为 `status='failed'`，保留原始数据用于调试
- **解析失败**：记录错误信息到 `data` 字段的 `error` 字段
- **缺失字段**：使用默认值（空字符串或空列表）

---

## 5. 索引和约束

### 5.1 MySQL 索引

- `idx_page (page)`：用于快速查找特定页面数据
- `idx_status (status)`：用于筛选待处理/已处理数据

### 5.2 Neo4j 约束

```cypher
CREATE CONSTRAINT disease_name IF NOT EXISTS 
FOR (d:Disease) REQUIRE d.name IS UNIQUE;

CREATE CONSTRAINT symptom_name IF NOT EXISTS 
FOR (s:Symptom) REQUIRE s.name IS UNIQUE;

CREATE CONSTRAINT drug_name IF NOT EXISTS 
FOR (d:Drug) REQUIRE d.name IS UNIQUE;

CREATE CONSTRAINT check_name IF NOT EXISTS 
FOR (c:Check) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT department_name IF NOT EXISTS 
FOR (d:Department) REQUIRE d.name IS UNIQUE;

CREATE CONSTRAINT food_name IF NOT EXISTS 
FOR (f:Food) REQUIRE f.name IS UNIQUE;
```

---

## 6. 数据迁移和导入

### 6.1 导入流程

1. **数据采集**：`data_spider.py` → MySQL `raw_spider_data`
2. **数据清洗**：`build_data.py` → `data/medical_data.json`
3. **数据导入**：`neo4j_import.py` → Neo4j 知识图谱

### 6.2 批量处理策略

- **MySQL 读取**：每次查询 1000 条记录
- **JSON 输出**：标准 JSON 数组格式
- **Neo4j 导入**：批处理大小 100 条/批次（可配置）

---

## 7. 数据一致性保证

### 7.1 事务处理

- **MySQL**：每条数据插入使用事务，失败时回滚
- **Neo4j**：批量导入使用事务，失败时回滚整个批次

### 7.2 去重策略

- **MySQL**：通过 `page` 字段判断，存在则更新，不存在则插入
- **Neo4j**：使用 `MERGE` 语句自动去重（基于唯一约束）

---

## 8. 后续扩展点

### 8.1 症状数据扩展
- 支持从 `zzk.xywy.com` 采集的症状数据
- 存储格式：`page = 2000000 + symptom_id`
- 类型标识：`data.type = 'symptom'`

### 8.2 检查项数据扩展
- 支持检查项详情页面的解析和存储
- 存储格式：`data.type = 'inspect'`
- 后续可通过 `build_data.py` 的 `get_inspect()` 方法关联

---

## 更新记录

- **2025-01-20**: 初始版本，定义数据流程和字段映射
- **2025-01-20**: 添加症状数据格式适配决策（修复字典/列表格式不匹配问题）
- **2025-01-20**: 添加数据清洗规则和错误处理策略

