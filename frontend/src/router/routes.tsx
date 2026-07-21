import type { RouteObject } from 'react-router-dom';

import { MainLayout } from '../layouts/MainLayout';
import { HomePage } from '../pages/HomePage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { PlaceholderPage } from '../pages/PlaceholderPage';

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
        element: (
          <PlaceholderPage
            description="El acceso de usuarios se implementará en la siguiente fase."
            title="Iniciar sesión"
          />
        ),
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
          <PlaceholderPage
            description="La gestión del carrito todavía no está disponible."
            title="Carrito"
          />
        ),
      },
      {
        path: 'pedidos',
        element: (
          <PlaceholderPage
            description="El historial de pedidos se implementará más adelante."
            title="Pedidos"
          />
        ),
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
];
