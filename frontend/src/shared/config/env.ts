/**
 * Environment configuration
 * Loads values from import.meta.env (Vite environment variables)
 */

export const ENV = {
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
} as const;
