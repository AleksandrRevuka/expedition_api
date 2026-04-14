import React, { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Modal } from '@/shared/ui/Modal';
import { updateExpedition } from '../api';
import { Expedition } from '@/shared/types';

export interface EditExpeditionModalProps {
  isOpen: boolean;
  onClose: () => void;
  expedition: Expedition | null;
}

export const EditExpeditionModal: React.FC<EditExpeditionModalProps> = ({
  isOpen,
  onClose,
  expedition,
}) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const queryClient = useQueryClient();

  // Pre-fill form when expedition changes
  useEffect(() => {
    if (expedition) {
      setTitle(expedition.title);
      setDescription(expedition.description);
      setError(null);
    }
  }, [expedition]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!expedition) {
      setError('No expedition selected');
      return;
    }

    setIsLoading(true);

    try {
      await updateExpedition(expedition.id, {
        title,
        description,
      });

      // Invalidate both expedition-specific and expeditions list queries
      await queryClient.invalidateQueries({
        queryKey: ['expedition', expedition.id],
      });
      await queryClient.invalidateQueries({
        queryKey: ['expeditions'],
      });

      onClose();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to update expedition. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Edit Expedition">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title input */}
        <div>
          <label htmlFor="title" className="block text-sm text-gray-300 mb-1">
            Title
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Expedition title"
            required
            disabled={isLoading}
            className="w-full px-3 py-2 bg-dark-bg border border-neon-cyan border-opacity-30 rounded text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan focus:border-opacity-100 transition-colors disabled:opacity-50"
          />
        </div>

        {/* Description textarea */}
        <div>
          <label htmlFor="description" className="block text-sm text-gray-300 mb-1">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Expedition description"
            required
            disabled={isLoading}
            rows={4}
            className="w-full px-3 py-2 bg-dark-bg border border-neon-cyan border-opacity-30 rounded text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan focus:border-opacity-100 transition-colors disabled:opacity-50 resize-none"
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
          {isLoading ? 'Saving...' : 'Save Changes'}
        </button>
      </form>
    </Modal>
  );
};

EditExpeditionModal.displayName = 'EditExpeditionModal';
