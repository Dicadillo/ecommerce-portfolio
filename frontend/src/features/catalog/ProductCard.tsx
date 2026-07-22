import { Link } from 'react-router-dom';

import type { Product } from '../../types/catalog';
import { formatPrice } from '../../utils/catalog';

interface ProductCardProps {
  categoryName: string;
  product: Product;
}

export function ProductCard({ categoryName, product }: ProductCardProps) {
  const isAvailable = product.activo && product.stock > 0;

  return (
    <article className="product-card">
      <div className="product-card-header">
        <p className="product-category">{categoryName}</p>
        <div className="product-badges">
          <span className={`status-badge ${product.activo ? 'active' : 'inactive'}`}>
            {product.activo ? 'Activo' : 'Inactivo'}
          </span>
          {product.stock === 0 && (
            <span className="status-badge out-of-stock">Sin stock</span>
          )}
        </div>
      </div>

      <h2>
        <Link to={`/productos/${product.id}`}>{product.nombre}</Link>
      </h2>
      <p className="product-description">{product.descripcion}</p>

      <div className="product-card-footer">
        <div>
          <p className="product-price">{formatPrice(product.precio)}</p>
          <p className="product-stock">
            {product.stock > 0 ? `${product.stock} unidades disponibles` : 'Sin stock'}
          </p>
        </div>
        <button
          className="primary-button"
          disabled
          title={isAvailable ? 'El carrito se implementará próximamente' : undefined}
          type="button"
        >
          {isAvailable ? 'Añadir próximamente' : 'No disponible'}
        </button>
      </div>
    </article>
  );
}
