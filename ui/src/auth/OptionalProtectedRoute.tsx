import React from 'react';
import { ProtectedRoute } from './ProtectedRoute';
import { REQUIRE_AUTH } from '../config/auth.config';

interface OptionalProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
}

/**
 * Component that optionally protects routes based on configuration
 */
export const OptionalProtectedRoute: React.FC<OptionalProtectedRouteProps> = ({ 
  children, 
  requireAuth = REQUIRE_AUTH 
}) => {
  // If authentication is not required, render children directly
  if (!requireAuth) {
    return <>{children}</>;
  }

  // Otherwise, use the ProtectedRoute component
  return <ProtectedRoute>{children}</ProtectedRoute>;
};