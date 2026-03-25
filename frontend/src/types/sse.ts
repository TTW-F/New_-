// SSE 事件类型定义

import type { Entity } from './chat';

/** SSE 事件类型 */
export type SSEEventType = 
  | 'tool_start' 
  | 'tool_end' 
  | 'chunk' 
  | 'meta' 
  | 'error';

/** SSE 事件基类 */
export interface SSEEvent {
  type: SSEEventType;
}

/** 工具开始事件 */
export interface ToolStartEvent extends SSEEvent {
  type: 'tool_start';
  tool_id: string;
  tool_name: string;
  arguments: Record<string, any>;
}

/** 工具结束事件 */
export interface ToolEndEvent extends SSEEvent {
  type: 'tool_end';
  tool_id: string;
  tool_name: string;
  status: 'success' | 'error';
  result?: string;
  error?: string;
  entities?: Entity[];
}

/** 内容块事件 */
export interface ChunkEvent extends SSEEvent {
  type: 'chunk';
  content: string;
}

/** 元数据事件 */
export interface MetaEvent extends SSEEvent {
  type: 'meta';
  question_id: string;
  session_id: string;
  response_time_ms: number;
  entities: Entity[];
  tool_calls: any[];
  citations: any[];
}

/** 错误事件 */
export interface ErrorEvent extends SSEEvent {
  type: 'error';
  message: string;
}

/** SSE 事件联合类型 */
export type SSEEventData = 
  | ToolStartEvent 
  | ToolEndEvent 
  | ChunkEvent 
  | MetaEvent 
  | ErrorEvent;
