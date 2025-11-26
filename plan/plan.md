# 医疗诊断智能问答系统 - 技术规划文档 (Planning)

基于 `plan/spec.md`，本文档定义系统的整体架构、技术选型、数据模型和 API 契约。

## 1. 技术栈选型

### 1.1 数据层（存储和索引）
| 组件 | 选择 | 用途 | 版本 |
|------|------|------|------|
| 图数据库 | Neo4j | 知识图谱存储和查询 | 5.0+ |
| 关系数据库 | MySQL | 用户数据、对话历史、反馈、原始爬虫数据 | 8.0+ |
| 缓存引擎 | Redis | 热数据缓存、会话管理 | 7.0+ |

### 1.2 应用层（业务逻辑）
| 组件 | 选择 | 用途 | 版本 |
|------|------|------|------|
| 编程语言 | Python | 主要开发语言 | 3.8+ |
| Web 框架 | FastAPI | RESTful API 服务 | 0.100+ |
| 异步框架 | APScheduler | 定时任务（数据采集） | 3.10+ |
| ORM 框架 | SQLAlchemy | MySQL 数据操作 | 2.0+ |
| 图查询驱动 | Neo4j Driver | Neo4j 交互 | 5.0+ |

### 1.3 RAG 和 LLM 集成
| 组件 | 选择 | 用途 | 版本 |
|------|------|------|------|
| RAG 实现方式 | 自实现 GraphRAG | 子图检索和上下文构建 | 自定义 |
| LLM 提供商 | DeepSeek | 自然语言生成 | 最新 |
| 嵌入模型 | 本地 Qwen3-Embedding-8B | 实体匹配（可选） | 本地模型 |

### 1.4 部署方式
| 组件 | 选择 | 用途 |
|------|------|------|
| 部署方式 | 本地直接运行（无容器化） | 开发和部署 |
| Web 服务器 | 可选 Nginx（通过 FastAPI 内置服务器） | 反向代理 |
| 日志管理 | Python logging + 文件 | 应用日志记录 |
| 监控 | 可选 | 性能监控 |

---

## 2. 系统架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    用户交互层（UI）                          │
│               Web 前端（医生版/患者版）                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  应用服务层（API Server）                   │
│  认证服务 │ 问答服务 │ GraphRAG 检索 │ 对话管理 │ 用户管理 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              GraphRAG 管道（RAG 核心层）                    │
│    文档索引 │ 实体提取 │ 子图检索 │ 上下文构建           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 LLM 集成层（大模型接口）                    │
│         提示词管理 │ 响应处理 │ Token 计数               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   数据存储层（多引擎）                       │
│  Neo4j │ MySQL │ Redis                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  数据管道（ETL）                            │
│  采集 (Spider) → 清洗 (Clean) → 导入 (Import)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    数据源（寻医问药网）                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 数据模型设计

### 3.1 Neo4j 节点类型（知识图谱）

#### Disease（疾病）
```
属性：
  - name: 疾病名称 (UNIQUE, INDEXED)
  - desc: 疾病描述
  - category: 所属类别 (Array)
  - yibao_status: 医保状态
  - get_prob: 患病比例
  - easy_get: 易感人群
  - cured_prob: 治愈率
  - cause: 成因
  - prevent: 预防措施
```

#### Symptom（症状）、Drug（药品）、Check（检查）、Department（科室）、Food（食物）
```
简化结构，主要包含：
  - name: 实体名称 (UNIQUE, INDEXED)
  - desc: 详细描述
```

### 3.2 Neo4j 关系类型

| 源→目标 | 关系名 | 属性 | 含义 |
|--------|-------|------|------|
| Disease → Symptom | HAS_SYMPTOM | weight: 0-1 | 症状权重 |
| Disease → Drug | RECOMMAND_DRUG | usage: String | 用药建议 |
| Disease → Check | NEED_CHECK | priority: String | 检查优先级 |
| Disease → Department | BELONGS_DEPARTMENT | - | 科室归属 |
| Disease → Food | SHOULD_EAT / SHOULD_AVOID | reason: String | 饮食建议 |
| Disease → Disease | COMPLICATION | probability: String | 并发症 |
| Disease → Disease | SIMILAR_TO | similarity_score: Float | 相似疾病 |

### 3.3 MySQL 表设计

