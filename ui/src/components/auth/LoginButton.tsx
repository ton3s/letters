import React from 'react';
import { useAuth } from '../../auth/AuthProvider';
import { ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';

interface LoginButtonProps {
  className?: string;
  showIcon?: boolean;
  variant?: 'primary' | 'secondary' | 'text';
}

export const LoginButton: React.FC<LoginButtonProps> = ({ 
  className = '', 
  showIcon = true,
  variant = 'primary' 
}) => {
  const { login, isLoading } = useAuth();

  const baseClasses = "inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800";
  
  const variantClasses = {
    primary: "px-4 py-2 border border-transparent rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 dark:bg-red-600 dark:hover:bg-red-700 focus:ring-red-500 dark:focus:ring-red-400",
    secondary: "px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:ring-red-500 dark:focus:ring-red-400",
    text: "text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100"
  };

  const handleLogin = async () => {
    try {
      await login();
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <button
      onClick={handleLogin}
      disabled={isLoading}
      className={`${baseClasses} ${variantClasses[variant]} ${className} ${
        isLoading ? 'opacity-50 cursor-not-allowed' : ''
      }`}
    >
      {showIcon && (
        <ArrowRightOnRectangleIcon className="w-5 h-5 mr-2" aria-hidden="true" />
      )}
      {isLoading ? 'Signing in...' : 'Sign In'}
    </button>
  );
};