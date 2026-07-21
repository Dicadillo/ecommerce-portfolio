import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <section className="placeholder-page">
      <p className="eyebrow">Error 404</p>
      <h1>Página no encontrada</h1>
      <p>La dirección solicitada no existe.</p>
      <Link className="primary-link" to="/">
        Volver al inicio
      </Link>
    </section>
  );
}
