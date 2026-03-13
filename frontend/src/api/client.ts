/**
 * API client with MSAL authentication
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { ApiError } from '../types';

// API base URL from environment
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Create axios instance with default configuration
 */
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 second timeout
  });

  // Request interceptor to add auth token
  client.interceptors.request.use(
    async (config) => {
      // TODO: Get token from MSAL
      // const token = await getAccessToken();
      // if (token) {
      //   config.headers.Authorization = `Bearer ${token}`;
      // }

      // Development token for testing
      if (import.meta.env.DEV) {
        config.headers.Authorization = 'Bearer dev-token';
      }

      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError<ApiError>) => {
      if (error.response) {
        // Server responded with error status
        const apiError: ApiError = {
          detail: error.response.data?.detail || 'An error occurred',
          status_code: error.response.status,
        };

        // Handle 401 - redirect to login
        if (error.response.status === 401) {
          // TODO: Trigger MSAL login
          console.error('Authentication required');
        }

        return Promise.reject(apiError);
      }

      // Network error or timeout
      return Promise.reject({
        detail: error.message || 'Network error',
        status_code: 0,
      } as ApiError);
    }
  );

  return client;
};

// Export singleton instance
export const apiClient = createApiClient();

/**
 * Type-safe API request helper
 */
export async function apiRequest<T>(
  config: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.request<T>(config);
  return response.data;
}

/**
 * GET request helper
 */
export async function get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  return apiRequest<T>({ method: 'GET', url, params });
}

/**
 * POST request helper
 */
export async function post<T>(url: string, data?: unknown): Promise<T> {
  return apiRequest<T>({ method: 'POST', url, data });
}

/**
 * PUT request helper
 */
export async function put<T>(url: string, data?: unknown): Promise<T> {
  return apiRequest<T>({ method: 'PUT', url, data });
}

/**
 * DELETE request helper
 */
export async function del<T>(url: string): Promise<T> {
  return apiRequest<T>({ method: 'DELETE', url });
}
