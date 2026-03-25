// 对话历史 API

import apiClient from './client';
import type { HistoryListResponse, SessionListResponse } from '@/types/api';

/** 获取会话列表 */
export async function getSessions(): Promise<SessionListResponse> {
  const response = await apiClient.get<SessionListResponse>('/api/v1/history/sessions');
  return response.data;
}

/** 获取会话列表（带分页） */
export async function getSessionList(page: number = 1, pageSize: number = 10): Promise<any> {
  const response = await apiClient.get('/api/v1/history/sessions', {
    params: { page, page_size: pageSize }
  });
  return response.data;
}

/** 获取对话历史 */
export async function getHistory(params?: {
  session_id?: string;
  page?: number;
  page_size?: number;
}): Promise<HistoryListResponse> {
  const response = await apiClient.get<HistoryListResponse>('/api/v1/history', { params });
  return response.data;
}

/** 删除会话 */
export async function deleteSession(sessionId: string): Promise<void> {
  await apiClient.delete(`/api/v1/history/sessions/${sessionId}`);
}

