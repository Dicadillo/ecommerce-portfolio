import { screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getProfile } from '../../api/authApi';
import { getCart } from '../../api/cartApi';
import { getProduct } from '../../api/catalogApi';
import { getOrder } from '../../api/orderApi';
import { createPayment, getPayment, refundPayment } from '../../api/paymentApi';
import { renderRoute } from '../../test/renderRoute';
import type { Cart } from '../../types/cart';
import type { Product } from '../../types/catalog';
import type { Order } from '../../types/order';
import type { Payment, PaymentStatus } from '../../types/payment';
import { saveAuthSession } from '../auth/authStorage';
import { clearPaymentRegistry, rememberPayment } from './paymentRegistry';

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

vi.mock('../../api/paymentApi', () => ({
  createPayment: vi.fn(),
  getPayment: vi.fn(),
  refundPayment: vi.fn(),
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

const emptyCart: Cart = {
  id: 3,
  articulos: [],
  cantidad_total: 0,
  total: '0.00',
};

const order: Order = {
  id: 42,
  estado: 'pendiente',
  nombre_destinatario: 'Santi García',
  direccion: 'Calle Mayor 10',
  ciudad: 'Madrid',
  codigo_postal: '28001',
  pais: 'España',
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

function paymentWithStatus(status: PaymentStatus): Payment {
  return {
    id: 9,
    pedido: order.id,
    estado: status,
    importe: '25.00',
    referencia: 'c665e417-f291-4d87-adac-740d84501593',
    proveedor: 'pasarela-simulada',
    ultimos_cuatro: status === 'rechazado' ? '0002' : '1111',
    fecha_creacion: '2026-07-20T10:35:00Z',
    fecha_actualizacion: '2026-07-20T10:35:00Z',
  };
}

const approvedPayment = paymentWithStatus('aprobado');

function authenticate() {
  saveAuthSession({ acceso: 'token-acceso', refresco: 'token-refresco' });
}

async function fillPaymentForm(
  user: ReturnType<typeof renderRoute>['user'],
  cardNumber = '4111111111111111',
  expiration = '12/30',
  cvv = '123',
) {
  await user.type(screen.getByLabelText('Número de tarjeta'), cardNumber);
  await user.type(screen.getByLabelText('Titular'), 'Santi García');
  await user.type(screen.getByLabelText('Fecha de expiración'), expiration);
  await user.type(screen.getByLabelText('CVV'), cvv);
}

describe('pagos simulados', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    clearPaymentRegistry();
    vi.mocked(getProfile).mockResolvedValue(profile);
    vi.mocked(getCart).mockResolvedValue(emptyCart);
    vi.mocked(getProduct).mockResolvedValue(product);
    vi.mocked(getOrder).mockResolvedValue(order);
    vi.mocked(createPayment).mockResolvedValue(approvedPayment);
    vi.mocked(getPayment).mockResolvedValue(approvedPayment);
    vi.mocked(refundPayment).mockResolvedValue(paymentWithStatus('reembolsado'));
  });

  it('renderiza el formulario y el resumen del pedido', async () => {
    authenticate();

    renderRoute('/pedidos/42/pagar');

    expect(
      await screen.findByRole('heading', { name: 'Pagar pedido #42' }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText('Número de tarjeta')).toBeInTheDocument();
    expect(screen.getByLabelText('CVV')).toHaveAttribute('type', 'password');
    const summary = screen
      .getByRole('heading', { name: 'Resumen del pedido' })
      .closest('aside');

    expect(summary).not.toBeNull();
    expect(within(summary!).getByText('Teclado mecánico')).toBeInTheDocument();
    expect(within(summary!).getAllByText(/25,00/)).toHaveLength(2);
  });

  it('valida el número de tarjeta con el algoritmo de Luhn', async () => {
    authenticate();
    const { user } = renderRoute('/pedidos/42/pagar');

    await screen.findByRole('heading', { name: 'Pagar pedido #42' });
    await fillPaymentForm(user, '4111111111111112');
    await user.click(screen.getByRole('button', { name: 'Pagar pedido' }));

    expect(
      screen.getByText('Introduce un número de tarjeta válido.'),
    ).toBeInTheDocument();
    expect(createPayment).not.toHaveBeenCalled();
  });

  it('valida la fecha de expiración y el CVV', async () => {
    authenticate();
    const { user } = renderRoute('/pedidos/42/pagar');

    await screen.findByRole('heading', { name: 'Pagar pedido #42' });
    await fillPaymentForm(user, '4111111111111111', '13/30', '12');
    await user.click(screen.getByRole('button', { name: 'Pagar pedido' }));

    expect(
      screen.getByText('Introduce una fecha válida con formato MM/AA.'),
    ).toBeInTheDocument();
    expect(
      screen.getByText('El CVV debe tener tres o cuatro dígitos.'),
    ).toBeInTheDocument();
    expect(createPayment).not.toHaveBeenCalled();
  });

  it('muestra un pago aprobado y actualiza el pedido a confirmado', async () => {
    authenticate();
    const { user } = renderRoute('/pedidos/42/pagar');

    await screen.findByRole('heading', { name: 'Pagar pedido #42' });
    await fillPaymentForm(user);
    await user.click(screen.getByRole('button', { name: 'Pagar pedido' }));

    expect(await screen.findByText('Aprobado')).toBeInTheDocument();
    expect(screen.getByText('El pago simulado ha sido aprobado.')).toBeInTheDocument();
    expect(screen.getByText('Confirmado')).toBeInTheDocument();
    expect(screen.getByText('Terminada en 1111')).toBeInTheDocument();
    expect(createPayment).toHaveBeenCalledWith<Parameters<typeof createPayment>>({
      pedido: 42,
      numero_tarjeta: '4111111111111111',
      titular: 'Santi García',
      fecha_expiracion: '12/30',
      cvv: '123',
    });
  });

  it('muestra un pago rechazado sin confirmar el pedido', async () => {
    authenticate();
    vi.mocked(createPayment).mockResolvedValue(paymentWithStatus('rechazado'));
    const { user } = renderRoute('/pedidos/42/pagar');

    await screen.findByRole('heading', { name: 'Pagar pedido #42' });
    await fillPaymentForm(user, '4000000000000002');
    await user.click(screen.getByRole('button', { name: 'Pagar pedido' }));

    expect(await screen.findByText('Rechazado')).toBeInTheDocument();
    expect(screen.getByText('El pago simulado ha sido rechazado.')).toBeInTheDocument();
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
  });

  it('muestra un pago pendiente', async () => {
    authenticate();
    vi.mocked(createPayment).mockResolvedValue(paymentWithStatus('pendiente'));
    const { user } = renderRoute('/pedidos/42/pagar');

    await screen.findByRole('heading', { name: 'Pagar pedido #42' });
    await fillPaymentForm(user, '5555555555554444');
    await user.click(screen.getByRole('button', { name: 'Pagar pedido' }));

    expect(await screen.findAllByText('Pendiente')).toHaveLength(2);
    expect(
      screen.getByText(
        'El pago permanece pendiente de resolución en la pasarela simulada.',
      ),
    ).toBeInTheDocument();
  });

  it('impide pagar un pedido cancelado', async () => {
    authenticate();
    vi.mocked(getOrder).mockResolvedValue({ ...order, estado: 'cancelado' });

    renderRoute('/pedidos/42/pagar');

    expect(
      await screen.findByRole('heading', { name: 'Pedido cancelado' }),
    ).toBeInTheDocument();
    expect(
      screen.getByText('Un pedido cancelado no se puede pagar.'),
    ).toBeInTheDocument();
    expect(screen.queryByLabelText('Número de tarjeta')).not.toBeInTheDocument();
    expect(createPayment).not.toHaveBeenCalled();
  });

  it('muestra el error del backend al intentar duplicar un pago', async () => {
    authenticate();
    vi.mocked(createPayment).mockRejectedValue({
      isAxiosError: true,
      response: {
        data: {
          error: {
            codigo: 'regla_de_negocio',
            mensaje: 'La operación incumple una regla de negocio.',
            detalles: { pedido: ['El pedido ya tiene un pago.'] },
          },
        },
      },
    });
    const { user } = renderRoute('/pedidos/42/pagar');

    await screen.findByRole('heading', { name: 'Pagar pedido #42' });
    await fillPaymentForm(user);
    await user.click(screen.getByRole('button', { name: 'Pagar pedido' }));

    expect(await screen.findByText('El pedido ya tiene un pago.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Pagar pedido' })).toBeEnabled();
  });

  it('consulta un pago conocido y no vuelve a mostrar el formulario', async () => {
    authenticate();
    rememberPayment(approvedPayment);

    renderRoute('/pedidos/42/pagar');

    expect(await screen.findByText('Aprobado')).toBeInTheDocument();
    expect(getPayment).toHaveBeenCalledWith(
      approvedPayment.id,
      expect.any(AbortSignal),
    );
    expect(screen.queryByLabelText('Número de tarjeta')).not.toBeInTheDocument();
    expect(createPayment).not.toHaveBeenCalled();
  });

  it('limpia número y CVV tras enviar y no los persiste', async () => {
    authenticate();
    vi.mocked(createPayment).mockRejectedValue(new Error('Sin conexión'));
    const { user } = renderRoute('/pedidos/42/pagar');

    await screen.findByRole('heading', { name: 'Pagar pedido #42' });
    await fillPaymentForm(user);
    await user.click(screen.getByRole('button', { name: 'Pagar pedido' }));

    expect(await screen.findByText('No se pudo procesar el pago.')).toBeInTheDocument();
    expect(screen.getByLabelText('Número de tarjeta')).toHaveValue('');
    expect(screen.getByLabelText('CVV')).toHaveValue('');

    const persistedValues = [window.localStorage, window.sessionStorage].flatMap(
      (storage) =>
        Array.from({ length: storage.length }, (_, index) =>
          storage.getItem(storage.key(index) ?? ''),
        ),
    );
    expect(persistedValues).not.toContain('4111111111111111');
    expect(persistedValues).not.toContain('123');
  });

  it('reembolsa un pago aprobado y actualiza el pedido', async () => {
    authenticate();
    rememberPayment(approvedPayment);
    vi.mocked(getOrder).mockResolvedValue({ ...order, estado: 'confirmado' });
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(true);
    const { user } = renderRoute('/pedidos/42');

    await user.click(await screen.findByRole('button', { name: 'Reembolsar pago' }));

    await waitFor(() => expect(refundPayment).toHaveBeenCalledWith(9));
    expect(await screen.findByText('Reembolsado')).toBeInTheDocument();
    expect(screen.getByText('Cancelado')).toBeInTheDocument();
    expect(confirm).toHaveBeenCalledWith('¿Seguro que quieres reembolsar este pago?');
    confirm.mockRestore();
  });

  it('muestra el error cuando el backend no permite reembolsar', async () => {
    authenticate();
    rememberPayment(approvedPayment);
    vi.mocked(getOrder).mockResolvedValue({ ...order, estado: 'confirmado' });
    vi.mocked(refundPayment).mockRejectedValue({
      isAxiosError: true,
      response: {
        data: {
          error: {
            codigo: 'regla_de_negocio',
            mensaje: 'La operación incumple una regla de negocio.',
            detalles: {
              estado: ['Solo se pueden reembolsar pagos aprobados.'],
            },
          },
        },
      },
    });
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(true);
    const { user } = renderRoute('/pedidos/42');

    await user.click(await screen.findByRole('button', { name: 'Reembolsar pago' }));

    expect(
      await screen.findByText('Solo se pueden reembolsar pagos aprobados.'),
    ).toBeInTheDocument();
    expect(screen.getByText('Aprobado')).toBeInTheDocument();
    confirm.mockRestore();
  });

  it('redirige al login al acceder sin autenticación', async () => {
    const { router } = renderRoute('/pedidos/42/pagar');

    expect(
      await screen.findByRole('heading', { name: 'Iniciar sesión' }),
    ).toBeInTheDocument();
    expect(router.state.location.pathname).toBe('/login');
    expect(getOrder).not.toHaveBeenCalled();
    expect(createPayment).not.toHaveBeenCalled();
  });
});
