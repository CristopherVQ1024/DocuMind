import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';
import { Doc, Source, StreamEvent } from './models';

export interface StoredMessage {
  role: 'user' | 'assistant';
  text: string;
  sources: Source[];
  error: string;
}

interface ChatBody {
  question: string;
  doc_ids: string[];
  history: { role: string; text: string }[];
}

@Injectable({ providedIn: 'root' })
export class Api {
  private readonly http = inject(HttpClient);
  private readonly auth = inject(AuthService);
  private readonly base = environment.apiUrl;

  listDocuments() {
    return this.http.get<Doc[]>(`${this.base}/documents`);
  }

  upload(file: File) {
    const form = new FormData();
    form.append('file', file, file.name);
    return this.http.post<Doc>(`${this.base}/documents`, form);
  }

  remove(id: string) {
    return this.http.delete<void>(`${this.base}/documents/${id}`);
  }

  listMessages() {
    return this.http.get<StoredMessage[]>(`${this.base}/messages`);
  }

  clearMessages() {
    return this.http.delete<void>(`${this.base}/messages`);
  }

  async *chat(body: ChatBody, signal: AbortSignal): AsyncGenerator<StreamEvent> {
    const token = await this.auth.token();
    const response = await fetch(`${this.base}/chat`, {
      method: 'POST',
      signal,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(body),
    });
    if (!response.ok || !response.body) {
      const detail = await response.json().catch(() => null);
      throw new Error(detail?.detail ?? 'No se pudo consultar. Intenta de nuevo.');
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let cut: number;
      while ((cut = buffer.indexOf('\n\n')) >= 0) {
        const block = buffer.slice(0, cut);
        buffer = buffer.slice(cut + 2);
        const event = /^event: (.+)$/m.exec(block)?.[1];
        const data = /^data: (.+)$/m.exec(block)?.[1];
        if (event && data) yield { event, data: JSON.parse(data) } as StreamEvent;
      }
    }
  }
}
