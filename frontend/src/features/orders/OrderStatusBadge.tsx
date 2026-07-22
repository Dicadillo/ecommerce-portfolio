import type { OrderStatus } from '../../types/order';
import { orderStatusLabels } from '../../utils/order';

interface OrderStatusBadgeProps {
  status: OrderStatus;
}

export function OrderStatusBadge({ status }: OrderStatusBadgeProps) {
  return (
    <span className={`order-status order-status-${status}`}>
      {orderStatusLabels[status]}
    </span>
  );
}
