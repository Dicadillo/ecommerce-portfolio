import type { Payment } from '../../types/payment';
import { formatPrice } from '../../utils/catalog';
import { formatOrderDate } from '../../utils/order';
import { paymentResultMessages } from '../../utils/payment';
import { PaymentStatusBadge } from './PaymentStatusBadge';

interface PaymentDetailsProps {
  payment: Payment;
}

export function PaymentDetails({ payment }: PaymentDetailsProps) {
  return (
    <div className={`payment-result payment-result-${payment.estado}`}>
      <header>
        <div>
          <p className="eyebrow">Resultado del pago</p>
          <h2>Pago #{payment.id}</h2>
        </div>
        <PaymentStatusBadge status={payment.estado} />
      </header>

      <p>{paymentResultMessages[payment.estado]}</p>

      <dl className="payment-metadata">
        <div>
          <dt>Importe</dt>
          <dd>{formatPrice(payment.importe)}</dd>
        </div>
        <div>
          <dt>Referencia</dt>
          <dd>{payment.referencia}</dd>
        </div>
        <div>
          <dt>Proveedor</dt>
          <dd>{payment.proveedor}</dd>
        </div>
        {payment.ultimos_cuatro && (
          <div>
            <dt>Tarjeta</dt>
            <dd>Terminada en {payment.ultimos_cuatro}</dd>
          </div>
        )}
        <div>
          <dt>Fecha</dt>
          <dd>
            <time dateTime={payment.fecha_creacion}>
              {formatOrderDate(payment.fecha_creacion)}
            </time>
          </dd>
        </div>
      </dl>
    </div>
  );
}
