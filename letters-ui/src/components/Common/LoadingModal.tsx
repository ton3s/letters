import React, { useState, useEffect } from 'react';
import { LoadingSpinner } from './LoadingSpinner';

interface LoadingModalProps {
  isOpen: boolean;
  message?: string;
}

const progressMessages = [
  { delay: 0, message: 'Initializing letter generation...' },
  { delay: 2000, message: 'Letter Writer agent is drafting your letter...' },
  { delay: 8000, message: 'Compliance Reviewer agent is reviewing for compliance...' },
  { delay: 14000, message: 'Customer Service Reviewer agent is checking customer experience...' },
  { delay: 20000, message: 'Finalizing your letter...' },
];

export const LoadingModal: React.FC<LoadingModalProps> = ({ isOpen, message = 'Generating letter...' }) => {
  const [currentMessage, setCurrentMessage] = useState(message);
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    if (!isOpen) {
      setMessageIndex(0);
      setCurrentMessage(message);
      return;
    }

    // Set initial message
    setCurrentMessage(progressMessages[0].message);
    
    // Create timers for subsequent messages
    const timers: NodeJS.Timeout[] = [];
    
    progressMessages.forEach((item, index) => {
      if (index > 0) {
        const timer = setTimeout(() => {
          setCurrentMessage(item.message);
          setMessageIndex(index);
        }, item.delay);
        timers.push(timer);
      }
    });

    // Cleanup timers on unmount or when modal closes
    return () => {
      timers.forEach(timer => clearTimeout(timer));
    };
  }, [isOpen, message]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black bg-opacity-50" />
      
      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 max-w-md w-full mx-4">
        <div className="flex flex-col items-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-lg font-semibold text-gray-900 dark:text-white text-center">
            {currentMessage}
          </p>
          <div className="mt-4 w-full">
            <div className="flex space-x-1">
              {progressMessages.map((_, index) => (
                <div
                  key={index}
                  className={`flex-1 h-1 rounded-full transition-colors duration-500 ${
                    index <= messageIndex
                      ? 'bg-primary-500'
                      : 'bg-gray-300 dark:bg-gray-600'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};