import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Divider, Alert, Button } from '@mui/material';
import Form, { FormValues } from '../../components/form/Form';
import PredictionResult, { PredictionData } from '../../components/predictionResults/PredictionResult';
import { messages } from '../../components/form/messages';
import './styles.scss';
import CircularProgress from '@mui/material/CircularProgress';
import { getPredictionData } from './utils';

const CreatePrediction: React.FC = () => {
  const navigate = useNavigate();
  const [predictionData, setPredictionData] = useState<PredictionData[] | null>(null);
  const [inputData, setInputData] = useState<FormValues | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFormSubmit = async (values: FormValues) => {
    setIsLoading(true);
    setSuccessMessage(null);
    setErrorMessage(null);
    try {
      const predictions = await getPredictionData(values);
      setPredictionData(predictions);
      setInputData(values);
      setSuccessMessage(messages.createPrediction.successMessage);
    } catch (error) {
      console.error('Error generating predictions:', error);
      setErrorMessage(messages.createPrediction.errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoToOrders = () => {
    navigate('/orders');
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

      {successMessage && (
        <Alert 
          severity="success" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={handleGoToOrders}>
              {messages.createPrediction.goToOrders}
            </Button>
          }
        >
          {successMessage}
        </Alert>
      )}

      {errorMessage && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {errorMessage}
        </Alert>
      )}

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