#### users（用户表）
```sql
- id: INT PRIMARY KEY
- username: VARCHAR(50) UNIQUE
- email: VARCHAR(100) UNIQUE
- password_hash: VARCHAR(255)
- user_type: ENUM('doctor', 'patient', 'admin')
- created_at: TIMESTAMP
- is_active: BOOLEAN
```

#### raw_spider_data（原始爬虫数据）
```sql
- id: INT PRIMARY KEY
- page: INT
- data: JSON (原始爬虫采集数据)
- status: ENUM('pending', 'processed', 'failed')
- created_at: TIMESTAMP
- INDEX idx_page (page)
- INDEX idx_status (status)
```

#### conversation_history（对话历史）
```sql
- id: INT PRIMARY KEY
- user_id: INT FOREIGN KEY
- session_id: VARCHAR(100)
- question: TEXT
- answer: TEXT
- related_entities: JSON
- citations: JSON
- response_time: INT
- created_at: TIMESTAMP
```

#### feedback（用户反馈）
```sql
- id: INT PRIMARY KEY
- user_id: INT FOREIGN KEY
- conversation_id: INT FOREIGN KEY
- rating: INT (1-5)
- comment: TEXT
- feedback_type: ENUM('helpful', 'incorrect', 'unclear', 'other')
- created_at: TIMESTAMP
```

---

## 4. GraphRAG 完整查询流程

### 4.1 自实现 GraphRAG 流程

我们的 GraphRAG 实现包含以下步骤：

1. **实体识别与链接**: 从问题中提取医学实体，在知识图谱中匹配节点
2. **子图检索**: 从匹配的实体出发，检索多跳关系，构建知识子图
3. **上下文构建**: 将子图转换为结构化的文本上下文
4. **提示词构建**: 构建包含问题和知识上下文的提示词
5. **LLM 生成**: 调用大模型基于知识上下文生成专业回答

### 4.2 实现方式

自实现的 GraphRAG 服务：

```python
from graphrag_service import GraphRAGService

# 1. 初始化 GraphRAG 服务
service = GraphRAGService()

# 2. 查询知识图谱
# 服务内部自动执行：实体识别 → 子图检索 → 上下文构建 → LLM 生成

results = service.query(
    question="我头痛发热，可能是什么病？",
    max_hops=2  # 最大检索跳数
)

# 3. 返回结果
# results["answer"]: DeepSeek 生成的专业答案
# results["entities"]: 识别到的实体列表
# results["citations"]: 引用的知识图谱节点
# results["context_summary"]: 构建的上下文摘要
```

---

## 5. API 契约设计

### 5.1 认证端点

**POST /api/v1/auth/register** - 用户注册
```json
请求：
{
  "username": "user123",
  "email": "user@example.com",
  "password": "secure_pwd",
  "user_type": "patient"  // or "doctor"
}

响应：
{
  "status": "success",
  "data": {
    "user_id": 1,
    "token": "jwt_token"
  }
}
```

**POST /api/v1/auth/login** - 用户登录
```json
请求：
{
  "username": "user123",
  "password": "secure_pwd"
}

响应：
{
  "status": "success",
  "data": {
    "user_id": 1,
    "token": "jwt_token",
    "user_type": "patient"
  }
}
```

### 5.2 问答端点

**POST /api/v1/qa** - 提交问答
```json
请求：
{
  "question": "头痛发热应该怎么办？",
  "session_id": "session_uuid",
  "user_id": 1,
  "context": {
    "previous_qa": [...],
    "user_type": "patient"
  }
}

响应：
{
  "status": "success",
  "data": {
    "question_id": "q_xxx",
    "answer": "根据您提到的症状...",
    "related_entities": {
      "diseases": [...],
      "symptoms": [...],
      "checks": [...],
      "drugs": [...]
    },
    "citations": [
      {
        "text": "感冒是病毒引起的...",
        "entity_type": "Disease",
        "entity_id": "d_001"
      }
    ],
    "response_time_ms": 2340
  }
}
```

**GET /api/v1/qa/history** - 获取对话历史
```json
请求参数：
  - user_id: INT
  - session_id: STRING (可选)
  - limit: INT (默认 20)
  - offset: INT (默认 0)

响应：
{
  "status": "success",
  "data": {
    "conversations": [...],
    "total": 100,
    "returned": 20
  }
}
```

### 5.3 搜索端点

