import axios, { type AxiosRequestConfig, type InternalAxiosRequestConfig } from 'axios';

import {
  clearAuthSession,
  getAccessToken,
  getRefreshToken,
  updateAccessToken,
} from '../features/auth/authStorage';
import type { AccessTokenResponse } from '../types/auth';

const apiUrl = import.meta.env.VITE_API_URL;

if (!apiUrl) {
  throw new Error('La variable VITE_API_URL no está configurada.');
}

const clientConfig: AxiosRequestConfig = {
  baseURL: apiUrl,
  headers: {
    Accept: 'application/json',
  },
  timeout: 10_000,
};

export const publicApiClient = axios.create(clientConfig);
export const apiClient = axios.create(clientConfig);

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  hasRetriedAuthentication?: boolean;
}

let refreshPromise: Promise<string> | null = null;
let sessionExpiredHandler: () => void = () => undefined;

export function setSessionExpiredHandler(handler: () => void) {
  sessionExpiredHandler = handler;

  return () => {
    if (sessionExpiredHandler === handler) {
      sessionExpiredHandler = () => undefined;
    }
  };
}

export async function requestAccessTokenRefresh(refreshToken: string) {
  const response = await publicApiClient.post<AccessTokenResponse>(
    'autenticacion/refrescar/',
    { refresco: refreshToken },
  );

  return response.data;
}

async function refreshAccessToken() {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    throw new Error('No hay un token de refresco disponible.');
  }

  const response = await requestAccessTokenRefresh(refreshToken);
  updateAccessToken(response.acceso);
  return response.acceso;
}

function getRefreshPromise() {
  if (!refreshPromise) {
    refreshPromise = refreshAccessToken().finally(() => {
      refreshPromise = null;
    });
  }

  return refreshPromise;
}

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (!axios.isAxiosError(error)) {
      return Promise.reject(error);
    }

    const originalRequest = error.config as RetryableRequestConfig | undefined;

    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest.hasRetriedAuthentication
    ) {
      return Promise.reject(error);
    }

    originalRequest.hasRetriedAuthentication = true;

    try {
      const newAccessToken = await getRefreshPromise();
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return await apiClient.request(originalRequest);
    } catch (refreshError) {
      clearAuthSession();
      sessionExpiredHandler();
      return Promise.reject(refreshError);
    }
  },
);
