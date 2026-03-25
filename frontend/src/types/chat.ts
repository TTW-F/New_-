// 聊天相关类型定义

/** 消息角色 */
export type MessageRole = 'user' | 'assistant' | 'system';

/** 消息状态 */
export type MessageStatus = 'sending' | 'sent' | 'streaming' | 'completed' | 'error';

/** 工具调用状态 */
export type ToolCallStatus = 'pending' | 'running' | 'success' | 'error';

/** 实体类型 */
export type EntityType = 'Disease' | 'Symptom' | 'Drug' | 'Treatment';

/** 实体 */
export interface Entity {
  type: EntityType;
  name: string;
  text: string;  // 添加 text 字段用于显示
  score?: number;
}

/** 工具调用 */
export interface ToolCall {
  id: string;
  tool_id: string;
  tool_name: string;
  arguments: Record<string, any>;
  result?: string;
  error?: string;
  status: ToolCallStatus;
  entities?: Entity[];
  timestamp?: string;
}

/** 消息 */
export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  status: MessageStatus;
  toolCalls?: ToolCall[];
  entities?: Entity[];
  timestamp: string;
  sessionId: string;
}

/** 会话 */
export interface Session {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  messages: Message[];  // 添加 messages 字段
}
