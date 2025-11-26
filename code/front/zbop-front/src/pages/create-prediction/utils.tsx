import { FormValues } from '../../components/form/Form';
import { PredictionData } from '../../components/predictionResults';

// API response type matching the actual backend response structure
type ApiPredictionResponse = {
  day: number;
  orderAmount: number;
  consumedAmount: number;
  remainingAmount: number;
  unit: string;
}[];

// Function to make API call for predictions
export async function getPredictionData(formData: FormValues): Promise<PredictionData[]> {
  try {
    // Prepare request payload matching the v2 API schema
    const requestBody = {
      storage_capacity_kg: Number(formData.storageCapacityKg) || 150,
      purchase_costs_pln_per_kg_daily: formData.purchaseCostsDaily,
      transport_cost_pln: Number(formData.transportCostPln) || 100,
      num_conferences_daily: formData.numConferencesDaily,
      num_workers_daily: formData.numWorkersDaily,
      initial_inventory_kg: Number(formData.initialInventoryKg) || 40,
      daily_loss_fraction: Number(formData.dailyLossFraction) || 0.1,
      planning_horizon_days: formData.planningHorizonDays
    };

    // Validate that we have valid numbers
    if (requestBody.planning_horizon_days <= 0) {
      throw new Error('Please provide valid planning horizon');
    }

    // Make API call to backend v2 endpoint
    const response = await fetch(`http://localhost:8000/create_predictions_v2`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}: ${response.statusText}`);
    }

    const apiData: ApiPredictionResponse = await response.json();

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
};
