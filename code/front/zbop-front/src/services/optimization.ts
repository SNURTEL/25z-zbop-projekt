// Optimization Service

import { api } from './api';
import { API_ENDPOINTS } from '../config/api';
import { 
  OptimizationRequestCreate, 
  OptimizationRequestResponse,
  PredictionRequestV2,
  DayPredictionV2 
} from '../types';

export const optimizationService = {
  /**
   * Create a new optimization request (authenticated)
   * Uses the modern /optimization/requests endpoint
   */
  async createOptimizationRequest(data: OptimizationRequestCreate): Promise<OptimizationRequestResponse> {
    return api.post<OptimizationRequestResponse>(API_ENDPOINTS.OPTIMIZATION.CREATE, data);
  },

  /**
   * Get optimization request by ID
   */
  async getOptimizationRequest(id: number): Promise<OptimizationRequestResponse> {
    return api.get<OptimizationRequestResponse>(API_ENDPOINTS.OPTIMIZATION.DETAIL(id));
  },

  /**
   * Get list of optimization requests
   */
  async getOptimizationRequests(params?: { office_id?: number; limit?: number }): Promise<OptimizationRequestResponse[]> {
    return api.get<OptimizationRequestResponse[]>(API_ENDPOINTS.OPTIMIZATION.CREATE, {
      params: params as Record<string, string | number | boolean | undefined>,
    });
  },

  /**
   * Create predictions using legacy v2 endpoint (no authentication required)
   * This endpoint is maintained for backward compatibility
   */
  async createPredictionsV2(data: PredictionRequestV2): Promise<DayPredictionV2[]> {
    return api.post<DayPredictionV2[]>(
      API_ENDPOINTS.LEGACY.CREATE_PREDICTIONS_V2, 
      data,
      { skipAuth: true }
    );
  },
};
