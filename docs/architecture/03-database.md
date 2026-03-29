# 数据库与图谱架构

**最后更新：** 2026-03-29

## 存储分工

- MySQL：账号、会话历史、反馈、token 黑名单
- Redis：缓存与连通性检查基础设施
- Neo4j：疾病/症状/药品等知识图谱关系

## MySQL 表

| 表名 | 说明 |
|---|---|
| `users` | 用户账号信息 |
| `token_blacklist` | 登出后的 token 拉黑 |
| `conversation_history` | 问答历史（支持软删除） |
| `feedback` | 对话反馈 |

## 关键字段设计

- `conversation_history.session_id`：多轮会话聚合键
- `conversation_history.related_entities`：JSON 实体列表
- `conversation_history.citations`：JSON 引用信息
- `conversation_history.is_deleted`：软删除标记

## 图谱层（Neo4j）

常见节点：`Disease`、`Symptom`、`Drug`、`Check`、`Department`、`Food`。  
常见关系：`HAS_SYMPTOM`、`RECOMMAND_DRUG`、`NEED_CHECK`、`BELONGS_DEPARTMENT`、`SHOULD_EAT`、`SHOULD_AVOID`、`COMPLICATION`。

## 数据流

```text
数据脚本(prepare_data/*)
 -> 结构化 JSON
 -> neo4j_import.py
 -> Neo4j 图谱

在线查询
 -> FastAPI
 -> service/router
 -> MySQL/Neo4j
```
