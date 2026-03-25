# API参考文档

**最后更新**: 2026-03-25  
**API版本**: v1  
**Base URL**: `http://localhost:8000/api/v1`

---

## 📋 目录

- [认证](#认证)
- [认证端点](#认证端点)
- [问答端点](#问答端点)
- [历史记录端点](#历史记录端点)
- [反馈端点](#反馈端点)
- [健康检查端点](#健康检查端点)
- [错误响应](#错误响应)
- [速率限制](#速率限制)

---

## 🔐 认证

### 认证方式

API使用JWT (JSON Web Token) 进行认证。

### 获取Token

通过登录端点获取访问令牌：

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user123",
  "password": "password123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com"
  }
}
```

### 使用Token

在请求头中添加Authorization字段：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token有效期

- 默认有效期: 24小时
- 过期后需要重新登录

---

## 👤 认证端点

### 1. 用户注册

**端点**: `POST /auth/register`

**认证**: 不需要

**请求体**:
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "Password123!"
}
```

**字段说明**:
- `username`: 用户名 (3-50字符，唯一)
- `email`: 邮箱地址 (有效邮箱格式，唯一)
- `password`: 密码 (至少8位，包含大小写字母和数字)

**成功响应** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "created_at": "2026-03-25T12:00:00Z"
  }
}
```

**错误响应**:
```json
// 400 - 用户名已存在
{
  "detail": "用户名已被使用"
}

// 400 - 邮箱已存在
{
  "detail": "邮箱已被注册"
}

// 400 - 密码强度不足
{
  "detail": "密码必须至少8位，包含大小写字母和数字"
}
```

---

### 2. 用户登录 (JSON)

**端点**: `POST /auth/login`

**认证**: 不需要

**请求体**:
```json
{
  "username": "user123",
  "password": "Password123!"
}
```

**成功响应** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com"
  }
}
```

**错误响应**:
```json
// 401 - 用户名或密码错误
{
  "detail": "用户名或密码错误"
}

// 403 - 账户已禁用
{
  "detail": "账户已被禁用"
}
```

---

### 3. 用户登录 (表单)

**端点**: `POST /auth/login-form`

**认证**: 不需要

**Content-Type**: `application/x-www-form-urlencoded`

**请求体**:
```
username=user123&password=Password123!
```

**响应**: 同JSON登录

---

### 4. 用户登出

**端点**: `POST /auth/logout`

**认证**: 需要

**请求头**:
```http
Authorization: Bearer <token>
```

**成功响应** (200 OK):
```json
{
  "message": "登出成功"
}
```

---

### 5. 获取当前用户信息

**端点**: `GET /auth/me`

**认证**: 需要

**请求头**:
```http
Authorization: Bearer <token>
```

**成功响应** (200 OK):
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "created_at": "2026-03-25T12:00:00Z",
  "is_active": true
}
```

---

## 💬 问答端点

### 1. 同步问答

**端点**: `POST /qa`

**认证**: 需要

**请求体**:
```json
{
  "question": "糖尿病有什么症状？",
  "session_id": "session-123"  // 可选，不提供则创建新会话
}
```

**字段说明**:
- `question`: 用户问题 (必填，1-1000字符)
- `session_id`: 会话ID (可选，用于多轮对话)

**成功响应** (200 OK):
```json
{
  "question_id": "conv-456",
  "session_id": "session-123",
  "question": "糖尿病有什么症状？",
  "answer": "糖尿病的主要症状包括：\n\n1. **多饮**：经常感到口渴\n2. **多尿**：尿量增多\n3. **多食**：容易饥饿\n4. **体重下降**：不明原因的体重减轻\n\n建议您及时就医检查。",
  "tool_calls": [
    {
      "id": "call_abc123",
      "name": "search_disease_info",
      "arguments": {
        "disease_name": "糖尿病"
      },
      "result": "{...}",
      "status": "success"
    }
  ],
  "entities": [
    {
      "type": "Disease",
      "name": "糖尿病"
    },
    {
      "type": "Symptom",
      "name": "多饮"
    }
  ],
  "response_time_ms": 1234
}
```

**错误响应**:
```json
// 400 - 问题为空
{
  "detail": "问题不能为空"
}

// 500 - Agent错误
{
  "detail": "处理问题时发生错误，请稍后重试"
}
```

---

### 2. 流式问答 (SSE)

**端点**: `POST /qa/stream`

**认证**: 需要

**Content-Type**: `application/json`

**Accept**: `text/event-stream`

**请求体**:
```json
{
  "question": "糖尿病怎么治疗？",
  "session_id": "session-123"
}
```

**响应**: Server-Sent Events (SSE) 流

**事件类型**:

#### tool_start - 工具开始执行
```
data: {"type":"tool_start","tool_id":"call_abc123","tool_name":"search_disease_info","arguments":{"disease_name":"糖尿病"}}
```

#### tool_end - 工具执行完成
```
data: {"type":"tool_end","tool_id":"call_abc123","status":"success","result":"{\"disease\":{...}}"}
```

#### chunk - 文本内容块
```
data: {"type":"chunk","content":"糖尿病"}

data: {"type":"chunk","content":"的治疗"}

data: {"type":"chunk","content":"包括："}
```

#### meta - 元数据
```
data: {"type":"meta","entities":[{"type":"Disease","name":"糖尿病"}],"session_id":"session-123","response_time_ms":1234}
```

#### 结束标记
```
data: [DONE]
```

**完整示例**:
```
data: {"type":"tool_start","tool_id":"call_1","tool_name":"search_disease_info","arguments":{"disease_name":"糖尿病"}}

data: {"type":"tool_end","tool_id":"call_1","status":"success","result":"..."}

data: {"type":"chunk","content":"糖尿病"}

data: {"type":"chunk","content":"的治疗方案"}

data: {"type":"chunk","content":"主要包括："}

data: {"type":"meta","entities":[...],"session_id":"session-123"}

data: [DONE]
```

**客户端示例**:
```javascript
const eventSource = new EventSource('/api/v1/qa/stream', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

eventSource.onmessage = (event) => {
  if (event.data === '[DONE]') {
    eventSource.close();
    return;
  }
  
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'tool_start':
      console.log('工具开始:', data.tool_name);
      break;
    case 'tool_end':
      console.log('工具完成:', data.status);
      break;
    case 'chunk':
      appendContent(data.content);
      break;
    case 'meta':
      console.log('元数据:', data.entities);
      break;
  }
};

eventSource.onerror = (error) => {
  console.error('SSE错误:', error);
  eventSource.close();
};
```

---

### 3. 问答服务健康检查

**端点**: `GET /qa/health`

**认证**: 不需要

**成功响应** (200 OK):
```json
{
  "status": "healthy",
  "neo4j_connected": true,
  "agent_ready": true
}
```

---

### 4. 恢复会话上下文

**端点**: `POST /qa/restore-session`

**认证**: 需要

**请求体**:
```json
{
  "session_id": "session-123"
}
```

**功能**: 从数据库加载历史对话到Agent记忆，用于恢复多轮对话上下文

**成功响应** (200 OK):
```json
{
  "message": "会话上下文已恢复",
  "session_id": "session-123",
  "messages_loaded": 5
}
```

---

### 5. 清除会话

**端点**: `POST /qa/clear-session`

**认证**: 需要

**请求体**:
```json
{
  "session_id": "session-123"
}
```

**功能**: 清除Agent记忆中的会话上下文（不删除数据库记录）

**成功响应** (200 OK):
```json
{
  "message": "会话已清除",
  "session_id": "session-123"
}
```

---

## 📜 历史记录端点

### 1. 获取对话历史

**端点**: `GET /history`

**认证**: 需要

**查询参数**:
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 20，最大: 100)

**请求示例**:
```http
GET /api/v1/history?page=1&page_size=20
Authorization: Bearer <token>
```

**成功响应** (200 OK):
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5,
  "conversations": [
    {
      "id": 1,
      "session_id": "session-123",
      "question": "糖尿病有什么症状？",
      "answer": "糖尿病的主要症状包括...",
      "tool_calls": [...],
      "entities": [...],
      "response_time_ms": 1234,
      "created_at": "2026-03-25T12:00:00Z"
    }
  ]
}
```

---

### 2. 获取会话列表

**端点**: `GET /history/sessions`

**认证**: 需要

**成功响应** (200 OK):
```json
{
  "sessions": [
    {
      "session_id": "session-123",
      "first_message": "糖尿病有什么症状？",
      "message_count": 5,
      "created_at": "2026-03-25T12:00:00Z",
      "updated_at": "2026-03-25T13:00:00Z"
    }
  ]
}
```

---

### 3. 获取用户统计

**端点**: `GET /history/stats`

**认证**: 需要

**成功响应** (200 OK):
```json
{
  "total_conversations": 100,
  "total_sessions": 20,
  "avg_response_time_ms": 1500,
  "most_asked_topics": [
    {
      "topic": "糖尿病",
      "count": 15
    }
  ]
}
```

---

### 4. 获取单个对话

**端点**: `GET /history/{conversation_id}`

**认证**: 需要

**路径参数**:
- `conversation_id`: 对话ID

**成功响应** (200 OK):
```json
{
  "id": 1,
  "session_id": "session-123",
  "question": "糖尿病有什么症状？",
  "answer": "糖尿病的主要症状包括...",
  "tool_calls": [...],
  "entities": [...],
  "response_time_ms": 1234,
  "created_at": "2026-03-25T12:00:00Z"
}
```

**错误响应**:
```json
// 404 - 对话不存在
{
  "detail": "对话不存在"
}

// 403 - 无权访问
{
  "detail": "无权访问此对话"
}
```

---

### 5. 删除对话

**端点**: `DELETE /history/{conversation_id}`

**认证**: 需要

**路径参数**:
- `conversation_id`: 对话ID

**成功响应** (200 OK):
```json
{
  "message": "对话已删除",
  "conversation_id": 1
}
```

---

## 💭 反馈端点

### 1. 提交反馈

**端点**: `POST /feedback`

**认证**: 需要

**请求体**:
```json
{
  "conversation_id": 1,
  "rating": 5,
  "comment": "回答很准确，很有帮助！"
}
```

**字段说明**:
- `conversation_id`: 对话ID (必填)
- `rating`: 评分 (必填，1-5)
- `comment`: 评论 (可选，最多500字符)

**成功响应** (201 Created):
```json
{
  "id": 1,
  "conversation_id": 1,
  "rating": 5,
  "comment": "回答很准确，很有帮助！",
  "created_at": "2026-03-25T12:00:00Z"
}
```

---

### 2. 获取对话反馈

**端点**: `GET /feedback/{conversation_id}`

**认证**: 需要

**路径参数**:
- `conversation_id`: 对话ID

**成功响应** (200 OK):
```json
{
  "id": 1,
  "conversation_id": 1,
  "rating": 5,
  "comment": "回答很准确，很有帮助！",
  "created_at": "2026-03-25T12:00:00Z"
}
```

---

## 🏥 健康检查端点

### 系统健康检查

**端点**: `GET /health`

**认证**: 不需要

**成功响应** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-03-25T12:00:00Z",
  "components": {
    "database": "healthy",
    "neo4j": "healthy",
    "agent": "healthy"
  },
  "version": "1.0.0"
}
```

**部分故障响应** (200 OK):
```json
{
  "status": "degraded",
  "timestamp": "2026-03-25T12:00:00Z",
  "components": {
    "database": "healthy",
    "neo4j": "unhealthy",
    "agent": "healthy"
  },
  "version": "1.0.0"
}
```

**完全故障响应** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "timestamp": "2026-03-25T12:00:00Z",
  "components": {
    "database": "unhealthy",
    "neo4j": "unhealthy",
    "agent": "unhealthy"
  },
  "version": "1.0.0"
}
```

---

## ⚠️ 错误响应

### 标准错误格式

所有错误响应都遵循以下格式：

```json
{
  "detail": "错误描述信息"
}
```

### HTTP状态码

| 状态码 | 说明 | 场景 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或Token无效 |
| 403 | Forbidden | 无权限访问资源 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 429 | Too Many Requests | 超过速率限制 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务暂时不可用 |

### 常见错误示例

#### 401 - 未认证
```json
{
  "detail": "未提供认证凭据"
}
```

#### 401 - Token无效
```json
{
  "detail": "Token已过期或无效"
}
```

#### 422 - 验证错误
```json
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 429 - 速率限制
```json
{
  "detail": "请求过于频繁，请稍后再试"
}
```

---

## 🚦 速率限制

### 限制规则

| 用户类型 | 限制 | 时间窗口 |
|---------|------|---------|
| 匿名用户 | 10次 | 1分钟 |
| 认证用户 | 60次 | 1分钟 |
| 问答端点 | 30次 | 1分钟 |

### 响应头

速率限制信息会在响应头中返回：

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1711363200
```

**字段说明**:
- `X-RateLimit-Limit`: 时间窗口内的请求限制
- `X-RateLimit-Remaining`: 剩余可用请求数
- `X-RateLimit-Reset`: 限制重置时间 (Unix时间戳)

### 超限响应

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1711363200
Retry-After: 60

{
  "detail": "请求过于频繁，请60秒后再试"
}
```

---

## 📝 最佳实践

### 1. 错误处理

```javascript
try {
  const response = await fetch('/api/v1/qa', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ question: '...' })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  const data = await response.json();
  // 处理成功响应
} catch (error) {
  console.error('请求失败:', error.message);
}
```

### 2. Token刷新

```javascript
// 检查Token是否即将过期
function isTokenExpiringSoon(token) {
  const payload = JSON.parse(atob(token.split('.')[1]));
  const expiresAt = payload.exp * 1000;
  const now = Date.now();
  return expiresAt - now < 5 * 60 * 1000; // 5分钟内过期
}

// 自动刷新Token
if (isTokenExpiringSoon(token)) {
  await refreshToken();
}
```

### 3. 重试机制

```javascript
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      
      if (response.status === 429) {
        const retryAfter = response.headers.get('Retry-After');
        await sleep(retryAfter * 1000);
        continue;
      }
      
      return response;
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(1000 * Math.pow(2, i)); // 指数退避
    }
  }
}
```

---

## 🔗 相关文档

- [后端架构文档](./backend.md)
- [Agent系统文档](./agent.md)
- [前端架构文档](./frontend.md)
- [数据库架构文档](./database.md)

---

*本文档由 doc-updater agent 生成 @ 2026-03-25*
