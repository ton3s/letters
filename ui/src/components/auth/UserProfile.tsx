import React, { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { useAuth } from '../../auth/AuthProvider';
import { LogoutButton } from './LogoutButton';
import { 
  UserCircleIcon, 
  ChevronDownIcon,
  UserIcon,
  EnvelopeIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';

export const UserProfile: React.FC = () => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return null;
  }

  // Extract initials from name
  const getInitials = (name: string) => {
    const names = name.split(' ');
    if (names.length >= 2) {
      return `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const initials = user.name ? getInitials(user.name) : user.username?.substring(0, 2).toUpperCase() || 'U';

  return (
    <Menu as="div" className="relative">
      <Menu.Button className="flex items-center max-w-xs text-sm bg-white rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 lg:p-2 lg:rounded-md lg:hover:bg-gray-50">
        <div className="flex items-center justify-center w-8 h-8 text-white bg-red-600 rounded-full">
          <span className="text-sm font-medium">{initials}</span>
        </div>
        <span className="hidden ml-3 text-gray-700 lg:block">
          <span className="text-sm font-medium">{user.name || user.username}</span>
        </span>
        <ChevronDownIcon
          className="flex-shrink-0 hidden w-5 h-5 ml-1 text-gray-400 lg:block"
          aria-hidden="true"
        />
      </Menu.Button>
      
      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className="absolute right-0 z-10 w-64 py-1 mt-2 origin-top-right bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
          <div className="px-4 py-3 border-b border-gray-200">
            <p className="text-sm font-medium text-gray-900">{user.name || user.username}</p>
            {user.username && (
              <p className="text-sm text-gray-500 truncate">{user.username}</p>
            )}
          </div>
          
          <div className="py-1">
            <Menu.Item disabled>
              <div className="flex items-center px-4 py-2 text-sm text-gray-700">
                <UserIcon className="w-5 h-5 mr-3 text-gray-400" />
                <span className="truncate">{user.name || 'No name'}</span>
              </div>
            </Menu.Item>
            
            {user.username && (
              <Menu.Item disabled>
                <div className="flex items-center px-4 py-2 text-sm text-gray-700">
                  <EnvelopeIcon className="w-5 h-5 mr-3 text-gray-400" />
                  <span className="truncate">{user.username}</span>
                </div>
              </Menu.Item>
            )}
            
            {user.tenantId && (
              <Menu.Item disabled>
                <div className="flex items-center px-4 py-2 text-sm text-gray-700">
                  <BuildingOfficeIcon className="w-5 h-5 mr-3 text-gray-400" />
                  <span className="text-xs truncate">Tenant: {user.tenantId}</span>
                </div>
              </Menu.Item>
            )}
          </div>
          
          <div className="pt-1 border-t border-gray-200">
            <Menu.Item>
              {({ active }) => (
                <div className={`${active ? 'bg-gray-100' : ''} px-4 py-2`}>
                  <LogoutButton variant="text" className="w-full text-left" />
                </div>
              )}
            </Menu.Item>
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  );
};