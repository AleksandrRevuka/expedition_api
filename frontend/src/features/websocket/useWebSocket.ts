/**
 * useExpeditionWs hook - Manages WebSocket connection for expedition updates
 */

import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { WsMessage } from '@/shared/types';
import { ExpeditionWsManager } from './manager';

interface UseExpeditionWsOptions {
  expeditionId: string | null;
  token: string | null;
  onAuthError?: () => void;
}

/**
 * Hook to manage WebSocket connection for expedition real-time updates
 * - Only connects when both expeditionId and token are provided
 * - Invalidates expedition queries on any message
 * - Automatically disconnects on unmount
 * - Calls onAuthError when auth fails (1008 close code)
 */
export function useExpeditionWs(options: UseExpeditionWsOptions): void {
  const { expeditionId, token, onAuthError } = options;
  const queryClient = useQueryClient();
  const managerRef = useRef<ExpeditionWsManager | null>(null);

  useEffect(() => {
    // Only connect if both expeditionId and token are provided
    if (!expeditionId || !token) {
      return;
    }

    // Create manager
    const manager = new ExpeditionWsManager({
      expeditionId,
      token,
      onAuthError,
    });

    managerRef.current = manager;

    // Connect
    manager.connect();

    // Subscribe to messages and invalidate queries
    const unsubscribe = manager.subscribe((message: WsMessage) => {
      console.log('Received WS message:', message);

      // Invalidate expedition-specific and all expeditions queries
      queryClient.invalidateQueries({
        queryKey: ['expedition', expeditionId],
      });
      queryClient.invalidateQueries({
        queryKey: ['expeditions'],
      });
    });

    // Cleanup on unmount or when dependencies change
    return () => {
      unsubscribe();
      manager.disconnect();
      managerRef.current = null;
    };
  }, [expeditionId, token, onAuthError, queryClient]);
}
