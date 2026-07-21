import type { TokenPair } from '../../types/auth';

const refreshTokenKey = 'ecommerce.auth.refresh';

let accessToken: string | null = null;

export function getAccessToken() {
  return accessToken;
}

export function getRefreshToken() {
  return window.sessionStorage.getItem(refreshTokenKey);
}

export function saveAuthSession(tokens: TokenPair) {
  accessToken = tokens.acceso;
  window.sessionStorage.setItem(refreshTokenKey, tokens.refresco);
}

export function updateAccessToken(token: string) {
  accessToken = token;
}

export function clearAuthSession() {
  accessToken = null;
  window.sessionStorage.removeItem(refreshTokenKey);
}
