import type { AxiosError } from 'axios';

/**
 * 错误类型
 */
export enum ErrorType {
  NETWORK = 'NETWORK',
  AUTH = 'AUTH',
  VALIDATION = 'VALIDATION',
  SERVER = 'SERVER',
  UNKNOWN = 'UNKNOWN'
}

/**
 * 应用错误类
 */
export class AppError extends Error {
  type: ErrorType;
  statusCode?: number;
  details?: any;

  constructor(message: string, type: ErrorType = ErrorType.UNKNOWN, statusCode?: number, details?: any) {
    super(message);
    this.name = 'AppError';
    this.type = type;
    this.statusCode = statusCode;
    this.details = details;
  }
}

/**
 * 处理 Axios 错误
 */
export function handleAxiosError(error: AxiosError): AppError {
  if (!error.response) {
    return new AppError(
      '网络连接失败,请检查您的网络设置',
      ErrorType.NETWORK
    );
  }

  const { status, data } = error.response;
  const serverMessage =
    (data as any)?.message ||
    (data as any)?.detail ||
    (typeof data === 'string' ? data : '');
  const message = serverMessage || '请求失败';

  switch (status) {
    case 400:
      return new AppError(message, ErrorType.VALIDATION, status, data);
    case 401:
      // 登录失败（用户名/密码错误）与 Token 过期都会返回 401，这里优先展示服务端 message
      return new AppError(message || '用户名或密码错误', ErrorType.AUTH, status, data);
    case 403:
      return new AppError('没有权限访问此资源', ErrorType.AUTH, status);
    case 422:
      return new AppError(message || '请求参数验证失败', ErrorType.VALIDATION, status, data);
    case 404:
      return new AppError('请求的资源不存在', ErrorType.SERVER, status);
    case 500:
      return new AppError('服务器内部错误', ErrorType.SERVER, status);
    case 502:
      return new AppError('网关错误', ErrorType.SERVER, status);
    case 503:
      return new AppError('服务暂时不可用', ErrorType.SERVER, status);
    default:
      return new AppError(message, ErrorType.SERVER, status, data);
  }
}

/**
 * 处理 SSE 错误
 */
export function handleSSEError(error: Event | Error): AppError {
  if (error instanceof Error) {
    return new AppError(
      `流式连接错误: ${error.message}`,
      ErrorType.NETWORK
    );
  }

  return new AppError(
    '流式连接中断,请重试',
    ErrorType.NETWORK
  );
}

/**
 * 获取用户友好的错误消息
 */
export function getUserFriendlyMessage(error: Error | AppError): string {
  if (error instanceof AppError) {
    return error.message;
  }

  // 默认错误消息
  return '操作失败,请稍后重试';
}

/**
 * 记录错误
 */
export function logError(error: Error | AppError, context?: string): void {
  const timestamp = new Date().toISOString();
  const errorInfo = {
    timestamp,
    context,
    message: error.message,
    stack: error.stack,
    ...(error instanceof AppError && {
      type: error.type,
      statusCode: error.statusCode,
      details: error.details
    })
  };

  console.error('[Error]', errorInfo);

  // 在生产环境中,可以将错误发送到错误追踪服务
  // if (import.meta.env.PROD) {
  //   sendToErrorTracking(errorInfo);
  // }
}

/**
 * 全局错误处理器
 */
export function handleError(error: any, context?: string): AppError {
  let appError: AppError;

  if (error instanceof AppError) {
    appError = error;
  } else if (error.isAxiosError) {
    appError = handleAxiosError(error);
  } else if (error instanceof Error) {
    appError = new AppError(error.message, ErrorType.UNKNOWN);
  } else {
    appError = new AppError('未知错误', ErrorType.UNKNOWN);
  }

  logError(appError, context);
  return appError;
}
