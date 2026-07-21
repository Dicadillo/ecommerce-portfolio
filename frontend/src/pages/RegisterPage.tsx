import { Navigate, Link, useNavigate } from 'react-router-dom';

import { RegisterForm } from '../features/auth/RegisterForm';
import { useAuth } from '../hooks/useAuth';
import type { RegistrationData } from '../types/auth';

export function RegisterPage() {
  const { isAuthenticated, register, status } = useAuth();
  const navigate = useNavigate();

  if (status === 'loading') {
    return <p role="status">Comprobando la sesión…</p>;
  }

  if (isAuthenticated) {
    return <Navigate replace to="/productos" />;
  }

  async function handleRegistration(data: RegistrationData) {
    await register(data);
    navigate('/login', {
      replace: true,
      state: { registrationSuccessful: true },
    });
  }

  return (
    <section className="auth-page">
      <p className="eyebrow">Nueva cuenta</p>
      <h1>Crear una cuenta</h1>
      <p>Regístrate para preparar tu carrito y consultar tus pedidos.</p>
      <RegisterForm onSubmit={handleRegistration} />
      <p className="auth-alternative">
        ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
      </p>
    </section>
  );
}
