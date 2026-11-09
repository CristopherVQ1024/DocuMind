import { Injectable, signal } from '@angular/core';
import { FirebaseApp, initializeApp } from 'firebase/app';
import {
  Auth,
  GoogleAuthProvider,
  getAuth,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
} from 'firebase/auth';
import { environment } from '../../environments/environment';

export interface AppUser {
  name: string;
  email: string;
  photo: string | null;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly app?: FirebaseApp;
  private readonly auth?: Auth;
  private resolveReady!: () => void;
  readonly ready = new Promise<void>((resolve) => (this.resolveReady = resolve));
  readonly user = signal<AppUser | null>(null);
  readonly signingIn = signal(false);
  readonly error = signal('');

  constructor() {
    if (environment.devAuth) {
      this.user.set({ name: 'Usuario local', email: 'dev@local', photo: null });
      this.resolveReady();
      return;
    }
    this.app = initializeApp(environment.firebase);
    this.auth = getAuth(this.app);
    onAuthStateChanged(this.auth, (u) => {
      this.user.set(
        u ? { name: u.displayName ?? u.email ?? 'Usuario', email: u.email ?? '', photo: u.photoURL } : null,
      );
      this.resolveReady();
    });
  }

  async login(): Promise<boolean> {
    if (!this.auth) return true;
    this.signingIn.set(true);
    this.error.set('');
    try {
      await signInWithPopup(this.auth, new GoogleAuthProvider());
      return true;
    } catch (e) {
      const code = (e as { code?: string }).code;
      if (code !== 'auth/popup-closed-by-user' && code !== 'auth/cancelled-popup-request') {
        this.error.set('No se pudo iniciar sesión con Google. Intenta de nuevo.');
      }
      return false;
    } finally {
      this.signingIn.set(false);
    }
  }

  async logout(): Promise<void> {
    if (this.auth) await signOut(this.auth);
    else this.user.set(null);
  }

  async token(): Promise<string | null> {
    return (await this.auth?.currentUser?.getIdToken()) ?? null;
  }
}
