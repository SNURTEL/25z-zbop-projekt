import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Formik, Form, Field, FormikHelpers } from 'formik';
import * as Yup from 'yup';
import { ordersService } from '../../services/orders';
import { OrderResponse, OrderCorrectionCreate, OrderCorrectionResponse } from '../../types';
import { ordersMessages } from './messages';
import './styles.scss';

const EditOrder: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<OrderResponse | null>(null);
  const [corrections, setCorrections] = useState<OrderCorrectionResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchOrderData = useCallback(async () => {
    if (!id) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const [orderData, correctionsData] = await Promise.all([
        ordersService.getOrder(parseInt(id)),
        ordersService.getCorrections(parseInt(id)),
      ]);
      setOrder(orderData);
      setCorrections(correctionsData);
    } catch (err) {
      console.error('Error fetching order:', err);
      setError(ordersMessages.edit.orderNotFound);
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchOrderData();
  }, [fetchOrderData]);

  const validationSchema = Yup.object({
    quantity_increase: Yup.number()
      .min(0, ordersMessages.validation.increaseMin)
      .required(),
    quantity_decrease: Yup.number()
      .min(0, ordersMessages.validation.decreaseMin)
      .max(order?.quantity_kg || 0, ordersMessages.validation.decreaseMax)
      .required(),
    reason: Yup.string(),
  });

  const initialValues: OrderCorrectionCreate = {
    quantity_increase: 0,
    quantity_decrease: 0,
    reason: '',
  };

  const handleSubmit = async (
    values: OrderCorrectionCreate,
    { setSubmitting, resetForm }: FormikHelpers<OrderCorrectionCreate>
  ) => {
    if (!id) return;
    
    if (values.quantity_increase === 0 && values.quantity_decrease === 0) {
      setError(ordersMessages.validation.bothZero);
      setSubmitting(false);
      return;
    }

    setError(null);
    setSuccessMessage(null);
    
    try {
      await ordersService.createCorrection(parseInt(id), values);
      setSuccessMessage(ordersMessages.edit.successMessage);
      resetForm();
      fetchOrderData(); // Refresh data
    } catch (err) {
      console.error('Error creating correction:', err);
      setError(ordersMessages.edit.errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('pl-PL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatDateTime = (dateString: string): string => {
    return new Date(dateString).toLocaleString('pl-PL', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
    }).format(value);
  };

  const getStatusLabel = (status: string): string => {
    return ordersMessages.status[status as keyof typeof ordersMessages.status] || status;
  };

  if (isLoading) {
    return (
      <div className="edit-order-page">
        <div className="loading-state">
          <div className="loading-spinner" />
          <p className="loading-text">{ordersMessages.edit.loadingOrder}</p>
        </div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="edit-order-page">
        <div className="error-state">
          <span className="error-icon">⚠️</span>
          <p className="error-message">{ordersMessages.edit.orderNotFound}</p>
          <Link to="/orders" className="retry-button">
            {ordersMessages.edit.backButton}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="edit-order-page">
      <div className="page-header">
        <Link to="/orders" className="back-link">
          ← {ordersMessages.edit.backButton}
        </Link>
        <h1 className="page-title">{ordersMessages.edit.title} #{order.id}</h1>
        <p className="page-subtitle">{ordersMessages.edit.subtitle}</p>
      </div>

      {successMessage && (
        <div className="alert success">{successMessage}</div>
      )}

      {error && (
        <div className="alert error">{error}</div>
      )}

      <div className="edit-content">
        <div className="order-details">
          <h2 className="section-title">{ordersMessages.edit.orderDetails}</h2>
          <div className="detail-row">
            <span className="detail-label">{ordersMessages.card.status}</span>
            <span className="detail-value">{getStatusLabel(order.status)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">{ordersMessages.card.orderDate}</span>
            <span className="detail-value">{formatDate(order.order_date)}</span>
          </div>
          {order.delivery_date && (
            <div className="detail-row">
              <span className="detail-label">{ordersMessages.card.deliveryDate}</span>
              <span className="detail-value">{formatDate(order.delivery_date)}</span>
            </div>
          )}
          <div className="detail-row">
            <span className="detail-label">{ordersMessages.edit.currentQuantity}</span>
            <span className="detail-value">{order.quantity_kg} kg</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">{ordersMessages.card.totalCost}</span>
            <span className="detail-value">{formatCurrency(order.total_cost)}</span>
          </div>

          {/* Corrections History */}
          <div className="corrections-history">
            <h3 className="section-title">{ordersMessages.edit.correctionHistory}</h3>
            {corrections.length === 0 ? (
              <p className="no-corrections">{ordersMessages.edit.noCorrections}</p>
            ) : (
              corrections.map((correction) => (
                <div key={correction.id} className="correction-item">
                  <div className="correction-header">
                    <span className="correction-date">
                      {formatDateTime(correction.correction_date)}
                    </span>
                    <span className="correction-cost">
                      {formatCurrency(correction.correction_cost)}
                    </span>
                  </div>
                  <div className="correction-values">
                    {correction.quantity_increase > 0 && (
                      <span className="increase">+{correction.quantity_increase} kg</span>
                    )}
                    {correction.quantity_decrease > 0 && (
                      <span className="decrease">-{correction.quantity_decrease} kg</span>
                    )}
                  </div>
                  {correction.reason && (
                    <p className="correction-reason">{correction.reason}</p>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        <div className="correction-section">
          <h2 className="section-title">{ordersMessages.edit.correctionForm}</h2>
          
          <Formik
            initialValues={initialValues}
            validationSchema={validationSchema}
            onSubmit={handleSubmit}
          >
            {({ errors, touched, isSubmitting, values }) => (
              <Form className="correction-form">
                <div className="form-group">
                  <label htmlFor="quantity_increase">
                    {ordersMessages.edit.increaseLabel}
                  </label>
                  <Field
                    id="quantity_increase"
                    name="quantity_increase"
                    type="number"
                    min="0"
                    step="0.1"
                    className={errors.quantity_increase && touched.quantity_increase ? 'error' : ''}
                  />
                  {errors.quantity_increase && touched.quantity_increase && (
                    <span className="field-error">{errors.quantity_increase}</span>
                  )}
                </div>

                <div className="form-group">
                  <label htmlFor="quantity_decrease">
                    {ordersMessages.edit.decreaseLabel}
                  </label>
                  <Field
                    id="quantity_decrease"
                    name="quantity_decrease"
                    type="number"
                    min="0"
                    max={order.quantity_kg}
                    step="0.1"
                    className={errors.quantity_decrease && touched.quantity_decrease ? 'error' : ''}
                  />
                  {errors.quantity_decrease && touched.quantity_decrease && (
                    <span className="field-error">{errors.quantity_decrease}</span>
                  )}
                </div>

                <div className="quantity-preview">
                  <div className="preview-row">
                    <span className="preview-label">{ordersMessages.edit.currentQuantity}:</span>
                    <span className="preview-value">{order.quantity_kg} kg</span>
                  </div>
                  <div className="preview-row">
                    <span className="preview-label">{ordersMessages.edit.newQuantity}:</span>
                    <span className="preview-value">
                      {Math.max(0, order.quantity_kg + values.quantity_increase - values.quantity_decrease).toFixed(1)} kg
                    </span>
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="reason">
                    {ordersMessages.edit.reasonLabel}
                  </label>
                  <Field
                    as="textarea"
                    id="reason"
                    name="reason"
                    placeholder={ordersMessages.edit.reasonPlaceholder}
                  />
                </div>

                <div className="form-actions">
                  <button
                    type="button"
                    className="cancel-button"
                    onClick={() => navigate('/orders')}
                  >
                    {ordersMessages.edit.cancelButton}
                  </button>
                  <button
                    type="submit"
                    className="submit-button"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? '...' : ordersMessages.edit.submitButton}
                  </button>
                </div>
              </Form>
            )}
          </Formik>
        </div>
      </div>
    </div>
  );
};

export default EditOrder;
