import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/features/auth/store';
import { useExpeditionWs } from '@/features/websocket/useWebSocket';
import { useUser } from '@/features/users/useUser';
import {
  fetchExpedition,
  deleteExpedition,
  confirmMembership,
  removeMember,
  changeExpeditionStatus,
} from '../api';
import { ExpeditionStatus, MemberState, Role } from '@/shared/types';
import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { GlassPanel } from '@/shared/ui/GlassPanel';
import {
  EditExpeditionModal,
  InviteMemberModal,
} from '.';

export interface ExpeditionDetailProps {
  expeditionId: string;
  onDeleted?: () => void;
}

// Skeleton placeholder for loading member name
const NameSkeleton: React.FC = () => (
  <div className="h-5 w-24 bg-gray-600 bg-opacity-50 rounded animate-pulse" />
);

// Status text formatter
const formatStatus = (status: ExpeditionStatus): string => {
  const statusMap: Record<ExpeditionStatus, string> = {
    [ExpeditionStatus.Draft]: 'Draft',
    [ExpeditionStatus.Ready]: 'Ready',
    [ExpeditionStatus.Active]: 'Active',
    [ExpeditionStatus.Finished]: 'Finished',
  };
  return statusMap[status];
};

// Status badge variant
const getStatusVariant = (status: ExpeditionStatus): 'cyan' | 'purple' | 'green' | 'yellow' | 'red' | 'gray' => {
  const variantMap: Record<ExpeditionStatus, 'cyan' | 'purple' | 'green' | 'yellow' | 'red' | 'gray'> = {
    [ExpeditionStatus.Draft]: 'yellow',
    [ExpeditionStatus.Ready]: 'purple',
    [ExpeditionStatus.Active]: 'cyan',
    [ExpeditionStatus.Finished]: 'green',
  };
  return variantMap[status];
};

// Member state badge variant
const getMemberStateVariant = (state: MemberState): 'green' | 'yellow' => {
  return state === MemberState.Confirmed ? 'green' : 'yellow';
};

const getMemberStateText = (state: MemberState): string => {
  return state === MemberState.Confirmed ? 'Confirmed' : 'Invited';
};

// Member row component
const MemberRow: React.FC<{
  userId: string;
  state: MemberState;
  isChief: boolean;
  expeditionId: string;
  onRemoveLoading?: (loading: boolean) => void;
}> = ({ userId, state, isChief, expeditionId, onRemoveLoading }) => {
  const { data: user, isLoading: isLoadingUser } = useUser(userId);
  const [isRemoving, setIsRemoving] = useState(false);
  const queryClient = useQueryClient();

  const handleRemove = async () => {
    setIsRemoving(true);
    onRemoveLoading?.(true);
    try {
      await removeMember(expeditionId, userId);
      await queryClient.invalidateQueries({
        queryKey: ['expedition', expeditionId],
      });
    } finally {
      setIsRemoving(false);
      onRemoveLoading?.(false);
    }
  };

  return (
    <div className="flex items-center justify-between py-3 px-4 border-b border-gray-700 last:border-b-0">
      <div className="flex items-center gap-4 flex-1">
        <div className="flex-1 min-w-0">
          {isLoadingUser ? (
            <NameSkeleton />
          ) : (
            <p className="text-white font-semibold truncate">{user?.name || 'Unknown User'}</p>
          )}
        </div>
        <Badge variant={getMemberStateVariant(state)}>
          {getMemberStateText(state)}
        </Badge>
      </div>
      {isChief && (
        <button
          onClick={handleRemove}
          disabled={isRemoving || isLoadingUser}
          className="ml-4 px-2 py-1 text-red-400 text-sm hover:bg-red-500 hover:bg-opacity-10 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isRemoving ? 'Removing...' : 'Remove'}
        </button>
      )}
    </div>
  );
};

