import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './useAuth';

export default function RoleRoute({ children, allowedRoles }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;
  if (allowedRoles.includes(user.role)) return children;
  return <Navigate to="/no-access" />;
}
