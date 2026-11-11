import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  effect,
  inject,
  output,
  signal,
  viewChild,
} from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideArrowUp, lucideSquare } from '@ng-icons/lucide';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { WorkspaceStore } from '../../core/workspace-store';
import { ChatMessageView } from './chat-message';

@Component({
  selector: 'app-chat',
  imports: [NgIcon, HlmButtonImports, ChatMessageView],
  providers: [provideIcons({ lucideArrowUp, lucideSquare })],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './chat.html',
  host: { class: 'block' },
})
export class Chat {
  protected readonly store = inject(WorkspaceStore);
  readonly goNormas = output<void>();
  protected readonly draft = signal('');
  protected readonly confirmClear = signal(false);
  private clearTimer?: ReturnType<typeof setTimeout>;
  private readonly box = viewChild<ElementRef<HTMLTextAreaElement>>('box');
  private readonly scroller = viewChild<ElementRef<HTMLElement>>('scroller');
  protected readonly suggestions = [
    '¿Qué derechos tengo sobre mis datos personales?',
    '¿Qué debo hacer si hay una filtración de datos personales?',
    '¿Qué pena tiene el acceso ilícito a un sistema informático?',
  ];

  constructor() {
    effect(() => {
      this.store.messages();
      const el = this.scroller()?.nativeElement;
      if (!el) return;
      const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 160;
      if (nearBottom) queueMicrotask(() => el.scrollTo({ top: el.scrollHeight }));
    });
  }

  protected send(text = this.draft()) {
    const question = text.trim();
    if (!question || this.store.asking() || !this.store.estado().listo) return;
    this.draft.set('');
    const box = this.box()?.nativeElement;
    if (box) box.style.height = '';
    this.store.ask(question);
    queueMicrotask(() => {
      const el = this.scroller()?.nativeElement;
      el?.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
    });
  }

  protected clear() {
    clearTimeout(this.clearTimer);
    if (this.confirmClear()) {
      this.confirmClear.set(false);
      this.store.clearHistory();
      return;
    }
    this.confirmClear.set(true);
    this.clearTimer = setTimeout(() => this.confirmClear.set(false), 3500);
  }

  protected onKey(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      this.send();
    }
  }

  protected onInput(event: Event) {
    const el = event.target as HTMLTextAreaElement;
    this.draft.set(el.value);
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 168)}px`;
  }
}
