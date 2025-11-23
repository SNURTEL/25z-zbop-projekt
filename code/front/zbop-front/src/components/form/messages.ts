export const messages = {
  title: 'Coffie demand prediction',
  fields: {
    maxCoffeeMagazineCapacity: 'Max capacity of coffee magazine',
    conferencesPerWeek: 'Number of conferences per week',
    normalWorkersDaily: 'Number of normal workers daily',
  },
  actions: {
    submit: 'Submit',
    reset: 'Reset',
  },
  validation: {
    required: 'This field is required',
    number: 'Please enter a valid number',
    integer: 'Please enter an integer value',
    nonNegative: 'Value must be non-negative',
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


