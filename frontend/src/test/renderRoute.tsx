import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';

import { AuthProvider } from '../features/auth/AuthProvider';
import { routes } from '../router/routes';

export function renderRoute(initialPath = '/') {
  const router = createMemoryRouter(routes, {
    initialEntries: [initialPath],
  });

  return {
    router,
    user: userEvent.setup(),
    ...render(
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>,
    ),
  };
}
