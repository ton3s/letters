import React from 'react';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="md:flex md:items-center md:justify-between">
          <div className="flex justify-center md:justify-start">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              &copy; {currentYear} Insurance Letter Generator. All rights reserved.
            </p>
          </div>
          <div className="mt-4 md:mt-0">
            <nav className="flex justify-center md:justify-end space-x-6">
              <a
                href="#"
                className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                Privacy Policy
              </a>
              <a
                href="#"
                className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                Terms of Service
              </a>
              <a
                href="#"
                className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                Documentation
              </a>
              <a
                href="#"
                className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                API Status
              </a>
            </nav>
          </div>
        </div>
        <div className="mt-4 flex justify-center md:justify-start">
          <p className="text-xs text-gray-400 dark:text-gray-500">
            Powered by AI • Version 1.0.0
          </p>
        </div>
      </div>
    </footer>
  );
};