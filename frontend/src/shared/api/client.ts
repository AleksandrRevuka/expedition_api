/**
 * Configured Axios instance for API requests
 * Includes authentication and error handling interceptors
 */

import axios, { AxiosError, AxiosResponse } from 'axios';
import { ENV } from '../config/env';

/**
 * Create API client with baseURL and interceptors
 */
export const apiClient = axios.create({
  baseURL: `${ENV.API_URL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor: Add authentication token from localStorage
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor: Handle 401 Unauthorized
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear auth token and reload the page to redirect to login
      localStorage.removeItem('auth_token');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);
