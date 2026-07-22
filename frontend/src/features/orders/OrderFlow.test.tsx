import { screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getProfile } from '../../api/authApi';
import { getCart } from '../../api/cartApi';
import { getProduct } from '../../api/catalogApi';
import { cancelOrder, createOrder, getOrder, getOrders } from '../../api/orderApi';
import { renderRoute } from '../../test/renderRoute';
import type { Cart } from '../../types/cart';
import type { Product } from '../../types/catalog';
import type { CheckoutData, Order } from '../../types/order';
import { saveAuthSession } from '../auth/authStorage';

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

vi.mock('../../api/orderApi', () => ({
  cancelOrder: vi.fn(),
  createOrder: vi.fn(),
  getOrder: vi.fn(),
  getOrders: vi.fn(),
}));

const profile = {
  id: 7,
  usuario: 'santi',
  correo: 'santi@example.com',
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

const cartWithItems: Cart = {
  id: 3,
  articulos: [
    {
      id: 21,
      producto: product.id,
      cantidad: 2,
      subtotal: '25.00',
    },
  ],
  cantidad_total: 2,
  total: '25.00',
};

const emptyCart: Cart = {
  id: 3,
  articulos: [],
  cantidad_total: 0,
  total: '0.00',
};

const checkoutData: CheckoutData = {
  nombre_destinatario: 'Santi García',
  direccion: 'Calle Mayor 10',
  ciudad: 'Madrid',
  codigo_postal: '28001',
  pais: 'España',
};

const order: Order = {
  id: 42,
  estado: 'pendiente',
  ...checkoutData,
  total: '25.00',
  fecha_creacion: '2026-07-20T10:30:00Z',
  fecha_actualizacion: '2026-07-20T10:30:00Z',
  articulos: [
    {
      id: 80,
      producto: product.id,
      nombre_producto: 'Teclado mecánico',
      precio_unitario: '12.50',
      cantidad: 2,
      subtotal: '25.00',
    },
  ],
};

function authenticate() {
  saveAuthSession({ acceso: 'token-acceso', refresco: 'token-refresco' });
}

async function completeCheckoutForm(user: ReturnType<typeof renderRoute>['user']) {
  await user.type(screen.getByLabelText('Nombre del destinatario'), 'Santi García');
  await user.type(screen.getByLabelText('Dirección'), 'Calle Mayor 10');
  await user.type(screen.getByLabelText('Ciudad'), 'Madrid');
  await user.type(screen.getByLabelText('Código postal'), '28001');
  await user.type(screen.getByLabelText('País'), 'España');
}

describe('checkout y pedidos', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(getProfile).mockResolvedValue(profile);
    vi.mocked(getCart).mockResolvedValue(cartWithItems);
    vi.mocked(getProduct).mockResolvedValue(product);
    vi.mocked(createOrder).mockResolvedValue(order);
    vi.mocked(getOrders).mockResolvedValue([order]);
    vi.mocked(getOrder).mockResolvedValue(order);
    vi.mocked(cancelOrder).mockResolvedValue({ ...order, estado: 'cancelado' });
  });

  it('renderiza el checkout con el resumen del carrito', async () => {
    authenticate();

    renderRoute('/checkout');

    expect(
      await screen.findByRole('heading', { name: 'Checkout' }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText('Nombre del destinatario')).toBeInTheDocument();
    const summary = screen
      .getByRole('heading', { name: 'Resumen del carrito' })
      .closest('aside');

    expect(summary).not.toBeNull();
    expect(within(summary!).getByText(/Teclado mecánico × 2/)).toBeInTheDocument();
    expect(within(summary!).getAllByText(/25,00/)).toHaveLength(2);
  });

  it('valida los campos obligatorios antes de crear el pedido', async () => {
    authenticate();
    const { user } = renderRoute('/checkout');

    await user.click(await screen.findByRole('button', { name: 'Confirmar pedido' }));

    expect(screen.getByText('Introduce nombre del destinatario.')).toBeInTheDocument();
    expect(screen.getByText('Introduce dirección.')).toBeInTheDocument();
    expect(screen.getByText('Introduce ciudad.')).toBeInTheDocument();
    expect(screen.getByText('Introduce código postal.')).toBeInTheDocument();
    expect(screen.getByText('Introduce país.')).toBeInTheDocument();
    expect(createOrder).not.toHaveBeenCalled();
  });

  it('redirige al carrito cuando el checkout está vacío', async () => {
    authenticate();
    vi.mocked(getCart).mockResolvedValue(emptyCart);
    const { router } = renderRoute('/checkout');

    expect(
      await screen.findByRole('heading', { name: 'Tu carrito está vacío' }),
    ).toBeInTheDocument();
    expect(router.state.location.pathname).toBe('/carrito');
  });

  it('crea el pedido y redirige a su detalle con confirmación', async () => {
    authenticate();
    const { router, user } = renderRoute('/checkout');

    await screen.findByRole('heading', { name: 'Checkout' });
    await completeCheckoutForm(user);
    await user.click(screen.getByRole('button', { name: 'Confirmar pedido' }));

    expect(
      await screen.findByRole('heading', { name: 'Pedido #42' }),
    ).toBeInTheDocument();
    expect(screen.getByText('Pedido creado correctamente.')).toBeInTheDocument();
    expect(router.state.location.pathname).toBe('/pedidos/42');
    expect(createOrder).toHaveBeenCalledWith(checkoutData);
  });

  it('muestra el error de stock recibido durante el checkout', async () => {
    authenticate();
    vi.mocked(createOrder).mockRejectedValue({
      isAxiosError: true,
      response: {
        data: {
          error: {
            codigo: 'stock_insuficiente',
            mensaje: 'No se pudo completar el pedido.',
            detalles: {
              carrito: ['No hay stock suficiente para Teclado mecánico.'],
            },
          },
        },
      },
    });
    const { user } = renderRoute('/checkout');

    await screen.findByRole('heading', { name: 'Checkout' });
    await completeCheckoutForm(user);
    await user.click(screen.getByRole('button', { name: 'Confirmar pedido' }));

    expect(
      await screen.findByText('No hay stock suficiente para Teclado mecánico.'),
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Confirmar pedido' })).toBeEnabled();
  });

  it('vacía el estado local y actualiza el contador tras el checkout', async () => {
    authenticate();
    const { user } = renderRoute('/checkout');

    await screen.findByRole('heading', { name: 'Checkout' });
    expect(screen.getByRole('link', { name: 'Carrito (2)' })).toBeInTheDocument();
    await completeCheckoutForm(user);
    await user.click(screen.getByRole('button', { name: 'Confirmar pedido' }));

    await screen.findByRole('heading', { name: 'Pedido #42' });
    expect(screen.getByRole('link', { name: 'Carrito' })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Carrito (2)' })).not.toBeInTheDocument();
  });

  it('lista los pedidos con artículos y precios históricos', async () => {
    authenticate();

    renderRoute('/pedidos');

    const orderLink = await screen.findByRole('link', { name: 'Pedido #42' });
    const orderCard = orderLink.closest('article');

    expect(orderCard).not.toBeNull();
    expect(within(orderCard!).getByText('Pendiente')).toBeInTheDocument();
    expect(within(orderCard!).getByText('Teclado mecánico')).toBeInTheDocument();
    expect(within(orderCard!).getByText(/12,50.*× 2/)).toBeInTheDocument();
    expect(within(orderCard!).getAllByText(/25,00/)).toHaveLength(2);
  });

  it('muestra el estado vacío del historial de pedidos', async () => {
    authenticate();
    vi.mocked(getOrders).mockResolvedValue([]);

    renderRoute('/pedidos');

    expect(
      await screen.findByRole('heading', { name: 'Todavía no tienes pedidos' }),
    ).toBeInTheDocument();
  });

  it('muestra el detalle completo del pedido', async () => {
    authenticate();

    renderRoute('/pedidos/42');

    expect(
      await screen.findByRole('heading', { name: 'Pedido #42' }),
    ).toBeInTheDocument();
    expect(screen.getByText('Teclado mecánico')).toBeInTheDocument();
    expect(screen.getByText(/12,50.*× 2/)).toBeInTheDocument();
    expect(screen.getByText('Santi García')).toBeInTheDocument();
    expect(screen.getByText('Calle Mayor 10')).toBeInTheDocument();
    expect(screen.getByText('28001 Madrid')).toBeInTheDocument();
    expect(screen.getByText('España')).toBeInTheDocument();
  });

  it('cancela un pedido después de pedir confirmación', async () => {
    authenticate();
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(true);
    const { user } = renderRoute('/pedidos/42');

    await user.click(await screen.findByRole('button', { name: 'Cancelar pedido' }));

    await waitFor(() => expect(cancelOrder).toHaveBeenCalledWith(42));
    expect(await screen.findByText('Cancelado')).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: 'Cancelar pedido' }),
    ).not.toBeInTheDocument();
    expect(confirm).toHaveBeenCalledWith('¿Seguro que quieres cancelar este pedido?');
    confirm.mockRestore();
  });

  it('no ofrece cancelar un pedido en un estado no permitido', async () => {
    authenticate();
    vi.mocked(getOrder).mockResolvedValue({ ...order, estado: 'enviado' });

    renderRoute('/pedidos/42');

    expect(await screen.findByText('Enviado')).toBeInTheDocument();
    expect(
      screen.getByText('Este pedido no se puede cancelar en su estado actual.'),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: 'Cancelar pedido' }),
    ).not.toBeInTheDocument();
  });

  it('trata por igual un pedido inexistente o perteneciente a otro usuario', async () => {
    authenticate();
    vi.mocked(getOrder).mockRejectedValue({
      isAxiosError: true,
      response: { status: 404 },
    });

    renderRoute('/pedidos/99');

    expect(
      await screen.findByRole('heading', { name: 'Pedido no encontrado' }),
    ).toBeInTheDocument();
    expect(
      screen.getByText('El pedido no existe o no pertenece a tu cuenta.'),
    ).toBeInTheDocument();
  });

  it('redirige al login al acceder sin sesión', async () => {
    const { router } = renderRoute('/checkout');

    expect(
      await screen.findByRole('heading', { name: 'Iniciar sesión' }),
    ).toBeInTheDocument();
    expect(router.state.location.pathname).toBe('/login');
    expect(getCart).not.toHaveBeenCalled();
    expect(createOrder).not.toHaveBeenCalled();
  });
});
