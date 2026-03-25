// API 请求/响应类型定义

import type { Entity } from './chat';

/** 问答请求 */
export interface QARequest {
  question: string;
  session_id?: string;
}

/** 问答响应 */
export interface QAResponse {
  question_id: string;
  session_id: string;
  question: string;
  answer: string;
  entities: Entity[];
  citations: any[];
  response_time_ms: number;
}

/** 登录请求 */
export interface LoginRequest {
  username: string;
  password: string;
}

/** 注册请求 */
export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

/** 用户信息 */
export interface User {
  id: number;
  username: string;
  email: string;
}

/** 登录响应 */
export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/** API 错误响应 */
export interface APIError {
  status: string;
  message: string;
  detail?: string;
}

/** 对话记录 */
export interface ConversationRecord {
  id: number;
  session_id: string;
  question: string;
  answer: string | null;
  entities: any[];
  citations: any[];
  response_time_ms: number | null;
  created_at: string;
}

/** 对话历史列表响应 */
export interface HistoryListResponse {
  status: 'success' | 'error';
  data: ConversationRecord[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/** 会话信息 */
export interface SessionInfo {
  session_id: string;
  first_question: string;
  created_at: string;
}

/** 会话列表响应 */
export interface SessionListResponse {
  status: 'success' | 'error';
  sessions: SessionInfo[];
  total: number;
}
