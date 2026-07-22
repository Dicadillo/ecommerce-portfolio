import type { Payment, PaymentData } from '../types/payment';
import { apiClient } from './apiClient';

export async function createPayment(data: PaymentData) {
  const response = await apiClient.post<Payment>('pagos/', data);
  return response.data;
}

export async function getPayment(id: number, signal?: AbortSignal) {
  const response = await apiClient.get<Payment>(`pagos/${id}/`, { signal });
  return response.data;
}

export async function refundPayment(id: number) {
  const response = await apiClient.post<Payment>(`pagos/${id}/reembolsar/`);
  return response.data;
}
