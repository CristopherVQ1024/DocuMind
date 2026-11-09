import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { toast } from '@spartan-ng/brain/sonner';
import { Api } from './api';
import { ChatMessage, Doc } from './models';

@Injectable({ providedIn: 'root' })
export class WorkspaceStore {
  private readonly api = inject(Api);
  private pollTimer?: ReturnType<typeof setTimeout>;
  private abort?: AbortController;
  private nextId = 1;

  readonly documents = signal<Doc[]>([]);
  readonly loaded = signal(false);
  readonly uploading = signal(0);
  readonly selected = signal<ReadonlySet<string>>(new Set());
  readonly messages = signal<ChatMessage[]>([]);
  readonly asking = signal(false);

  readonly readyDocs = computed(() => this.documents().filter((d) => d.status === 'ready'));
  readonly scopeCount = computed(() => {
    const ready = this.readyDocs();
    const picked = this.selected();
    return picked.size ? ready.filter((d) => picked.has(d.id)).length : ready.length;
  });

  load() {
    this.api.listDocuments().subscribe({
      next: (docs) => {
        this.documents.set(docs);
        this.loaded.set(true);
        this.schedulePoll();
      },
      error: () => {
        this.loaded.set(true);
        toast.error('No se pudo cargar tu biblioteca');
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
    if (this.documents().some((d) => d.status === 'indexing')) {
      this.pollTimer = setTimeout(() => this.load(), 2000);
    }
  }

  upload(files: File[]) {
    for (const file of files) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        toast.error(`${file.name} no es un PDF`);
        continue;
      }
      this.uploading.update((n) => n + 1);
      this.api.upload(file).subscribe({
        next: (doc) => {
          this.documents.update((docs) => [doc, ...docs]);
          this.uploading.update((n) => n - 1);
          this.schedulePoll();
        },
        error: (e: HttpErrorResponse) => {
          this.uploading.update((n) => n - 1);
          toast.error(`${file.name}: ${e.error?.detail ?? 'no se pudo subir'}`);
        },
      });
    }
  }

  remove(id: string) {
    this.api.remove(id).subscribe({
      next: () => {
        this.documents.update((docs) => docs.filter((d) => d.id !== id));
        this.selected.update((s) => new Set([...s].filter((x) => x !== id)));
      },
      error: () => toast.error('No se pudo borrar el documento'),
    });
  }

  toggle(id: string) {
    this.selected.update((s) => {
      const next = new Set(s);
      if (!next.delete(id)) next.add(id);
      return next;
    });
  }

  clearSelection() {
    this.selected.set(new Set());
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
        { question, doc_ids: [...this.selected()], history },
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
    this.documents.set([]);
    this.messages.set([]);
    this.selected.set(new Set());
    this.loaded.set(false);
    this.asking.set(false);
  }
}
