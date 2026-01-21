import { FormValues } from '../../components/form/Form';
import { PredictionData } from '../../components/predictionResults';
import { optimizationService } from '../../services/optimization';
import { PredictionRequestV2 } from '../../types';

// Default values according to OpenAPI spec
const DEFAULT_DAILY_LOSS_FRACTION = 0.1;
const DEFAULT_TRANSPORT_COST = 100.0;

// Function to make API call for predictions
export async function getPredictionData(formData: FormValues): Promise<PredictionData[]> {
  try {
    // Validate input
    if (formData.planningHorizonDays <= 0) {
      throw new Error('Please provide valid planning horizon');
    }

    if (formData.numConferencesDaily.length !== formData.planningHorizonDays) {
      throw new Error('Number of conferences array must match planning horizon');
    }

    if (formData.numWorkersDaily.length !== formData.planningHorizonDays) {
      throw new Error('Number of workers array must match planning horizon');
    }

    // Generate default purchase costs if not provided
    // Using realistic values that vary by day
    const defaultPurchaseCosts = Array(formData.planningHorizonDays).fill(0).map(() => 
      Math.round((10 + Math.random() * 10) * 100) / 100
    );

    // Prepare request payload matching the OpenAPI PredictionRequestV2 schema exactly
    const requestBody: PredictionRequestV2 = {
      storage_capacity_kg: Number(formData.storageCapacityKg) || 150,
      purchase_costs_pln_per_kg_daily: defaultPurchaseCosts,
      transport_cost_pln: DEFAULT_TRANSPORT_COST,
      num_conferences_daily: formData.numConferencesDaily.map(Number),
      num_workers_daily: formData.numWorkersDaily.map(Number),
      initial_inventory_kg: Number(formData.initialInventoryKg) || 40,
      daily_loss_fraction: DEFAULT_DAILY_LOSS_FRACTION,
      planning_horizon_days: formData.planningHorizonDays
    };

    // Make API call using the optimization service
    const apiData = await optimizationService.createPredictionsV2(requestBody);

    // Transform API response to match our frontend data structure
    return apiData.map((item) => ({
      day: `Day ${item.day}`,
      orderAmount: typeof item.orderAmount === 'number' ? item.orderAmount : 0,
      consumedAmount: typeof item.consumedAmount === 'number' ? item.consumedAmount : 0,
      remainingAmount: typeof item.remainingAmount === 'number' ? item.remainingAmount : 0,
      unit: item.unit || 'kg'
    }));

  } catch (error) {
    console.error('Failed to fetch prediction data:', error);
    throw new Error(`Failed to generate predictions: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}
