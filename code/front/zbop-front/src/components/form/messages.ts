export const messages = {
  title: 'Coffie demand prediction',
  fields: {
    planningHorizonDays: 'Planning Horizon (Days)',
    numConferencesDaily: 'Number of Conferences per Day',
    numWorkersDaily: 'Number of Workers per Day',
    purchaseCostsDaily: 'Purchase Costs (PLN per kg) per Day',
    fillAllConferences: 'Fill all days with same value',
    fillAllWorkers: 'Fill all days with same value',
    fillAllCosts: 'Fill all days with same value',
    storageCapacityKg: 'Storage Capacity (kg)',
    transportCostPln: 'Transport Cost (PLN)',
    initialInventoryKg: 'Initial Inventory (kg)',
    dailyLossFraction: 'Daily Loss Fraction (0.0 to 1.0)',
    advancedSettingsExpanded: 'Edit Constants (click to collapse)',
    advancedSettingsCollapsed: 'Edit Constants (click to expand)',
  },
  actions: {
    submit: 'Generate Predictions',
    reset: 'Reset',
  },
  validation: {
    required: 'This field is required',
    number: 'Please enter a valid number',
    integer: 'Please enter an integer value',
    nonNegative: 'Value must be non-negative',
    positive: 'Value must be positive',
    between0and1: 'Value must be between 0.0 and 1.0',
    positiveFloat: 'Please enter a positive decimal number',
  },
  predictionResult: {
    title: 'Daily Coffee Order and Consumption Forecast',
    headers: {
      day: 'Day',
      orderAmount: 'Order Amount',
      consumedAmount: 'Consumed',
      remainingAmount: 'Remaining',
      unit: 'Unit',
    },
    noResults: 'No prediction results available. Please submit the form above to generate predictions.',
  },
  createPrediction: {
    title: 'Coffee Demand Prediction System',
    subtitle: 'Enter the parameters below to get predictions for coffee consumption',
  },
};


