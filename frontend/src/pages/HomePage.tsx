import { Link } from 'react-router-dom';

export function HomePage() {
  return (
    <section className="hero">
      <p className="eyebrow">Ecommerce de demostración</p>
      <h1>Una base preparada para crecer</h1>
      <p>
        El frontend ya dispone de navegación, pruebas y un cliente centralizado para
        consumir la API REST.
      </p>
      <Link className="primary-link" to="/productos">
        Ver productos
      </Link>
    </section>
  );
}
