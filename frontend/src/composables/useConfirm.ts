import { ref } from 'vue';

export interface ConfirmOptions {
  title?: string;
  message: string;
  description?: string;
  type?: 'success' | 'warning' | 'danger' | 'info';
  confirmText?: string;
  cancelText?: string;
}

interface ConfirmState extends ConfirmOptions {
  visible: boolean;
  resolve?: (value: boolean) => void;
}

const state = ref<ConfirmState>({
  visible: false,
  message: ''
});

export function useConfirm() {
  /**
   * 显示确认对话框
   */
  const confirm = (options: ConfirmOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      state.value = {
        ...options,
        visible: true,
        resolve
      };
    });
  };

  /**
   * 确认
   */
  const handleConfirm = () => {
    if (state.value.resolve) {
      state.value.resolve(true);
    }
    state.value.visible = false;
  };

  /**
   * 取消
   */
  const handleCancel = () => {
    if (state.value.resolve) {
      state.value.resolve(false);
    }
    state.value.visible = false;
  };

  return {
    state,
    confirm,
    handleConfirm,
    handleCancel
  };
}
