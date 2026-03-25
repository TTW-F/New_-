// useChat - 聊天逻辑

import { ref } from 'vue';
import { useChatStore } from '@/stores/chat';
import type { SSEEventData } from '@/types/sse';

export function useChat() {
  const chatStore = useChatStore();
  const error = ref<string | null>(null);
  let abortController: AbortController | null = null;
  
  async function sendMessage(content: string): Promise<void> {
    try {
      error.value = null;
      
      // 添加用户消息
      chatStore.addUserMessage(content);
      
      // 开始 AI 回答
      chatStore.startAssistantMessage();
      
      // 创建 SSE 连接
      const sessionId = chatStore.currentSessionId;
      const token = localStorage.getItem('access_token') || '';
      
      // 创建 AbortController 用于取消请求
      abortController = new AbortController();
      
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/v1/qa/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify({
          question: content,
          session_id: sessionId
        }),
        signal: abortController.signal
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      // 读取 SSE 流
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('无法读取响应流');
      }
      
      const decoder = new TextDecoder();
      
      async function readStream(): Promise<void> {
        if (!reader) return;
        
        const { done, value } = await reader.read();
        
        if (done) {
          chatStore.completeStreaming();
          abortController = null;
          return;
        }
        
        const text = decoder.decode(value, { stream: true });
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.substring(6);
            
            if (data === '[DONE]') {
              chatStore.completeStreaming();
              abortController = null;
              return;
            }
            
            try {
              const event: SSEEventData = JSON.parse(data);
              handleSSEMessage(event);
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
        
        return readStream();
      }
      
      await readStream();
      
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        // 用户主动取消,不显示错误
        return;
      }
      
      const message = err instanceof Error ? err.message : '发送消息失败';
      error.value = message;
      chatStore.setError(message);
    } finally {
      abortController = null;
    }
  }
  
  function stopStreaming(): void {
    if (abortController) {
      abortController.abort();
      abortController = null;
    }
    chatStore.completeStreaming();
  }
  
  function handleSSEMessage(event: SSEEventData): void {
    switch (event.type) {
      case 'tool_start':
        chatStore.addToolCall({
          tool_id: event.tool_id,
          tool_name: event.tool_name,
          arguments: event.arguments,
          status: 'running'
        });
        break;
        
      case 'tool_end':
        chatStore.updateToolCallStatus(
          event.tool_id,
          event.status === 'success' ? 'success' : 'error',
          event.result,
          event.error,
          event.entities
        );
        break;
        
      case 'chunk':
        chatStore.appendContent(event.content);
        break;
        
      case 'meta':
        chatStore.completeStreaming(event.entities);
        break;
        
      case 'error':
        error.value = event.message;
        chatStore.setError(event.message);
        break;
    }
  }
  
  return {
    sendMessage,
    stopStreaming,
    error
  };
}
