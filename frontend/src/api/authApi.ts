import { apiClient, publicApiClient, requestAccessTokenRefresh } from './apiClient';
import type {
  AccessTokenResponse,
  LoginCredentials,
  RegistrationData,
  TokenPair,
  User,
} from '../types/auth';

export async function registerUser(data: RegistrationData) {
  const response = await publicApiClient.post<User>('autenticacion/registro/', data);
  return response.data;
}

export async function loginUser(credentials: LoginCredentials) {
  const response = await publicApiClient.post<TokenPair>(
    'autenticacion/login/',
    credentials,
  );
  return response.data;
}

export function refreshSession(refreshToken: string): Promise<AccessTokenResponse> {
  return requestAccessTokenRefresh(refreshToken);
}

export async function getProfile() {
  const response = await apiClient.get<User>('autenticacion/perfil/');
  return response.data;
}

export async function logoutUser(refreshToken: string) {
  await apiClient.post('autenticacion/logout/', { refresco: refreshToken });
}
