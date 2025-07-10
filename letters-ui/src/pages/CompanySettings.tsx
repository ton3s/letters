import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CompanyProfile, CompanyProfileService } from '../services/companyProfile';
import { 
  BuildingOfficeIcon, 
  CheckCircleIcon,
  ArrowLeftIcon,
} from '@heroicons/react/24/outline';

export const CompanySettings: React.FC = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<CompanyProfile>(CompanyProfileService.getDefault());
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const savedProfile = CompanyProfileService.get();
    if (savedProfile) {
      setProfile(savedProfile);
    }
  }, []);

  const handleChange = (field: keyof CompanyProfile, value: string) => {
    setProfile(prev => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  const handleSave = () => {
    CompanyProfileService.save(profile);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleReset = () => {
    const defaultProfile = CompanyProfileService.getDefault();
    setProfile(defaultProfile);
    CompanyProfileService.save(defaultProfile);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 mb-4"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Back
        </button>
        
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
          <BuildingOfficeIcon className="h-8 w-8 mr-3" />
          Company Settings
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Configure your company information to automatically populate in generated letters
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Company Information
          </h2>
        </div>
        
        <div className="px-6 py-6 space-y-6">
          {/* Company Name */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
              Company Name
            </label>
            <input
              type="text"
              value={profile.companyName}
              onChange={(e) => handleChange('companyName', e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {/* Company Address */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
              Company Address
            </label>
            <input
              type="text"
              value={profile.companyAddress}
              onChange={(e) => handleChange('companyAddress', e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Company Phone */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                Company Phone
              </label>
              <input
                type="tel"
                value={profile.companyPhone}
                onChange={(e) => handleChange('companyPhone', e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            {/* Company Email */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                Company Email
              </label>
              <input
                type="email"
                value={profile.companyEmail}
                onChange={(e) => handleChange('companyEmail', e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          {/* Company Website */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
              Company Website
            </label>
            <input
              type="url"
              value={profile.companyWebsite}
              onChange={(e) => handleChange('companyWebsite', e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {/* Letterhead Text */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
              Letterhead Text
            </label>
            <input
              type="text"
              value={profile.letterheadText}
              onChange={(e) => handleChange('letterheadText', e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="Text to replace [Insurance Company Letterhead]"
            />
          </div>
        </div>

        {/* Default Agent Information */}
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Default Agent Information
          </h2>
          
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Agent Name */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Default Agent Name
                </label>
                <input
                  type="text"
                  value={profile.defaultAgentName || ''}
                  onChange={(e) => handleChange('defaultAgentName', e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              {/* Agent Title */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Default Agent Title
                </label>
                <input
                  type="text"
                  value={profile.defaultAgentTitle || ''}
                  onChange={(e) => handleChange('defaultAgentTitle', e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              {/* Agent Email */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Default Agent Email
                </label>
                <input
                  type="email"
                  value={profile.defaultAgentEmail || ''}
                  onChange={(e) => handleChange('defaultAgentEmail', e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              {/* Agent Phone */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Default Agent Phone
                </label>
                <input
                  type="tel"
                  value={profile.defaultAgentPhone || ''}
                  onChange={(e) => handleChange('defaultAgentPhone', e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <button
            onClick={handleReset}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Reset to Defaults
          </button>
          
          <div className="flex items-center space-x-3">
            {saved && (
              <span className="inline-flex items-center text-sm text-green-600 dark:text-green-400">
                <CheckCircleIcon className="h-5 w-5 mr-1" />
                Settings saved
              </span>
            )}
            
            <button
              onClick={handleSave}
              className="px-4 py-2 border border-transparent shadow-sm text-sm font-bold rounded-md text-white bg-primary-500 hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};