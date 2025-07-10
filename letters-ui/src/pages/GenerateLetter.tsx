import React from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { LetterType, LetterRequest } from '../types';
import { LoadingModal, Tooltip } from '../components/Common';
import { generateLetter } from '../services/api';
import { LetterHistoryService } from '../services/letterHistory';
import { useApi } from '../hooks/useApi';
import {
  DocumentTextIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

const letterTypes: { value: LetterType; label: string; description: string }[] = [
  { value: 'claim_denial', label: 'Claim Denial', description: 'Notify customer of claim denial with reasons' },
  { value: 'claim_approval', label: 'Claim Approval', description: 'Approve insurance claim and payment details' },
  { value: 'policy_renewal', label: 'Policy Renewal', description: 'Remind customer about policy renewal' },
  { value: 'coverage_change', label: 'Coverage Change', description: 'Inform about changes in coverage' },
  { value: 'premium_increase', label: 'Premium Increase', description: 'Notify about premium rate changes' },
  { value: 'cancellation', label: 'Cancellation', description: 'Policy cancellation notice' },
  { value: 'welcome', label: 'Welcome', description: 'Welcome new policyholder' },
  { value: 'general', label: 'General', description: 'General correspondence' },
];

export const GenerateLetter: React.FC = () => {
  const navigate = useNavigate();
  const { execute: executeGenerateLetter, isLoading, error } = useApi(generateLetter);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<LetterRequest>();

  const selectedLetterType = watch('letter_type');

  const onSubmit = async (data: LetterRequest) => {
    const response = await executeGenerateLetter(data);
    if (response) {
      // Save to history
      LetterHistoryService.save(
        response, 
        data.customer_info.name, 
        data.letter_type
      );
      
      // Navigate to the letter view page after successful generation
      navigate('/letter/view', { state: { letter: response } });
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Generate Letter</h1>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Create professional insurance letters with AI assistance
        </p>
      </div>

      <div className="grid grid-cols-1 max-w-2xl mx-auto">
        {/* Form Section */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Letter Type */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Letter Type
                <Tooltip content="Choose the type of letter that best matches your purpose. This helps generate appropriate content and tone." />
              </label>
              <select
                {...register('letter_type', { required: 'Letter type is required' })}
                className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">Select a letter type</option>
                {letterTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              {selectedLetterType && (
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {letterTypes.find(t => t.value === selectedLetterType)?.description}
                </p>
              )}
              {errors.letter_type && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.letter_type.message}
                </p>
              )}
            </div>

            {/* Customer Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                Customer Information
              </h3>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Customer Name
                  <Tooltip content="Enter the full name of the policyholder as it appears on their policy documents." />
                </label>
                <input
                  {...register('customer_info.name', { required: 'Customer name is required' })}
                  type="text"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="John Doe"
                />
                {errors.customer_info?.name && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.customer_info.name.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Policy Number
                  <Tooltip content="Enter the complete policy number including any prefixes (e.g., POL-123456)." />
                </label>
                <input
                  {...register('customer_info.policy_number', { required: 'Policy number is required' })}
                  type="text"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="POL-123456"
                />
                {errors.customer_info?.policy_number && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.customer_info.policy_number.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Email (Optional)
                </label>
                <input
                  {...register('customer_info.email')}
                  type="email"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="john@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Agent Name (Optional)
                </label>
                <input
                  {...register('customer_info.agent_name')}
                  type="text"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Sarah Johnson"
                />
              </div>
            </div>

            {/* Additional Instructions */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                Additional Instructions
                <Tooltip content="Be specific about the letter content. Include relevant policy details, mention any regulatory requirements, and specify the desired tone (formal, friendly, etc.)." />
              </label>
              <textarea
                {...register('user_prompt', { required: 'Please provide instructions' })}
                rows={4}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Provide specific details about the letter content..."
              />
              {errors.user_prompt && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.user_prompt.message}
                </p>
              )}
            </div>

            {/* Options */}
            <div className="flex items-center">
              <input
                {...register('include_conversation')}
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                Show agent conversation
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-md text-sm font-bold text-white bg-primary-500 hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <DocumentTextIcon className="h-5 w-5 mr-2" />
              Generate Letter
            </button>
          </form>
        </div>

        {/* Additional Section */}
        <div className="mt-6 space-y-6">
          {/* Error Display */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <div className="flex">
                <ExclamationTriangleIcon className="h-5 w-5 text-primary-500 flex-shrink-0" />
                <div className="ml-3">
                  <h4 className="text-sm font-bold text-red-800 dark:text-red-200">
                    Error generating letter
                  </h4>
                  <p className="mt-1 text-sm text-red-700 dark:text-red-300">
                    {error.message}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Loading Modal */}
          <LoadingModal isOpen={isLoading} message="Generating letter..." />

        </div>
      </div>
    </div>
  );
};