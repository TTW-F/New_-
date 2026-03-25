// 问答 API

import apiClient from './client';
import type { QARequest, QAResponse } from '@/types/api';

/** 同步问答 API */
export async function askQuestion(request: QARequest): Promise<QAResponse> {
  const response = await apiClient.post<QAResponse>('/api/v1/qa', request);
  return response.data;
}

/** 清空会话 */
export async function clearSession(sessionId: string): Promise<void> {
  await apiClient.post('/api/v1/qa/clear', null, {
    params: { session_id: sessionId }
  });
}

/** 删除会话 */
export async function deleteSession(sessionId: string): Promise<void> {
  await apiClient.delete(`/api/v1/qa/session/${sessionId}`);
}
