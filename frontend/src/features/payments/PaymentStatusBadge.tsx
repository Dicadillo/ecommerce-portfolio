import type { PaymentStatus } from '../../types/payment';
import { paymentStatusLabels } from '../../utils/payment';

interface PaymentStatusBadgeProps {
  status: PaymentStatus;
}

export function PaymentStatusBadge({ status }: PaymentStatusBadgeProps) {
  return (
    <span className={`payment-status payment-status-${status}`}>
      {paymentStatusLabels[status]}
    </span>
  );
}
