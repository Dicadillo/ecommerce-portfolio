import { useState } from 'react';
import { NavLink } from 'react-router-dom';

import { useAuth } from '../hooks/useAuth';
import { useCart } from '../hooks/useCart';

interface NavigationItem {
  end?: boolean;
  label: string;
  to: string;
}

const navigationItems: readonly NavigationItem[] = [
  { to: '/', label: 'Inicio', end: true },
  { to: '/productos', label: 'Productos' },
  { to: '/carrito', label: 'Carrito' },
  { to: '/pedidos', label: 'Pedidos' },
];

export function MainNavigation() {
  const { isAuthenticated, logout, status, user } = useAuth();
  const { itemCount } = useCart();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  async function handleLogout() {
    setIsLoggingOut(true);
    await logout();
    setIsLoggingOut(false);
  }

  return (
    <nav aria-label="Navegación principal" data-testid="main-navigation">
      <ul className="main-navigation">
        {navigationItems.map(({ to, label, end }) => {
          const visibleLabel =
            to === '/carrito' && isAuthenticated && itemCount > 0
              ? `${label} (${itemCount})`
              : label;

          return (
            <li key={to}>
              <NavLink
                className={({ isActive }) => (isActive ? 'active' : undefined)}
                data-testid={`nav-${to === '/' ? 'home' : to.slice(1)}`}
                end={end}
                to={to}
              >
                {visibleLabel}
              </NavLink>
            </li>
          );
        })}
        {status !== 'loading' && !isAuthenticated && (
          <>
            <li>
              <NavLink data-testid="nav-login" to="/login">Iniciar sesión</NavLink>
            </li>
            <li>
              <NavLink data-testid="nav-register" to="/registro">Registrarse</NavLink>
            </li>
          </>
        )}
        {isAuthenticated && (
          <>
            <li className="session-user">Hola, {user?.usuario}</li>
            <li>
              <button
                className="navigation-button"
                data-testid="logout-button"
                disabled={isLoggingOut}
                onClick={handleLogout}
                type="button"
              >
                {isLoggingOut ? 'Cerrando sesión…' : 'Cerrar sesión'}
              </button>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
}
