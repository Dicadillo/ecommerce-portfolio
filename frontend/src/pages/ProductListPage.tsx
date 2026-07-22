import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { getCategories, getProducts } from '../api/catalogApi';
import { ErrorState, LoadingState } from '../features/catalog/CatalogState';
import { ProductCard } from '../features/catalog/ProductCard';
import { ProductFiltersForm } from '../features/catalog/ProductFiltersForm';
import type { Category, PaginatedResponse, Product } from '../types/catalog';
import { filtersFromSearchParams } from '../utils/catalog';
import { parseApiError } from '../utils/apiErrors';

const emptyPage: PaginatedResponse<Product> = {
  conteo: 0,
  siguiente: null,
  anterior: null,
  resultados: [],
};

interface ProductsRequestState {
  data: PaginatedResponse<Product>;
  error: string;
  key: string;
  status: 'loading' | 'ready' | 'error';
}

export function ProductListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesError, setCategoriesError] = useState('');
  const [categoriesRetry, setCategoriesRetry] = useState(0);
  const [productsRetry, setProductsRetry] = useState(0);

  const productQuery = searchParams.toString();
  const searchTerm = searchParams.get('buscar') ?? '';
  const category = searchParams.get('categoria') ?? '';
  const inStock = searchParams.get('con_stock') === 'true';
  const ordering = searchParams.get('ordenar') ?? '';
  const currentPage = Number.parseInt(searchParams.get('pagina') ?? '1', 10) || 1;
  const requestKey = `${productQuery}:${productsRetry}`;
  const [productsRequest, setProductsRequest] = useState<ProductsRequestState>({
    data: emptyPage,
    error: '',
    key: requestKey,
    status: 'loading',
  });
  const currentRequest =
    productsRequest.key === requestKey
      ? productsRequest
      : { data: emptyPage, error: '', key: requestKey, status: 'loading' as const };
  const products = currentRequest.data;
  const error = currentRequest.error;
  const isLoading = currentRequest.status === 'loading';

  useEffect(() => {
    const controller = new AbortController();

    void getCategories(controller.signal)
      .then((response) => setCategories(response.resultados))
      .catch((requestError: unknown) => {
        if (!controller.signal.aborted) {
          setCategoriesError(
            parseApiError(requestError, 'No se pudieron cargar las categorías.')
              .message,
          );
        }
      });

    return () => controller.abort();
  }, [categoriesRetry]);

  useEffect(() => {
    const controller = new AbortController();

    void getProducts(
      filtersFromSearchParams(new URLSearchParams(productQuery)),
      controller.signal,
    )
      .then((response) => {
        setProductsRequest({
          data: response,
          error: '',
          key: requestKey,
          status: 'ready',
        });
      })
      .catch((requestError: unknown) => {
        if (!controller.signal.aborted) {
          setProductsRequest({
            data: emptyPage,
            error: parseApiError(requestError, 'No se pudieron cargar los productos.')
              .message,
            key: requestKey,
            status: 'error',
          });
        }
      });

    return () => controller.abort();
  }, [productQuery, productsRetry, requestKey]);

  function updateFilters(updates: Record<string, string | null>) {
    setSearchParams((current) => {
      const next = new URLSearchParams(current);

      Object.entries(updates).forEach(([key, value]) => {
        if (value) {
          next.set(key, value);
        } else {
          next.delete(key);
        }
      });

      next.delete('pagina');
      return next;
    });
  }

  function changePage(page: number) {
    setSearchParams((current) => {
      const next = new URLSearchParams(current);

      if (page > 1) {
        next.set('pagina', String(page));
      } else {
        next.delete('pagina');
      }

      return next;
    });
  }

  function retryCategories() {
    setCategoriesError('');
    setCategoriesRetry((value) => value + 1);
  }

  const categoryNames = new Map(
    categories.map((item) => [item.id, item.nombre] as const),
  );

  return (
    <section className="catalog-page">
      <header className="catalog-heading">
        <div>
          <p className="eyebrow">Catálogo</p>
          <h1>Productos</h1>
        </div>
        {!isLoading && !error && (
          <p className="result-count">
            {products.conteo} {products.conteo === 1 ? 'producto' : 'productos'}
          </p>
        )}
      </header>

      <ProductFiltersForm
        categories={categories}
        category={category}
        inStock={inStock}
        onFilterChange={updateFilters}
        ordering={ordering}
        searchTerm={searchTerm}
      />

      {categoriesError && (
        <div className="inline-error" role="alert">
          <span>{categoriesError}</span>
          <button onClick={retryCategories} type="button">
            Reintentar categorías
          </button>
        </div>
      )}

      {isLoading && <LoadingState message="Cargando productos…" />}

      {!isLoading && error && (
        <ErrorState
          message={error}
          onRetry={() => setProductsRetry((value) => value + 1)}
        />
      )}

      {!isLoading && !error && products.resultados.length === 0 && (
        <div className="catalog-state">
          <h2>No hay productos</h2>
          <p>Prueba a cambiar la búsqueda o los filtros seleccionados.</p>
        </div>
      )}

      {!isLoading && !error && products.resultados.length > 0 && (
        <>
          <ul className="product-grid">
            {products.resultados.map((product) => (
              <li key={product.id}>
                <ProductCard
                  categoryName={
                    categoryNames.get(product.categoria) ??
                    `Categoría ${product.categoria}`
                  }
                  product={product}
                />
              </li>
            ))}
          </ul>

          <nav aria-label="Paginación de productos" className="pagination">
            <button
              className="secondary-button"
              disabled={!products.anterior}
              onClick={() => changePage(Math.max(1, currentPage - 1))}
              type="button"
            >
              Anterior
            </button>
            <span>Página {currentPage}</span>
            <button
              className="secondary-button"
              disabled={!products.siguiente}
              onClick={() => changePage(currentPage + 1)}
              type="button"
            >
              Siguiente
            </button>
          </nav>
        </>
      )}
    </section>
  );
}
