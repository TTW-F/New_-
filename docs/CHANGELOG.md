# 文档更新日志

## 2026-03-25 (晚上) - 历史记录功能完整修复

### 修复内容

#### 🐛 后端历史记录API修复

**问题描述**:
- 前端调用 `/api/v1/history/sessions` 期望返回带分页的会话详细列表
- 后端只返回简单的会话ID列表，缺少消息数量、平均响应时间等信息
- 缺少删除会话的API端点
- Schema 定义与实际返回数据不匹配导致验证失败

**修复内容**:

1. **api/services/conversation_service.py**
   - 新增 `get_sessions_with_details()` 方法
   - 支持分页查询（page, page_size）
   - 返回会话详细信息：
     - session_id: 会话ID
     - title: 会话标题（取第一条问题的前30字）
     - message_count: 消息数量
     - avg_response_time: 平均响应时间（毫秒）
     - updated_at: 最后更新时间
     - last_question: 最后一条提问
   - 新增 `delete_session()` 方法用于软删除整个会话

2. **api/routers/history.py**
   - 更新 `GET /api/v1/history/sessions` 端点
   - 添加分页参数（page, page_size）
   - 调用新的 `get_sessions_with_details()` 方法
   - 新增 `DELETE /api/v1/history/sessions/{session_id}` 端点
   - 支持删除整个会话的所有对话记录

3. **api/schemas/history.py**
   - 修复 `SessionInfo` schema 定义
   - 更新字段：title, message_count, avg_response_time, updated_at, last_question
   - 移除旧字段：first_question, created_at

4. **前端日期格式化修复**
   - **frontend/src/utils/format.ts**
     - 增强 `formatDistanceToNow()` 函数
     - 添加日期有效性检查
     - 添加错误处理和降级显示
   - **frontend/src/views/HomeView.vue**
     - 修复 `formatTime()` 函数，添加空值检查
     - 添加 try-catch 错误处理
   - **frontend/src/views/HistoryView.vue**
     - 同样修复日期格式化问题

5. **测试脚本**
   - 创建 `测试历史记录.bat` 用于测试历史记录API
   - 创建 `测试会话列表API.bat` 用于检查返回数据格式
   - 创建 `检查历史记录数据.py` 和 `.bat` 用于检查数据库数据

**API变更**:
```
GET /api/v1/history/sessions?page=1&page_size=10
返回格式：
{
  "status": "success",
  "sessions": [
    {
      "session_id": "uuid",
      "title": "关于高血压的咨询...",
      "message_count": 5,
      "avg_response_time": 1234,
      "updated_at": "2026-03-25T20:00:00",
      "last_question": "高血压患者应该注意什么？"
    }
  ],
  "total": 10
}

DELETE /api/v1/history/sessions/{session_id}
软删除指定会话的所有对话记录
```

**前端兼容性**:
- frontend/src/views/HistoryView.vue 已修复日期显示问题
- frontend/src/views/HomeView.vue 已修复日期显示问题
- frontend/src/api/history.ts 已有对应的API调用
- frontend/src/utils/format.ts 增强了日期格式化的健壮性

---

## 2026-03-25 (下午) - 前端页面更新

### 更新内容

#### 📄 前端架构文档 (docs/CODEMAPS/frontend.md)

**新增页面文档**:
1. **HomeView.vue** - 首页
   - 系统特点展示（4个特性卡片）
   - 最近对话列表
   - 快速导航按钮

2. **HistoryView.vue** - 历史记录页面
   - 会话列表展示
   - 搜索和过滤功能
   - 分页加载
   - 继续对话/删除会话

3. **KnowledgeView.vue** - 知识库页面
   - 医疗实体搜索
   - 类型过滤（疾病/症状/药品/检查）
   - 搜索结果展示
   - 实体详情查看
   - 向AI咨询功能

4. **ProfileView.vue** - 个人中心页面
   - 用户信息展示
   - 修改密码功能
   - 退出登录

5. **AdminView.vue** - 管理后台页面（开发中）
   - 系统管理功能规划

6. **Navbar.vue** - 顶部导航栏组件
   - 全局导航菜单
   - 用户下拉菜单
   - 响应式设计

**更新路由配置**:
- 新增5个路由（Home, History, Knowledge, Profile, Admin）
- 更新路由守卫逻辑
- 添加用户信息自动恢复

**新增内容**:
- 页面视图详解（8个页面）
- 导航组件说明
- 页面样式系统（CSS变量）
- 响应式设计规范
- 页面间导航流程图

### 文档统计

- **新增页面文档**: 6个
- **新增代码示例**: 20+个
- **新增功能说明**: 30+项
- **文档增量**: ~8,000字

### 页面功能覆盖

