// Optimization types based on OpenAPI specification

import { OrderResponse } from './orders';

export type SolverStatus = 'OPTIMAL' | 'INFEASIBLE' | 'UNBOUNDED' | 'ERROR';

export interface InventorySnapshot {
  date: string;
  inventory_level: number;
  demand_fulfilled: number;
  loss_amount: number;
  deliveries_received: number;
}

export interface OptimizationRequestCreate {
  office_id: number;
  planning_horizon_start: string;
  planning_horizon_days: number;
  initial_inventory: number;
  purchase_costs_daily: number[];
  num_workers_daily: number[];
  num_conferences_daily: number[];
  transport_cost: number;
  is_correction_mode?: boolean;
}

export interface OptimizationRequestResponse {
  id: number;
  office_id: number;
  planning_horizon_start: string;
  planning_horizon_end: string;
  initial_inventory: number;
  total_cost: number;
  solver_status: SolverStatus;
  solve_time_ms: number;
  is_correction_mode: boolean;
  created_at: string;
  orders: OrderResponse[];
  inventory_projections: InventorySnapshot[];
}

// Legacy prediction types (for backward compatibility)
export interface PredictionRequestV2 {
  storage_capacity_kg: number;
  purchase_costs_pln_per_kg_daily: number[];
  transport_cost_pln: number;
  num_conferences_daily: number[];
  num_workers_daily: number[];
  initial_inventory_kg: number;
  daily_loss_fraction: number;
  planning_horizon_days: number;
}

export interface DayPredictionV2 {
  day: number;
  orderAmount: number;
  consumedAmount: number;
  remainingAmount: number;
  unit: string;
}
