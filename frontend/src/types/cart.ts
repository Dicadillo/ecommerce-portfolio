import type { Product } from './catalog';

export interface CartItem {
  id: number;
  producto: number;
  cantidad: number;
  subtotal: string;
}

export interface Cart {
  id: number;
  articulos: CartItem[];
  cantidad_total: number;
  total: string;
}

export type CartProducts = Record<number, Product>;
