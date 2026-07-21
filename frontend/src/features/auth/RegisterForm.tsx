import { useState, type FormEvent } from 'react';

import type { RegistrationData } from '../../types/auth';
import { parseApiError } from '../../utils/apiErrors';

type RegistrationField = keyof RegistrationData;

interface RegisterFormProps {
  onSubmit: (data: RegistrationData) => Promise<void>;
}

const initialValues: RegistrationData = {
  usuario: '',
  correo: '',
  contrasena: '',
  confirmacion_contrasena: '',
};

function validate(values: RegistrationData) {
  const errors: Partial<Record<RegistrationField, string>> = {};

  if (!values.usuario.trim()) {
    errors.usuario = 'Introduce un nombre de usuario.';
  }

  if (!values.correo.trim()) {
    errors.correo = 'Introduce un correo electrónico.';
  } else if (!/^\S+@\S+\.\S+$/.test(values.correo)) {
    errors.correo = 'Introduce un correo electrónico válido.';
  }

  if (!values.contrasena) {
    errors.contrasena = 'Introduce una contraseña.';
  }

  if (!values.confirmacion_contrasena) {
    errors.confirmacion_contrasena = 'Confirma tu contraseña.';
  } else if (values.contrasena !== values.confirmacion_contrasena) {
    errors.confirmacion_contrasena = 'Las contraseñas no coinciden.';
  }

  return errors;
}

export function RegisterForm({ onSubmit }: RegisterFormProps) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState<Partial<Record<RegistrationField, string>>>({});
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  function updateField(field: RegistrationField, value: string) {
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
      const parsedError = parseApiError(error, 'No se pudo completar el registro.');
      setErrors({
        usuario: parsedError.fieldErrors.usuario,
        correo: parsedError.fieldErrors.correo,
        contrasena: parsedError.fieldErrors.contrasena,
        confirmacion_contrasena: parsedError.fieldErrors.confirmacion_contrasena,
      });
      setServerError(parsedError.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="auth-form" noValidate onSubmit={handleSubmit}>
      {serverError && (
        <div className="form-banner form-banner-error" role="alert">
          {serverError}
        </div>
      )}

      <div className="form-field">
        <label htmlFor="registro-usuario">Usuario</label>
        <input
          aria-describedby={errors.usuario ? 'registro-usuario-error' : undefined}
          aria-invalid={Boolean(errors.usuario)}
          autoComplete="username"
          id="registro-usuario"
          onChange={(event) => updateField('usuario', event.target.value)}
          value={values.usuario}
        />
        {errors.usuario && (
          <span className="field-error" id="registro-usuario-error" role="alert">
            {errors.usuario}
          </span>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="registro-correo">Correo electrónico</label>
        <input
          aria-describedby={errors.correo ? 'registro-correo-error' : undefined}
          aria-invalid={Boolean(errors.correo)}
          autoComplete="email"
          id="registro-correo"
          onChange={(event) => updateField('correo', event.target.value)}
          type="email"
          value={values.correo}
        />
        {errors.correo && (
          <span className="field-error" id="registro-correo-error" role="alert">
            {errors.correo}
          </span>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="registro-contrasena">Contraseña</label>
        <input
          aria-describedby={errors.contrasena ? 'registro-contrasena-error' : undefined}
          aria-invalid={Boolean(errors.contrasena)}
          autoComplete="new-password"
          id="registro-contrasena"
          onChange={(event) => updateField('contrasena', event.target.value)}
          type="password"
          value={values.contrasena}
        />
        {errors.contrasena && (
          <span className="field-error" id="registro-contrasena-error" role="alert">
            {errors.contrasena}
          </span>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="registro-confirmacion">Confirmar contraseña</label>
        <input
          aria-describedby={
            errors.confirmacion_contrasena ? 'registro-confirmacion-error' : undefined
          }
          aria-invalid={Boolean(errors.confirmacion_contrasena)}
          autoComplete="new-password"
          id="registro-confirmacion"
          onChange={(event) =>
            updateField('confirmacion_contrasena', event.target.value)
          }
          type="password"
          value={values.confirmacion_contrasena}
        />
        {errors.confirmacion_contrasena && (
          <span className="field-error" id="registro-confirmacion-error" role="alert">
            {errors.confirmacion_contrasena}
          </span>
        )}
      </div>

      <button className="primary-button" disabled={isSubmitting} type="submit">
        {isSubmitting ? 'Creando cuenta…' : 'Crear cuenta'}
      </button>
    </form>
  );
}
