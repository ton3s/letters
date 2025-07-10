import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useIsAuthenticated, useMsal } from '@azure/msal-react';
import { InteractionStatus } from '@azure/msal-browser';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * Component that protects routes requiring authentication
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const isAuthenticated = useIsAuthenticated();
  const { inProgress, instance } = useMsal();
  const location = useLocation();

  useEffect(() => {
    // If not authenticated and not in progress, try to login
    if (!isAuthenticated && inProgress === InteractionStatus.None) {
      instance.loginRedirect({
        scopes: ['User.Read'],
        state: location.pathname, // Save the path to redirect back after login
      }).catch(error => {
        console.error('Login redirect failed:', error);
      });
    }
  }, [isAuthenticated, inProgress, instance, location]);

  // Show loading spinner while authentication is in progress
  if (inProgress !== InteractionStatus.None) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  // If authenticated, render the protected content
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // Fallback: redirect to home if not authenticated
  // This should rarely be reached due to the useEffect above
  return <Navigate to="/" state={{ from: location }} replace />;
};