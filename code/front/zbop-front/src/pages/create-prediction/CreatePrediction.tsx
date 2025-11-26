import React, { useState } from 'react';
import { Box, Typography, Divider } from '@mui/material';
import Form, { FormValues } from '../../components/form/Form';
import PredictionResult, { PredictionData } from '../../components/predictionResults/PredictionResult';
import { messages } from '../../components/form/messages';
import './styles.scss';
import CircularProgress from '@mui/material/CircularProgress';
import { getPredictionData } from './utils';



const CreatePrediction: React.FC = () => {
  const [predictionData, setPredictionData] = useState<PredictionData[] | null>(null);
  const [inputData, setInputData] = useState<FormValues | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFormSubmit = async (values: FormValues) => {
    setIsLoading(true);
    try {
      const predictions = await getPredictionData(values);
      setPredictionData(predictions);
      setInputData(values);
    } catch (error) {
      console.error('Error generating predictions:', error);
      // In a real app, you would show an error message to the user
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ width: '100%', maxWidth: '2400px', margin: '0 auto', px: { xs: 2, sm: 3, md: 4 } }}>
      <Box className="create-prediction-page">
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
            ) : predictionData && predictionData.length > 0 && inputData ? (
              <PredictionResult 
                data={predictionData}
                demandData={inputData.numConferencesDaily.map((conf, i) => 
                  conf * 0.5 + inputData.numWorkersDaily[i] * 0.025
                )}
                purchaseCosts={inputData.purchaseCostsDaily}
                transportCost={Number(inputData.transportCostPln) || 0}
              />
            ) : (
              <Typography variant="body1" color="text.secondary">
                {messages.predictionResult.noResults}
              </Typography>
            )}
          </Box>
        </>
      )}
      </Box>
    </Box>
  );
};

export default CreatePrediction;
