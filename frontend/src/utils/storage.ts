/**
 * LocalStorage 封装
 */
export const storage = {
  /**
   * 获取数据
   */
  get<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(key);
      if (!item) return null;
      return JSON.parse(item) as T;
    } catch (error) {
      console.error(`Failed to get item from localStorage: ${key}`, error);
      return null;
    }
  },

  /**
   * 设置数据
   */
  set<T>(key: string, value: T): void {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Failed to set item to localStorage: ${key}`, error);
    }
  },

  /**
   * 删除数据
   */
  remove(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error(`Failed to remove item from localStorage: ${key}`, error);
    }
  },

  /**
   * 清空所有数据
   */
  clear(): void {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Failed to clear localStorage', error);
    }
  }
};

/**
 * SessionStorage 封装
 */
export const sessionStorage = {
  /**
   * 获取数据
   */
  get<T>(key: string): T | null {
    try {
      const item = window.sessionStorage.getItem(key);
      if (!item) return null;
      return JSON.parse(item) as T;
    } catch (error) {
      console.error(`Failed to get item from sessionStorage: ${key}`, error);
      return null;
    }
  },

  /**
   * 设置数据
   */
  set<T>(key: string, value: T): void {
    try {
      window.sessionStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Failed to set item to sessionStorage: ${key}`, error);
    }
  },

  /**
   * 删除数据
   */
  remove(key: string): void {
    try {
      window.sessionStorage.removeItem(key);
    } catch (error) {
      console.error(`Failed to remove item from sessionStorage: ${key}`, error);
    }
  },

  /**
   * 清空所有数据
   */
  clear(): void {
    try {
      window.sessionStorage.clear();
    } catch (error) {
      console.error('Failed to clear sessionStorage', error);
    }
  }
};
