import { useState, type FormEvent } from 'react';

import type { CheckoutData } from '../../types/order';
import { getApiErrorMessage, parseApiError } from '../../utils/apiErrors';

type CheckoutField = keyof CheckoutData;

interface CheckoutFormProps {
  onSubmit: (data: CheckoutData) => Promise<void>;
}

const initialValues: CheckoutData = {
  nombre_destinatario: '',
  direccion: '',
  ciudad: '',
  codigo_postal: '',
  pais: '',
};

const fieldLabels: Record<CheckoutField, string> = {
  nombre_destinatario: 'Nombre del destinatario',
  direccion: 'Dirección',
  ciudad: 'Ciudad',
  codigo_postal: 'Código postal',
  pais: 'País',
};

function validate(values: CheckoutData) {
  return Object.fromEntries(
    Object.entries(values).flatMap(([field, value]) =>
      value.trim()
        ? []
        : [[field, `Introduce ${fieldLabels[field as CheckoutField].toLowerCase()}.`]],
    ),
  ) as Partial<Record<CheckoutField, string>>;
}

export function CheckoutForm({ onSubmit }: CheckoutFormProps) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState<Partial<Record<CheckoutField, string>>>({});
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  function updateField(field: CheckoutField, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
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
      await onSubmit(values);
    } catch (error) {
      const parsedError = parseApiError(error, 'No se pudo crear el pedido.');
      setErrors({
        nombre_destinatario: parsedError.fieldErrors.nombre_destinatario,
        direccion: parsedError.fieldErrors.direccion,
        ciudad: parsedError.fieldErrors.ciudad,
        codigo_postal: parsedError.fieldErrors.codigo_postal,
        pais: parsedError.fieldErrors.pais,
      });
      setServerError(getApiErrorMessage(error, 'No se pudo crear el pedido.'));
    } finally {
      setIsSubmitting(false);
    }
  }

  const fields: Array<{
    autoComplete: string;
    field: CheckoutField;
  }> = [
    { field: 'nombre_destinatario', autoComplete: 'name' },
    { field: 'direccion', autoComplete: 'street-address' },
    { field: 'ciudad', autoComplete: 'address-level2' },
    { field: 'codigo_postal', autoComplete: 'postal-code' },
    { field: 'pais', autoComplete: 'country-name' },
  ];

  return (
    <form className="checkout-form" noValidate onSubmit={handleSubmit}>
      {serverError && (
        <div className="form-banner form-banner-error" role="alert">
          {serverError}
        </div>
      )}

      {fields.map(({ autoComplete, field }) => (
        <div className="form-field" key={field}>
          <label htmlFor={`checkout-${field}`}>{fieldLabels[field]}</label>
          <input
            aria-describedby={errors[field] ? `checkout-${field}-error` : undefined}
            aria-invalid={Boolean(errors[field])}
            autoComplete={autoComplete}
            id={`checkout-${field}`}
            onChange={(event) => updateField(field, event.target.value)}
            value={values[field]}
          />
          {errors[field] && (
            <span className="field-error" id={`checkout-${field}-error`} role="alert">
              {errors[field]}
            </span>
          )}
        </div>
      ))}

      <button className="primary-button" disabled={isSubmitting} type="submit">
        {isSubmitting ? 'Creando pedido…' : 'Confirmar pedido'}
      </button>
    </form>
  );
}
