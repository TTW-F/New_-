// 知识库 API

import apiClient from './client';

/** 搜索医疗知识 */
export async function searchKnowledge(
  keyword: string,
  entityType?: string,
  limit: number = 20
): Promise<any> {
  const params: any = { keyword, limit };
  if (entityType && entityType !== 'all') {
    params.entity_type = entityType;
  }
  const response = await apiClient.get('/api/v1/knowledge/search', { params });
  return response.data;
}

/** 获取推荐知识 */
export async function getRecommendedKnowledge(limit: number = 10): Promise<any> {
  const response = await apiClient.get('/api/v1/knowledge/recommend', {
    params: { limit }
  });
  return response.data;
}

/** 获取实体详情 */
export async function getEntityDetail(
  entityName: string,
  entityType?: string
): Promise<any> {
  const params: any = {};
  if (entityType) {
    params.entity_type = entityType;
  }
  const response = await apiClient.get(`/api/v1/knowledge/entity/${entityName}`, { params });
  return response.data;
}

/** 获取知识库统计 */
export async function getKnowledgeStats(): Promise<any> {
  const response = await apiClient.get('/api/v1/knowledge/stats');
  return response.data;
}

/** 获取实体关系图谱数据 */
export async function getEntityGraph(
  entityName: string,
  entityType?: string,
  depth: number = 1
): Promise<any> {
  const params: any = { depth };
  if (entityType) {
    params.entity_type = entityType;
  }
  const response = await apiClient.get(`/api/v1/knowledge/graph/${entityName}`, { params });
  return response.data;
}
