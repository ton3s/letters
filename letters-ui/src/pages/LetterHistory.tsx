import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ClockIcon, DocumentTextIcon, TrashIcon, EyeIcon } from '@heroicons/react/24/outline';
import { LetterHistoryService, StoredLetter } from '../services/letterHistory';
import { ConfirmDialog } from '../components/Common';

export const LetterHistory: React.FC = () => {
  const navigate = useNavigate();
  const [letters, setLetters] = useState<StoredLetter[]>([]);
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; letterId: string | null }>({
    isOpen: false,
    letterId: null,
  });

  useEffect(() => {
    loadLetters();
  }, []);

  const loadLetters = () => {
    const history = LetterHistoryService.getAll();
    setLetters(history);
  };

  const handleView = (letter: StoredLetter) => {
    navigate('/letter/view', { state: { letter } });
  };

  const handleDelete = (letterId: string) => {
    setDeleteConfirm({ isOpen: true, letterId });
  };

  const confirmDelete = () => {
    if (deleteConfirm.letterId) {
      LetterHistoryService.delete(deleteConfirm.letterId);
      loadLetters();
    }
    setDeleteConfirm({ isOpen: false, letterId: null });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatLetterType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Letter History</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">View and manage your previously generated letters</p>
      </div>

      {letters.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div className="text-center py-12">
            <ClockIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No letters yet</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Get started by generating your first letter.
            </p>
            <div className="mt-6">
              <a
                href="/generate"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-md text-sm font-bold rounded-md text-white bg-primary-500 hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
              >
                <DocumentTextIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                Generate Letter
              </a>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Letter Details
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Date Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {letters.map((letter) => (
                <tr key={letter.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {letter.customerName}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {letter.id}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                      {formatLetterType(letter.letterType)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {formatDate(letter.savedAt)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {letter.approval_status?.overall_approved ? (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                        Approved
                      </span>
                    ) : (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">
                        Pending
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleView(letter)}
                      className="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 mr-4"
                    >
                      <EyeIcon className="h-5 w-5 inline" />
                      <span className="ml-1">View</span>
                    </button>
                    <button
                      onClick={() => handleDelete(letter.id)}
                      className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                    >
                      <TrashIcon className="h-5 w-5 inline" />
                      <span className="ml-1">Delete</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        title="Delete Letter"
        message="Are you sure you want to delete this letter? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={confirmDelete}
        onCancel={() => setDeleteConfirm({ isOpen: false, letterId: null })}
        isDangerous
      />
    </div>
  );
};