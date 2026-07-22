import axios from 'axios';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import { getOrder } from '../api/orderApi';
import { createPayment, getPayment } from '../api/paymentApi';
import { ErrorState, LoadingState } from '../features/catalog/CatalogState';
import { OrderItems } from '../features/orders/OrderItems';
import { OrderStatusBadge } from '../features/orders/OrderStatusBadge';
import { PaymentDetails } from '../features/payments/PaymentDetails';
import { PaymentForm } from '../features/payments/PaymentForm';
import {
  forgetPayment,
  getKnownPaymentId,
  rememberPayment,
} from '../features/payments/paymentRegistry';
import type { Order } from '../types/order';
import type { Payment, PaymentData } from '../types/payment';
import { parseApiError } from '../utils/apiErrors';
import { formatPrice } from '../utils/catalog';
import { getOrderStatusAfterPayment } from '../utils/payment';

interface PaymentPageState {
  error: string;
  key: string;
  order: Order | null;
  payment: Payment | null;
  status: 'loading' | 'ready' | 'not-found' | 'error';
}

export function PaymentPage() {
  const { id } = useParams();
  const orderId = Number.parseInt(id ?? '', 10);
  const isValidOrderId = Number.isInteger(orderId) && orderId > 0;
  const [retry, setRetry] = useState(0);
  const requestKey = `${orderId}:${retry}`;
  const [request, setRequest] = useState<PaymentPageState>({
    error: '',
    key: requestKey,
    order: null,
    payment: null,
    status: 'loading',
  });
  const currentRequest =
    request.key === requestKey
      ? request
      : {
          error: '',
          key: requestKey,
          order: null,
          payment: null,
          status: 'loading' as const,
        };
  const status = isValidOrderId ? currentRequest.status : 'not-found';

  useEffect(() => {
    if (!isValidOrderId) {
      return;
    }

    const controller = new AbortController();

    async function loadPaymentPage() {
      const order = await getOrder(orderId, controller.signal);
      const paymentId = getKnownPaymentId(orderId);
      let payment: Payment | null = null;

      if (paymentId) {
        try {
          payment = await getPayment(paymentId, controller.signal);
        } catch (paymentError) {
          if (
            axios.isAxiosError(paymentError) &&
            paymentError.response?.status === 404
          ) {
            forgetPayment(orderId);
          } else {
            throw paymentError;
          }
        }
      }

      return { order, payment };
    }

    void loadPaymentPage()
      .then(({ order, payment }) => {
        setRequest({
          error: '',
          key: requestKey,
          order,
          payment,
          status: 'ready',
        });
      })
      .catch((requestError: unknown) => {
        if (controller.signal.aborted) {
          return;
        }

        if (axios.isAxiosError(requestError) && requestError.response?.status === 404) {
          setRequest({
            error: '',
            key: requestKey,
            order: null,
            payment: null,
            status: 'not-found',
          });
          return;
        }

        setRequest({
          error: parseApiError(requestError, 'No se pudo preparar el pago.').message,
          key: requestKey,
          order: null,
          payment: null,
          status: 'error',
        });
      });

    return () => controller.abort();
  }, [isValidOrderId, orderId, requestKey]);

  async function handlePayment(data: PaymentData) {
    if (!currentRequest.order) {
      return;
    }

    const payment = await createPayment(data);
    rememberPayment(payment);
    setRequest({
      error: '',
      key: requestKey,
      order: {
        ...currentRequest.order,
        estado: getOrderStatusAfterPayment(currentRequest.order.estado, payment.estado),
      },
      payment,
      status: 'ready',
    });
  }

  if (status === 'loading') {
    return <LoadingState message="Preparando pago…" />;
  }

  if (status === 'not-found') {
    return (
      <section className="catalog-state">
        <p className="eyebrow">Pagos</p>
        <h1>Pedido no encontrado</h1>
        <p>El pedido no existe o no pertenece a tu cuenta.</p>
        <Link className="primary-link" to="/pedidos">
          Volver a pedidos
        </Link>
      </section>
    );
  }

  if (status === 'error') {
    return (
      <ErrorState
        message={currentRequest.error}
        onRetry={() => setRetry((value) => value + 1)}
      />
    );
  }

  const order = currentRequest.order;

  if (!order) {
    return null;
  }

  return (
    <section className="payment-page">
      <Link className="back-link" to={`/pedidos/${order.id}`}>
        ← Volver al pedido
      </Link>

      <header className="payment-page-heading">
        <div>
          <p className="eyebrow">Pasarela simulada</p>
          <h1>Pagar pedido #{order.id}</h1>
        </div>
        <OrderStatusBadge status={order.estado} />
      </header>

      <div className="payment-layout">
        <div>
          {currentRequest.payment ? (
            <PaymentDetails payment={currentRequest.payment} />
          ) : order.estado === 'cancelado' ? (
            <div className="payment-blocked">
              <h2>Pedido cancelado</h2>
              <p>Un pedido cancelado no se puede pagar.</p>
            </div>
          ) : order.estado !== 'pendiente' ? (
            <div className="payment-blocked">
              <h2>Pago no disponible</h2>
              <p>Solo se pueden pagar pedidos pendientes.</p>
            </div>
          ) : (
            <PaymentForm onSubmit={handlePayment} orderId={order.id} />
          )}
        </div>

        <aside className="payment-order-summary">
          <h2>Resumen del pedido</h2>
          <OrderItems items={order.articulos} />
          <div>
            <span>Total</span>
            <strong>{formatPrice(order.total)}</strong>
          </div>
        </aside>
      </div>
    </section>
  );
}
