// Chat Store - 聊天状态管理

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Message, Session, ToolCall, Entity, ToolCallStatus } from '@/types/chat';
import { v4 as uuidv4 } from 'uuid';
import * as historyAPI from '@/api/history';

export const useChatStore = defineStore('chat', () => {
  // State
  const currentSessionId = ref<string | null>(null);
  const sessions = ref<Map<string, Session>>(new Map());
  const messages = ref<Map<string, Message[]>>(new Map());
  const isStreaming = ref(false);
  const currentStreamingMessageId = ref<string | null>(null);
  
  // Getters
  const currentSession = computed(() => {
    if (!currentSessionId.value) return null;
    return sessions.value.get(currentSessionId.value) || null;
  });
  
  const currentMessages = computed(() => {
    if (!currentSessionId.value) return [];
    return messages.value.get(currentSessionId.value) || [];
  });
  
  // Actions
  function createSession(): string {
    const sessionId = uuidv4().substring(0, 16);
    const session: Session = {
      id: sessionId,
      title: '新对话',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messageCount: 0,
      messages: []
    };
    
    sessions.value.set(sessionId, session);
    messages.value.set(sessionId, []);
    currentSessionId.value = sessionId;
    localStorage.setItem('last_session_id', sessionId);
    
    return sessionId;
  }
  
  async function switchSession(sessionId: string): Promise<void> {
    if (sessions.value.has(sessionId)) {
      currentSessionId.value = sessionId;
      localStorage.setItem('last_session_id', sessionId);
      
      // 登录用户：从后端恢复会话历史；同时恢复 agent 上下文（可选）
      await loadSessionHistoryFromServer(sessionId);
      restoreSessionContext(sessionId);
    }
  }
  
  async function restoreSessionContext(sessionId: string): Promise<void> {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.warn('未登录，无法恢复会话上下文');
        return;
      }
      
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/api/v1/qa/restore?session_id=${sessionId}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (response.ok) {
        const result = await response.json();
        console.log(`会话上下文已恢复: ${result.message}`);
      } else {
        console.warn('恢复会话上下文失败');
      }
    } catch (error) {
      console.error('恢复会话上下文出错:', error);
    }
  }

  async function loadSessionsFromServer(): Promise<void> {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const result = await historyAPI.getSessions();
    if (!result.sessions) return;

    const newSessions = new Map<string, Session>();
    const newMessages = new Map<string, Message[]>();

    for (const s of result.sessions) {
      const session: Session = {
        id: s.session_id,
        title: s.first_question || '历史会话',
        createdAt: s.created_at,
        updatedAt: s.created_at,
        messageCount: 0,
        messages: []
      };
      newSessions.set(session.id, session);
      newMessages.set(session.id, []);
    }

    sessions.value = newSessions;
    messages.value = newMessages;

    const lastSessionId = localStorage.getItem('last_session_id');
    const fallbackSessionId = lastSessionId && sessions.value.has(lastSessionId)
      ? lastSessionId
      : (sessions.value.keys().next().value as string | undefined);

    if (fallbackSessionId) {
      currentSessionId.value = fallbackSessionId;
      await loadSessionHistoryFromServer(fallbackSessionId);
      restoreSessionContext(fallbackSessionId);
    } else {
      createSession();
    }
  }

  async function loadSessionHistoryFromServer(sessionId: string): Promise<void> {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    if (!sessions.value.has(sessionId)) return;

    const pageSize = 100;
    let page = 1;
    const allRecords = [];

    // 分页拉取，直到取完
    while (true) {
      const res = await historyAPI.getHistory({ session_id: sessionId, page, page_size: pageSize });
      if (!res.data || res.data.length === 0) break;
      allRecords.push(...res.data);
      if (page >= res.total_pages) break;
      page += 1;
    }

    // 后端按 created_at 倒序；这里按时间升序展示
    allRecords.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());

    const sessionMessages: Message[] = [];

    for (const record of allRecords) {
      const userMsg: Message = {
        id: uuidv4(),
        role: 'user',
        content: record.question,
        status: 'sent',
        timestamp: record.created_at,
        sessionId
      };
      sessionMessages.push(userMsg);

      const assistantMsg: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: record.answer || '',
        status: 'completed',
        entities: (record.entities as any) || [],
        timestamp: record.created_at,
        sessionId
      };
      sessionMessages.push(assistantMsg);
    }

    messages.value.set(sessionId, sessionMessages);

    const session = sessions.value.get(sessionId);
    if (session) {
      session.messages = sessionMessages;
      session.messageCount = sessionMessages.length;
      session.updatedAt = sessionMessages.length > 0
        ? sessionMessages[sessionMessages.length - 1].timestamp
        : session.updatedAt;
    }
  }
  
  function addUserMessage(content: string): Message {
    if (!currentSessionId.value) {
      createSession();
    }
    
    const message: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      status: 'sent',
      timestamp: new Date().toISOString(),
      sessionId: currentSessionId.value!
    };
    
    const sessionMessages = messages.value.get(currentSessionId.value!) || [];
    sessionMessages.push(message);
    messages.value.set(currentSessionId.value!, sessionMessages);
    
    // 更新会话标题(使用第一条消息)
    const session = sessions.value.get(currentSessionId.value!);
    if (session && session.messageCount === 0) {
      session.title = content.substring(0, 30) + (content.length > 30 ? '...' : '');
    }
    session!.messageCount++;
    session!.updatedAt = new Date().toISOString();
    session!.messages = sessionMessages;
    
    return message;
  }
  
  function startAssistantMessage(): Message {
    if (!currentSessionId.value) {
      throw new Error('No active session');
    }
    
    const message: Message = {
      id: uuidv4(),
      role: 'assistant',
      content: '',
      status: 'streaming',
      toolCalls: [],
      entities: [],
      timestamp: new Date().toISOString(),
      sessionId: currentSessionId.value
    };
    
    const sessionMessages = messages.value.get(currentSessionId.value) || [];
    sessionMessages.push(message);
    messages.value.set(currentSessionId.value, sessionMessages);
    const session = sessions.value.get(currentSessionId.value);
    if (session) {
      session.messages = sessionMessages;
      session.messageCount = sessionMessages.length;
      session.updatedAt = new Date().toISOString();
    }
    
    currentStreamingMessageId.value = message.id;
    isStreaming.value = true;
    
    return message;
  }
  
  function appendContent(content: string): void {
    if (!currentStreamingMessageId.value || !currentSessionId.value) return;
    
    const sessionMessages = messages.value.get(currentSessionId.value) || [];
    const message = sessionMessages.find(m => m.id === currentStreamingMessageId.value);
    
    if (message) {
      message.content += content;
    }
  }
  
  function addToolCall(toolCall: Partial<ToolCall>): void {
    if (!currentStreamingMessageId.value || !currentSessionId.value) return;
    
    const sessionMessages = messages.value.get(currentSessionId.value) || [];
    const message = sessionMessages.find(m => m.id === currentStreamingMessageId.value);
    
    if (message) {
      if (!message.toolCalls) {
        message.toolCalls = [];
      }
      
      const existingToolCall = message.toolCalls.find(tc => tc.tool_id === toolCall.tool_id);
      
      if (existingToolCall) {
        Object.assign(existingToolCall, toolCall);
      } else {
        message.toolCalls.push({
          id: uuidv4(),
          tool_id: toolCall.tool_id!,
          tool_name: toolCall.tool_name!,
          arguments: toolCall.arguments || {},
          status: toolCall.status || 'pending',
          result: toolCall.result,
          error: toolCall.error,
          entities: toolCall.entities
        });
      }
    }
  }
  
  function updateToolCallStatus(
    toolId: string, 
    status: ToolCallStatus, 
    result?: string, 
    error?: string,
    entities?: Entity[]
  ): void {
    if (!currentStreamingMessageId.value || !currentSessionId.value) return;
    
    const sessionMessages = messages.value.get(currentSessionId.value) || [];
    const message = sessionMessages.find(m => m.id === currentStreamingMessageId.value);
    
    if (message && message.toolCalls) {
      const toolCall = message.toolCalls.find(tc => tc.tool_id === toolId);
      if (toolCall) {
        toolCall.status = status;
        if (result !== undefined) toolCall.result = result;
        if (error !== undefined) toolCall.error = error;
        if (entities !== undefined) toolCall.entities = entities;
      }
    }
  }
  
  function completeStreaming(entities?: Entity[]): void {
    if (!currentStreamingMessageId.value || !currentSessionId.value) return;
    
    const sessionMessages = messages.value.get(currentSessionId.value) || [];
    const message = sessionMessages.find(m => m.id === currentStreamingMessageId.value);
    
    if (message) {
      message.status = 'completed';
      if (entities) {
        message.entities = entities;
      }
    }
    
    isStreaming.value = false;
    currentStreamingMessageId.value = null;
    
    const session = sessions.value.get(currentSessionId.value);
    if (session) {
      session.updatedAt = new Date().toISOString();
    }
  }
  
  function setError(error: string): void {
    if (!currentStreamingMessageId.value || !currentSessionId.value) return;
    
    const sessionMessages = messages.value.get(currentSessionId.value) || [];
    const message = sessionMessages.find(m => m.id === currentStreamingMessageId.value);
    
    if (message) {
      message.status = 'error';
      message.content = error;
    }
    
    isStreaming.value = false;
    currentStreamingMessageId.value = null;
  }
  
  function deleteSessionById(sessionId: string): void {
    sessions.value.delete(sessionId);
    messages.value.delete(sessionId);
    
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = null;
    }
  }
  
  function clearCurrentSession(): void {
    if (!currentSessionId.value) return;
    messages.value.set(currentSessionId.value, []);
    const session = sessions.value.get(currentSessionId.value);
    if (session) {
      session.messageCount = 0;
      session.messages = [];
      session.updatedAt = new Date().toISOString();
    }
  }
  
  return {
    currentSessionId,
    sessions,
    messages,
    isStreaming,
    currentStreamingMessageId,
    currentSession,
    currentMessages,
    loadSessionsFromServer,
    loadSessionHistoryFromServer,
    createSession,
    switchSession,
    addUserMessage,
    startAssistantMessage,
    appendContent,
    addToolCall,
    updateToolCallStatus,
    completeStreaming,
    setError,
    deleteSessionById,
    clearCurrentSession
  };
});
