import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';
import { Corpus, Source, StreamEvent } from './models';

export interface StoredMessage {
  role: 'user' | 'assistant';
  text: string;
  sources: Source[];
  error: string;
}

interface ChatBody {
  question: string;
  history: { role: string; text: string }[];
}

@Injectable({ providedIn: 'root' })
export class Api {
  private readonly http = inject(HttpClient);
  private readonly auth = inject(AuthService);
  private readonly base = environment.apiUrl;

  corpus() {
    return this.http.get<Corpus>(`${this.base}/corpus`);
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
