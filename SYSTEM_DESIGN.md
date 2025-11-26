# 医疗诊断智能问答系统 - 系统设计文档

## 1. 项目概述

### 1.1 项目定义
- **项目名称**：基于知识图谱的医疗诊断智能问答系统（GraphRAG医疗QA）
- **项目类型**：毕业设计
- **核心技术栈**：Neo4j + LLM + Python
- **应用场景**：医生辅助诊断 + 患者自助问诊

### 1.2 系统定位
- **知识库**：医学知识图谱（从寻医问药网采集）
- **问答模式**：GraphRAG（图谱检索增强生成）
- **交互方式**：类似大模型的对话式问答
- **核心能力**：
  - 基于症状智能推荐疾病
  - 提供诊疗方案建议
  - 给出可信任的医学知识依据

### 1.3 关键特性
- 多轮对话支持（上下文感知）
- 知识可溯源（提供引用依据）
- 医生和患者双重适配
- 数据自动化采集和更新

---

## 2. 需求分析

### 2.1 功能需求

#### 2.1.1 数据采集模块
- 自动爬取寻医问药网医疗数据
- 支持断点续传和增量更新
- 数据越多越好（无上限）

#### 2.1.2 知识图谱构建
- 从原始数据中提取实体和关系
- 自动去重和数据清洗
- 批量导入Neo4j数据库

#### 2.1.3 问答服务
- 接收自然语言查询
- 检索相关知识图谱子图
- 生成可信任的医学回答
- 提供引用出处

### 2.2 非功能需求

| 需求项 | 指标 |
|--------|------|
| 并发能力 | 支持数百用户并发（毕业设计参考值） |
| 响应时间 | 问答响应 < 5秒 |
| 数据规模 | 疾病数：3000+，症状数：10000+，药品数：50000+ |
| 系统可用性 | 99%+ |
| 数据准确度 | 采集数据准确率 > 95% |

---

## 3. 数据模型设计

### 3.1 Neo4j 节点类型和属性

#### 3.1.1 Disease（疾病）节点
```
标签: Disease
属性:
  - name: String (UNIQUE, INDEXED)        # 疾病名称
  - desc: String                           # 疾病描述/简介
  - category: List[String]                 # 所属类别（如：内科、传染病等）
  - yibao_status: String                   # 医保状态（医保疾病/非医保）
  - get_prob: String                       # 患病比例
  - easy_get: String                       # 易感人群
  - get_way: String                        # 传染方式
  - cure_lasttime: String                  # 治疗周期
  - cured_prob: String                     # 治愈率
  - cost_money: String                     # 治疗费用
  - cause: String                          # 成因
  - prevent: String                        # 预防措施
  - data_source: String                    # 数据来源（用于溯源）
  - created_at: DateTime                   # 创建时间
  - updated_at: DateTime                   # 更新时间
```

#### 3.1.2 Symptom（症状）节点
```
标签: Symptom
属性:
  - name: String (UNIQUE, INDEXED)        # 症状名称
  - desc: String                           # 症状描述
  - category: String                       # 症状分类（局部/全身/等）
```

#### 3.1.3 Drug（药品）节点
```
标签: Drug
属性:
  - name: String (UNIQUE, INDEXED)        # 药品名称
  - desc: String                           # 药品描述
  - category: String                       # 药品分类（抗生素/消炎药/等）
```

#### 3.1.4 Check（检查项目）节点
```
标签: Check
属性:
  - name: String (UNIQUE, INDEXED)        # 检查项目名称
  - desc: String                           # 检查项目描述
  - category: String                       # 检查分类（化验/影像/等）
```

#### 3.1.5 Department（医疗科室）节点
```
标签: Department
属性:
  - name: String (UNIQUE, INDEXED)        # 科室名称
  - desc: String                           # 科室描述
```

#### 3.1.6 Food（食物）节点
```
标签: Food
属性:
  - name: String (UNIQUE, INDEXED)        # 食物名称
  - category: String                       # 食物分类（蔬菜/肉类/等）
```

