import { ChangeDetectionStrategy, Component, ElementRef, inject, signal, viewChild } from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
  lucideCircleAlert,
  lucideFileText,
  lucideFileUp,
  lucideLoaderCircle,
  lucideTrash2,
} from '@ng-icons/lucide';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCheckboxImports } from '@spartan-ng/helm/checkbox';
import { HlmSkeletonImports } from '@spartan-ng/helm/skeleton';
import { Doc } from '../../core/models';
import { WorkspaceStore } from '../../core/workspace-store';

@Component({
  selector: 'app-library',
  imports: [NgIcon, HlmButtonImports, HlmCheckboxImports, HlmSkeletonImports],
  providers: [
    provideIcons({ lucideCircleAlert, lucideFileText, lucideFileUp, lucideLoaderCircle, lucideTrash2 }),
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './library.html',
  host: { class: 'block' },
})
export class Library {
  protected readonly store = inject(WorkspaceStore);
  private readonly input = viewChild.required<ElementRef<HTMLInputElement>>('picker');
  protected readonly dragging = signal(false);
  protected readonly confirming = signal<string | null>(null);
  private confirmTimer?: ReturnType<typeof setTimeout>;

  protected pick() {
    this.input().nativeElement.click();
  }

  protected picked(event: Event) {
    const el = event.target as HTMLInputElement;
    this.store.upload(Array.from(el.files ?? []));
    el.value = '';
  }

  protected dropped(event: DragEvent) {
    event.preventDefault();
    this.dragging.set(false);
    this.store.upload(Array.from(event.dataTransfer?.files ?? []));
  }

  protected askDelete(doc: Doc) {
    clearTimeout(this.confirmTimer);
    if (this.confirming() === doc.id) {
      this.confirming.set(null);
      this.store.remove(doc.id);
      return;
    }
    this.confirming.set(doc.id);
    this.confirmTimer = setTimeout(() => this.confirming.set(null), 3500);
  }

  protected size(bytes: number) {
    return bytes < 1024 * 1024
      ? `${Math.max(1, Math.round(bytes / 1024))} KB`
      : `${(bytes / 1024 / 1024).toFixed(1).replace('.', ',')} MB`;
  }
}
