import { useState } from 'react';
import { Link } from 'react-router-dom';

import { ErrorState, LoadingState } from '../features/catalog/CatalogState';
import { useCart } from '../hooks/useCart';
import { formatPrice } from '../utils/catalog';
import { getApiErrorMessage } from '../utils/apiErrors';

export function CartPage() {
  const {
    cart,
    clear,
    error,
    isLoading,
    isMutating,
    products,
    removeItem,
    retry,
    updateQuantity,
  } = useCart();
  const [operationError, setOperationError] = useState('');

  async function runOperation(operation: () => Promise<void>) {
    setOperationError('');
    try {
      await operation();
    } catch (operationFailure) {
      setOperationError(
        getApiErrorMessage(operationFailure, 'No se pudo actualizar el carrito.'),
      );
    }
  }

  function handleClear() {
    if (window.confirm('¿Seguro que quieres vaciar el carrito?')) {
      void runOperation(clear);
    }
  }

  return (
    <section className="cart-page">
      <header className="cart-heading">
        <div>
          <p className="eyebrow">Tu compra</p>
          <h1>Carrito</h1>
        </div>
        {cart && cart.articulos.length > 0 && (
          <button
            className="danger-button"
            disabled={isMutating}
            onClick={handleClear}
            type="button"
          >
            Vaciar carrito
          </button>
        )}
      </header>

      {operationError && (
        <div className="form-banner form-banner-error" role="alert">
          {operationError}
        </div>
      )}

      {isLoading && <LoadingState message="Cargando carrito…" />}

      {!isLoading && error && <ErrorState message={error} onRetry={retry} />}

      {!isLoading && !error && cart?.articulos.length === 0 && (
        <div className="cart-empty">
          <h2>Tu carrito está vacío</h2>
          <p>Añade algún producto del catálogo para empezar.</p>
          <Link className="primary-link" to="/productos">
            Ver productos
          </Link>
        </div>
      )}

      {!isLoading && !error && cart && cart.articulos.length > 0 && (
        <div className="cart-layout">
          <ul className="cart-items">
            {cart.articulos.map((item) => {
              const product = products[item.producto];

              if (!product) {
                return null;
              }

              return (
                <li key={item.id}>
                  <article className="cart-item">
                    <div className="cart-item-info">
                      <h2>
                        <Link to={`/productos/${product.id}`}>{product.nombre}</Link>
                      </h2>
                      <p>Precio unitario: {formatPrice(product.precio)}</p>
                      <button
                        className="text-button danger-text"
                        disabled={isMutating}
                        onClick={() => void runOperation(() => removeItem(item.id))}
                        type="button"
                      >
                        Eliminar
                      </button>
                    </div>

                    <div className="quantity-control">
                      <span>Cantidad</span>
                      <div>
                        <button
                          aria-label={`Reducir cantidad de ${product.nombre}`}
                          disabled={isMutating || item.cantidad <= 1}
                          onClick={() =>
                            void runOperation(() =>
                              updateQuantity(item.id, item.cantidad - 1),
                            )
                          }
                          type="button"
                        >
                          −
                        </button>
                        <output aria-label={`Cantidad de ${product.nombre}`}>
                          {item.cantidad}
                        </output>
                        <button
                          aria-label={`Aumentar cantidad de ${product.nombre}`}
                          disabled={isMutating || item.cantidad >= product.stock}
                          onClick={() =>
                            void runOperation(() =>
                              updateQuantity(item.id, item.cantidad + 1),
                            )
                          }
                          type="button"
                        >
                          +
                        </button>
                      </div>
                    </div>

                    <div className="cart-item-subtotal">
                      <span>Subtotal</span>
                      <strong>{formatPrice(item.subtotal)}</strong>
                    </div>
                  </article>
                </li>
              );
            })}
          </ul>

          <aside className="cart-summary">
            <h2>Resumen</h2>
            <div>
              <span>Cantidad total</span>
              <strong>{cart.cantidad_total}</strong>
            </div>
            <div className="cart-total">
              <span>Total</span>
              <strong>{formatPrice(cart.total)}</strong>
            </div>
            <p>El checkout se implementará próximamente.</p>
          </aside>
        </div>
      )}
    </section>
  );
}
