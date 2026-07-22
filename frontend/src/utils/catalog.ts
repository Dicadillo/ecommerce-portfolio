import type { ProductFilters, ProductOrdering } from '../types/catalog';

const validOrderings = new Set<ProductOrdering>([
  'nombre',
  '-nombre',
  'precio',
  '-precio',
]);

function positiveInteger(value: string | null) {
  if (!value) {
    return undefined;
  }

  const parsedValue = Number.parseInt(value, 10);
  return parsedValue > 0 ? parsedValue : undefined;
}

export function filtersFromSearchParams(searchParams: URLSearchParams): ProductFilters {
  const search = searchParams.get('buscar')?.trim();
  const category = positiveInteger(searchParams.get('categoria'));
  const page = positiveInteger(searchParams.get('pagina'));
  const requestedOrdering = searchParams.get('ordenar') as ProductOrdering | null;
  const ordering =
    requestedOrdering && validOrderings.has(requestedOrdering)
      ? requestedOrdering
      : undefined;

  return {
    ...(search ? { buscar: search } : {}),
    ...(category ? { categoria: category } : {}),
    ...(searchParams.get('con_stock') === 'true' ? { con_stock: true } : {}),
    ...(ordering ? { ordenar: ordering } : {}),
    ...(page && page > 1 ? { pagina: page } : {}),
  };
}

export function formatPrice(price: string) {
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'EUR',
  }).format(Number(price));
}
