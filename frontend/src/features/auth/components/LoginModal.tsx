import React, { useState } from 'react';
import { Modal } from '@/shared/ui/Modal';
import { loginUser, fetchMe } from '../api';
import { useAuthStore } from '../store';

export interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToRegister: () => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({
  isOpen,
  onClose,
  onSwitchToRegister,
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const setAuth = useAuthStore((state) => state.setAuth);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // Call login API
      const tokenResponse = await loginUser(email, password);

      // Fetch user profile
      const user = await fetchMe();

      // Set auth state
      setAuth(tokenResponse.access_token, user);

      // Close modal on success
      onClose();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Login failed. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Log In">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email input */}
        <div>
          <label htmlFor="email" className="block text-sm text-gray-300 mb-1">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
            disabled={isLoading}
            className="w-full px-3 py-2 bg-dark-bg border border-neon-cyan border-opacity-30 rounded text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan focus:border-opacity-100 transition-colors disabled:opacity-50"
          />
        </div>

        {/* Password input */}
        <div>
          <label htmlFor="password" className="block text-sm text-gray-300 mb-1">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
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
          {isLoading ? 'Logging in...' : 'Log In'}
        </button>

        {/* Switch to register link */}
        <div className="text-center text-sm text-gray-400">
          Don't have an account?{' '}
          <button
            type="button"
            onClick={onSwitchToRegister}
            className="text-neon-cyan hover:underline transition-colors"
          >
            Create one
          </button>
        </div>
      </form>
    </Modal>
  );
};

LoginModal.displayName = 'LoginModal';