#### 3.1.7 MeasureMethod（预防措施）节点
```
标签: MeasureMethod
属性:
  - name: String (UNIQUE, INDEXED)        # 措施名称
  - desc: String                           # 措施描述
```

### 3.2 关系类型设计

#### 3.2.1 诊断关系
```
HAS_SYMPTOM
  源：Disease → 目标：Symptom
  属性：
    - weight: Float (0-1)                 # 症状关联权重（用于诊断优先级）
    - severity: String                    # 症状严重程度（轻/中/重）
  用途：症状到疾病的映射，用于反向诊断

COMPLICATION
  源：Disease → 目标：Disease
  属性：
    - probability: String                 # 并发概率
  用途：疾病并发症关系

SIMILAR_TO
  源：Disease → 目标：Disease
  属性：
    - similarity_score: Float (0-1)       # 相似度得分
  用途：鉴别诊断
```

#### 3.2.2 诊疗关系
```
RECOMMAND_DRUG
  源：Disease → 目标：Drug
  属性：
    - usage: String                       # 用法用量
    - frequency: String                   # 服用频率
  用途：疾病的推荐药品

NEED_CHECK
  源：Disease → 目标：Check
  属性：
    - priority: String                    # 优先级（必需/可选）
    - reason: String                      # 检查原因
  用途：诊断所需的检查项目

BELONGS_DEPARTMENT
  源：Disease → 目标：Department
  属性：
    - description: String                 # 科室说明
  用途：疾病所属医疗科室
```

#### 3.2.3 生活建议关系
```
SHOULD_EAT
  源：Disease → 目标：Food
  属性：
    - reason: String                      # 推荐原因
    - benefit: String                     # 益处说明
  用途：推荐饮食

SHOULD_AVOID
  源：Disease → 目标：Food
  属性：
    - reason: String                      # 避免原因
    - risk: String                        # 风险说明
  用途：禁忌饮食

PREVENT_BY
  源：Disease → 目标：MeasureMethod
  属性：
    - effectiveness: String               # 有效性
  用途：预防措施
```

### 3.3 索引和约束策略

```
【唯一性约束】
- Disease 节点的 name 唯一
- Symptom 节点的 name 唯一
- Drug 节点的 name 唯一
- Check 节点的 name 唯一
- Department 节点的 name 唯一
- Food 节点的 name 唯一

【查询优化索引】
- Disease(category)           # 疾病分类查询
- Disease(yibao_status)      # 医保状态查询
- Symptom(category)          # 症状分类查询
- Food(category)             # 食物分类查询

【Cypher 查询优化】
- 关键词搜索时先通过索引定位节点
- 多跳关系查询使用关系模式匹配
- 大规模图遍历使用 LIMIT 和分页
```

---

## 4. 系统架构设计

### 4.1 整体架构图

```
┌────────────────────────────────────────────────────────────────┐
│                      医疗诊断智能问答系统架构                       │
└────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        用户交互层（UI）                           │
│  ├─ Web 前端（医生版）    ├─ Web 前端（患者版）  ├─ API 客户端      │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                       应用服务层（API Server）                    │
│  ├─ 问答服务          ├─ 用户认证服务   ├─ 会话管理         │
│  ├─ GraphRAG 检索     ├─ 实体搜索      ├─ 结果排序          │
│  ├─ 对话历史管理      ├─ 缓存管理      ├─ 日志记录          │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LLM 集成层（大模型接口）                      │
│  ├─ 提示词管理        ├─ 响应处理       ├─ Token 计数        │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                  知识图谱查询层（Cypher 引擎）                    │
│  ├─ 实体链接          ├─ 子图检索       ├─ 关系推理         │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                      数据层（存储和索引）                         │
│  ├─ Neo4j Database    ├─ MySQL (用户数据)│ ├─ Redis (缓存)   │
│  ├─ MongoDB (原始数据) │                  │ ├─ Session 存储  │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                      数据管道（ETL）                             │
│  ├─ 数据采集 (Spider) │ 数据清洗 (Clean) │ 数据导入 (Import) │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                      数据源（寻医问药网）                        │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 数据处理流程

```
【数据采集阶段】
    爬虫脚本（data_spider.py）
    ├─ 获取疾病列表页 URL
    ├─ 逐页爬取以下内容：
    │  ├─ 基本信息：名称、描述、所属类别
    │  ├─ 诊疗信息：症状、检查、科室、治疗方式
    │  ├─ 医保信息：医保状态、患病比例、治愈率
    │  ├─ 药品信息：推荐用药
    │  └─ 饮食信息：宜食、忌食
    ├─ 支持断点续传（记录采集进度）
    ├─ 错误重试（3次重试 + 指数退避）
    └─ 数据存储至 MongoDB

