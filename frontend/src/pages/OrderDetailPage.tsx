import axios from 'axios';
import { useEffect, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';

import { cancelOrder, getOrder } from '../api/orderApi';
import { ErrorState, LoadingState } from '../features/catalog/CatalogState';
import { OrderItems } from '../features/orders/OrderItems';
import { OrderStatusBadge } from '../features/orders/OrderStatusBadge';
import type { Order } from '../types/order';
import { getApiErrorMessage, parseApiError } from '../utils/apiErrors';
import { formatPrice } from '../utils/catalog';
import { formatOrderDate, isCancelableStatus } from '../utils/order';

interface OrderLocationState {
  orderCreated?: boolean;
}

interface OrderRequestState {
  error: string;
  key: string;
  order: Order | null;
  status: 'loading' | 'ready' | 'not-found' | 'error';
}

export function OrderDetailPage() {
  const { id } = useParams();
  const location = useLocation();
  const orderId = Number.parseInt(id ?? '', 10);
  const isValidOrderId = Number.isInteger(orderId) && orderId > 0;
  const [retry, setRetry] = useState(0);
  const requestKey = `${orderId}:${retry}`;
  const [request, setRequest] = useState<OrderRequestState>({
    error: '',
    key: requestKey,
    order: null,
    status: 'loading',
  });
  const [isCancelling, setIsCancelling] = useState(false);
  const [cancelError, setCancelError] = useState('');
  const currentRequest =
    request.key === requestKey
      ? request
      : { error: '', key: requestKey, order: null, status: 'loading' as const };
  const status = isValidOrderId ? currentRequest.status : 'not-found';
  const locationState = location.state as OrderLocationState | null;

  useEffect(() => {
    if (!isValidOrderId) {
      return;
    }

    const controller = new AbortController();

    void getOrder(orderId, controller.signal)
      .then((order) =>
        setRequest({ error: '', key: requestKey, order, status: 'ready' }),
      )
      .catch((requestError: unknown) => {
        if (controller.signal.aborted) {
          return;
        }

        if (axios.isAxiosError(requestError) && requestError.response?.status === 404) {
          setRequest({
            error: '',
            key: requestKey,
            order: null,
            status: 'not-found',
          });
          return;
        }

        setRequest({
          error: parseApiError(requestError, 'No se pudo cargar el pedido.').message,
          key: requestKey,
          order: null,
          status: 'error',
        });
      });

    return () => controller.abort();
  }, [isValidOrderId, orderId, requestKey]);

  async function handleCancel() {
    if (
      !currentRequest.order ||
      !window.confirm('¿Seguro que quieres cancelar este pedido?')
    ) {
      return;
    }

    setCancelError('');
    setIsCancelling(true);

    try {
      const canceledOrder = await cancelOrder(currentRequest.order.id);
      setRequest({
        error: '',
        key: requestKey,
        order: canceledOrder,
        status: 'ready',
      });
    } catch (error) {
      setCancelError(getApiErrorMessage(error, 'No se pudo cancelar el pedido.'));
    } finally {
      setIsCancelling(false);
    }
  }

  if (status === 'loading') {
    return <LoadingState message="Cargando pedido…" />;
  }

  if (status === 'not-found') {
    return (
      <section className="catalog-state">
        <p className="eyebrow">Pedidos</p>
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

  const cancelable = isCancelableStatus(order.estado);

  return (
    <article className="order-detail">
      <Link className="back-link" to="/pedidos">
        ← Volver a pedidos
      </Link>

      {locationState?.orderCreated && (
        <div className="form-banner form-banner-success" role="status">
          Pedido creado correctamente.
        </div>
      )}

      {cancelError && (
        <div className="form-banner form-banner-error" role="alert">
          {cancelError}
        </div>
      )}

      <header className="order-detail-heading">
        <div>
          <p className="eyebrow">Pedido</p>
          <h1>Pedido #{order.id}</h1>
          <time dateTime={order.fecha_creacion}>
            {formatOrderDate(order.fecha_creacion)}
          </time>
        </div>
        <OrderStatusBadge status={order.estado} />
      </header>

      <div className="order-detail-layout">
        <section className="order-detail-card">
          <h2>Productos</h2>
          <OrderItems items={order.articulos} />
          <div className="order-detail-total">
            <span>Total</span>
            <strong>{formatPrice(order.total)}</strong>
          </div>
        </section>

        <aside className="shipping-address">
          <h2>Dirección de envío</h2>
          <address>
            <strong>{order.nombre_destinatario}</strong>
            <span>{order.direccion}</span>
            <span>
              {order.codigo_postal} {order.ciudad}
            </span>
            <span>{order.pais}</span>
          </address>

          {cancelable ? (
            <button
              className="danger-button"
              disabled={isCancelling}
              onClick={handleCancel}
              type="button"
            >
              {isCancelling ? 'Cancelando…' : 'Cancelar pedido'}
            </button>
          ) : (
            <p className="non-cancelable-message">
              Este pedido no se puede cancelar en su estado actual.
            </p>
          )}
        </aside>
      </div>
    </article>
  );
}
