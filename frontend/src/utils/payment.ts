import type { OrderStatus } from '../types/order';
import type { PaymentStatus } from '../types/payment';

export const paymentStatusLabels: Record<PaymentStatus, string> = {
  pendiente: 'Pendiente',
  aprobado: 'Aprobado',
  rechazado: 'Rechazado',
  reembolsado: 'Reembolsado',
};

export const paymentResultMessages: Record<PaymentStatus, string> = {
  pendiente: 'El pago permanece pendiente de resolución en la pasarela simulada.',
  aprobado: 'El pago simulado ha sido aprobado.',
  rechazado: 'El pago simulado ha sido rechazado.',
  reembolsado: 'El pago ha sido reembolsado y el pedido se ha cancelado.',
};

export function normalizeCardNumber(cardNumber: string) {
  return cardNumber.replace(/[ -]/g, '');
}

export function isValidCardNumber(cardNumber: string) {
  const normalized = normalizeCardNumber(cardNumber);

  if (!/^\d{13,19}$/.test(normalized)) {
    return false;
  }

  const checksum = [...normalized].reverse().reduce((total, character, index) => {
    let digit = Number(character);

    if (index % 2 === 1) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }

    return total + digit;
  }, 0);

  return checksum % 10 === 0;
}

export function isValidExpirationDate(expirationDate: string) {
  const match = /^(0[1-9]|1[0-2])\/(\d{2})$/.exec(expirationDate);

  if (!match) {
    return false;
  }

  const today = new Date();
  const month = Number(match[1]);
  const year = 2000 + Number(match[2]);

  return (
    year > today.getFullYear() ||
    (year === today.getFullYear() && month >= today.getMonth() + 1)
  );
}

export function getOrderStatusAfterPayment(
  currentStatus: OrderStatus,
  paymentStatus: PaymentStatus,
): OrderStatus {
  if (paymentStatus === 'aprobado') {
    return 'confirmado';
  }

  if (paymentStatus === 'reembolsado') {
    return 'cancelado';
  }

  return currentStatus;
}
