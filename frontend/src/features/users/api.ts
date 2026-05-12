/**
 * Users API functions
 */

import { apiClient } from '@/shared/api/client';
import { User } from '@/shared/types';

/**
 * Fetch a user by ID
 */
export async function fetchUser(userId: string): Promise<User> {
  const response = await apiClient.get<User>(`/users/${userId}`);
  return response.data;
}

/**
 * Fetch all users with member role
 */
export async function fetchMembers(): Promise<User[]> {
  const response = await apiClient.get<{ users: User[] }>('/users');
  return response.data.users;
}
