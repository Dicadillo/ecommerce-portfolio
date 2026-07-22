import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { getOrders } from '../api/orderApi';
import { ErrorState, LoadingState } from '../features/catalog/CatalogState';
import { OrderItems } from '../features/orders/OrderItems';
import { OrderStatusBadge } from '../features/orders/OrderStatusBadge';
import type { Order } from '../types/order';
import { parseApiError } from '../utils/apiErrors';
import { formatPrice } from '../utils/catalog';
import { formatOrderDate } from '../utils/order';

interface OrdersRequestState {
  error: string;
  orders: Order[];
  status: 'loading' | 'ready' | 'error';
}

export function OrderListPage() {
  const [retry, setRetry] = useState(0);
  const [request, setRequest] = useState<OrdersRequestState>({
    error: '',
    orders: [],
    status: 'loading',
  });

  useEffect(() => {
    const controller = new AbortController();

    void getOrders(controller.signal)
      .then((orders) => setRequest({ error: '', orders, status: 'ready' }))
      .catch((requestError: unknown) => {
        if (!controller.signal.aborted) {
          setRequest({
            error: parseApiError(requestError, 'No se pudieron cargar los pedidos.')
              .message,
            orders: [],
            status: 'error',
          });
        }
      });

    return () => controller.abort();
  }, [retry]);

  function retryRequest() {
    setRequest({ error: '', orders: [], status: 'loading' });
    setRetry((value) => value + 1);
  }

  return (
    <section className="orders-page">
      <header>
        <p className="eyebrow">Historial</p>
        <h1>Pedidos</h1>
      </header>

      {request.status === 'loading' && <LoadingState message="Cargando pedidos…" />}

      {request.status === 'error' && (
        <ErrorState message={request.error} onRetry={retryRequest} />
      )}

      {request.status === 'ready' && request.orders.length === 0 && (
        <div className="orders-empty">
          <h2>Todavía no tienes pedidos</h2>
          <p>Cuando completes una compra aparecerá aquí.</p>
          <Link className="primary-link" to="/productos">
            Ver productos
          </Link>
        </div>
      )}

      {request.status === 'ready' && request.orders.length > 0 && (
        <ul className="orders-list">
          {request.orders.map((order) => (
            <li key={order.id}>
              <article className="order-card">
                <header>
                  <div>
                    <h2>
                      <Link to={`/pedidos/${order.id}`}>Pedido #{order.id}</Link>
                    </h2>
                    <time dateTime={order.fecha_creacion}>
                      {formatOrderDate(order.fecha_creacion)}
                    </time>
                  </div>
                  <OrderStatusBadge status={order.estado} />
                </header>
                <OrderItems items={order.articulos} />
                <footer>
                  <span>Total</span>
                  <strong>{formatPrice(order.total)}</strong>
                </footer>
              </article>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
