import React from 'react';
import { LoadingSpinner } from './LoadingSpinner';

interface LoadingModalProps {
  isOpen: boolean;
  message?: string;
}

export const LoadingModal: React.FC<LoadingModalProps> = ({ isOpen, message = 'Generating letter...' }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black bg-opacity-50" />
      
      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 max-w-sm w-full mx-4">
        <div className="flex flex-col items-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">
            {message}
          </p>
        </div>
      </div>
    </div>
  );
};