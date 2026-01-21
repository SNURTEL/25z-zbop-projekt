import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import { useAuth } from '../../hooks/useAuth';
import { layoutMessages } from './messages';
import './styles.scss';

const MainLayout: React.FC = () => {
  const { isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" />
        <p className="loading-text">{layoutMessages.loading.text}</p>
      </div>
    );
  }

  return (
    <div className="main-layout">
      <Navbar />
      <main className="main-content">
        <div className="content-container">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default MainLayout;
