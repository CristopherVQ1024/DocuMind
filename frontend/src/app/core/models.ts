export interface Norma {
  id: string;
  nombre: string;
  corto: string;
  tipo: string;
  tema: string;
  publicada: string;
  url: string;
  articulos: number;
}

export interface CorpusEstado {
  listo: boolean;
  indexando: boolean;
  progreso: number;
  total: number;
  error: string;
}

export interface Corpus {
  normas: Norma[];
  estado: CorpusEstado;
}

export interface Source {
  n: number;
  articulo_id: string;
  norma_id: string;
  norma: string;
  corto: string;
  etiqueta: string;
  titulo_articulo: string;
  ruta: string;
  url: string;
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
