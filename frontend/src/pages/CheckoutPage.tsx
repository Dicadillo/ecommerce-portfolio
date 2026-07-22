import { useState } from 'react';
import { Navigate } from 'react-router-dom';

import { createOrder } from '../api/orderApi';
import { ErrorState, LoadingState } from '../features/catalog/CatalogState';
import { CheckoutForm } from '../features/orders/CheckoutForm';
import { useCart } from '../hooks/useCart';
import type { CheckoutData } from '../types/order';
import { formatPrice } from '../utils/catalog';

export function CheckoutPage() {
  const { cart, completeCheckout, error, isLoading, products, retry } = useCart();
  const [createdOrderId, setCreatedOrderId] = useState<number | null>(null);

  if (createdOrderId) {
    return (
      <Navigate
        replace
        state={{ orderCreated: true }}
        to={`/pedidos/${createdOrderId}`}
      />
    );
  }

  if (isLoading) {
    return <LoadingState message="Preparando checkout…" />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={retry} />;
  }

  if (!cart || cart.articulos.length === 0) {
    return <Navigate replace to="/carrito" />;
  }

  async function handleCheckout(data: CheckoutData) {
    const order = await createOrder(data);
    completeCheckout();
    setCreatedOrderId(order.id);
  }

  return (
    <section className="checkout-page">
      <header>
        <p className="eyebrow">Finalizar compra</p>
        <h1>Checkout</h1>
        <p>Indica dónde debemos enviar tu pedido.</p>
      </header>

      <div className="checkout-layout">
        <CheckoutForm onSubmit={handleCheckout} />

        <aside className="checkout-summary">
          <h2>Resumen del carrito</h2>
          <ul>
            {cart.articulos.map((item) => (
              <li key={item.id}>
                <span>
                  {products[item.producto]?.nombre ?? `Producto ${item.producto}`} ×{' '}
                  {item.cantidad}
                </span>
                <strong>{formatPrice(item.subtotal)}</strong>
              </li>
            ))}
          </ul>
          <div>
            <span>Total</span>
            <strong>{formatPrice(cart.total)}</strong>
          </div>
          <p>El pago no se solicita en esta fase.</p>
        </aside>
      </div>
    </section>
  );
}
