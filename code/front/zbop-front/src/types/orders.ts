// Order types based on OpenAPI specification

export type OrderStatus = 'planned' | 'confirmed' | 'delivered' | 'cancelled';

export interface OrderSummary {
  id: number;
  order_date: string;
  quantity_kg: number;
  status: OrderStatus;
}

export interface OrderCorrectionCreate {
  quantity_increase: number;
  quantity_decrease: number;
  reason?: string;
}

export interface OrderCorrectionResponse {
  id: number;
  original_order_id: number;
  correction_date: string;
  quantity_increase: number;
  quantity_decrease: number;
  correction_cost: number;
  reason?: string;
}

export interface OrderCreate {
  office_id: number;
  distributor_id?: number | null;
  order_date: string;
  delivery_date?: string;
  quantity_kg: number;
  unit_price: number;
  transport_cost: number;
}

export interface OrderResponse {
  id: number;
  optimization_request_id?: number | null;
  office_id: number;
  distributor_id?: number | null;
  order_date: string;
  delivery_date?: string;
  quantity_kg: number;
  unit_price: number;
  transport_cost: number;
  total_cost: number;
  status: OrderStatus;
  created_at: string;
  corrections?: OrderCorrectionResponse[];
}

export interface OrderFilters {
  office_id?: number;
  status?: OrderStatus;
  start_date?: string;  // OpenAPI spec uses start_date, not date_from
  end_date?: string;    // OpenAPI spec uses end_date, not date_to
}
