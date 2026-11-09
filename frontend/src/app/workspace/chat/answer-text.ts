import { ChangeDetectionStrategy, Component, computed, input, output } from '@angular/core';

interface Segment {
  text: string;
  cite: number | null;
  bold: boolean;
}

@Component({
  selector: 'app-answer-text',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { class: 'whitespace-pre-wrap' },
  template: `@for (s of segments(); track $index) {@if (s.cite !== null) {<button type="button" class="chip" [attr.aria-label]="'Ver fuente ' + s.cite" (click)="cite.emit(s.cite)">{{ s.cite }}</button>} @else if (s.bold) {<strong>{{ s.text }}</strong>} @else {{{ s.text }}}}`,
  styles: `
    .chip {
      display: inline-grid;
      place-items: center;
      min-width: 1.4em;
      height: 1.4em;
      padding-inline: 0.3em;
      margin-inline: 0.1em;
      border-radius: 999px;
      background: var(--primary);
      color: var(--primary-foreground);
      font: 600 0.72rem/1 var(--font-sans);
      vertical-align: 0.12em;
      cursor: pointer;
      transition: transform 0.15s cubic-bezier(0.16, 1, 0.3, 1), background-color 0.15s;
    }
    .chip:hover {
      background: color-mix(in oklch, var(--primary), var(--foreground) 20%);
    }
    .chip:active {
      transform: scale(0.92);
    }
  `,
})
export class AnswerText {
  readonly text = input.required<string>();
  readonly cite = output<number>();

  protected readonly segments = computed<Segment[]>(() =>
    this.text()
      .split(/(\*\*[^*]+\*\*|\[\d{1,2}\])/)
      .filter(Boolean)
      .map((part): Segment => {
        const cite = /^\[(\d{1,2})\]$/.exec(part);
        if (cite) return { text: '', cite: Number(cite[1]), bold: false };
        if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
          return { text: part.slice(2, -2), cite: null, bold: true };
        }
        return { text: part.replaceAll('**', ''), cite: null, bold: false };
      }),
  );
}
