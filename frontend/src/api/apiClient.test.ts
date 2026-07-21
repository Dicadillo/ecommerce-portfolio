import MockAdapter from 'axios-mock-adapter';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  clearAuthSession,
  getAccessToken,
  getRefreshToken,
  saveAuthSession,
} from '../features/auth/authStorage';
import { apiClient, publicApiClient, setSessionExpiredHandler } from './apiClient';

describe('interceptor de autenticación', () => {
  const apiMock = new MockAdapter(apiClient);
  const publicApiMock = new MockAdapter(publicApiClient);

  beforeEach(() => {
    clearAuthSession();
    apiMock.reset();
    publicApiMock.reset();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('refresca el access token una vez y repite la petición', async () => {
    saveAuthSession({ acceso: 'acceso-caducado', refresco: 'refresco-valido' });
    publicApiMock
      .onPost('autenticacion/refrescar/', { refresco: 'refresco-valido' })
      .reply(200, { acceso: 'acceso-renovado' });
    apiMock
      .onGet('recurso-privado')
      .reply((config) =>
        config.headers?.Authorization === 'Bearer acceso-renovado'
          ? [200, { estado: 'ok' }]
          : [401, {}],
      );

    const response = await apiClient.get<{ estado: string }>('recurso-privado');

    expect(response.data).toEqual({ estado: 'ok' });
    expect(getAccessToken()).toBe('acceso-renovado');
    expect(publicApiMock.history.post).toHaveLength(1);
    expect(apiMock.history.get).toHaveLength(2);
  });

  it('limpia la sesión si falla el refresh', async () => {
    const sessionExpired = vi.fn();
    const removeHandler = setSessionExpiredHandler(sessionExpired);
    saveAuthSession({ acceso: 'acceso-caducado', refresco: 'refresco-invalido' });
    apiMock.onGet('recurso-privado').reply(401, {});
    publicApiMock
      .onPost('autenticacion/refrescar/', { refresco: 'refresco-invalido' })
      .reply(400, {});

    await expect(apiClient.get('recurso-privado')).rejects.toBeDefined();

    expect(publicApiMock.history.post).toHaveLength(1);
    expect(apiMock.history.get).toHaveLength(1);
    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
    expect(sessionExpired).toHaveBeenCalledOnce();
    removeHandler();
  });
});
