// 用户相关 API

import apiClient from './client';

/** 修改密码 */
export async function changePassword(
  oldPassword: string,
  newPassword: string
): Promise<any> {
  const response = await apiClient.post('/api/v1/auth/change-password', null, {
    params: {
      old_password: oldPassword,
      new_password: newPassword
    }
  });
  return response.data;
}
