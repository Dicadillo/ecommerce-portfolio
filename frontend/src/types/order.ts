export type OrderStatus =
  'pendiente' | 'confirmado' | 'enviado' | 'entregado' | 'cancelado';

export interface OrderItem {
  id: number;
  producto: number | null;
  nombre_producto: string;
  precio_unitario: string;
  cantidad: number;
  subtotal: string;
}

export interface Order {
  id: number;
  estado: OrderStatus;
  nombre_destinatario: string;
  direccion: string;
  ciudad: string;
  codigo_postal: string;
  pais: string;
  total: string;
  fecha_creacion: string;
  fecha_actualizacion: string;
  articulos: OrderItem[];
}

export interface CheckoutData {
  nombre_destinatario: string;
  direccion: string;
  ciudad: string;
  codigo_postal: string;
  pais: string;
}