【数据清洗阶段】
    清洗脚本（build_data.py）
    ├─ 数据验证（缺失值检查、类型检查）
    ├─ 文本规范化：
    │  ├─ 去除特殊字符和多余空格
    │  ├─ 编码统一（UTF-8）
    │  └─ 繁简转换
    ├─ 数据去重（基于名称和描述的哈希）
    ├─ 分词处理（使用 max_cut.py 进行中文分词）
    ├─ 属性值规范化（数值、枚举值的标准化）
    └─ 生成清洗后的数据集（JSON 格式）

【数据导入阶段】
    导入脚本（neo4j_import.py）- 待开发
    ├─ 创建节点：
    │  ├─ Disease 节点（从疾病数据创建）
    │  ├─ Symptom 节点（从症状数据创建，自动去重）
    │  ├─ Drug 节点（从药品数据创建）
    │  ├─ Check 节点（从检查项目创建）
    │  ├─ Department 节点（从科室创建）
    │  ├─ Food 节点（从食物数据创建）
    │  └─ MeasureMethod 节点（从预防措施创建）
    ├─ 创建关系：
    │  ├─ HAS_SYMPTOM（带权重）
    │  ├─ RECOMMAND_DRUG
    │  ├─ NEED_CHECK
    │  ├─ BELONGS_DEPARTMENT
    │  ├─ SHOULD_EAT / SHOULD_AVOID
    │  ├─ PREVENT_BY
    │  ├─ COMPLICATION
    │  └─ SIMILAR_TO（基于症状相似度计算）
    ├─ 批量导入（事务处理，确保数据一致性）
    ├─ 创建索引和约束
    └─ 数据验证

【查询和应用阶段】
    问答服务（qa_service.py）- 待开发
    ├─ 用户问题输入
    ├─ 实体链接（NER + 知识图谱匹配）
    ├─ GraphRAG 检索：
    │  ├─ 基于实体进行多跳关系查询
    │  ├─ 收集相关疾病、症状、检查、药品等
    │  └─ 生成结构化知识上下文
    ├─ LLM 增强生成：
    │  ├─ 构建提示词（包含知识上下文）
    │  ├─ 调用大模型 API
    │  ├─ 获取模型生成回答
    │  └─ 提取和标注引用源
    └─ 返回最终答案
```

---

## 5. 模块设计

### 5.1 模块划分

#### 5.1.1 数据采集模块（Data Spider）
**文件**：`data_spider.py`

**功能**：
- 多线程爬取寻医问药网医疗数据
- 支持自定义爬取范围和速率
- 自动重试和错误处理
- 进度日志记录

**关键方法**：
```python
class MedicalSpider:
    def spider_main(start_page, end_page)     # 主爬虫流程
    def get_html(url, retry, timeout)         # 网页获取
    def basicinfo_spider(url)                 # 基本信息解析
    def symptom_spider(url)                   # 症状解析
    def drug_spider(url)                      # 药品解析
    def check_spider(url)                     # 检查项目解析
    def food_spider(url)                      # 食物信息解析
    def common_spider(url)                    # 通用解析
