/**
 * 验证邮箱格式
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * 验证用户名格式
 * 规则: 3-50个字符,只能包含字母、数字、下划线
 */
export function isValidUsername(username: string): boolean {
  const usernameRegex = /^[a-zA-Z0-9_]{3,50}$/;
  return usernameRegex.test(username);
}

/**
 * 验证密码强度
 * 规则: 至少8个字符,包含字母和数字（与后端一致）
 */
export function isValidPassword(password: string): boolean {
  if (password.length < 8) return false;
  
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumber = /\d/.test(password);
  return hasLetter && hasNumber;
}

/**
 * 验证手机号格式
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
}

/**
 * 验证 URL 格式
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * 验证必填字段
 */
export function isRequired(value: string | null | undefined): boolean {
  if (value === null || value === undefined) return false;
  return value.trim().length > 0;
}

/**
 * 验证字符串长度
 */
export function isValidLength(value: string, min: number, max: number): boolean {
  const length = value.trim().length;
  return length >= min && length <= max;
}

/**
 * 表单验证规则
 */
export interface ValidationRule {
  validator: (value: any) => boolean;
  message: string;
}

/**
 * 执行验证
 */
export function validate(value: any, rules: ValidationRule[]): string | null {
  for (const rule of rules) {
    if (!rule.validator(value)) {
      return rule.message;
    }
  }
  return null;
}

/**
 * 常用验证规则
 */
export const rules = {
  required: (message: string = '此字段为必填项'): ValidationRule => ({
    validator: isRequired,
    message
  }),
  
  email: (message: string = '请输入有效的邮箱地址'): ValidationRule => ({
    validator: isValidEmail,
    message
  }),
  
  username: (message: string = '用户名必须是3-50个字符,只能包含字母、数字、下划线'): ValidationRule => ({
    validator: isValidUsername,
    message
  }),
  
  password: (message: string = '密码必须至少8个字符,包含字母和数字'): ValidationRule => ({
    validator: isValidPassword,
    message
  }),
  
  phone: (message: string = '请输入有效的手机号'): ValidationRule => ({
    validator: isValidPhone,
    message
  }),
  
  minLength: (min: number, message?: string): ValidationRule => ({
    validator: (value: string) => value.length >= min,
    message: message || `最少需要${min}个字符`
  }),
  
  maxLength: (max: number, message?: string): ValidationRule => ({
    validator: (value: string) => value.length <= max,
    message: message || `最多允许${max}个字符`
  })
};
