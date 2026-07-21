import { RouterProvider } from 'react-router-dom';

import { AuthProvider } from './features/auth/AuthProvider';
import { router } from './router/router';

export function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  );
}
