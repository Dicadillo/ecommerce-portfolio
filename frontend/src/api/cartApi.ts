import type { Cart, CartItem } from '../types/cart';
import { apiClient } from './apiClient';

export async function getCart(signal?: AbortSignal) {
  const response = await apiClient.get<Cart>('carrito/', { signal });
  return response.data;
}

export async function addCartItem(productId: number, quantity: number) {
  const response = await apiClient.post<CartItem>('carrito/articulos/', {
    producto: productId,
    cantidad: quantity,
  });
  return response.data;
}

export async function updateCartItem(itemId: number, quantity: number) {
  const response = await apiClient.patch<CartItem>(`carrito/articulos/${itemId}/`, {
    cantidad: quantity,
  });
  return response.data;
}

export async function deleteCartItem(itemId: number) {
  await apiClient.delete(`carrito/articulos/${itemId}/`);
}

export async function clearCart() {
  await apiClient.delete('carrito/vaciar/');
}
