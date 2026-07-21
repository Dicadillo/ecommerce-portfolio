import { Navigate, Link, useLocation, useNavigate } from 'react-router-dom';

import { LoginForm } from '../features/auth/LoginForm';
import { useAuth } from '../hooks/useAuth';
import type { LoginCredentials } from '../types/auth';

interface LoginLocationState {
  registrationSuccessful?: boolean;
}

export function LoginPage() {
  const { isAuthenticated, login, status } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const locationState = location.state as LoginLocationState | null;

  if (status === 'loading') {
    return <p role="status">Comprobando la sesión…</p>;
  }

  if (isAuthenticated) {
    return <Navigate replace to="/productos" />;
  }

  async function handleLogin(credentials: LoginCredentials) {
    await login(credentials);
    navigate('/productos', { replace: true });
  }

  return (
    <section className="auth-page">
      <p className="eyebrow">Tu cuenta</p>
      <h1>Iniciar sesión</h1>
      <p>Accede para consultar tu carrito y tus pedidos.</p>

      {locationState?.registrationSuccessful && (
        <div className="form-banner form-banner-success" role="status">
          Tu cuenta se ha creado. Ya puedes iniciar sesión.
        </div>
      )}

      <LoginForm onSubmit={handleLogin} />
      <p className="auth-alternative">
        ¿Todavía no tienes cuenta? <Link to="/registro">Regístrate</Link>
      </p>
    </section>
  );
}
