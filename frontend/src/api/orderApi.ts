import type { CheckoutData, Order } from '../types/order';
import { apiClient } from './apiClient';

export async function createOrder(data: CheckoutData) {
  const response = await apiClient.post<Order>('pedidos/', data);
  return response.data;
}

export async function getOrders(signal?: AbortSignal) {
  const response = await apiClient.get<Order[]>('pedidos/', { signal });
  return response.data;
}

export async function getOrder(id: number, signal?: AbortSignal) {
  const response = await apiClient.get<Order>(`pedidos/${id}/`, { signal });
  return response.data;
}

export async function cancelOrder(id: number) {
  const response = await apiClient.post<Order>(`pedidos/${id}/cancelar/`);
  return response.data;
}
