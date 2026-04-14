import React, { useState } from 'react';
import { Modal } from '@/shared/ui/Modal';
import { registerUser, loginUser, fetchMe } from '../api';
import { useAuthStore } from '../store';

export interface RegisterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToLogin: () => void;
}

export const RegisterModal: React.FC<RegisterModalProps> = ({
  isOpen,
  onClose,
  onSwitchToLogin,
}) => {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'member' | 'chief'>('member');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const setAuth = useAuthStore((state) => state.setAuth);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // Call register API
      await registerUser({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        role,
      });

      // Auto-login: call login API
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
          : 'Registration failed. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Account">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* First name input */}
        <div>
          <label htmlFor="firstName" className="block text-sm text-gray-300 mb-1">
            First Name
          </label>
          <input
            id="firstName"
            type="text"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            placeholder="John"
            required
            disabled={isLoading}
            className="w-full px-3 py-2 bg-dark-bg border border-neon-cyan border-opacity-30 rounded text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan focus:border-opacity-100 transition-colors disabled:opacity-50"
          />
        </div>

        {/* Last name input */}
        <div>
          <label htmlFor="lastName" className="block text-sm text-gray-300 mb-1">
            Last Name
          </label>
          <input
            id="lastName"
            type="text"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            placeholder="Doe"
            required
            disabled={isLoading}
            className="w-full px-3 py-2 bg-dark-bg border border-neon-cyan border-opacity-30 rounded text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan focus:border-opacity-100 transition-colors disabled:opacity-50"
          />
        </div>

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

        {/* Role select */}
        <div>
          <label htmlFor="role" className="block text-sm text-gray-300 mb-1">
            Role
          </label>
          <select
            id="role"
            value={role}
            onChange={(e) => setRole(e.target.value as 'member' | 'chief')}
            disabled={isLoading}
            className="w-full px-3 py-2 bg-dark-bg border border-neon-cyan border-opacity-30 rounded text-white focus:outline-none focus:border-neon-cyan focus:border-opacity-100 transition-colors disabled:opacity-50 cursor-pointer"
          >
            <option value="member">Member</option>
            <option value="chief">Chief</option>
          </select>
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
          {isLoading ? 'Creating account...' : 'Create Account'}
        </button>

        {/* Switch to login link */}
        <div className="text-center text-sm text-gray-400">
          Already have an account?{' '}
          <button
            type="button"
            onClick={onSwitchToLogin}
            className="text-neon-cyan hover:underline transition-colors"
          >
            Log in
          </button>
        </div>
      </form>
    </Modal>
  );
};

RegisterModal.displayName = 'RegisterModal';
