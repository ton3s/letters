import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Footer } from './Footer';
import { Bars3Icon } from '@heroicons/react/24/outline';

interface LayoutProps {
  onThemeToggle: () => void;
  isDarkMode: boolean;
}

export const Layout: React.FC<LayoutProps> = ({ onThemeToggle, isDarkMode }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  
  // Don't show footer on generate and history pages
  const showFooter = !['/generate', '/history', '/letter/view'].includes(location.pathname);

  return (
    <div className="h-screen flex overflow-hidden bg-gray-100 dark:bg-gray-900">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header onThemeToggle={onThemeToggle} isDarkMode={isDarkMode} />

        {/* Mobile menu button */}
        <div className="lg:hidden">
          <button
            onClick={() => setSidebarOpen(true)}
            className="fixed bottom-4 right-4 z-20 bg-primary-600 hover:bg-primary-700 text-white rounded-full p-3 shadow-lg"
          >
            <Bars3Icon className="h-6 w-6" />
          </button>
        </div>

        {/* Main content */}
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <Outlet />
            </div>
          </div>
          {showFooter && <Footer />}
        </main>
      </div>
    </div>
  );
};