import React, { useState } from 'react';
import { QuestionMarkCircleIcon } from '@heroicons/react/24/outline';

interface TooltipProps {
  content: string;
  className?: string;
}

export const Tooltip: React.FC<TooltipProps> = ({ content, className = '' }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className={`relative inline-block ${className}`}>
      <button
        type="button"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onFocus={() => setIsVisible(true)}
        onBlur={() => setIsVisible(false)}
        className="ml-1 text-gray-400 hover:text-gray-500 focus:outline-none"
      >
        <QuestionMarkCircleIcon className="h-4 w-4" />
      </button>
      
      {isVisible && (
        <div className="absolute z-10 w-64 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg -top-2 left-6 dark:bg-gray-700">
          <div 
            className="absolute -left-1.5 top-1/2 -translate-y-1/2 w-0 h-0"
            style={{
              borderTop: '6px solid transparent',
              borderRight: '6px solid #111827',
              borderBottom: '6px solid transparent',
            }}
          />
          {content}
        </div>
      )}
    </div>
  );
};