```

#### 5.1.2 数据清洗模块（Data Cleaning）
**文件**：`build_data.py`

**功能**：
- 数据验证和质量检查
- 文本规范化和去重
- 属性值标准化
- 生成结构化数据集

**关键方法**：
```python
class MedicalGraph:
    def collect_medical()                     # 采集并清洗数据
    def validate_data()                       # 数据验证
    def normalize_text()                      # 文本规范化
    def deduplicate()                         # 数据去重
    def generate_output()                     # 输出清洗结果
```

#### 5.1.3 分词工具模块（Word Segmentation）
**文件**：`max_cut.py`

**功能**：
- 中文文本分词
- 最大匹配算法（前向/后向/双向）
- 词典加载和管理

**关键方法**：
```python
class CutWords:
    def load_words(dict_path)                 # 加载词典
    def max_forward_cut(sent)                 # 前向最大匹配
    def max_backward_cut(sent)                # 后向最大匹配
    def max_biward_cut(sent)                  # 双向最大匹配
```

#### 5.1.4 知识图谱导入模块（Neo4j Import）- 待开发
**文件**：`neo4j_import.py`

**功能**：
- 从清洗数据创建 Neo4j 节点
- 创建实体间关系
- 批量导入和事务管理
- 索引创建和约束设置

**关键方法**：
```python
class Neo4jImporter:
    def create_nodes()                       # 创建所有节点类型
    def create_relationships()               # 创建关系
    def batch_import(data, batch_size)       # 批量导入
    def create_indexes()                     # 创建索引
    def validate_import()                    # 验证导入结果
```

#### 5.1.5 知识图谱查询模块（Graph Query）- 待开发
**文件**：`graph_query.py`

**功能**：
- Cypher 查询封装
- 实体链接（Named Entity Recognition）
- 子图检索和扩展
- 结果映射和缓存

**关键方法**：
```python
class GraphQuery:
    def entity_linking(question)              # 实体链接
    def retrieve_subgraph(entities)           # 子图检索
    def expand_context(subgraph, hops)        # 上下文扩展
    def format_result(graph_result)           # 结果格式化
```

#### 5.1.6 GraphRAG 检索模块（GraphRAG Retrieval）- 待开发
**文件**：`graph_rag.py`

**功能**：
- 检索增强生成（RAG）的核心逻辑
- 知识上下文构建
- 结果排序和去重
- 提示词构建

**关键方法**：
```python
class GraphRAG:
    def retrieve_knowledge(question, top_k)   # 检索相关知识
    def build_context(knowledge)              # 构建知识上下文
    def rank_results(results)                 # 结果排序
    def build_prompt(question, context)       # 构建提示词
```

#### 5.1.7 问答服务模块（QA Service）- 待开发
**文件**：`qa_service.py`

**功能**：
- 接收和处理用户问题
- 调用 GraphRAG 和 LLM
- 生成最终答案
- 答案格式化和引用管理

**关键方法**：
```python
class QAService:
    def answer_question(question)             # 问答主流程
    def extract_entities(question)            # 实体抽取
    def retrieve_evidence(entities)           # 证据检索
    def generate_answer(question, evidence)   # 生成答案
    def format_output(answer, citations)      # 输出格式化
```

#### 5.1.8 用户数据管理模块（User Management） - 待开发
**文件**：`user_manager.py`

**功能**：
- 用户注册、登录、退出登录
- 会话管理（创建、查询、压縮会话歴史）
- 用户反馈（赞輐、住評、改進）
- 用户偏好設置（醫生版、患者版、学生版）
- 費用管理（导出对话歴史）

**关遒SQL表**：
- `users`: 用户信息表
- `conversation_history`: 对话歴史
- `feedback`: 反馈記録表

**主要方法**：
```python
class UserManager:
    def register(username, email, password, user_type)      # 注册
    def login(username, password)                           # 登录
    def logout(user_id)                                     # 退出登录
    def get_user_profile(user_id)                           # 获取用户资料
    def get_conversation_history(user_id, limit, offset)   # 取对话歴史
    def save_conversation(user_id, question, answer, ...)  # 保存对话
    def submit_feedback(user_id, conversation_id, rating, comment)  # 提交反馈
    def get_user_stats(user_id)                             # 获取用户统计
    def export_history(user_id)                             # 导出对话歴史
