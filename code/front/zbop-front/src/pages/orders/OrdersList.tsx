import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { ordersService } from '../../services/orders';
import { OrderResponse } from '../../types';
import { ordersMessages } from './messages';
import './styles.scss';

const OrdersList: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrders = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await ordersService.getOrders({
        office_id: user?.office_id || undefined,
      });
      setOrders(data);
    } catch (err) {
      console.error('Error fetching orders:', err);
      setError(ordersMessages.list.error);
    } finally {
      setIsLoading(false);
    }
  }, [user?.office_id]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('pl-PL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
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
      <div className="orders-page">
        <div className="loading-state">
          <div className="loading-spinner" />
          <p className="loading-text">{ordersMessages.list.loading}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="orders-page">
        <div className="error-state">
          <span className="error-icon">⚠️</span>
          <p className="error-message">{error}</p>
          <button className="retry-button" onClick={fetchOrders}>
            {ordersMessages.list.retry}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="orders-page">
      <div className="page-header">
        <h1 className="page-title">{ordersMessages.list.title}</h1>
        <p className="page-subtitle">{ordersMessages.list.subtitle}</p>
      </div>

      {orders.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">📦</span>
          <h2 className="empty-title">{ordersMessages.list.emptyState.title}</h2>
          <p className="empty-description">{ordersMessages.list.emptyState.description}</p>
          <Link to="/orders/create" className="empty-button">
            {ordersMessages.list.emptyState.createButton}
          </Link>
        </div>
      ) : (
        <div className="orders-grid">
          {orders.map((order) => (
            <div key={order.id} className="order-card">
              <div className="card-header">
                <span className="order-id">#{order.id}</span>
                <span className={`order-status ${order.status}`}>
                  {getStatusLabel(order.status)}
                </span>
              </div>
              <div className="card-body">
                <div className="card-row">
                  <span className="row-label">{ordersMessages.card.orderDate}</span>
                  <span className="row-value">{formatDate(order.order_date)}</span>
                </div>
                {order.delivery_date && (
                  <div className="card-row">
                    <span className="row-label">{ordersMessages.card.deliveryDate}</span>
                    <span className="row-value">{formatDate(order.delivery_date)}</span>
                  </div>
                )}
                <div className="card-row">
                  <span className="row-label">{ordersMessages.card.quantity}</span>
                  <span className="row-value quantity">{order.quantity_kg} kg</span>
                </div>
                <div className="card-row">
                  <span className="row-label">{ordersMessages.card.totalCost}</span>
                  <span className="row-value cost">{formatCurrency(order.total_cost)}</span>
                </div>
              </div>
              <div className="card-footer">
                <button
                  className="edit-button"
                  onClick={() => navigate(`/orders/${order.id}/edit`)}
                >
                  {ordersMessages.card.editButton}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default OrdersList;
