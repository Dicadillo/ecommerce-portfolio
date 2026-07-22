import { useState, type FormEvent } from 'react';

import type { PaymentData } from '../../types/payment';
import { getApiErrorMessage, parseApiError } from '../../utils/apiErrors';
import {
  isValidCardNumber,
  isValidExpirationDate,
  normalizeCardNumber,
} from '../../utils/payment';

type PaymentFormValues = Omit<PaymentData, 'pedido'>;
type PaymentField = keyof PaymentFormValues;

interface PaymentFormProps {
  onSubmit: (data: PaymentData) => Promise<void>;
  orderId: number;
}

const initialValues: PaymentFormValues = {
  numero_tarjeta: '',
  titular: '',
  fecha_expiracion: '',
  cvv: '',
};

function validate(values: PaymentFormValues) {
  const errors: Partial<Record<PaymentField, string>> = {};

  if (!isValidCardNumber(values.numero_tarjeta)) {
    errors.numero_tarjeta = 'Introduce un número de tarjeta válido.';
  }

  if (!values.titular.trim()) {
    errors.titular = 'Introduce el nombre del titular.';
  }

  if (!isValidExpirationDate(values.fecha_expiracion)) {
    errors.fecha_expiracion = 'Introduce una fecha válida con formato MM/AA.';
  }

  if (!/^\d{3,4}$/.test(values.cvv)) {
    errors.cvv = 'El CVV debe tener tres o cuatro dígitos.';
  }

  return errors;
}

export function PaymentForm({ onSubmit, orderId }: PaymentFormProps) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState<Partial<Record<PaymentField, string>>>({});
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  function updateField(field: PaymentField, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
    setErrors((current) => ({ ...current, [field]: undefined }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setServerError('');

    const validationErrors = validate(values);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);

    try {
      await onSubmit({
        ...values,
        pedido: orderId,
        numero_tarjeta: normalizeCardNumber(values.numero_tarjeta),
      });
    } catch (error) {
      const parsedError = parseApiError(error, 'No se pudo procesar el pago.');
      setErrors({
        numero_tarjeta: parsedError.fieldErrors.numero_tarjeta,
        titular: parsedError.fieldErrors.titular,
        fecha_expiracion: parsedError.fieldErrors.fecha_expiracion,
        cvv: parsedError.fieldErrors.cvv,
      });
      setServerError(getApiErrorMessage(error, 'No se pudo procesar el pago.'));
    } finally {
      setValues((current) => ({ ...current, numero_tarjeta: '', cvv: '' }));
      setIsSubmitting(false);
    }
  }

  return (
    <form className="payment-form" noValidate onSubmit={handleSubmit}>
      <header>
        <h2>Datos de pago simulado</h2>
        <p>No introduzcas datos de una tarjeta real.</p>
      </header>

      {serverError && (
        <div className="form-banner form-banner-error" role="alert">
          {serverError}
        </div>
      )}

      <div className="form-field">
        <label htmlFor="payment-card-number">Número de tarjeta</label>
        <input
          aria-describedby={
            errors.numero_tarjeta ? 'payment-card-number-error' : undefined
          }
          aria-invalid={Boolean(errors.numero_tarjeta)}
          autoComplete="cc-number"
          id="payment-card-number"
          inputMode="numeric"
          maxLength={25}
          onChange={(event) => updateField('numero_tarjeta', event.target.value)}
          placeholder="4111 1111 1111 1111"
          value={values.numero_tarjeta}
        />
        {errors.numero_tarjeta && (
          <span className="field-error" id="payment-card-number-error" role="alert">
            {errors.numero_tarjeta}
          </span>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="payment-cardholder">Titular</label>
        <input
          aria-describedby={errors.titular ? 'payment-cardholder-error' : undefined}
          aria-invalid={Boolean(errors.titular)}
          autoComplete="cc-name"
          id="payment-cardholder"
          maxLength={200}
          onChange={(event) => updateField('titular', event.target.value)}
          value={values.titular}
        />
        {errors.titular && (
          <span className="field-error" id="payment-cardholder-error" role="alert">
            {errors.titular}
          </span>
        )}
      </div>

      <div className="payment-form-row">
        <div className="form-field">
          <label htmlFor="payment-expiration">Fecha de expiración</label>
          <input
            aria-describedby={
              errors.fecha_expiracion ? 'payment-expiration-error' : undefined
            }
            aria-invalid={Boolean(errors.fecha_expiracion)}
            autoComplete="cc-exp"
            id="payment-expiration"
            inputMode="numeric"
            maxLength={5}
            onChange={(event) => updateField('fecha_expiracion', event.target.value)}
            placeholder="MM/AA"
            value={values.fecha_expiracion}
          />
          {errors.fecha_expiracion && (
            <span className="field-error" id="payment-expiration-error" role="alert">
              {errors.fecha_expiracion}
            </span>
          )}
        </div>

        <div className="form-field">
          <label htmlFor="payment-cvv">CVV</label>
          <input
            aria-describedby={errors.cvv ? 'payment-cvv-error' : undefined}
            aria-invalid={Boolean(errors.cvv)}
            autoComplete="cc-csc"
            id="payment-cvv"
            inputMode="numeric"
            maxLength={4}
            onChange={(event) => updateField('cvv', event.target.value)}
            type="password"
            value={values.cvv}
          />
          {errors.cvv && (
            <span className="field-error" id="payment-cvv-error" role="alert">
              {errors.cvv}
            </span>
          )}
        </div>
      </div>

      <div className="simulated-cards" aria-label="Tarjetas de prueba">
        <strong>Escenarios disponibles</strong>
        <span>4111111111111111: aprobado</span>
        <span>4000000000000002: rechazado</span>
        <span>Otra tarjeta válida: pendiente</span>
      </div>

      <button className="primary-button" disabled={isSubmitting} type="submit">
        {isSubmitting ? 'Procesando pago…' : 'Pagar pedido'}
      </button>
    </form>
  );
}
