/**
 * useUser hook - Fetches and caches user by ID
 */

import { useQuery } from '@tanstack/react-query';
import { User } from '@/shared/types';
import { fetchUser } from './api';

interface UseUserResult {
  data: User | undefined;
  isLoading: boolean;
}

/**
 * Hook to fetch and cache a user by ID
 * Deduplicates requests for the same userId across multiple components
 * Sets staleTime: Infinity so user data never becomes stale
 */
export function useUser(userId: string): UseUserResult {
  const { data, isLoading } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: Infinity,
  });

  return {
    data,
    isLoading,
  };
}
