import { screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  getCategories,
  getCategory,
  getProduct,
  getProducts,
} from '../../api/catalogApi';
import { renderRoute } from '../../test/renderRoute';
import type { Category, PaginatedResponse, Product } from '../../types/catalog';

vi.mock('../../api/catalogApi', () => ({
  getCategories: vi.fn(),
  getCategory: vi.fn(),
  getProduct: vi.fn(),
  getProducts: vi.fn(),
}));

const category: Category = {
  id: 1,
  nombre: 'Accesorios',
  slug: 'accesorios',
  activo: true,
  creado_en: '2026-01-15T10:00:00Z',
  actualizado_en: '2026-01-15T10:00:00Z',
};

const product: Product = {
  id: 10,
  categoria: category.id,
  nombre: 'Teclado mecánico',
  slug: 'teclado-mecanico',
  descripcion: 'Teclado preparado para largas sesiones de automatización.',
  precio: '49.90',
  stock: 8,
  activo: true,
  creado_en: '2026-01-15T10:00:00Z',
  actualizado_en: '2026-01-15T10:00:00Z',
};

function paginated<T>(results: T[], overrides = {}): PaginatedResponse<T> {
  return {
    conteo: results.length,
    siguiente: null,
    anterior: null,
    resultados: results,
    ...overrides,
  };
}

