import React, { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Modal } from '@/shared/ui/Modal';
import { inviteMember } from '../api';

export interface InviteMemberModalProps {
  isOpen: boolean;
  onClose: () => void;
  expeditionId: string | null;
}

export const InviteMemberModal: React.FC<InviteMemberModalProps> = ({
  isOpen,
  onClose,
  expeditionId,
}) => {
  const [userId, setUserId] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const queryClient = useQueryClient();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!expeditionId) {
      setError('No expedition selected');
      return;
    }

    setIsLoading(true);

    try {
      await inviteMember(expeditionId, userId);

      // Invalidate expedition query
      await queryClient.invalidateQueries({
        queryKey: ['expedition', expeditionId],
      });

      // Reset form and close modal
      setUserId('');
      onClose();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to invite member. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Invite Member">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Note about member role requirement */}
        <div className="p-3 bg-neon-cyan bg-opacity-10 border border-neon-cyan border-opacity-30 rounded text-gray-300 text-sm">
          The invited user must have the member role to accept the invitation.
        </div>

        {/* User ID input */}
        <div>
          <label htmlFor="userId" className="block text-sm text-gray-300 mb-1">
            Member UUID
          </label>
          <input
            id="userId"
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="UUID of the member to invite"
            required
            disabled={isLoading}
            className="w-full px-3 py-2 bg-dark-bg border border-neon-cyan border-opacity-30 rounded text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan focus:border-opacity-100 transition-colors disabled:opacity-50 font-mono text-sm"
          />
        </div>

        {/* Error message */}
        {error && (
          <div className="p-3 bg-red-500 bg-opacity-20 border border-red-500 border-opacity-50 rounded text-red-200 text-sm">
            {error}
          </div>
        )}

        {/* Submit button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full px-4 py-2 bg-neon-cyan text-dark-bg font-bold rounded hover:bg-opacity-80 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Inviting...' : 'Send Invitation'}
        </button>
      </form>
    </Modal>
  );
};

InviteMemberModal.displayName = 'InviteMemberModal';
