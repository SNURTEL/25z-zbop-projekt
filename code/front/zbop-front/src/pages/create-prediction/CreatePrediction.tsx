import React, { useState } from 'react';
import { Box, Container, Typography, Divider } from '@mui/material';
import Form, { FormValues } from '../../components/form/Form';
import PredictionResult, { PredictionData } from '../../components/predictionResults/PredictionResult';
import { messages } from '../../components/form/messages';
import './styles.scss';
import CircularProgress from '@mui/material/CircularProgress';

// Mock function to simulate API call for predictions
const generatePredictionData = async (formData: FormValues): Promise<PredictionData[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock prediction calculations based on form data
  const capacity = Number(formData.maxCoffeeMagazineCapacity);
  const conferences = Number(formData.conferencesPerWeek);
  const workers = Number(formData.normalWorkersDaily);
  
  // Calculate daily consumption in grams
  const dailyConsumptionGrams = Math.round((workers * 2.5 + conferences * 15) * 12); // 12g per cup
  
  // Calculate optimal order amount (with 20% buffer for safety)
  const orderAmount = Math.round(dailyConsumptionGrams * 1.2);
  
  // Generate data for a week (7 days)
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  let cumulativeRemaining = 0;
  
  return days.map((day, index) => {
    // Weekend consumption is typically 30% less
    const isWeekend = index >= 5;
    const dailyConsumption = isWeekend ? Math.round(dailyConsumptionGrams * 0.7) : dailyConsumptionGrams;
    
    // Calculate remaining after consumption
    const remaining = cumulativeRemaining + orderAmount - dailyConsumption;
    cumulativeRemaining = Math.max(0, remaining);
    
    return {
      day: day,
      orderAmount: orderAmount,
      consumedAmount: dailyConsumption,
      remainingAmount: cumulativeRemaining,
      unit: 'grams'
    };
  });
};

const CreatePrediction: React.FC = () => {
  const [predictionData, setPredictionData] = useState<PredictionData[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFormSubmit = async (values: FormValues) => {
    setIsLoading(true);
    try {
      const predictions = await generatePredictionData(values);
      setPredictionData(predictions);
    } catch (error) {
      console.error('Error generating predictions:', error);
      // In a real app, you would show an error message to the user
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" className="create-prediction-page">
      <Box className="page-header">
        <Typography variant="h3" component="h1" gutterBottom>
          {messages.createPrediction.title}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" paragraph>
          {messages.createPrediction.subtitle}
        </Typography>
      </Box>

      <Box className="form-section">
        <Form onSubmit={handleFormSubmit} />
      </Box>

      {(predictionData || isLoading) && (
        <>
          <Divider className="section-divider" />
          <Box className="results-section">
            {isLoading ? (
              <Box className="loading-state">
                <CircularProgress />
              </Box>
            ) : predictionData && predictionData.length > 0 ? (
              <PredictionResult data={predictionData} />
            ) : (
              <Typography variant="body1" color="text.secondary">
                {messages.predictionResult.noResults}
              </Typography>
            )}
          </Box>
        </>
      )}
    </Container>
  );
};

export default CreatePrediction;
