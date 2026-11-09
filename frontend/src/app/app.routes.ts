import { Routes } from '@angular/router';
import { authGuard, guestGuard } from './core/auth-guard';

export const routes: Routes = [
  {
    path: 'login',
    canActivate: [guestGuard],
    loadComponent: () => import('./login/login').then((m) => m.Login),
  },
  {
    path: '',
    pathMatch: 'full',
    canActivate: [authGuard],
    loadComponent: () => import('./workspace/workspace').then((m) => m.Workspace),
  },
  { path: '**', redirectTo: '' },
];