export const ExpeditionDetail: React.FC<ExpeditionDetailProps> = ({ expeditionId, onDeleted }) => {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const token = useAuthStore((state) => state.token);
  const queryClient = useQueryClient();

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isChangingStatus, setIsChangingStatus] = useState<ExpeditionStatus | null>(null);

  // Fetch expedition
  const { data: expedition, isLoading, error, refetch } = useQuery({
    queryKey: ['expedition', expeditionId],
    queryFn: () => fetchExpedition(expeditionId),
  });

  // Connect WebSocket
  useExpeditionWs({
    expeditionId,
    token,
    onAuthError: () => {
      logout();
    },
  });

  // Determine if user can see content (chief or confirmed member)
  const isChief = user?.role === Role.Chief && user?.id === expedition?.chief_id;
  const isMember = expedition?.members?.some(
    (m) => m.user_id === user?.id && m.state === MemberState.Confirmed
  );
  const isInvited = expedition?.members?.some(
    (m) => m.user_id === user?.id && m.state === MemberState.Invited
  );
  const canViewContent = isChief || isMember;

  // Handle delete
  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await deleteExpedition(expeditionId);
      await queryClient.invalidateQueries({
        queryKey: ['expeditions'],
      });
      onDeleted?.();
    } finally {
      setIsDeleting(false);
      setIsDeleteDialogOpen(false);
    }
  };

  // Handle status change
  const handleStatusChange = async (newStatus: ExpeditionStatus) => {
    if (!expedition) return;
    setIsChangingStatus(newStatus);
    try {
      await changeExpeditionStatus(expeditionId, newStatus);
      await queryClient.invalidateQueries({
        queryKey: ['expedition', expeditionId],
      });
    } finally {
      setIsChangingStatus(null);
    }
  };

  // Handle confirm membership
  const handleConfirmMembership = async () => {
    try {
      await confirmMembership(expeditionId);
      await queryClient.invalidateQueries({
        queryKey: ['expedition', expeditionId],
      });
    } catch (err) {
      console.error('Failed to confirm membership:', err);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
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
        <span className="ml-3 text-neon-cyan font-orbitron">Loading expedition...</span>
      </div>
    );
  }

  // Error state
  if (error || !expedition) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <div className="text-center space-y-2">
          <p className="text-red-400 font-orbitron">Failed to load expedition</p>
          <p className="text-sm text-gray-400">
            {error instanceof Error ? error.message : 'An unknown error occurred'}
          </p>
        </div>
        <Button variant="primary" onClick={() => refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  // Calculate member count
  const confirmedMembers = expedition.members?.filter(
    (m) => m.state === MemberState.Confirmed
  ).length || 0;

  return (
    <div className="space-y-4">
      {/* Header with title and status */}
      <GlassPanel glow="cyan" className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-white font-orbitron mb-2">
              {expedition.title}
            </h2>
            <Badge variant={getStatusVariant(expedition.status)}>
              {formatStatus(expedition.status)}
            </Badge>
          </div>
        </div>

        {/* Description */}
        <p className="text-gray-300 mb-4">{expedition.description}</p>

        {/* Meta info */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-400 mb-1">Start Date</p>
            <p className="text-white font-semibold">
              {new Date(expedition.start_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>
          <div>
            <p className="text-gray-400 mb-1">Capacity</p>
            <p className="text-white font-semibold">
              {confirmedMembers} / {expedition.capacity} members
            </p>
          </div>
        </div>
      </GlassPanel>

      {/* Invitation banner for invited members */}
      {isInvited && !isMember && (
        <GlassPanel glow="purple" className="p-4">
          <div className="flex items-center justify-between">
            <p className="text-neon-purple font-semibold">
              You have been invited to this expedition
            </p>
            <Button
              variant="secondary"
              onClick={handleConfirmMembership}
            >
              CONFIRM
            </Button>
          </div>
        </GlassPanel>
      )}

      {/* Chief command panel */}
      {isChief && (
        <GlassPanel className="p-4">
          <div className="space-y-4">
            <p className="text-gray-400 text-sm font-semibold">COMMANDS</p>

            {/* Status switcher buttons */}
            <div className="grid grid-cols-2 gap-2">
              {Object.values(ExpeditionStatus).map((status) => (
                <button
                  key={status}
                  onClick={() => handleStatusChange(status)}
                  disabled={isChangingStatus === status || expedition.status === status}
                  className={`px-3 py-2 rounded text-sm font-semibold transition-all ${
                    expedition.status === status
                      ? 'bg-neon-cyan bg-opacity-30 text-neon-cyan border border-neon-cyan'
                      : isChangingStatus === status
                      ? 'bg-gray-600 text-gray-300 opacity-50'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {isChangingStatus === status && (
                    <span className="inline-block mr-2">⏳</span>
                  )}
                  {formatStatus(status)}
                </button>
              ))}
            </div>

            {/* Action buttons */}
            <div className="grid grid-cols-3 gap-2">
              <Button
                variant="secondary"
                onClick={() => setIsEditModalOpen(true)}
                className="flex-1"
              >
                Edit
              </Button>
              <Button
                variant="secondary"
                onClick={() => setIsInviteModalOpen(true)}
                className="flex-1"
              >
                Invite
              </Button>
              <Button
                variant="danger"
                onClick={() => setIsDeleteDialogOpen(true)}
                className="flex-1"
              >
                Delete
              </Button>
            </div>

            {/* Delete confirmation dialog */}
            {isDeleteDialogOpen && (
              <GlassPanel className="p-4 border border-red-500 border-opacity-50 bg-red-500 bg-opacity-5">
                <p className="text-red-200 mb-3 text-sm">
                  Are you sure? This action cannot be undone.
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="danger"
                    onClick={handleDelete}
                    disabled={isDeleting}
                    className="flex-1"
                  >
                    {isDeleting ? 'Deleting...' : 'Confirm Delete'}
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={() => setIsDeleteDialogOpen(false)}
                    disabled={isDeleting}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </div>
              </GlassPanel>
            )}
          </div>
        </GlassPanel>
      )}

      {/* Members section */}
      {canViewContent && (
        <GlassPanel className="p-4">
          <p className="text-gray-400 text-sm font-semibold mb-3">
            MEMBERS ({expedition.members?.length || 0})
          </p>
          <div className="divide-y divide-gray-700">
            {expedition.members && expedition.members.length > 0 ? (
              expedition.members.map((member) => (
                <MemberRow
                  key={member.user_id}
                  userId={member.user_id}
                  state={member.state}
                  isChief={isChief}
                  expeditionId={expeditionId}
                />
              ))
            ) : (
              <p className="py-3 px-4 text-gray-400 text-sm">No members yet</p>
            )}
          </div>
        </GlassPanel>
      )}

      {/* Edit modal */}
      <EditExpeditionModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        expedition={expedition}
      />

      {/* Invite modal */}
      <InviteMemberModal
        isOpen={isInviteModalOpen}
        onClose={() => setIsInviteModalOpen(false)}
        expeditionId={expeditionId}
      />
    </div>
  );
};

ExpeditionDetail.displayName = 'ExpeditionDetail';
