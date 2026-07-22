import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth';
import { useCart } from '../../hooks/useCart';
import type { Product } from '../../types/catalog';
import { getApiErrorMessage } from '../../utils/apiErrors';

interface AddToCartButtonProps {
  product: Product;
}

export function AddToCartButton({ product }: AddToCartButtonProps) {
  const { isAuthenticated, status } = useAuth();
  const { addProduct, isMutating } = useCart();
  const navigate = useNavigate();
  const [feedback, setFeedback] = useState('');
  const [isError, setIsError] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const isAvailable = product.activo && product.stock > 0;

  async function handleAdd() {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    setFeedback('');
    setIsError(false);
    setIsAdding(true);

    try {
      await addProduct(product);
      setFeedback('Producto añadido al carrito.');
    } catch (error) {
      setFeedback(
        getApiErrorMessage(error, 'No se pudo añadir el producto al carrito.'),
      );
      setIsError(true);
    } finally {
      setIsAdding(false);
    }
  }

  return (
    <div className="add-to-cart-action">
      <button
        className="primary-button"
        disabled={!isAvailable || status === 'loading' || isMutating}
        onClick={handleAdd}
        type="button"
      >
        {!isAvailable ? 'No disponible' : isAdding ? 'Añadiendo…' : 'Añadir al carrito'}
      </button>
      {feedback && (
        <span
          className={isError ? 'action-error' : 'action-success'}
          role={isError ? 'alert' : 'status'}
        >
          {feedback}
        </span>
      )}
    </div>
  );
}
