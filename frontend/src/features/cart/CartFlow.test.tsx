import { screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getProfile } from '../../api/authApi';
import {
  addCartItem,
  clearCart,
  deleteCartItem,
  getCart,
  updateCartItem,
} from '../../api/cartApi';
import { getCategories, getProduct, getProducts } from '../../api/catalogApi';
import { saveAuthSession } from '../auth/authStorage';
import { renderRoute } from '../../test/renderRoute';
import type { Cart, CartItem } from '../../types/cart';
import type { Category, Product } from '../../types/catalog';

vi.mock('../../api/authApi', () => ({
  getProfile: vi.fn(),
  loginUser: vi.fn(),
  logoutUser: vi.fn(),
  refreshSession: vi.fn(),
  registerUser: vi.fn(),
}));

vi.mock('../../api/cartApi', () => ({
  addCartItem: vi.fn(),
  clearCart: vi.fn(),
  deleteCartItem: vi.fn(),
  getCart: vi.fn(),
  updateCartItem: vi.fn(),
}));

vi.mock('../../api/catalogApi', () => ({
  getCategories: vi.fn(),
  getCategory: vi.fn(),
  getProduct: vi.fn(),
  getProducts: vi.fn(),
}));

const profile = {
  id: 7,
  usuario: 'santi',
  correo: 'santi@example.com',
};

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
  categoria: 1,
  nombre: 'Teclado mecánico',
  slug: 'teclado-mecanico',
  descripcion: 'Teclado para automatización.',
  precio: '12.50',
  stock: 5,
  activo: true,
  creado_en: '2026-01-15T10:00:00Z',
  actualizado_en: '2026-01-15T10:00:00Z',
};

const emptyCart: Cart = {
  id: 3,
  articulos: [],
  cantidad_total: 0,
  total: '0.00',
};

function cartItem(quantity = 2, subtotal = '25.00'): CartItem {
  return {
    id: 21,
    producto: product.id,
    cantidad: quantity,
    subtotal,
  };
}

function cartWithItem(quantity = 2, total = '25.00'): Cart {
  return {
    id: 3,
    articulos: [cartItem(quantity, total)],
    cantidad_total: quantity,
    total,
  };
}

function authenticate() {
  saveAuthSession({ acceso: 'token-acceso', refresco: 'token-refresco' });
}

