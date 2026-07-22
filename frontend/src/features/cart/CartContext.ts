import { createContext } from 'react';

import type { Cart, CartProducts } from '../../types/cart';
import type { Product } from '../../types/catalog';

export interface CartContextValue {
  addProduct: (product: Product, quantity?: number) => Promise<void>;
  cart: Cart | null;
  clear: () => Promise<void>;
  error: string;
  isLoading: boolean;
  isMutating: boolean;
  itemCount: number;
  products: CartProducts;
  removeItem: (itemId: number) => Promise<void>;
  retry: () => void;
  updateQuantity: (itemId: number, quantity: number) => Promise<void>;
}

export const CartContext = createContext<CartContextValue | null>(null);
