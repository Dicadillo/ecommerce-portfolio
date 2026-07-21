import { screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getProfile, loginUser, logoutUser, registerUser } from '../../api/authApi';
import { renderRoute } from '../../test/renderRoute';
import {
  clearAuthSession,
  getAccessToken,
  getRefreshToken,
  saveAuthSession,
} from './authStorage';

vi.mock('../../api/authApi', () => ({
  getProfile: vi.fn(),
  loginUser: vi.fn(),
  logoutUser: vi.fn(),
  refreshSession: vi.fn(),
  registerUser: vi.fn(),
}));

const userProfile = {
  id: 7,
  usuario: 'santi',
  correo: 'santi@example.com',
};

const tokens = {
  acceso: 'token-acceso',
  refresco: 'token-refresco',
};

describe('flujo de autenticación', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    clearAuthSession();
  });

  it('renderiza el formulario de login', () => {
    renderRoute('/login');

    expect(screen.getByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument();
    expect(screen.getByLabelText('Usuario')).toBeInTheDocument();
    expect(screen.getByLabelText('Contraseña')).toHaveAttribute('type', 'password');
  });

  it('valida los campos obligatorios del login', async () => {
    const { user } = renderRoute('/login');

    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }));

    expect(screen.getByText('Introduce tu nombre de usuario.')).toBeInTheDocument();
    expect(screen.getByText('Introduce tu contraseña.')).toBeInTheDocument();
    expect(loginUser).not.toHaveBeenCalled();
  });

  it('inicia sesión y redirige a productos', async () => {
    vi.mocked(loginUser).mockResolvedValue(tokens);
    vi.mocked(getProfile).mockResolvedValue(userProfile);
    const { router, user } = renderRoute('/login');

    await user.type(screen.getByLabelText('Usuario'), 'santi');
    await user.type(screen.getByLabelText('Contraseña'), 'ClaveSegura!2026');
    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }));

    expect(
      await screen.findByRole('heading', { name: 'Productos' }),
    ).toBeInTheDocument();
    expect(router.state.location.pathname).toBe('/productos');
    expect(loginUser).toHaveBeenCalledWith({
      usuario: 'santi',
      contrasena: 'ClaveSegura!2026',
    });
    expect(getRefreshToken()).toBe('token-refresco');
    expect(getAccessToken()).toBe('token-acceso');
  });

  it('muestra el error devuelto por un login incorrecto', async () => {
    vi.mocked(loginUser).mockRejectedValue({
      isAxiosError: true,
      response: {
        data: {
          error: {
            codigo: 'autenticacion_fallida',
            mensaje: 'No se pudo validar la autenticación.',
            detalles: {},
          },
        },
      },
    });
    const { user } = renderRoute('/login');

    await user.type(screen.getByLabelText('Usuario'), 'santi');
    await user.type(screen.getByLabelText('Contraseña'), 'incorrecta');
    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }));

    expect(
      await screen.findByText('No se pudo validar la autenticación.'),
    ).toBeInTheDocument();
    expect(getRefreshToken()).toBeNull();
  });

  it('registra un usuario y lo dirige al login', async () => {
    vi.mocked(registerUser).mockResolvedValue(userProfile);
    const { router, user } = renderRoute('/registro');

    await user.type(screen.getByLabelText('Usuario'), 'santi');
    await user.type(screen.getByLabelText('Correo electrónico'), 'santi@example.com');
    await user.type(screen.getByLabelText('Contraseña'), 'ClaveSegura!2026');
    await user.type(screen.getByLabelText('Confirmar contraseña'), 'ClaveSegura!2026');
    await user.click(screen.getByRole('button', { name: 'Crear cuenta' }));

    expect(
      await screen.findByRole('heading', { name: 'Iniciar sesión' }),
    ).toBeInTheDocument();
    expect(
      screen.getByText('Tu cuenta se ha creado. Ya puedes iniciar sesión.'),
    ).toBeInTheDocument();
    expect(router.state.location.pathname).toBe('/login');
    expect(registerUser).toHaveBeenCalledWith({
      usuario: 'santi',
      correo: 'santi@example.com',
      contrasena: 'ClaveSegura!2026',
      confirmacion_contrasena: 'ClaveSegura!2026',
    });
  });

  it('redirige una ruta protegida al login sin sesión', async () => {
    const { router } = renderRoute('/carrito');

    expect(
      await screen.findByRole('heading', { name: 'Iniciar sesión' }),
    ).toBeInTheDocument();
    expect(router.state.location.pathname).toBe('/login');
  });

  it('permite acceder a una ruta protegida con sesión', async () => {
    saveAuthSession(tokens);
    vi.mocked(getProfile).mockResolvedValue(userProfile);

    renderRoute('/carrito');

    expect(await screen.findByRole('heading', { name: 'Carrito' })).toBeInTheDocument();
    expect(getProfile).toHaveBeenCalledOnce();
  });

  it('cierra la sesión local y remota', async () => {
    saveAuthSession(tokens);
    vi.mocked(getProfile).mockResolvedValue(userProfile);
    vi.mocked(logoutUser).mockResolvedValue(undefined);
    const { user } = renderRoute('/productos');

    await user.click(await screen.findByRole('button', { name: 'Cerrar sesión' }));

    await waitFor(() => {
      expect(screen.getByRole('link', { name: 'Iniciar sesión' })).toBeInTheDocument();
    });
    expect(logoutUser).toHaveBeenCalledWith('token-refresco');
    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
  });
});
