export interface User {
  id: number;
  usuario: string;
  correo: string;
}

export interface LoginCredentials {
  usuario: string;
  contrasena: string;
}

export interface RegistrationData extends LoginCredentials {
  correo: string;
  confirmacion_contrasena: string;
}

export interface TokenPair {
  acceso: string;
  refresco: string;
}

export interface AccessTokenResponse {
  acceso: string;
}

export type AuthStatus = 'loading' | 'authenticated' | 'anonymous';
