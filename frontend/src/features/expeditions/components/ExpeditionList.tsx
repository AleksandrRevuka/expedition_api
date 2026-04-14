import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/features/auth/store';
import { fetchExpeditions } from '@/features/expeditions/api';
import { ExpeditionCard } from './ExpeditionCard';
import { Button } from '@/shared/ui/Button';
import { Role } from '@/shared/types';

export interface ExpeditionListProps {
  onSelectExpedition?: (id: string) => void;
  onCreateNew?: () => void;
  selectedExpeditionId?: string | null;
}

export const ExpeditionList: React.FC<ExpeditionListProps> = ({
  onSelectExpedition,
  onCreateNew,
  selectedExpeditionId,
}) => {
  const user = useAuthStore((state) => state.user);

  const { data: expeditions, isLoading, error, refetch } = useQuery({
    queryKey: ['expeditions'],
    queryFn: fetchExpeditions,
  });

  const handleSelectExpedition = (id: string) => {
    onSelectExpedition?.(id);
  };

  const handleRetry = () => {
    refetch();
  };

  const handleCreateNew = () => {
    onCreateNew?.();
  };

  const isChief = user?.role === Role.Chief;

  return (
    <div className="space-y-4">
      {/* NEW Button for Chiefs */}
      {isChief && (
        <div className="flex justify-end">
          <Button variant="secondary" onClick={handleCreateNew}>
            + NEW
          </Button>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <svg
            className="h-8 w-8 animate-spin text-neon-cyan"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span className="ml-3 text-neon-cyan font-orbitron">
            Loading expeditions...
          </span>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <div className="text-center space-y-2">
            <p className="text-red-400 font-orbitron">
              Failed to load expeditions
            </p>
            <p className="text-sm text-gray-400">
              {error instanceof Error ? error.message : 'An unknown error occurred'}
            </p>
          </div>
          <Button variant="primary" onClick={handleRetry}>
            Retry
          </Button>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && (!expeditions || expeditions.length === 0) && (
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <div className="text-center space-y-2">
            <p className="text-neon-cyan font-orbitron text-lg">
              No expeditions yet
            </p>
            <p className="text-sm text-gray-400">
              {isChief
                ? 'Create your first expedition to get started'
                : 'Wait for a chief to create an expedition'}
            </p>
          </div>
        </div>
      )}

      {/* Expeditions Grid */}
      {!isLoading && !error && expeditions && expeditions.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {expeditions.map((expedition) => (
            <ExpeditionCard
              key={expedition.id}
              expedition={expedition}
              isSelected={selectedExpeditionId === expedition.id}
              onSelect={handleSelectExpedition}
            />
          ))}
        </div>
      )}
    </div>
  );
};

ExpeditionList.displayName = 'ExpeditionList';