describe('catálogo de productos', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(getCategories).mockResolvedValue(paginated([category]));
    vi.mocked(getProducts).mockResolvedValue(paginated([product]));
    vi.mocked(getProduct).mockResolvedValue(product);
    vi.mocked(getCategory).mockResolvedValue(category);
  });

  it('renderiza el listado con los datos principales', async () => {
    renderRoute('/productos');

    const productLink = await screen.findByRole('link', {
      name: 'Teclado mecánico',
    });
    const productCard = productLink.closest('article');

    expect(productCard).not.toBeNull();
    expect(within(productCard!).getByText('Accesorios')).toBeInTheDocument();
    expect(within(productCard!).getByText(/49,90/)).toBeInTheDocument();
    expect(
      within(productCard!).getByText('8 unidades disponibles'),
    ).toBeInTheDocument();
    expect(within(productCard!).getByText('Activo')).toBeInTheDocument();
  });

  it('muestra un indicador durante la carga', () => {
    vi.mocked(getProducts).mockReturnValue(new Promise(() => undefined));

    renderRoute('/productos');

    expect(screen.getByRole('status')).toHaveTextContent('Cargando productos…');
  });

  it('muestra el error y permite reintentar', async () => {
    vi.mocked(getProducts)
      .mockRejectedValueOnce(new Error('Fallo de red'))
      .mockResolvedValueOnce(paginated([product]));
    const { user } = renderRoute('/productos');

    expect(
      await screen.findByText('No se pudieron cargar los productos.'),
    ).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Reintentar' }));

    expect(
      await screen.findByRole('link', { name: 'Teclado mecánico' }),
    ).toBeInTheDocument();
    expect(getProducts).toHaveBeenCalledTimes(2);
  });

  it('muestra el estado de listado vacío', async () => {
    vi.mocked(getProducts).mockResolvedValue(paginated([]));

    renderRoute('/productos');

    expect(
      await screen.findByRole('heading', { name: 'No hay productos' }),
    ).toBeInTheDocument();
  });

  it('busca por nombre y sincroniza la URL', async () => {
    const { router, user } = renderRoute('/productos');
    await screen.findByRole('link', { name: 'Teclado mecánico' });

    await user.type(screen.getByLabelText('Buscar por nombre'), 'teclado');
    await user.click(screen.getByRole('button', { name: 'Buscar' }));

    await waitFor(() => {
      expect(getProducts).toHaveBeenLastCalledWith(
        { buscar: 'teclado' },
        expect.any(AbortSignal),
      );
    });
    expect(router.state.location.search).toBe('?buscar=teclado');
  });

  it('filtra por categoría y sincroniza la URL', async () => {
    const { router, user } = renderRoute('/productos');
    await screen.findByRole('link', { name: 'Teclado mecánico' });

    await user.selectOptions(screen.getByLabelText('Categoría'), '1');

    await waitFor(() => {
      expect(getProducts).toHaveBeenLastCalledWith(
        { categoria: 1 },
        expect.any(AbortSignal),
      );
    });
    expect(router.state.location.search).toBe('?categoria=1');
  });

  it('filtra productos con stock', async () => {
    const { router, user } = renderRoute('/productos');
    await screen.findByRole('link', { name: 'Teclado mecánico' });

    await user.click(screen.getByLabelText('Solo productos con stock'));

    await waitFor(() => {
      expect(getProducts).toHaveBeenLastCalledWith(
        { con_stock: true },
        expect.any(AbortSignal),
      );
    });
    expect(router.state.location.search).toBe('?con_stock=true');
  });

  it('ordena por precio', async () => {
    const { router, user } = renderRoute('/productos');
    await screen.findByRole('link', { name: 'Teclado mecánico' });

    await user.selectOptions(screen.getByLabelText('Ordenar'), '-precio');

    await waitFor(() => {
      expect(getProducts).toHaveBeenLastCalledWith(
        { ordenar: '-precio' },
        expect.any(AbortSignal),
      );
    });
    expect(router.state.location.search).toBe('?ordenar=-precio');
  });

  it('avanza a la página siguiente conservando los filtros', async () => {
    vi.mocked(getProducts).mockResolvedValue(
      paginated([product], {
        conteo: 12,
        siguiente: 'http://localhost:8000/api/productos/?pagina=2',
      }),
    );
    const { router, user } = renderRoute('/productos?buscar=teclado');
    await screen.findByRole('link', { name: 'Teclado mecánico' });

    await user.click(screen.getByRole('button', { name: 'Siguiente' }));

    await waitFor(() => {
      expect(getProducts).toHaveBeenLastCalledWith(
        { buscar: 'teclado', pagina: 2 },
        expect.any(AbortSignal),
      );
    });
    expect(router.state.location.search).toContain('buscar=teclado');
    expect(router.state.location.search).toContain('pagina=2');
  });

  it('muestra el detalle de un producto', async () => {
    renderRoute('/productos/10');

    expect(
      await screen.findByRole('heading', { name: 'Teclado mecánico' }),
    ).toBeInTheDocument();
    expect(screen.getByText(product.descripcion)).toBeInTheDocument();
    expect(screen.getByText('Accesorios')).toBeInTheDocument();
    expect(screen.getByText(/49,90/)).toBeInTheDocument();
    expect(getProduct).toHaveBeenCalledWith(10, expect.any(AbortSignal));
    expect(getCategory).toHaveBeenCalledWith(1, expect.any(AbortSignal));
  });

  it('muestra un estado específico para un producto inexistente', async () => {
    vi.mocked(getProduct).mockRejectedValue({
      isAxiosError: true,
      response: { status: 404 },
    });

    renderRoute('/productos/999');

    expect(
      await screen.findByRole('heading', { name: 'Producto no encontrado' }),
    ).toBeInTheDocument();
    expect(getCategory).not.toHaveBeenCalled();
  });

  it('marca un producto sin stock e impide comprarlo', async () => {
    vi.mocked(getProduct).mockResolvedValue({ ...product, stock: 0 });

    renderRoute('/productos/10');

    expect(await screen.findByText('Sin stock disponible')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'No disponible' })).toBeDisabled();
  });

  it('marca un producto inactivo e impide comprarlo', async () => {
    vi.mocked(getProduct).mockResolvedValue({ ...product, activo: false });

    renderRoute('/productos/10');

    expect(
      await screen.findByText('Este producto no está disponible actualmente.'),
    ).toBeInTheDocument();
    expect(screen.getByText('Inactivo')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'No disponible' })).toBeDisabled();
  });
});
