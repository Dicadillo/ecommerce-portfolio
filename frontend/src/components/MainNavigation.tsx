import { NavLink } from 'react-router-dom';

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
  { to: '/login', label: 'Iniciar sesión' },
];

export function MainNavigation() {
  return (
    <nav aria-label="Navegación principal">
      <ul className="main-navigation">
        {navigationItems.map(({ to, label, end }) => (
          <li key={to}>
            <NavLink
              className={({ isActive }) => (isActive ? 'active' : undefined)}
              end={end}
              to={to}
            >
              {label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
