import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Form, { FormValues } from '../../components/form/Form';
import PredictionResult, { PredictionData } from '../../components/predictionResults/PredictionResult';
import { messages } from '../../components/form/messages';
import './styles.scss';
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
    console.log("aaSubmitting form with values:", values);
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
    <div className="create-prediction-page">
      <div className="page-header">
        <h1 className="page-title">{messages.createPrediction.title}</h1>
        <p className="page-subtitle">{messages.createPrediction.subtitle}</p>
      </div>

      {successMessage && (
        <div className="alert alert-success">
          <span className="alert-icon">✓</span>
          <span className="alert-message">{successMessage}</span>
          <button className="alert-action" onClick={handleGoToOrders}>
            {messages.createPrediction.goToOrders}
          </button>
        </div>
      )}

      {errorMessage && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          <span className="alert-message">{errorMessage}</span>
        </div>
      )}

      <div className="form-section">
        <Form onSubmit={handleFormSubmit} />
      </div>

      {(predictionData || isLoading) && (
        <>
          <hr className="section-divider" />
          <div className="results-section">
            {isLoading ? (
              <div className="loading-state">
                <div className="loading-spinner" />
                <p className="loading-text">Generowanie predykcji...</p>
              </div>
            ) : predictionData && predictionData.length > 0 && inputData ? (
              <PredictionResult 
                data={predictionData}
                demandData={inputData.numConferencesDaily.map((conf, i) => 
                  conf * 0.5 + inputData.numWorkersDaily[i] * 0.025
                )}
              />
            ) : (
              <p className="no-results">{messages.predictionResult.noResults}</p>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default CreatePrediction;
