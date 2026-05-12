/**
 * useMembers hook - Fetches and caches all users with member role
 */

import { useQuery } from '@tanstack/react-query';
import { User } from '@/shared/types';
import { fetchMembers } from './api';

interface UseMembersResult {
  members: User[] | undefined;
  isLoading: boolean;
  error: Error | null;
}

/**
 * Hook to fetch and cache all members
 */
export function useMembers(): UseMembersResult {
  const { data: members, isLoading, error } = useQuery({
    queryKey: ['members'],
    queryFn: fetchMembers,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return {
    members,
    isLoading,
    error: error as Error | null,
  };
}
