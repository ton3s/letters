import React from 'react';
import { Navigate } from 'react-router-dom';
import { useIsAuthenticated } from '@azure/msal-react';
import { useTheme } from '../contexts/ThemeContext';
import { LoginButton } from '../components/auth/LoginButton';
import { EnvelopeIcon, ShieldCheckIcon, DocumentTextIcon, ClockIcon, SunIcon, MoonIcon } from '@heroicons/react/24/outline';

export const Login: React.FC = () => {
  const isAuthenticated = useIsAuthenticated();
  const { toggleTheme, isDarkMode } = useTheme();

  // If already authenticated, redirect to the main app
  if (isAuthenticated) {
    return <Navigate to="/generate" replace />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex flex-col">
      {/* Header */}
      <header className="w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <EnvelopeIcon className="h-10 w-10 text-red-600 dark:text-red-500" />
              <h1 className="ml-3 text-2xl font-bold text-gray-900 dark:text-white">
                Insurance Letter Generator
              </h1>
            </div>
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-gray-500 hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label="Toggle theme"
            >
              {isDarkMode ? (
                <SunIcon className="h-5 w-5" />
              ) : (
                <MoonIcon className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full">
          {/* Login Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8">
            {/* Logo and Title */}
            <div className="text-center mb-8">
              <div className="mx-auto h-20 w-20 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mb-4">
                <EnvelopeIcon className="h-12 w-12 text-red-600 dark:text-red-500" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                Welcome Back
              </h2>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Sign in to access your insurance letter tools
              </p>
            </div>

            {/* Features List */}
            <div className="space-y-3 mb-8">
              <div className="flex items-start">
                <DocumentTextIcon className="h-5 w-5 text-red-600 dark:text-red-500 mt-0.5 flex-shrink-0" />
                <p className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                  Generate professional insurance letters with AI assistance
                </p>
              </div>
              <div className="flex items-start">
                <ShieldCheckIcon className="h-5 w-5 text-red-600 dark:text-red-500 mt-0.5 flex-shrink-0" />
                <p className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                  Built-in compliance review for regulatory requirements
                </p>
              </div>
              <div className="flex items-start">
                <ClockIcon className="h-5 w-5 text-red-600 dark:text-red-500 mt-0.5 flex-shrink-0" />
                <p className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                  Save time with intelligent placeholder management
                </p>
              </div>
            </div>

            {/* Login Button */}
            <div className="space-y-4">
              <LoginButton 
                variant="primary" 
                className="w-full py-3 text-base"
                showIcon={true}
              />
              
              {/* Security Notice */}
              <p className="text-xs text-center text-gray-500 dark:text-gray-400">
                Secured by Microsoft Entra ID. Your organization's credentials are required to access this application.
              </p>
            </div>
          </div>

          {/* Additional Information */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Having trouble signing in?
            </p>
            <a 
              href="mailto:support@company.com" 
              className="text-sm text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 font-medium"
            >
              Contact IT Support
            </a>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500 dark:text-gray-400">
            © 2025 Insurance Letter Generator. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};