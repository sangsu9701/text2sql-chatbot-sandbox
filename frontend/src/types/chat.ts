export interface ChatRequest {
  question: string;
  wants_visualization?: boolean;
  chart_type?: string;
  session_id?: string;
}

export interface ChatResponse {
  answer_text: string;
  sql: string;
  rows: any[];
  columns: string[];
  row_count: number;
  chart_suggestion?: string;
  execution_time: number;
  cached: boolean;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  data?: ChatResponse; // AI 메시지의 경우에만 포함
}

export interface SchemaResponse {
  tables: any[];
  relationships: any[];
}
