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
