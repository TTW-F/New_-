import type { SSEEvent } from '@/types/sse';

export type SSEEventHandler = (event: SSEEvent) => void;
export type SSEErrorHandler = (error: Error) => void;

/**
 * SSE 客户端类
 */
export class SSEClient {
  private eventSource: EventSource | null = null;
  private url: string;
  private eventHandlers: Map<string, SSEEventHandler[]> = new Map();
  private errorHandlers: SSEErrorHandler[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;
  private reconnectDelay = 1000;

  constructor(url: string) {
    this.url = url;
  }

  /**
   * 连接 SSE
   */
  connect(): void {
    if (this.eventSource) {
      this.close();
    }

    try {
      this.eventSource = new EventSource(this.url);

      this.eventSource.onopen = () => {
        this.reconnectAttempts = 0;
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as SSEEvent;
          this.handleEvent(data);
        } catch (error) {
          console.error('Failed to parse SSE message:', error);
        }
      };

      this.eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        this.handleError(new Error('SSE connection error'));

        // 自动重连
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          setTimeout(() => {
            this.connect();
          }, this.reconnectDelay * this.reconnectAttempts);
        } else {
          this.close();
        }
      };
    } catch (error) {
      this.handleError(error as Error);
    }
  }

  /**
   * 监听事件
   */
  on(eventType: string, handler: SSEEventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)!.push(handler);
  }

  /**
   * 移除事件监听
   */
  off(eventType: string, handler: SSEEventHandler): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * 监听错误
   */
  onError(handler: SSEErrorHandler): void {
    this.errorHandlers.push(handler);
  }

  /**
   * 关闭连接
   */
  close(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.reconnectAttempts = 0;
  }

  /**
   * 检查是否已连接
   */
  isConnected(): boolean {
    return this.eventSource !== null && this.eventSource.readyState === EventSource.OPEN;
  }

  /**
   * 处理事件
   */
  private handleEvent(event: SSEEvent): void {
    const handlers = this.eventHandlers.get(event.type);
    if (handlers) {
      handlers.forEach(handler => handler(event));
    }

    // 触发通用事件处理器
    const allHandlers = this.eventHandlers.get('*');
    if (allHandlers) {
      allHandlers.forEach(handler => handler(event));
    }
  }

  /**
   * 处理错误
   */
  private handleError(error: Error): void {
    this.errorHandlers.forEach(handler => handler(error));
  }
}

/**
 * 创建 SSE 客户端
 */
export function createSSEClient(url: string): SSEClient {
  return new SSEClient(url);
}
