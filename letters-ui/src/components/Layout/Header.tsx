import React from 'react';
import {
  SunIcon,
  MoonIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline';

interface HeaderProps {
  onThemeToggle: () => void;
  isDarkMode: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onThemeToggle, isDarkMode }) => {

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center">
            <EnvelopeIcon className="h-8 w-8 text-primary-500" />
            <h1 className="ml-2 text-xl font-bold text-gray-900 dark:text-white">
              Insurance Letter Generator
            </h1>
          </div>

          {/* Right side actions */}
          <div className="flex items-center">
            {/* Theme Toggle */}
            <button
              onClick={onThemeToggle}
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
      </div>
    </header>
  );
};