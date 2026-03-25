import { ref } from 'vue';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

const toasts = ref<Toast[]>([]);
let toastId = 0;

export function useToast() {
  /**
   * 显示 Toast
   */
  const showToast = (
    type: Toast['type'],
    message: string,
    duration: number = 3000
  ): void => {
    const id = `toast-${++toastId}`;
    const toast: Toast = { id, type, message, duration };

    toasts.value.push(toast);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
  };

  /**
   * 移除 Toast
   */
  const removeToast = (id: string): void => {
    const index = toasts.value.findIndex(t => t.id === id);
    if (index > -1) {
      toasts.value.splice(index, 1);
    }
  };

  /**
   * 成功提示
   */
  const success = (message: string, duration?: number): void => {
    showToast('success', message, duration);
  };

  /**
   * 错误提示
   */
  const error = (message: string, duration?: number): void => {
    showToast('error', message, duration);
  };

  /**
   * 警告提示
   */
  const warning = (message: string, duration?: number): void => {
    showToast('warning', message, duration);
  };

  /**
   * 信息提示
   */
  const info = (message: string, duration?: number): void => {
    showToast('info', message, duration);
  };

  /**
   * 清空所有 Toast
   */
  const clearAll = (): void => {
    toasts.value = [];
  };

  return {
    toasts,
    success,
    error,
    warning,
    info,
    removeToast,
    clearAll
  };
}
