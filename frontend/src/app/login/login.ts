import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideBookOpenText, lucideLoaderCircle } from '@ng-icons/lucide';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { AuthService } from '../core/auth';

@Component({
  selector: 'app-login',
  imports: [NgIcon, HlmButtonImports],
  providers: [provideIcons({ lucideBookOpenText, lucideLoaderCircle })],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  protected readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  protected async signIn() {
    if (await this.auth.login()) this.router.navigateByUrl('/');
  }
}