describe('carrito', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(getProfile).mockResolvedValue(profile);
    vi.mocked(getCart).mockResolvedValue(emptyCart);
    vi.mocked(getProduct).mockResolvedValue(product);
    vi.mocked(getCategories).mockResolvedValue({
      conteo: 1,
      siguiente: null,
      anterior: null,
      resultados: [category],
    });
    vi.mocked(getProducts).mockResolvedValue({
      conteo: 1,
      siguiente: null,
      anterior: null,
      resultados: [product],
    });
    vi.mocked(addCartItem).mockResolvedValue(cartItem(1, '12.50'));
    vi.mocked(updateCartItem).mockResolvedValue(cartItem());
    vi.mocked(deleteCartItem).mockResolvedValue(undefined);
    vi.mocked(clearCart).mockResolvedValue(undefined);
  });

  it('añade un producto desde el catálogo', async () => {
    authenticate();
    vi.mocked(getCart)
      .mockResolvedValueOnce(emptyCart)
      .mockResolvedValueOnce(cartWithItem(1, '12.50'));
    const { user } = renderRoute('/productos');

    await user.click(await screen.findByRole('button', { name: 'Añadir al carrito' }));

    expect(addCartItem).toHaveBeenCalledWith(product.id, 1);
    expect(await screen.findByText('Producto añadido al carrito.')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Carrito (1)' })).toBeInTheDocument();
  });

  it('impide añadir un producto sin stock', async () => {
    authenticate();
    vi.mocked(getProducts).mockResolvedValue({
      conteo: 1,
      siguiente: null,
      anterior: null,
      resultados: [{ ...product, stock: 0 }],
    });

    renderRoute('/productos');

    expect(await screen.findByRole('button', { name: 'No disponible' })).toBeDisabled();
    expect(addCartItem).not.toHaveBeenCalled();
  });

  it('renderiza un carrito vacío', async () => {
    authenticate();

    renderRoute('/carrito');

    expect(
      await screen.findByRole('heading', { name: 'Tu carrito está vacío' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Ver productos' })).toBeInTheDocument();
  });

  it('renderiza un carrito con artículos', async () => {
    authenticate();
    vi.mocked(getCart).mockResolvedValue(cartWithItem());

    renderRoute('/carrito');

    expect(
      await screen.findByRole('link', { name: 'Teclado mecánico' }),
    ).toBeInTheDocument();
    expect(screen.getByText(/Precio unitario: 12,50/)).toBeInTheDocument();
    expect(screen.getByLabelText('Cantidad de Teclado mecánico')).toHaveTextContent(
      '2',
    );
  });

  it('modifica la cantidad de un artículo', async () => {
    authenticate();
    vi.mocked(getCart)
      .mockResolvedValueOnce(cartWithItem())
      .mockResolvedValueOnce(cartWithItem(3, '37.50'));
    vi.mocked(updateCartItem).mockResolvedValue(cartItem(3, '37.50'));
    const { user } = renderRoute('/carrito');

    await user.click(
      await screen.findByRole('button', {
        name: 'Aumentar cantidad de Teclado mecánico',
      }),
    );

    expect(updateCartItem).toHaveBeenCalledWith(21, 3);
    await waitFor(() => {
      expect(screen.getByLabelText('Cantidad de Teclado mecánico')).toHaveTextContent(
        '3',
      );
    });
  });

  it('elimina un artículo', async () => {
    authenticate();
    vi.mocked(getCart)
      .mockResolvedValueOnce(cartWithItem())
      .mockResolvedValueOnce(emptyCart);
    const { user } = renderRoute('/carrito');

    await user.click(await screen.findByRole('button', { name: 'Eliminar' }));

    expect(deleteCartItem).toHaveBeenCalledWith(21);
    expect(
      await screen.findByRole('heading', { name: 'Tu carrito está vacío' }),
    ).toBeInTheDocument();
  });

  it('vacía el carrito después de confirmar', async () => {
    authenticate();
    vi.mocked(getCart)
      .mockResolvedValueOnce(cartWithItem())
      .mockResolvedValueOnce(emptyCart);
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(true);
    const { user } = renderRoute('/carrito');

    await user.click(await screen.findByRole('button', { name: 'Vaciar carrito' }));

    expect(confirm).toHaveBeenCalledWith('¿Seguro que quieres vaciar el carrito?');
    expect(clearCart).toHaveBeenCalledOnce();
    expect(
      await screen.findByRole('heading', { name: 'Tu carrito está vacío' }),
    ).toBeInTheDocument();
    confirm.mockRestore();
  });

  it('muestra precio, subtotal, cantidad total y total', async () => {
    authenticate();
    vi.mocked(getCart).mockResolvedValue(cartWithItem());

    renderRoute('/carrito');

    const itemLink = await screen.findByRole('link', { name: 'Teclado mecánico' });
    const item = itemLink.closest('article');
    const summary = screen.getByRole('heading', { name: 'Resumen' }).closest('aside');

    expect(item).not.toBeNull();
    expect(summary).not.toBeNull();
    expect(within(item!).getByText(/Precio unitario: 12,50/)).toBeInTheDocument();
    expect(within(item!).getByText(/25,00/)).toBeInTheDocument();
    expect(within(summary!).getByText('2')).toBeInTheDocument();
    expect(within(summary!).getByText(/25,00/)).toBeInTheDocument();
  });

  it('muestra el error de stock devuelto por el backend', async () => {
    authenticate();
    vi.mocked(addCartItem).mockRejectedValue({
      isAxiosError: true,
      response: {
        data: {
          error: {
            codigo: 'regla_de_negocio',
            mensaje: 'La operación incumple una regla de negocio.',
            detalles: {
              cantidad: ['La cantidad supera el stock disponible.'],
            },
          },
        },
      },
    });
    const { user } = renderRoute('/productos');

    await user.click(await screen.findByRole('button', { name: 'Añadir al carrito' }));

    expect(
      await screen.findByText('La cantidad supera el stock disponible.'),
    ).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveTextContent(
      'La cantidad supera el stock disponible.',
    );
  });

  it('redirige al login al acceder sin sesión', async () => {
    const { router } = renderRoute('/carrito');

    expect(
      await screen.findByRole('heading', { name: 'Iniciar sesión' }),
    ).toBeInTheDocument();
    expect(router.state.location.pathname).toBe('/login');
    expect(getCart).not.toHaveBeenCalled();
  });

  it('actualiza el contador del carrito en la navegación', async () => {
    authenticate();
    vi.mocked(getCart).mockResolvedValue(cartWithItem(3, '37.50'));

    renderRoute('/');

    expect(
      await screen.findByRole('link', { name: 'Carrito (3)' }),
    ).toBeInTheDocument();
  });
});
