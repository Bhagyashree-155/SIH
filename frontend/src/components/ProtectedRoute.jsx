import React from 'react';
import { Navigate } from 'react-router-dom';
import authService from '../services/authService';

const ProtectedRoute = ({ children, requireRole }) => {
  const isLogged = authService.isLoggedIn();
  const role = authService.getRole();
  if (!isLogged) return <Navigate to="/login" replace />;
  if (requireRole && role !== requireRole) return <Navigate to="/" replace />;
  return children;
};

export default ProtectedRoute;


