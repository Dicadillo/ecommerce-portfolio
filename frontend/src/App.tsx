import { RouterProvider } from 'react-router-dom';

import { AuthProvider } from './features/auth/AuthProvider';
import { CartProvider } from './features/cart/CartProvider';
import { router } from './router/router';

export function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <RouterProvider router={router} />
      </CartProvider>
    </AuthProvider>
  );
}
