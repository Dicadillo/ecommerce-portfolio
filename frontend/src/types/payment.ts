export type PaymentStatus = 'pendiente' | 'aprobado' | 'rechazado' | 'reembolsado';

export interface Payment {
  id: number;
  pedido: number;
  estado: PaymentStatus;
  importe: string;
  referencia: string;
  proveedor: string;
  ultimos_cuatro?: string;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export interface PaymentData {
  pedido: number;
  numero_tarjeta: string;
  titular: string;
  fecha_expiracion: string;
  cvv: string;
}
