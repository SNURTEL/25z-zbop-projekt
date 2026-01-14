import React, { useState, useEffect, useCallback } from 'react';
import { ordersService } from '../../services/orders';
import { OrderResponse, OrderStatus, OrderFilters } from '../../types';
import { vendorMessages } from './messages';
import './styles.scss';

const ALL_STATUSES: OrderStatus[] = ['planned', 'confirmed', 'delivered', 'cancelled'];

const VendorOrders: React.FC = () => {
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<OrderStatus | 'all'>('all');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [updatingOrderId, setUpdatingOrderId] = useState<number | null>(null);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchOrders = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const filters: OrderFilters = {};
      if (statusFilter !== 'all') {
        filters.status = statusFilter;
      }
      if (dateFrom) {
        filters.date_from = dateFrom;
      }
      if (dateTo) {
        filters.date_to = dateTo;
      }
      
      const data = await ordersService.getOrders(filters);
      setOrders(data);
    } catch (err) {
      console.error('Error fetching orders:', err);
      setError(vendorMessages.orders.error);
    } finally {
      setIsLoading(false);
    }
  }, [statusFilter, dateFrom, dateTo]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('pl-PL');
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
    }).format(value);
  };

  const getStatusLabel = (status: string): string => {
    return vendorMessages.status[status as keyof typeof vendorMessages.status] || status;
  };

  const clearFilters = () => {
    setStatusFilter('all');
    setDateFrom('');
    setDateTo('');
  };

  const handleStatusChange = async (orderId: number, newStatus: OrderStatus) => {
    setUpdatingOrderId(orderId);
    setStatusMessage(null);
    try {
      const updatedOrder = await ordersService.updateOrderStatus(orderId, newStatus);
      setOrders(prev => prev.map(order => 
        order.id === orderId ? updatedOrder : order
      ));
      setStatusMessage({ type: 'success', text: vendorMessages.statusChange.success });
      setTimeout(() => setStatusMessage(null), 3000);
    } catch (err) {
      console.error('Error updating order status:', err);
      setStatusMessage({ type: 'error', text: vendorMessages.statusChange.error });
    } finally {
      setUpdatingOrderId(null);
    }
  };

  const statusOptions: Array<OrderStatus | 'all'> = ['all', 'planned', 'confirmed', 'delivered', 'cancelled'];

  if (isLoading) {
    return (
      <div className="vendor-page">
        <div className="loading-state">
          <div className="loading-spinner" />
          <p className="loading-text">{vendorMessages.orders.loading}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="vendor-page">
        <div className="error-state">
          <span className="error-icon">⚠️</span>
          <p className="error-message">{error}</p>
          <button className="retry-button" onClick={fetchOrders}>
            {vendorMessages.orders.retry}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="vendor-page">
      <div className="page-header">
        <h1 className="page-title">{vendorMessages.orders.title}</h1>
        <p className="page-subtitle">{vendorMessages.orders.subtitle}</p>
      </div>

      {statusMessage && (
        <div className={`status-message ${statusMessage.type}`}>
          {statusMessage.text}
        </div>
      )}

      <div className="filters-section">
        <div className="filters-row">
          <div className="status-filters">
            {statusOptions.map((status) => (
              <button
                key={status}
                className={`status-button ${statusFilter === status ? 'active' : ''}`}
                onClick={() => setStatusFilter(status)}
              >
                {status === 'all' 
                  ? vendorMessages.filters.all 
                  : vendorMessages.filters[status as keyof typeof vendorMessages.filters]
                }
              </button>
            ))}
          </div>

          <div className="filter-group">
            <label>{vendorMessages.filters.dateFrom}</label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
          </div>

          <div className="filter-group">
            <label>{vendorMessages.filters.dateTo}</label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
          </div>

          {(statusFilter !== 'all' || dateFrom || dateTo) && (
            <button className="clear-filters" onClick={clearFilters}>
              {vendorMessages.filters.clearFilters}
            </button>
          )}
        </div>
      </div>

      {orders.length === 0 ? (
        <div className="vendor-empty-state">
          <span className="empty-icon">📦</span>
          <h2 className="empty-title">{vendorMessages.orders.emptyState.title}</h2>
          <p className="empty-description">{vendorMessages.orders.emptyState.description}</p>
        </div>
      ) : (
        <div className="orders-table-container">
          <table className="orders-table">
            <thead>
              <tr>
                <th>{vendorMessages.table.id}</th>
                <th>{vendorMessages.table.orderDate}</th>
                <th>{vendorMessages.table.deliveryDate}</th>
                <th>{vendorMessages.table.quantity}</th>
                <th>{vendorMessages.table.unitPrice}</th>
                <th>{vendorMessages.table.transportCost}</th>
                <th>{vendorMessages.table.totalCost}</th>
                <th>{vendorMessages.table.status}</th>
                <th>{vendorMessages.table.actions}</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id}>
                  <td className="order-id">#{order.id}</td>
                  <td>{formatDate(order.order_date)}</td>
                  <td>{order.delivery_date ? formatDate(order.delivery_date) : '-'}</td>
                  <td className="quantity-cell">{order.quantity_kg} kg</td>
                  <td>{formatCurrency(order.unit_price)}/kg</td>
                  <td>{formatCurrency(order.transport_cost)}</td>
                  <td className="cost-cell">{formatCurrency(order.total_cost)}</td>
                  <td>
                    <span className={`status-badge ${order.status}`}>
                      {getStatusLabel(order.status)}
                    </span>
                  </td>
                  <td>
                    <select
                      className="status-select"
                      value={order.status}
                      onChange={(e) => handleStatusChange(order.id, e.target.value as OrderStatus)}
                      disabled={updatingOrderId === order.id}
                    >
                      {ALL_STATUSES.map((status) => (
                        <option key={status} value={status}>
                          {getStatusLabel(status)}
                        </option>
                      ))}
                    </select>
                    {updatingOrderId === order.id && (
                      <span className="updating-text">{vendorMessages.statusChange.updating}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default VendorOrders;
