// Orders Service

import { api } from './api';
import { API_ENDPOINTS } from '../config/api';
import { 
  OrderResponse, 
  OrderCreate, 
  OrderFilters, 
  OrderCorrectionCreate, 
  OrderCorrectionResponse,
  OrderStatus 
} from '../types';

export const ordersService = {
  /**
   * Get list of orders with optional filters
   */
  async getOrders(filters?: OrderFilters): Promise<OrderResponse[]> {
    return api.get<OrderResponse[]>(API_ENDPOINTS.ORDERS.LIST, {
      params: filters as Record<string, string | number | boolean | undefined>,
    });
  },

  /**
   * Get single order by ID
   */
  async getOrder(id: number): Promise<OrderResponse> {
    return api.get<OrderResponse>(API_ENDPOINTS.ORDERS.DETAIL(id));
  },

  /**
   * Create a new order
   */
  async createOrder(data: OrderCreate): Promise<OrderResponse> {
    return api.post<OrderResponse>(API_ENDPOINTS.ORDERS.LIST, data);
  },

  /**
   * Update order status
   * According to OpenAPI spec, status is passed as query parameter
   */
  async updateOrderStatus(orderId: number, status: OrderStatus): Promise<OrderResponse> {
    return api.patch<OrderResponse>(API_ENDPOINTS.ORDERS.UPDATE_STATUS(orderId), undefined, {
      params: { new_status: status }
    });
  },

  /**
   * Get corrections for an order
   */
  async getCorrections(orderId: number): Promise<OrderCorrectionResponse[]> {
    return api.get<OrderCorrectionResponse[]>(API_ENDPOINTS.ORDERS.CORRECTIONS(orderId));
  },

  /**
   * Create a correction for an order
   */
  async createCorrection(
    orderId: number, 
    data: OrderCorrectionCreate
  ): Promise<OrderCorrectionResponse> {
    return api.post<OrderCorrectionResponse>(
      API_ENDPOINTS.ORDERS.CORRECTIONS(orderId), 
      data
    );
  },
};
