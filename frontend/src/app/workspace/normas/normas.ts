import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideCircleAlert, lucideExternalLink, lucideLoaderCircle, lucideScale } from '@ng-icons/lucide';
import { HlmSkeletonImports } from '@spartan-ng/helm/skeleton';
import { Norma } from '../../core/models';
import { WorkspaceStore } from '../../core/workspace-store';

@Component({
  selector: 'app-normas',
  imports: [NgIcon, HlmSkeletonImports],
  providers: [provideIcons({ lucideCircleAlert, lucideExternalLink, lucideLoaderCircle, lucideScale })],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './normas.html',
  host: { class: 'block' },
})
export class Normas {
  protected readonly store = inject(WorkspaceStore);

  protected readonly grupos = computed(() => {
    const porTema = new Map<string, Norma[]>();
    for (const n of this.store.normas()) porTema.set(n.tema, [...(porTema.get(n.tema) ?? []), n]);
    return [...porTema].map(([tema, normas]) => ({ tema, normas }));
  });

  protected readonly porcentaje = computed(() => {
    const e = this.store.estado();
    return e.total ? Math.round((e.progreso / e.total) * 100) : 0;
  });

  protected anio(fecha: string) {
    return fecha.slice(0, 4);
  }
}
