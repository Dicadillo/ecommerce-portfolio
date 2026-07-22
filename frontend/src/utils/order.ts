import type { OrderStatus } from '../types/order';

export const orderStatusLabels: Record<OrderStatus, string> = {
  pendiente: 'Pendiente',
  confirmado: 'Confirmado',
  enviado: 'Enviado',
  entregado: 'Entregado',
  cancelado: 'Cancelado',
};

export function formatOrderDate(date: string) {
  return new Intl.DateTimeFormat('es-ES', {
    dateStyle: 'long',
    timeStyle: 'short',
  }).format(new Date(date));
}

export function isCancelableStatus(status: OrderStatus) {
  return status === 'pendiente' || status === 'confirmado';
}