✅ 首页（系统介绍）  
✅ 智能问答（聊天界面）  
✅ 历史记录（会话管理）  
✅ 知识库（实体搜索）  
✅ 个人中心（用户管理）  
✅ 管理后台（规划中）  
✅ 登录认证  
✅ 404处理  

---

## 2026-03-25 (上午) - 全面文档更新

### 新增文档

#### 📚 代码地图系统 (docs/CODEMAPS/)

1. **INDEX.md** - 文档导航索引
   - 系统架构概览
   - 技术栈总结
   - 项目统计数据
   - 快速导航指南

2. **backend.md** - 后端架构文档
   - FastAPI应用结构
   - 三层架构设计（路由-服务-数据）
   - 5个API路由模块详解
   - 3个服务层类详解
   - JWT认证机制
   - 速率限制配置
   - 依赖注入模式
   - 错误处理规范
   - 性能优化建议

3. **agent.md** - Agent系统文档
   - MedicalAgent核心架构
   - Agent循环流程（最多5轮迭代）
   - 5个内置工具详解
   - 工具注册机制
   - 对话记忆管理
   - 流式输出事件类型
   - Function Calling实现
   - 错误处理策略

4. **frontend.md** - 前端架构文档
   - Vue 3 + TypeScript + Pinia架构
   - 组件系统（8大类34个组件）
   - 状态管理（3个Store）
   - API通信层（5个模块）
   - SSE流式通信实现
   - 路由系统和守卫
   - 工具函数库
   - 样式系统（SCSS）

5. **database.md** - 数据库架构文档
   - 双数据库架构设计
   - Neo4j知识图谱
     - 6种节点类型（17,550个节点）
     - 7种关系类型（110,000条关系）
     - 完整的Cypher查询示例
   - SQLite关系数据库
     - 3张表结构（users, conversations, feedback）
   - 6个查询接口详解
   - 数据导入流程
   - 性能优化策略
   - 备份恢复方案

6. **api.md** - API参考文档
   - 完整的API端点列表（18个端点）
   - JWT认证流程
   - 请求/响应格式
   - SSE流式通信协议
   - 错误响应规范
   - 速率限制规则
   - 客户端最佳实践

### 更新文档

1. **.kiro/CODE_MAP.md**
   - 添加详细文档链接
   - 更新最后更新时间

### 文档统计

- **总文档数**: 6个核心文档
- **总字数**: 约50,000字
- **代码示例**: 100+个
- **架构图**: 10+个
- **表格**: 30+个

### 文档特点

✅ **从代码生成**: 所有文档都基于实际代码结构生成，确保准确性  
✅ **中文编写**: 全中文文档，便于阅读理解  
✅ **结构清晰**: 统一的文档结构和格式  
✅ **示例丰富**: 包含大量代码示例和使用场景  
✅ **实用性强**: 提供最佳实践和故障排查指南  
✅ **易于维护**: 模块化文档，便于更新  

### 覆盖范围

- ✅ 前端架构（Vue 3）
- ✅ 后端架构（FastAPI）
- ✅ Agent系统（MedicalAgent）
- ✅ 数据库设计（Neo4j + SQLite）
- ✅ API接口（18个端点）
- ✅ 认证授权（JWT）
- ✅ 流式通信（SSE）
- ✅ 状态管理（Pinia）
- ✅ 工具系统（5个工具）
- ✅ 错误处理
- ✅ 性能优化
- ✅ 部署运维

### 使用指南

#### 新手入门
1. 阅读 [INDEX.md](./CODEMAPS/INDEX.md) 了解整体架构
2. 阅读 [backend.md](./CODEMAPS/backend.md) 理解后端结构
3. 阅读 [agent.md](./CODEMAPS/agent.md) 掌握核心逻辑
4. 阅读 [frontend.md](./CODEMAPS/frontend.md) 学习前端实现

#### 功能开发
- 添加新API → [backend.md](./CODEMAPS/backend.md) + [api.md](./CODEMAPS/api.md)
- 添加新工具 → [agent.md](./CODEMAPS/agent.md)
- 修改UI → [frontend.md](./CODEMAPS/frontend.md)
- 扩展数据 → [database.md](./CODEMAPS/database.md)

#### 问题排查
1. 查看对应模块的文档
2. 检查数据流图
3. 查看依赖关系
4. 参考故障排查章节

---

## 下一步计划

### 短期（1周内）
- [ ] 添加部署文档
- [ ] 添加测试文档
- [ ] 添加性能监控文档

### 中期（1个月内）
- [ ] 添加开发指南
- [ ] 添加贡献指南
- [ ] 添加安全最佳实践

### 长期（持续）
- [ ] 保持文档与代码同步
- [ ] 根据反馈完善文档
- [ ] 添加更多示例和教程

---

*文档由 doc-updater agent 自动生成和维护*
