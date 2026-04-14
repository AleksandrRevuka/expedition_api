import React, { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Modal } from '@/shared/ui/Modal';
import { createExpedition } from '../api';

export interface CreateExpeditionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CreateExpeditionModal: React.FC<CreateExpeditionModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [startAt, setStartAt] = useState('');
  const [capacity, setCapacity] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const queryClient = useQueryClient();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await createExpedition({
        title,
        description,
        start_at: startAt,
        capacity: Number(capacity),
      });

      // Invalidate expeditions list query
      await queryClient.invalidateQueries({
        queryKey: ['expeditions'],
      });

      // Reset form and close modal
      setTitle('');
      setDescription('');
      setStartAt('');
      setCapacity('');
      onClose();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to create expedition. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Expedition">
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

        {/* Start date/time input */}
        <div>
          <label htmlFor="startAt" className="block text-sm text-gray-300 mb-1">
            Start Date & Time
          </label>
          <input
            id="startAt"
            type="datetime-local"
            value={startAt}
            onChange={(e) => setStartAt(e.target.value)}
            required
            disabled={isLoading}
            className="w-full px-3 py-2 bg-dark-bg border border-neon-cyan border-opacity-30 rounded text-white focus:outline-none focus:border-neon-cyan focus:border-opacity-100 transition-colors disabled:opacity-50"
          />
        </div>

        {/* Capacity input */}
        <div>
          <label htmlFor="capacity" className="block text-sm text-gray-300 mb-1">
            Capacity
          </label>
          <input
            id="capacity"
            type="number"
            value={capacity}
            onChange={(e) => setCapacity(e.target.value)}
            placeholder="Number of participants"
            min="1"
            required
            disabled={isLoading}
            className="w-full px-3 py-2 bg-dark-bg border border-neon-cyan border-opacity-30 rounded text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan focus:border-opacity-100 transition-colors disabled:opacity-50"
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
          {isLoading ? 'Creating...' : 'Create Expedition'}
        </button>
      </form>
    </Modal>
  );
};

CreateExpeditionModal.displayName = 'CreateExpeditionModal';
