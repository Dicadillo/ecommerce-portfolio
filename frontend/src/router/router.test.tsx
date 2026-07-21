import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { renderRoute } from '../test/renderRoute';

describe('enrutador principal', () => {
  it('permite navegar a una ruta provisional', async () => {
    const { router, user } = renderRoute();

    await user.click(screen.getByRole('link', { name: 'Productos' }));

    expect(
      await screen.findByRole('heading', { name: 'Productos' }),
    ).toBeInTheDocument();
    expect(router.state.location.pathname).toBe('/productos');
  });

  it('muestra la página 404 para una ruta desconocida', () => {
    renderRoute('/ruta-inexistente');

    expect(
      screen.getByRole('heading', { name: 'Página no encontrada' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Volver al inicio' })).toBeInTheDocument();
  });
});