```

#### 5.1.9 API 服务层（API Server） - 待开发
**文件**：`app.py`

**功能**：
- RESTful API 接口
- 请求验证和応应格式化
- 缓存和速率限制
- 错误处理和日志

**主要端点**：
```
POST   /api/v1/auth/register                    # 注册
POST   /api/v1/auth/login                      # 登录
POST   /api/v1/auth/logout                     # 退出登录

POST   /api/v1/qa                              # 提交问答请求
GET    /api/v1/qa/history                      # 获取对话歴史
GET    /api/v1/disease/{id}                    # 获取疾病详情
GET    /api/v1/search                          # 通用搜索

POST   /api/v1/feedback                        # 提交反馈
GET    /api/v1/user/profile                    # 获取用户信息
GET    /api/v1/health                          # 健康检查
```

---

## 6. GraphRAG 检索流程详解

### 6.1 问答处理流程

```
用户问题
    ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤1：问题预处理                                        │
│  ├─ 文本规范化（去除噪声、统一格式）                     │
│  ├─ 关键词抽取                                          │
│  └─ 问题分类（诊断/症状/药品等）                       │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤2：实体链接（Entity Linking）                       │
│  ├─ 使用 NER 模型识别实体类型                          │
│  ├─ 在知识图谱中匹配实体节点                            │
│  ├─ 模糊匹配处理（近似名称识别）                       │
│  └─ 实体消歧（同名不同义的处理）                       │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤3：GraphRAG 检索                                     │
│  ├─ 基于实体构建 Cypher 查询                            │
│  ├─ 执行多跳关系查询（2-3 跳）                         │
│  ├─ 收集相关节点和属性                                  │
│  └─ 根据边权重进行排序                                  │
│                                                         │
│ 示例查询：                                              │
│  MATCH (symptom:Symptom)<-[r:HAS_SYMPTOM]-(d:Disease)  │
│  WHERE symptom.name IN $symptoms                        │
│  MATCH (d)-[:RECOMMAND_DRUG]->(drug:Drug)              │
│  MATCH (d)-[:NEED_CHECK]->(check:Check)                │
│  RETURN d, r.weight, drug, check                        │
│  ORDER BY r.weight DESC                                │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤4：知识上下文构建                                    │
│  ├─ 整理检索结果成结构化格式                            │
│  │  {                                                   │
│  │    "related_diseases": [...],                       │
│  │    "symptoms": [...],                               │
│  │    "recommended_drugs": [...],                       │
│  │    "required_checks": [...],                        │
│  │    "departments": [...],                            │
│  │    "dietary_advice": {...}                          │
│  │  }                                                   │
│  ├─ 去除冗余和低相关性结果                              │
│  └─ 优化上下文大小（不超过 LLM Token 限制）            │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤5：提示词构建（Prompt Engineering）                 │
│  ├─ 组织系统提示词                                      │
│  ├─ 插入知识上下文                                      │
│  ├─ 附加用户问题                                        │
│  └─ 添加输出格式指导                                    │
│                                                         │
│ 示例提示词：                                            │
│  """                                                    │
│  你是一位专业的医学顾问。基于以下医学知识库信息，       │
│  回答用户的健康问题。所有答案必须基于提供的信息，       │
│  不可凭空编造。                                        │
│                                                         │
│  【知识库信息】                                         │
│  相关疾病：...                                          │
│  常见症状：...                                          │
│  推荐检查：...                                          │
│  推荐药物：...                                          │
│                                                         │
│  用户问题：{question}                                   │
│                                                         │
│  请提供专业但易懂的健康建议。                          │
│  """                                                    │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤6：LLM 生成回答                                      │
│  ├─ 调用大模型 API（OpenAI/通义千问等）                │
│  ├─ 流式获取生成结果（支持实时返回）                   │
│  └─ 错误处理和降级策略                                  │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤7：答案处理和引用管理                                │
│  ├─ 答案文本处理（格式化、去除不当内容）               │
│  ├─ 自动提取引用源                                      │
│  │  └─ 匹配答案中提及的知识图谱实体                    │
│  ├─ 生成引用链接或参考                                  │
│  └─ 转换为最终输出格式                                  │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 步骤8：返回最终答案                                      │
│  {                                                      │
│    "answer": "基于症状分析...",                        │
│    "related_entities": {                               │
│      "diseases": [...],                                │
│      "symptoms": [...],                                │
│      "checks": [...]                                   │
│    },                                                  │
│    "citations": [                                      │
│      {                                                 │
│        "text": "提及的信息片段",                       │
│        "source": "疾病X",                              │
│        "link": "kg_entity_id"                          │
│      }                                                 │
│    ],                                                  │
│    "confidence": 0.85,                                 │
│    "response_time": 2.3                                │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
```

### 6.2 关键算法和优化

#### 6.2.1 实体链接算法
```
算法：模糊匹配 + 向量相似度

输入：用户问题中的实体文本
输出：知识图谱中最匹配的实体节点

步骤：
1. 精确匹配：先尝试在知识图谱中精确查找实体
2. 模糊匹配：如果精确匹配失败，使用编辑距离（Levenshtein）
3. 向量相似度：计算文本向量相似度（如果有 embedding）
4. 返回 Top-K 最相关的实体
```

#### 6.2.2 子图检索优化
```
策略：限制查询范围和深度

参数：
- max_hops: 最大关系深度（推荐 2-3 跳）
- max_results: 每种关系返回的最大节点数
- weight_threshold: 权重阈值（过滤低相关性）

优化：
- 使用关系权重排序（权重高的优先返回）
- 分批查询（避免一次性返回过多数据）
- 缓存热门查询（LRU Cache）
```

#### 6.2.3 结果排序策略
```
排序因子：
1. 关系权重（HAS_SYMPTOM 的 weight）
2. 节点重要度（如疾病的患病率）
3. 查询相关度（问题和节点文本的相似度）
4. 节点热度（被查询次数）

最终排序公式（可调整）：
score = 0.4 * weight + 0.3 * relevance + 0.2 * importance + 0.1 * popularity
```

---

## 7. API 接口设计

### 7.1 问答接口

**接口**：`POST /api/v1/qa`

**请求格式**：
```json
{
  "question": "头痛发热应该怎么办？",
  "user_id": "user123",
  "session_id": "session456",
  "context": {
    "previous_qa": [
      {"q": "之前的问题", "a": "之前的回答"}
    ],
    "patient_info": {
      "age": 30,
      "gender": "M"
    }
  },
  "options": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

**返回格式**：
```json
{
  "status": "success",
  "data": {
    "question_id": "q_7846928374",
    "answer": "根据您提到的症状（头痛、发热），...",
    "related_entities": {
      "diseases": [
        {"id": "d_001", "name": "感冒", "confidence": 0.92}
      ],
      "symptoms": [
        {"id": "s_001", "name": "头痛"},
        {"id": "s_002", "name": "发热"}
      ],
      "checks": [
        {"id": "c_001", "name": "血常规"}
      ],
      "drugs": [
        {"id": "dr_001", "name": "阿司匹林"}
      ]
    },
    "citations": [
      {
        "text": "感冒是由病毒引起的呼吸道疾病",
        "entity_type": "Disease",
        "entity_id": "d_001",
        "source_url": "graph_entity"
      }
    ],
    "confidence": 0.85,
    "response_time_ms": 2340
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 7.2 实体搜索接口

**接口**：`GET /api/v1/search`

**参数**：
- `q`: 搜索关键词（必填）
- `type`: 实体类型（Disease/Symptom/Drug/Check/Department，可选）
- `limit`: 返回结果数量（默认10）

**返回格式**：
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "id": "d_001",
        "type": "Disease",
        "name": "感冒",
        "description": "感冒是一种常见的病毒性呼吸道疾病",
        "match_score": 0.98
      }
    ],
    "total": 15,
    "returned": 10
  }
}
```

### 7.3 实体详情接口

**接口**：`GET /api/v1/disease/{id}`

**返回格式**：
```json
{
  "status": "success",
  "data": {
    "id": "d_001",
    "name": "感冒",
    "description": "感冒是由病毒引起的呼吸道疾病...",
    "category": ["传染病", "呼吸系统疾病"],
    "yibao_status": "医保疾病",
    "get_prob": "3-5%",
    "easy_get": "儿童、老人、免疫力低下人群",
    "cured_prob": "95%以上",
    "symptoms": [
      {"id": "s_001", "name": "发热", "weight": 0.95},
      {"id": "s_002", "name": "咳嗽", "weight": 0.88}
    ],
    "recommended_checks": [
      {"id": "c_001", "name": "血常规"}
    ],
    "recommended_drugs": [
      {"id": "dr_001", "name": "阿司匹林", "usage": "每次500mg，每日2-3次"}
    ],
    "department": ["内科", "呼吸科"],
    "dietary_advice": {
      "should_eat": ["清粥", "白菜"],
      "should_avoid": ["辛辣", "油腻"]
    },
    "complications": [
      {"id": "d_002", "name": "肺炎", "probability": "10%"}
    ]
  }
}
```

---

## 8. 数据库配置

### 8.1 Neo4j 配置

```properties
# neo4j.conf

# 服务器配置
server.default_listen_address=0.0.0.0
server.default_advertised_address=localhost
server.http_port=7474
server.https_port=7473
server.bolt_port=7687

# 内存配置（毕业设计，建议 4GB 起）
server.memory.heap.initial_size=2G
server.memory.heap.max_size=4G
server.memory.pagecache.size=2G

# 安全配置
dbms.security.auth_enabled=true

# 日志配置
server.logs.debug.level=INFO
```

### 8.2 MySQL 配置

```python
# MySQL 用于管理用户数据、对话歴史、摊失记录
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "medical_qa",
    "charset": "utf8mb4"
}

# MySQL 表结构
# 1. 用户表 (users)
# CREATE TABLE users (
#     id INT PRIMARY KEY AUTO_INCREMENT,
#     username VARCHAR(50) UNIQUE NOT NULL,
#     email VARCHAR(100) UNIQUE NOT NULL,
#     password_hash VARCHAR(255) NOT NULL,
#     user_type ENUM('doctor', 'patient', 'admin') DEFAULT 'patient',
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#     is_active BOOLEAN DEFAULT TRUE,
#     INDEX idx_username (username),
#     INDEX idx_email (email)
# );

# 2. 对话歴史表 (conversation_history)
# CREATE TABLE conversation_history (
#     id INT PRIMARY KEY AUTO_INCREMENT,
#     user_id INT NOT NULL,
#     session_id VARCHAR(100) NOT NULL,
#     question TEXT NOT NULL,
#     answer TEXT,
#     related_entities JSON,
#     citations JSON,
#     response_time INT,
#     model_version VARCHAR(50),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
#     INDEX idx_user_id (user_id),
#     INDEX idx_session_id (session_id),
#     INDEX idx_created_at (created_at)
# );

# 3. 摊失记录表 (feedback)
# CREATE TABLE feedback (
#     id INT PRIMARY KEY AUTO_INCREMENT,
#     user_id INT NOT NULL,
#     conversation_id INT NOT NULL,
#     rating INT CHECK (rating >= 1 AND rating <= 5),
#     comment TEXT,
#     feedback_type ENUM('helpful', 'incorrect', 'unclear', 'other'),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
#     FOREIGN KEY (conversation_id) REFERENCES conversation_history(id) ON DELETE CASCADE,
#     INDEX idx_user_id (user_id),
#     INDEX idx_rating (rating)
# );
```

### 8.4 Redis 配置

```python
# Redis 用于缓存和会话管理
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "ttl": {
        "qa_cache": 3600,  # 问答缓存 1 小时
        "entity_cache": 86400,  # 实体缓存 1 天
        "session": 1800  # 会话 30 分钟
    }
}
```

---

## 9. 开发计划

### 9.1 阶段划分

| 阶段 | 时间 | 关键产出物 |
|------|------|----------|
| 需求分析 | Week 1 | 需求规范文档 |
| 系统设计 | Week 2 | 设计文档、ER图 |
| 开发实现 | Week 3-5 | 完整代码、部署脚本 |
| 测试验证 | Week 6 | 测试报告、质量指标 |
| 部署上线 | Week 7 | 生产环境、回滚方案 |
| 运维优化 | Week 8+ | 运维手册、优化建议 |

### 9.2 技术栈

```
后端框架：
  - Python 3.8+
  - Flask / FastAPI（API 服务）
  - Neo4j Python Driver（图数据库）
  - PyMongo（MongoDB 驱动）

数据处理：
  - lxml（网页解析）
  - jieba / max_cut（分词）
  - pandas（数据处理）

LLM 集成：
  - OpenAI API / 通义千问 SDK
  - LangChain（可选，RAG 框架）

部署：
  - Docker / Docker Compose
  - Nginx（反向代理）
  - Systemd（进程管理）

监控：
  - Prometheus + Grafana
  - ELK Stack（日志管理）
```

---

## 10. 质量保证

### 10.1 测试策略

```
单元测试：
  - 爬虫模块：网页解析、数据提取
  - 清洗模块：数据验证、文本规范化
  - 图谱查询：Cypher 查询、结果映射

集成测试：
  - 端到端流程：采集 → 清洗 → 导入 → 查询
  - 问答系统：问题理解 → 知识检索 → LLM 生成

性能测试：
  - 导入性能：单位时间内导入的节点数
  - 查询性能：问答响应时间、吞吐量
  - 并发能力：支持的并发用户数

覆盖率目标：单元测试 > 80%，关键路径 100%
```

### 10.2 数据质量指标

```
数据准确度：
  - 实体信息准确性 > 95%
  - 关系完整性 > 90%
  - 去重效果：重复率 < 5%

数据完整性：
  - 关键字段填充率 > 90%
  - 缺失值处理率 100%

数据一致性：
  - 同名实体统一性检查
  - 关系的正确性验证
```

---

## 11. 安全和隐私考虑

### 11.1 数据安全
- Neo4j 身份认证和授权
- 数据传输加密（HTTPS/TLS）
- 定期数据备份
- 敏感信息脱敏

### 11.2 隐私保护
- 用户数据最小化收集
- 会话数据定期清理
- 医疗数据法规遵从（如适用）

### 11.3 系统安全
- API 速率限制（防止滥用）
- 输入验证和清理
- 错误信息不泄露敏感信息
- 定期安全审计

---

## 12. 总结

本系统设计文档完整定义了基于知识图谱的医疗诊断智能问答系统（GraphRAG）的架构、数据模型、模块划分和开发计划。

**核心创新点**：
1. **GraphRAG 融合**：知识图谱 + 大模型 = 可信任的医学问答
2. **多源数据采集**：自动化爬虫 + 智能清洗
3. **灵活的知识建模**：支持多种医学实体和关系
4. **开放的 API 设计**：易于与其他系统集成

**预期收益**：
- 医生：快速获取疾病诊疗参考
- 患者：获得可信任的健康指导
- 学生：完整的系统设计和开发体验

---

**文档版本**：1.0  
**最后更新**：2024-01-15  
**作者**：QA 系统开发团队
