import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Context
import { AuthProvider } from '../context/AuthContext';

// Components
import { MainLayout } from '../components/layout';
import { ProtectedRoute } from '../components/auth';

// Pages
import { Login, Register } from './auth';
import CreatePrediction from './create-prediction/CreatePrediction';
import { OrdersList, EditOrder } from './orders';
import { VendorOrders } from './vendor';

const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',
    },
    secondary: {
      main: '#764ba2',
    },
  },
});

// Component to handle root redirect based on user role
const RootRedirect: React.FC = () => {
  return <Navigate to="/orders" replace />;
};

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected routes with layout */}
            <Route
              element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              {/* Root redirect */}
              <Route path="/" element={<RootRedirect />} />

              {/* User routes */}
              <Route
                path="/orders/create"
                element={
                  <ProtectedRoute allowedRoles={['user']}>
                    <CreatePrediction />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/orders"
                element={
                  <ProtectedRoute allowedRoles={['user']}>
                    <OrdersList />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/orders/:id/edit"
                element={
                  <ProtectedRoute allowedRoles={['user']}>
                    <EditOrder />
                  </ProtectedRoute>
                }
              />

              {/* Vendor routes */}
              <Route
                path="/vendor/orders"
                element={
                  <ProtectedRoute allowedRoles={['vendor']}>
                    <VendorOrders />
                  </ProtectedRoute>
                }
              />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
