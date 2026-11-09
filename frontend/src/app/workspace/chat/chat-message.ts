import { ChangeDetectionStrategy, Component, computed, input, signal } from '@angular/core';
import { ChatMessage } from '../../core/models';
import { AnswerText } from './answer-text';

@Component({
  selector: 'app-chat-message',
  imports: [AnswerText],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './chat-message.html',
  styleUrl: './chat-message.scss',
  host: { class: 'block' },
})
export class ChatMessageView {
  readonly message = input.required<ChatMessage>();
  protected readonly open = signal<number | null>(null);

  protected readonly shown = computed(() => {
    const m = this.message();
    const cited = new Set([...m.text.matchAll(/\[(\d{1,2})\]/g)].map((x) => Number(x[1])));
    const picked = m.sources.filter((s) => cited.has(s.n));
    return picked.length || m.streaming ? picked : m.sources;
  });

  protected toggle(n: number) {
    this.open.update((current) => (current === n ? null : n));
  }
}
