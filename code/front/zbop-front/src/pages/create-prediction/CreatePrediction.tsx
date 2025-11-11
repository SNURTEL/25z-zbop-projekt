import React, { useState } from 'react';
import { Box, Container, Typography, Divider } from '@mui/material';
import Form, { FormValues } from '../../components/form/Form';
import PredictionResult, { PredictionData } from '../../components/predictionResults/PredictionResult';
import { messages } from '../../components/form/messages';
import './styles.scss';
import CircularProgress from '@mui/material/CircularProgress';
import { getPredictionData } from './utils';



const CreatePrediction: React.FC = () => {
  const [predictionData, setPredictionData] = useState<PredictionData[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFormSubmit = async (values: FormValues) => {
    setIsLoading(true);
    try {
      const predictions = await getPredictionData(values);
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
