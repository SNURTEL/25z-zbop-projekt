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
    // Prepare request payload matching the API schema
    const requestBody = {
      max_capacity: Number(formData.maxCoffeeMagazineCapacity) || 0,
      conferences_per_week: Number(formData.conferencesPerWeek) || 0,
      normal_workers_daily: Number(formData.normalWorkersDaily) || 0
    };

    // Validate that we have valid numbers
    if (requestBody.max_capacity <= 0 || requestBody.conferences_per_week < 0 || requestBody.normal_workers_daily <= 0) {
      throw new Error('Please provide valid positive numbers for all fields');
    }

    // Make API call to backend
    const response = await fetch(`http://localhost:8000/create_predictions`, {
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

    // Day names mapping
    const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

    // Transform API response to match our frontend data structure
    return apiData.map((item) => ({
      day: dayNames[item.day - 1] || `Day ${item.day}`,
      orderAmount: typeof item.orderAmount === 'number' ? item.orderAmount : 0,
      consumedAmount: typeof item.consumedAmount === 'number' ? item.consumedAmount : 0,
      remainingAmount: typeof item.remainingAmount === 'number' ? item.remainingAmount : 0,
      unit: item.unit || 'grams'
    }));

  } catch (error) {
    console.error('Failed to fetch prediction data:', error);
    throw new Error(`Failed to generate predictions: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};