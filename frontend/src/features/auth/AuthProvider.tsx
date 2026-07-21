import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';

import { getProfile, loginUser, logoutUser, registerUser } from '../../api/authApi';
import { setSessionExpiredHandler } from '../../api/apiClient';
import type {
  AuthStatus,
  LoginCredentials,
  RegistrationData,
  User,
} from '../../types/auth';
import { AuthContext } from './AuthContext';
import { clearAuthSession, getRefreshToken, saveAuthSession } from './authStorage';

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<AuthStatus>(() =>
    getRefreshToken() ? 'loading' : 'anonymous',
  );

  useEffect(() => {
    let isMounted = true;

    const removeSessionExpiredHandler = setSessionExpiredHandler(() => {
      if (isMounted) {
        setUser(null);
        setStatus('anonymous');
      }
    });

    if (getRefreshToken()) {
      void getProfile()
        .then((profile) => {
          if (isMounted) {
            setUser(profile);
            setStatus('authenticated');
          }
        })
        .catch(() => {
          clearAuthSession();
          if (isMounted) {
            setUser(null);
            setStatus('anonymous');
          }
        });
    }

    return () => {
      isMounted = false;
      removeSessionExpiredHandler();
    };
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const tokens = await loginUser(credentials);
    saveAuthSession(tokens);

    try {
      const profile = await getProfile();
      setUser(profile);
      setStatus('authenticated');
    } catch (error) {
      clearAuthSession();
      setUser(null);
      setStatus('anonymous');
      throw error;
    }
  }, []);

  const register = useCallback((data: RegistrationData) => registerUser(data), []);

  const logout = useCallback(async () => {
    const refreshToken = getRefreshToken();

    try {
      if (refreshToken) {
        await logoutUser(refreshToken);
      }
    } catch {
      // El cierre local debe completarse aunque el servidor no esté disponible.
    } finally {
      clearAuthSession();
      setUser(null);
      setStatus('anonymous');
    }
  }, []);

  const value = useMemo(
    () => ({
      isAuthenticated: status === 'authenticated',
      login,
      logout,
      register,
      status,
      user,
    }),
    [login, logout, register, status, user],
  );

  return <AuthContext value={value}>{children}</AuthContext>;
}
