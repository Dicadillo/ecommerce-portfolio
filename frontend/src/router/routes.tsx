import type { RouteObject } from 'react-router-dom';

import { ProtectedRoute } from '../components/ProtectedRoute';
import { MainLayout } from '../layouts/MainLayout';
import { HomePage } from '../pages/HomePage';
import { LoginPage } from '../pages/LoginPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { PlaceholderPage } from '../pages/PlaceholderPage';
import { RegisterPage } from '../pages/RegisterPage';

export const routes: RouteObject[] = [
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'login',
        element: <LoginPage />,
      },
      {
        path: 'registro',
        element: <RegisterPage />,
      },
      {
        path: 'productos',
        element: (
          <PlaceholderPage
            description="El catálogo se conectará con la API en una fase posterior."
            title="Productos"
          />
        ),
      },
      {
        path: 'carrito',
        element: (
          <ProtectedRoute>
            <PlaceholderPage
              description="La gestión del carrito todavía no está disponible."
              title="Carrito"
            />
          </ProtectedRoute>
        ),
      },
      {
        path: 'pedidos',
        element: (
          <ProtectedRoute>
            <PlaceholderPage
              description="El historial de pedidos se implementará más adelante."
              title="Pedidos"
            />
          </ProtectedRoute>
        ),
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
];
