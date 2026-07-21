import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { renderRoute } from '../test/renderRoute';

describe('página de inicio', () => {
  it('muestra el contenido principal y la navegación', () => {
    renderRoute();

    expect(
      screen.getByRole('heading', { name: 'Una base preparada para crecer' }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('navigation', { name: 'Navegación principal' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Productos' })).toBeInTheDocument();
  });
});
