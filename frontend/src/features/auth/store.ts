/**
 * Authentication store using Zustand
 */

import { create } from 'zustand';
import { User } from '@/shared/types';

export interface AuthState {
  token: string | null;
  user: User | null;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
}

/**
 * Create the auth store
 * - Initializes token from localStorage.auth_token
 * - Provides setAuth() to update both token and user, and persist token to localStorage
 * - Provides logout() to clear both and remove token from localStorage
 */
export const useAuthStore = create<AuthState>((set) => {
  // Initialize token from localStorage
  const initialToken = localStorage.getItem('auth_token');

  return {
    token: initialToken,
    user: null,
    setAuth: (token: string, user: User) => {
      localStorage.setItem('auth_token', token);
      set({ token, user });
    },
    logout: () => {
      localStorage.removeItem('auth_token');
      set({ token: null, user: null });
    },
  };
});
