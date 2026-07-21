import { createContext } from 'react';

import type {
  AuthStatus,
  LoginCredentials,
  RegistrationData,
  User,
} from '../../types/auth';

export interface AuthContextValue {
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: RegistrationData) => Promise<User>;
  status: AuthStatus;
  user: User | null;
}

export const AuthContext = createContext<AuthContextValue | null>(null);
