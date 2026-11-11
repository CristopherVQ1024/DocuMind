import { Injectable, computed, inject, signal } from '@angular/core';
import { toast } from '@spartan-ng/brain/sonner';
import { Api } from './api';
import { ChatMessage, CorpusEstado, Norma } from './models';

@Injectable({ providedIn: 'root' })
export class WorkspaceStore {
  private readonly api = inject(Api);
  private pollTimer?: ReturnType<typeof setTimeout>;
  private abort?: AbortController;
  private nextId = 1;

  readonly normas = signal<Norma[]>([]);
  readonly estado = signal<CorpusEstado>({ listo: false, indexando: false, progreso: 0, total: 0, error: '' });
  readonly loaded = signal(false);
  readonly messages = signal<ChatMessage[]>([]);
  readonly asking = signal(false);

  readonly articulos = computed(() => this.normas().reduce((sum, n) => sum + n.articulos, 0));

  load() {
    this.api.corpus().subscribe({
      next: (corpus) => {
        this.normas.set(corpus.normas);
        this.estado.set(corpus.estado);
        this.loaded.set(true);
        this.schedulePoll();
      },
      error: () => {
        this.loaded.set(true);
        toast.error('No se pudo cargar el corpus');
      },
    });
  }

  loadHistory() {
    this.api.listMessages().subscribe({
      next: (stored) => {
        if (this.messages().length) return;
        this.messages.set(
          stored.map((m) => ({ ...m, id: this.nextId++, streaming: false })),
        );
      },
      error: () => toast.error('No se pudo cargar tu conversación'),
    });
  }

  clearHistory() {
    if (this.asking()) return;
    this.api.clearMessages().subscribe({
      next: () => this.messages.set([]),
      error: () => toast.error('No se pudo borrar la conversación'),
    });
  }

  stop() {
    clearTimeout(this.pollTimer);
    this.abort?.abort();
  }

  private schedulePoll() {
    clearTimeout(this.pollTimer);
    if (!this.estado().listo && !this.estado().error) {
      this.pollTimer = setTimeout(() => this.load(), 3000);
    }
  }

  async ask(question: string) {
    if (this.asking() || !question.trim()) return;
    const history = this.messages()
      .filter((m) => m.text && !m.error)
      .map((m) => ({ role: m.role, text: m.text }));
    const reply: ChatMessage = {
      id: this.nextId++,
      role: 'assistant',
      text: '',
      sources: [],
      streaming: true,
      error: '',
    };
    this.messages.update((list) => [
      ...list,
      { id: this.nextId++, role: 'user', text: question, sources: [], streaming: false, error: '' },
      reply,
    ]);
    this.asking.set(true);
    this.abort = new AbortController();
    const patch = (fn: (m: ChatMessage) => ChatMessage) =>
      this.messages.update((list) => list.map((m) => (m.id === reply.id ? fn(m) : m)));
    try {
      const stream = this.api.chat(
        { question, history },
        this.abort.signal,
      );
      for await (const ev of stream) {
        if (ev.event === 'sources') patch((m) => ({ ...m, sources: ev.data }));
        else if (ev.event === 'token') patch((m) => ({ ...m, text: m.text + ev.data }));
        else if (ev.event === 'error') patch((m) => ({ ...m, error: ev.data.message }));
      }
    } catch (e) {
      if ((e as Error).name !== 'AbortError') {
        patch((m) => ({ ...m, error: (e as Error).message }));
      }
    } finally {
      patch((m) => ({ ...m, streaming: false }));
      this.asking.set(false);
    }
  }

  cancel() {
    this.abort?.abort();
  }

  reset() {
    this.stop();
    this.normas.set([]);
    this.messages.set([]);
    this.loaded.set(false);
    this.asking.set(false);
  }
}
