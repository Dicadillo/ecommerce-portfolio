import axios from 'axios';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { getPayment, refundPayment } from '../../api/paymentApi';
import type { Order } from '../../types/order';
import type { Payment } from '../../types/payment';
import { getApiErrorMessage } from '../../utils/apiErrors';
import { PaymentDetails } from './PaymentDetails';
import { forgetPayment, getKnownPaymentId, rememberPayment } from './paymentRegistry';

interface OrderPaymentSectionProps {
  onOrderRefunded: () => void;
  order: Order;
}

interface PaymentRequestState {
  error: string;
  key: string;
  payment: Payment | null;
  status: 'loading' | 'ready' | 'not-found' | 'error';
}

export function OrderPaymentSection({
  onOrderRefunded,
  order,
}: OrderPaymentSectionProps) {
  const paymentId = getKnownPaymentId(order.id);
  const [retry, setRetry] = useState(0);
  const requestKey = `${paymentId ?? 'none'}:${retry}`;
  const [request, setRequest] = useState<PaymentRequestState>({
    error: '',
    key: requestKey,
    payment: null,
    status: 'loading',
  });
  const [isRefunding, setIsRefunding] = useState(false);
  const [refundError, setRefundError] = useState('');
  const currentRequest =
    request.key === requestKey
      ? request
      : {
          error: '',
          key: requestKey,
          payment: null,
          status: 'loading' as const,
        };

  useEffect(() => {
    if (!paymentId) {
      return;
    }

    const controller = new AbortController();

    void getPayment(paymentId, controller.signal)
      .then((payment) =>
        setRequest({
          error: '',
          key: requestKey,
          payment,
          status: 'ready',
        }),
      )
      .catch((requestError: unknown) => {
        if (controller.signal.aborted) {
          return;
        }

        if (axios.isAxiosError(requestError) && requestError.response?.status === 404) {
          forgetPayment(order.id);
          setRequest({
            error: '',
            key: requestKey,
            payment: null,
            status: 'not-found',
          });
          return;
        }

        setRequest({
          error: getApiErrorMessage(requestError, 'No se pudo consultar el pago.'),
          key: requestKey,
          payment: null,
          status: 'error',
        });
      });

    return () => controller.abort();
  }, [order.id, paymentId, requestKey]);

  async function handleRefund() {
    const payment = currentRequest.payment;

    if (!payment || !window.confirm('¿Seguro que quieres reembolsar este pago?')) {
      return;
    }

    setRefundError('');
    setIsRefunding(true);

    try {
      const refundedPayment = await refundPayment(payment.id);
      rememberPayment(refundedPayment);
      setRequest({
        error: '',
        key: requestKey,
        payment: refundedPayment,
        status: 'ready',
      });
      onOrderRefunded();
    } catch (error) {
      setRefundError(getApiErrorMessage(error, 'No se pudo reembolsar el pago.'));
    } finally {
      setIsRefunding(false);
    }
  }

  if (!paymentId || currentRequest.status === 'not-found') {
    return (
      <section className="order-payment-section">
        <h2>Pago</h2>
        {order.estado === 'pendiente' ? (
          <>
            <p>Este pedido todavía está pendiente de pago.</p>
            <Link className="primary-link" to={`/pedidos/${order.id}/pagar`}>
              Pagar pedido
            </Link>
          </>
        ) : order.estado === 'cancelado' ? (
          <p>Los pedidos cancelados no se pueden pagar.</p>
        ) : (
          <p>No hay información de pago disponible en esta sesión.</p>
        )}
      </section>
    );
  }

  if (currentRequest.status === 'loading') {
    return (
      <section className="order-payment-section" aria-live="polite">
        <h2>Pago</h2>
        <p>Consultando el pago…</p>
      </section>
    );
  }

  if (currentRequest.status === 'error') {
    return (
      <section className="order-payment-section">
        <h2>Pago</h2>
        <div className="form-banner form-banner-error" role="alert">
          {currentRequest.error}
        </div>
        <button
          className="secondary-button"
          onClick={() => setRetry((value) => value + 1)}
          type="button"
        >
          Reintentar
        </button>
      </section>
    );
  }

  const payment = currentRequest.payment;

  if (!payment) {
    return null;
  }

  return (
    <section className="order-payment-section">
      {refundError && (
        <div className="form-banner form-banner-error" role="alert">
          {refundError}
        </div>
      )}

      <PaymentDetails payment={payment} />

      {payment.estado === 'aprobado' && (
        <button
          className="danger-button"
          disabled={isRefunding}
          onClick={handleRefund}
          type="button"
        >
          {isRefunding ? 'Reembolsando…' : 'Reembolsar pago'}
        </button>
      )}

      {payment.estado !== 'aprobado' && payment.estado !== 'reembolsado' && (
        <p className="non-refundable-message">
          Solo se pueden reembolsar pagos aprobados.
        </p>
      )}
    </section>
  );
}
