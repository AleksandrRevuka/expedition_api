/**
 * Authentication API functions
 */

import { apiClient } from '@/shared/api/client';
import { TokenResponse, User } from '@/shared/types';

/**
 * Register a new user
 */
export interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: 'member' | 'chief';
}

export async function registerUser(payload: RegisterPayload): Promise<User> {
  const response = await apiClient.post<User>('/auth/register', payload);
  return response.data;
}

/**
 * Login with email and password
 */
export async function loginUser(email: string, password: string): Promise<TokenResponse> {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await apiClient.post<TokenResponse>('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
}

/**
 * Fetch the current user profile.
 * Pass `token` explicitly when calling immediately after login/register,
 * before it has been stored to localStorage by setAuth.
 */
export async function fetchMe(token?: string): Promise<User> {
  const response = await apiClient.get<User>('/users/me', {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  return response.data;
}
