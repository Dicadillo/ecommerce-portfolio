import type {
  Category,
  PaginatedResponse,
  Product,
  ProductFilters,
} from '../types/catalog';
import { publicApiClient } from './apiClient';

export async function getCategories(signal?: AbortSignal) {
  const response = await publicApiClient.get<PaginatedResponse<Category>>(
    'categorias/',
    {
      params: { tamano_pagina: 100 },
      signal,
    },
  );
  return response.data;
}

export async function getCategory(id: number, signal?: AbortSignal) {
  const response = await publicApiClient.get<Category>(`categorias/${id}/`, {
    signal,
  });
  return response.data;
}

export async function getProducts(filters: ProductFilters, signal?: AbortSignal) {
  const response = await publicApiClient.get<PaginatedResponse<Product>>('productos/', {
    params: filters,
    signal,
  });
  return response.data;
}

export async function getProduct(id: number, signal?: AbortSignal) {
  const response = await publicApiClient.get<Product>(`productos/${id}/`, {
    signal,
  });
  return response.data;
}
