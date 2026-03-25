/**
 * 后台管理 API
 */

import { apiClient } from './client';

/**
 * 统计数据接口
 */
export interface Stats {
  total_users: number;
  today_users: number;
  total_conversations: number;
  today_conversations: number;
  total_entities: number;
  system_status: string;
}

/**
 * 用户列表项接口
 */
export interface UserListItem {
  id: number;
  username: string;
  email: string;
  user_type: string;
  is_active: boolean;
  created_at: string;
}

/**
 * 用户详情接口
 */
export interface UserDetail extends UserListItem {
  updated_at: string;
  stats: {
    conversation_count: number;
    feedback_count: number;
  };
}

/**
 * 对话列表项接口
 */
export interface ConversationListItem {
  id: number;
  user_id: number;
  username: string;
  session_id: string;
  title: string;
  message_count: number;
  created_at: string;
}

/**
 * 对话详情接口
 */
export interface ConversationDetail {
  id: number;
  user_id: number;
  username: string;
  session_id: string;
  question: string;
  answer: string;
  entities: any[];
  citations: any[];
  response_time: number;
  created_at: string;
  session_messages: Array<{
    id: number;
    question: string;
    answer: string;
    created_at: string;
  }>;
}

/**
 * 日志项接口
 */
export interface LogItem {
  id: number;
  level: string;
  message: string;
  timestamp: string;
}

/**
 * 获取系统统计数据
 */
export async function getStats(): Promise<Stats> {
  const response = await apiClient.get<Stats>('/admin/stats');
  return response.data;
}

/**
 * 获取用户列表
 */
export async function getUsers(params: {
  search?: string;
  page?: number;
  page_size?: number;
}): Promise<{
  users: UserListItem[];
  total: number;
  page: number;
  page_size: number;
}> {
  const response = await apiClient.get('/admin/users', { params });
  return response.data;
}

/**
 * 获取用户详情
 */
export async function getUserDetail(userId: number): Promise<UserDetail> {
  const response = await apiClient.get<UserDetail>(`/admin/users/${userId}`);
  return response.data;
}

/**
 * 获取对话列表
 */
export async function getConversations(params: {
  filter_type?: 'all' | 'today' | 'week';
  page?: number;
  page_size?: number;
}): Promise<{
  conversations: ConversationListItem[];
  total: number;
  page: number;
  page_size: number;
}> {
  const response = await apiClient.get('/admin/conversations', { params });
  return response.data;
}

/**
 * 获取对话详情
 */
export async function getConversationDetail(conversationId: number): Promise<ConversationDetail> {
  const response = await apiClient.get<ConversationDetail>(`/admin/conversations/${conversationId}`);
  return response.data;
}

/**
 * 获取系统日志
 */
export async function getLogs(params: {
  level?: 'all' | 'info' | 'warning' | 'error';
  page?: number;
  page_size?: number;
}): Promise<{
  logs: LogItem[];
  total: number;
  page: number;
  page_size: number;
}> {
  const response = await apiClient.get('/admin/logs', { params });
  return response.data;
}
