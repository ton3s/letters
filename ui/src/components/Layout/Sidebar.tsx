import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  XMarkIcon,
  PlusIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
}

const navigation: NavItem[] = [
  { name: 'Generate Letter', href: '/generate', icon: DocumentTextIcon },
  { name: 'Letter History', href: '/history', icon: ClipboardDocumentListIcon },
  { name: 'Company Settings', href: '/settings', icon: Cog6ToothIcon },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 z-30 lg:hidden"
          onClick={onClose}
        ></div>
      )}

      {/* Sidebar */}
      <div
        className={`
          fixed lg:static inset-y-0 left-0 z-40 w-64 
          transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} 
          lg:translate-x-0 transition-transform duration-300 ease-in-out
          flex flex-col bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700
        `}
      >
        {/* Mobile close button */}
        <div className="lg:hidden absolute top-2 right-2">
          <button
            onClick={onClose}
            className="flex items-center justify-center h-10 w-10 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Sidebar content */}
        <div className="flex-1 flex flex-col min-h-0 pt-5 pb-4 overflow-y-auto">
          <div className="flex-1 px-3">
            {/* Quick action button */}
            <NavLink 
              to="/generate"
              className="w-full mb-6 bg-primary-500 hover:bg-primary-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors flex items-center justify-center shadow-md"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              New Letter
            </NavLink>

            {/* Main navigation */}
            <nav className="space-y-1">
              {navigation.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                      isActive
                        ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400'
                        : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white'
                    }`
                  }
                >
                  <item.icon
                    className="mr-3 flex-shrink-0 h-6 w-6"
                    aria-hidden="true"
                  />
                  {item.name}
                  {item.badge && (
                    <span className="ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-600 text-white">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>

      </div>
    </>
  );
};