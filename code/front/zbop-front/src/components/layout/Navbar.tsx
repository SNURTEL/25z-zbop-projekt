import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { layoutMessages } from './messages';
import './styles.scss';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getInitials = (): string => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    return user?.email?.[0]?.toUpperCase() || 'U';
  };

  const getUserDisplayName = (): string => {
    if (user?.first_name) {
      return user.first_name;
    }
    return user?.email?.split('@')[0] || '';
  };

  // Check if user is a vendor
  const isVendor = user?.role === 'vendor';

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <NavLink to="/" className="navbar-brand">
          <span className="brand-icon">☕</span>
          <span className="brand-text">{layoutMessages.navbar.brand}</span>
        </NavLink>

        <div className="navbar-nav">
          {isVendor ? (
            // Vendor navigation
            <NavLink
              to="/vendor/orders"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <span className="nav-icon">📦</span>
              <span className="nav-text">{layoutMessages.navbar.vendorOrders}</span>
            </NavLink>
          ) : (
            // Regular user navigation
            <>
              <NavLink
                to="/orders/create"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                <span className="nav-icon">➕</span>
                <span className="nav-text">{layoutMessages.navbar.createOrder}</span>
              </NavLink>
              <NavLink
                to="/orders"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                <span className="nav-icon">📋</span>
                <span className="nav-text">{layoutMessages.navbar.myOrders}</span>
              </NavLink>
            </>
          )}
        </div>

        <div className="navbar-user">
          <div className="user-info">
            <div className="user-avatar">{getInitials()}</div>
            <span className="user-name">
              {layoutMessages.navbar.welcome}, {getUserDisplayName()}
            </span>
          </div>
          <button onClick={handleLogout} className="logout-button">
            <span className="logout-icon">🚪</span>
            <span className="logout-text">{layoutMessages.navbar.logout}</span>
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
