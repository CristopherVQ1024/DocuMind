import { ChangeDetectionStrategy, Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideBookOpenText, lucideLibrary, lucideLogOut, lucideMessagesSquare } from '@ng-icons/lucide';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { AuthService } from '../core/auth';
import { WorkspaceStore } from '../core/workspace-store';
import { Chat } from './chat/chat';
import { Library } from './library/library';

@Component({
  selector: 'app-workspace',
  imports: [NgIcon, HlmButtonImports, Library, Chat],
  providers: [provideIcons({ lucideBookOpenText, lucideLibrary, lucideLogOut, lucideMessagesSquare })],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './workspace.html',
})
export class Workspace implements OnInit, OnDestroy {
  protected readonly auth = inject(AuthService);
  protected readonly store = inject(WorkspaceStore);
  private readonly router = inject(Router);
  protected readonly tab = signal<'library' | 'chat'>('chat');

  ngOnInit() {
    this.store.load();
    this.store.loadHistory();
  }

  ngOnDestroy() {
    this.store.stop();
  }

  protected async signOut() {
    this.store.reset();
    await this.auth.logout();
    this.router.navigateByUrl('/login');
  }
}
