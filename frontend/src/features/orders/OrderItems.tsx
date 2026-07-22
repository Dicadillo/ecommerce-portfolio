import type { OrderItem } from '../../types/order';
import { formatPrice } from '../../utils/catalog';

interface OrderItemsProps {
  items: OrderItem[];
}

export function OrderItems({ items }: OrderItemsProps) {
  return (
    <ul className="order-items">
      {items.map((item) => (
        <li key={item.id}>
          <div>
            <strong>{item.nombre_producto}</strong>
            <span>
              {formatPrice(item.precio_unitario)} × {item.cantidad}
            </span>
          </div>
          <strong>{formatPrice(item.subtotal)}</strong>
        </li>
      ))}
    </ul>
  );
}
