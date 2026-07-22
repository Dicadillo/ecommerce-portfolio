import { use } from 'react';

import { CartContext } from '../features/cart/CartContext';

export function useCart() {
  const context = use(CartContext);

  if (!context) {
    throw new Error('useCart debe utilizarse dentro de CartProvider.');
  }

  return context;
}
