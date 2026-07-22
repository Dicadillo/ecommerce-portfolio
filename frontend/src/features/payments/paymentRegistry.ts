import type { Payment } from '../../types/payment';

const paymentIdsByOrder = new Map<number, number>();

export function rememberPayment(payment: Payment) {
  paymentIdsByOrder.set(payment.pedido, payment.id);
}

export function getKnownPaymentId(orderId: number) {
  return paymentIdsByOrder.get(orderId) ?? null;
}

export function forgetPayment(orderId: number) {
  paymentIdsByOrder.delete(orderId);
}

export function clearPaymentRegistry() {
  paymentIdsByOrder.clear();
}