**GET /api/v1/search** - 通用搜索
```json
请求参数：
  - q: STRING (搜索关键词)
  - type: STRING (可选: Disease/Symptom/Drug/Check)
  - limit: INT (默认 10)

响应：
{
  "status": "success",
  "data": {
    "results": [
      {
        "id": "d_001",
        "type": "Disease",
        "name": "感冒",
        "match_score": 0.98
      }
    ]
  }
}
```

### 5.4 反馈端点

**POST /api/v1/feedback** - 提交反馈
```json
请求：
{
  "user_id": 1,
  "conversation_id": 123,
  "rating": 4,
  "feedback_type": "helpful",
  "comment": "很有帮助"
}

响应：
{
  "status": "success",
  "data": {
    "feedback_id": 456
  }
}
```

---

## 6. 模块划分

| 模块 | 文件 | 责任 |
|------|------|------|
| 数据采集 | `data_spider.py` | 爬虫、数据获取、断点续传 |
| 数据清洗 | `build_data.py` | 验证、去重、规范化 |
| 分词工具 | `max_cut.py` | 中文分词 |
| Neo4j 导入 | `neo4j_import.py` | 节点/关系创建、批量导入 |
| GraphRAG 集成 | `graphrag_service.py` | 封装 GraphRAG API、管理索引 |
| 问答服务 | `qa_service.py` | 接收问题、调用 GraphRAG、返回答案 |
| 用户管理 | `user_manager.py` | 用户 CRUD、认证、权限管理 |
| API 服务 | `app.py` | Flask/FastAPI 应用、路由、中间件 |

---

## 7. 开发优先级

### Phase A：数据管道（Week 1-2）
- [x] 优化爬虫（断点续传）
- [x] 数据清洗和验证
- [ ] Neo4j 批量导入

### Phase B：GraphRAG 集成（Week 2-3）
- [ ] GraphRAG 环境配置
- [ ] 数据格式转换（适配 GraphRAG 输入）
- [ ] 索引创建和测试
- [ ] 查询接口封装

### Phase C：用户和问答（Week 3-4）
- [ ] MySQL 用户管理
- [ ] 问答服务实现
- [ ] LLM 集成测试
- [ ] 对话历史记录

### Phase D：API 和前端（Week 4-5）
- [ ] RESTful API 实现
- [ ] 认证和授权
- [ ] Web 前端（可选）

### Phase E：测试和部署（Week 5-6）
- [ ] 单元测试（覆盖 > 80%）
- [ ] 集成测试
- [ ] 性能测试
- [ ] Docker 部署

---

## 8. 关键架构决策

### ADR-001：为什么选择 Neo4j 而非其他图数据库？
**决策**：使用 Neo4j 作为主图数据库。
**原因**：
- 成熟稳定，生产级别
- Cypher 查询语言强大且易学
- 丰富的 Python 驱动支持
- 免费社区版本足以满足毕业设计需求

### ADR-002：为什么使用 MySQL 而非 NoSQL？
**决策**：用户数据、对话历史使用 MySQL，而非纯 NoSQL。
**原因**：
- 结构化数据，关系明确
- 需要事务支持（用户反馈关联）
- 查询灵活性强
- 毕业设计更容易演示复杂查询

### ADR-003：为什么自实现 GraphRAG 而非使用框架？
**决策**：自实现 GraphRAG 流程。
**原因**：
- 更灵活可控，可以根据医疗领域特点优化检索策略
- 与现有 Neo4j 结构完美适配，不需要重新索引数据
- 基于现有代码扩展（Neo4jService 已实现），实现难度适中
- 便于调试和优化，可以精确控制每个步骤
- 不需要学习新框架，降低学习成本

---

## 9. 风险和对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 数据采集被网站阻止 | 无法获取数据 | 加强 User-Agent 伪装、降低采集速率、轮换 IP |
| Neo4j 性能瓶颈 | 查询变慢 | 提前设计好索引、限制查询深度 |
| LLM API 成本过高 | 经费超支 | 使用免费额度、实现本地缓存、提示词优化 |
| MySQL 数据丢失 | 用户数据损失 | 定期备份、使用事务、主从复制 |
| GraphRAG 实现复杂度 | 实现困难 | 分阶段实现、参考 RAG 最佳实践、逐步优化 |

---

**文档版本**：1.1  
**创建日期**：2024-01-15  
**更新日期**：2024-01-16（集成 GraphRAG）  
**下一步**：根据本文档分解为具体任务（TASKS.md）
