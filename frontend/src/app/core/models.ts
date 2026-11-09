export type DocStatus = 'indexing' | 'ready' | 'error';

export interface Doc {
  id: string;
  name: string;
  size: number;
  status: DocStatus;
  pages: number;
  chunks: number;
  error: string | null;
  created_at: number;
}

export interface Source {
  n: number;
  doc_id: string;
  doc_name: string;
  page: number;
  text: string;
}

export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  text: string;
  sources: Source[];
  streaming: boolean;
  error: string;
}

export type StreamEvent =
  | { event: 'sources'; data: Source[] }
  | { event: 'token'; data: string }
  | { event: 'done'; data: object }
  | { event: 'error'; data: { message: string } };
