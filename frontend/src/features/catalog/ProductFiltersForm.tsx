import type { FormEvent } from 'react';

import type { Category, ProductOrdering } from '../../types/catalog';

interface ProductFiltersFormProps {
  categories: Category[];
  category: string;
  inStock: boolean;
  onFilterChange: (updates: Record<string, string | null>) => void;
  ordering: string;
  searchTerm: string;
}

export function ProductFiltersForm({
  categories,
  category,
  inStock,
  onFilterChange,
  ordering,
  searchTerm,
}: ProductFiltersFormProps) {
  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const search = String(formData.get('buscar') ?? '').trim();
    onFilterChange({ buscar: search || null });
  }

  return (
    <div className="catalog-controls">
      <form className="catalog-search" onSubmit={handleSearch} role="search">
        <label htmlFor="buscar-productos">Buscar por nombre</label>
        <div className="search-row">
          <input
            defaultValue={searchTerm}
            id="buscar-productos"
            key={searchTerm}
            name="buscar"
            placeholder="Por ejemplo, teclado"
            type="search"
          />
          <button className="primary-button" type="submit">
            Buscar
          </button>
        </div>
      </form>

      <div className="catalog-filter-grid">
        <div className="filter-field">
          <label htmlFor="filtro-categoria">Categoría</label>
          <select
            id="filtro-categoria"
            onChange={(event) =>
              onFilterChange({ categoria: event.target.value || null })
            }
            value={category}
          >
            <option value="">Todas las categorías</option>
            {categories.map((item) => (
              <option key={item.id} value={item.id}>
                {item.nombre}
                {item.activo ? '' : ' (inactiva)'}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-field">
          <label htmlFor="orden-productos">Ordenar</label>
          <select
            id="orden-productos"
            onChange={(event) =>
              onFilterChange({
                ordenar: event.target.value
                  ? (event.target.value as ProductOrdering)
                  : null,
              })
            }
            value={ordering}
          >
            <option value="">Orden predeterminado</option>
            <option value="nombre">Nombre: A–Z</option>
            <option value="-nombre">Nombre: Z–A</option>
            <option value="precio">Precio: menor a mayor</option>
            <option value="-precio">Precio: mayor a menor</option>
          </select>
        </div>

        <label className="checkbox-filter">
          <input
            checked={inStock}
            onChange={(event) =>
              onFilterChange({ con_stock: event.target.checked ? 'true' : null })
            }
            type="checkbox"
          />
          Solo productos con stock
        </label>
      </div>
    </div>
  );
}
