import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HlmToasterImports } from '@spartan-ng/helm/sonner';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, HlmToasterImports],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <router-outlet />
    <hlm-toaster position="bottom-center" />
  `,
})
export class App {}
