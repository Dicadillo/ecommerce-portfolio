import type { RouteObject } from 'react-router-dom';

import { ProtectedRoute } from '../components/ProtectedRoute';
import { MainLayout } from '../layouts/MainLayout';
import { CartPage } from '../pages/CartPage';
import { CheckoutPage } from '../pages/CheckoutPage';
import { HomePage } from '../pages/HomePage';
import { LoginPage } from '../pages/LoginPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { OrderDetailPage } from '../pages/OrderDetailPage';
import { OrderListPage } from '../pages/OrderListPage';
import { ProductDetailPage } from '../pages/ProductDetailPage';
import { ProductListPage } from '../pages/ProductListPage';
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
        element: <ProductListPage />,
      },
      {
        path: 'productos/:id',
        element: <ProductDetailPage />,
      },
      {
        path: 'carrito',
        element: (
          <ProtectedRoute>
            <CartPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'checkout',
        element: (
          <ProtectedRoute>
            <CheckoutPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'pedidos',
        element: (
          <ProtectedRoute>
            <OrderListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'pedidos/:id',
        element: (
          <ProtectedRoute>
            <OrderDetailPage />
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
