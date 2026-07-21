import { useState, type FormEvent } from 'react';

import type { LoginCredentials } from '../../types/auth';
import { parseApiError } from '../../utils/apiErrors';

type LoginField = keyof LoginCredentials;

interface LoginFormProps {
  onSubmit: (credentials: LoginCredentials) => Promise<void>;
}

function validate(values: LoginCredentials) {
  const errors: Partial<Record<LoginField, string>> = {};

  if (!values.usuario.trim()) {
    errors.usuario = 'Introduce tu nombre de usuario.';
  }

  if (!values.contrasena) {
    errors.contrasena = 'Introduce tu contraseña.';
  }

  return errors;
}

export function LoginForm({ onSubmit }: LoginFormProps) {
  const [values, setValues] = useState<LoginCredentials>({
    usuario: '',
    contrasena: '',
  });
  const [errors, setErrors] = useState<Partial<Record<LoginField, string>>>({});
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

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
      const parsedError = parseApiError(error, 'No se pudo iniciar sesión.');
      setErrors({
        usuario: parsedError.fieldErrors.usuario,
        contrasena: parsedError.fieldErrors.contrasena,
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
        <label htmlFor="login-usuario">Usuario</label>
        <input
          aria-describedby={errors.usuario ? 'login-usuario-error' : undefined}
          aria-invalid={Boolean(errors.usuario)}
          autoComplete="username"
          id="login-usuario"
          name="usuario"
          onChange={(event) =>
            setValues((current) => ({ ...current, usuario: event.target.value }))
          }
          value={values.usuario}
        />
        {errors.usuario && (
          <span className="field-error" id="login-usuario-error" role="alert">
            {errors.usuario}
          </span>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="login-contrasena">Contraseña</label>
        <input
          aria-describedby={errors.contrasena ? 'login-contrasena-error' : undefined}
          aria-invalid={Boolean(errors.contrasena)}
          autoComplete="current-password"
          id="login-contrasena"
          name="contrasena"
          onChange={(event) =>
            setValues((current) => ({ ...current, contrasena: event.target.value }))
          }
          type="password"
          value={values.contrasena}
        />
        {errors.contrasena && (
          <span className="field-error" id="login-contrasena-error" role="alert">
            {errors.contrasena}
          </span>
        )}
      </div>

      <button className="primary-button" disabled={isSubmitting} type="submit">
        {isSubmitting ? 'Iniciando sesión…' : 'Iniciar sesión'}
      </button>
    </form>
  );
}
