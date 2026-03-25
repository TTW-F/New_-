/**
 * LRU Cache 实现
 */
export class LRUCache<K, V> {
  private capacity: number;
  private cache: Map<K, V>;

  constructor(capacity: number = 100) {
    this.capacity = capacity;
    this.cache = new Map();
  }

  /**
   * 获取缓存值
   */
  get(key: K): V | undefined {
    if (!this.cache.has(key)) {
      return undefined;
    }

    // 将访问的项移到最后(最近使用)
    const value = this.cache.get(key)!;
    this.cache.delete(key);
    this.cache.set(key, value);

    return value;
  }

  /**
   * 设置缓存值
   */
  set(key: K, value: V): void {
    // 如果已存在,先删除
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }

    // 如果超过容量,删除最旧的项(第一个)
    if (this.cache.size >= this.capacity) {
      const firstKey = this.cache.keys().next().value as K;
      if (firstKey !== undefined) {
        this.cache.delete(firstKey);
      }
    }

    // 添加新项
    this.cache.set(key, value);
  }

  /**
   * 检查是否存在
   */
  has(key: K): boolean {
    return this.cache.has(key);
  }

  /**
   * 删除缓存
   */
  delete(key: K): boolean {
    return this.cache.delete(key);
  }

  /**
   * 清空缓存
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * 获取缓存大小
   */
  get size(): number {
    return this.cache.size;
  }
}

/**
 * 带过期时间的缓存
 */
interface CacheItem<T> {
  value: T;
  expireAt: number;
}

export class TTLCache<K, V> {
  private cache: Map<K, CacheItem<V>>;
  private defaultTTL: number;

  constructor(defaultTTL: number = 5 * 60 * 1000) {
    this.cache = new Map();
    this.defaultTTL = defaultTTL;
  }

  /**
   * 获取缓存值
   */
  get(key: K): V | undefined {
    const item = this.cache.get(key);

    if (!item) {
      return undefined;
    }

    // 检查是否过期
    if (Date.now() > item.expireAt) {
      this.cache.delete(key);
      return undefined;
    }

    return item.value;
  }

  /**
   * 设置缓存值
   */
  set(key: K, value: V, ttl?: number): void {
    const expireAt = Date.now() + (ttl || this.defaultTTL);
    this.cache.set(key, { value, expireAt });
  }

  /**
   * 检查是否存在且未过期
   */
  has(key: K): boolean {
    const item = this.cache.get(key);
    if (!item) return false;

    if (Date.now() > item.expireAt) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  /**
   * 删除缓存
   */
  delete(key: K): boolean {
    return this.cache.delete(key);
  }

  /**
   * 清空缓存
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * 清理过期缓存
   */
  cleanup(): void {
    const now = Date.now();
    for (const [key, item] of this.cache.entries()) {
      if (now > item.expireAt) {
        this.cache.delete(key);
      }
    }
  }

  /**
   * 获取缓存大小
   */
  get size(): number {
    return this.cache.size;
  }
}
