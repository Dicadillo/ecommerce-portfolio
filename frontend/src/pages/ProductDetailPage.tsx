import axios from 'axios';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import { getCategory, getProduct } from '../api/catalogApi';
import { ErrorState, LoadingState } from '../features/catalog/CatalogState';
import type { Category, Product } from '../types/catalog';
import { formatPrice } from '../utils/catalog';
import { parseApiError } from '../utils/apiErrors';

type DetailStatus = 'loading' | 'ready' | 'not-found' | 'error';

interface DetailRequestState {
  category: Category | null;
  error: string;
  key: string;
  product: Product | null;
  status: DetailStatus;
}

export function ProductDetailPage() {
  const { id } = useParams();
  const productId = Number.parseInt(id ?? '', 10);
  const [retry, setRetry] = useState(0);
  const isValidProductId = Number.isInteger(productId) && productId > 0;
  const requestKey = `${productId}:${retry}`;
  const [detailRequest, setDetailRequest] = useState<DetailRequestState>({
    category: null,
    error: '',
    key: requestKey,
    product: null,
    status: 'loading',
  });
  const currentRequest =
    detailRequest.key === requestKey
      ? detailRequest
      : {
          category: null,
          error: '',
          key: requestKey,
          product: null,
          status: 'loading' as const,
        };
  const status = isValidProductId ? currentRequest.status : 'not-found';
  const { category, error, product } = currentRequest;

  useEffect(() => {
    const controller = new AbortController();

    if (!isValidProductId) {
      return () => controller.abort();
    }

    void getProduct(productId, controller.signal)
      .then(async (productResponse) => {
        const categoryResponse = await getCategory(
          productResponse.categoria,
          controller.signal,
        );

        setDetailRequest({
          category: categoryResponse,
          error: '',
          key: requestKey,
          product: productResponse,
          status: 'ready',
        });
      })
      .catch((requestError: unknown) => {
        if (controller.signal.aborted) {
          return;
        }

        if (axios.isAxiosError(requestError) && requestError.response?.status === 404) {
          setDetailRequest({
            category: null,
            error: '',
            key: requestKey,
            product: null,
            status: 'not-found',
          });
          return;
        }

        setDetailRequest({
          category: null,
          error: parseApiError(requestError, 'No se pudo cargar el producto.').message,
          key: requestKey,
          product: null,
          status: 'error',
        });
      });

    return () => controller.abort();
  }, [isValidProductId, productId, requestKey]);

  if (status === 'loading') {
    return <LoadingState message="Cargando producto…" />;
  }

  if (status === 'not-found') {
    return (
      <section className="catalog-state">
        <p className="eyebrow">Catálogo</p>
        <h1>Producto no encontrado</h1>
        <p>El producto solicitado no existe o ya no está disponible.</p>
        <Link className="primary-link" to="/productos">
          Volver a productos
        </Link>
      </section>
    );
  }

  if (status === 'error') {
    return (
      <ErrorState message={error} onRetry={() => setRetry((value) => value + 1)} />
    );
  }

  if (!product || !category) {
    return null;
  }

  const isAvailable = product.activo && product.stock > 0;

  return (
    <article className="product-detail">
      <Link className="back-link" to="/productos">
        ← Volver a productos
      </Link>

      <div className="product-detail-content">
        <div>
          <p className="product-category">{category.nombre}</p>
          <div className="product-badges">
            <span className={`status-badge ${product.activo ? 'active' : 'inactive'}`}>
              {product.activo ? 'Activo' : 'Inactivo'}
            </span>
            {product.stock === 0 && (
              <span className="status-badge out-of-stock">Sin stock</span>
            )}
          </div>
          <h1>{product.nombre}</h1>
          <p className="product-detail-description">{product.descripcion}</p>
        </div>

        <aside className="purchase-panel">
          <p className="product-price">{formatPrice(product.precio)}</p>
          <p className="product-stock">
            {product.stock > 0
              ? `${product.stock} unidades disponibles`
              : 'Sin stock disponible'}
          </p>
          {!product.activo && (
            <p className="availability-warning">
              Este producto no está disponible actualmente.
            </p>
          )}
          <button className="primary-button" disabled type="button">
            {isAvailable ? 'Añadir al carrito próximamente' : 'No disponible'}
          </button>
        </aside>
      </div>
    </article>
  );
}
