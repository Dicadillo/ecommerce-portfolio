export interface Category {
  id: number;
  nombre: string;
  slug: string;
  activo: boolean;
  creado_en: string;
  actualizado_en: string;
}

export interface Product {
  id: number;
  categoria: number;
  nombre: string;
  slug: string;
  descripcion: string;
  precio: string;
  stock: number;
  activo: boolean;
  creado_en: string;
  actualizado_en: string;
}

export interface PaginatedResponse<T> {
  conteo: number;
  siguiente: string | null;
  anterior: string | null;
  resultados: T[];
}

export interface ProductFilters {
  buscar?: string;
  categoria?: number;
  con_stock?: true;
  ordenar?: ProductOrdering;
  pagina?: number;
}

export type ProductOrdering = 'nombre' | '-nombre' | 'precio' | '-precio';
