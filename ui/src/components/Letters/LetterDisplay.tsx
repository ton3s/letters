import React, { useState, useEffect, useCallback } from 'react';
import { LetterResponse } from '../../types';
import { AgentConversationModal } from './AgentConversationModal';
import { LetterWithPlaceholders } from './LetterWithPlaceholders';
import { LetterHistoryService } from '../../services/letterHistory';
import { PlaceholderService } from '../../services/placeholderService';
import { 
  DocumentTextIcon, 
  CheckCircleIcon,
  PrinterIcon,
  DocumentDuplicateIcon,
  ChatBubbleLeftRightIcon,
  PencilSquareIcon,
  CloudArrowUpIcon,
} from '@heroicons/react/24/outline';

interface LetterDisplayProps {
  letter: LetterResponse & { letterType?: string };
}

export const LetterDisplay: React.FC<LetterDisplayProps> = ({ letter }) => {
  const [showConversation, setShowConversation] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editedContent, setEditedContent] = useState(letter.letter_content);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');
  const [saveTimer, setSaveTimer] = useState<NodeJS.Timeout | null>(null);
  const [showActionsMenu, setShowActionsMenu] = useState(false);
  const [hasPlaceholders, setHasPlaceholders] = useState(false);

  // Check for placeholders whenever content changes
  useEffect(() => {
    const result = PlaceholderService.detect(editedContent);
    const foundPlaceholders = result.placeholders.length > 0;
    setHasPlaceholders(foundPlaceholders);
    
    // Exit edit mode if no placeholders remain
    if (!foundPlaceholders && editMode) {
      setEditMode(false);
    }
  }, [editedContent, editMode]);

  const formatLetterType = (type?: string): string => {
    if (!type) return 'Letter';
    
    const typeMap: Record<string, string> = {
      'claim_denial': 'Claim Denial Letter',
      'claim_approval': 'Claim Approval Letter',
      'policy_renewal': 'Policy Renewal Notice',
      'coverage_change': 'Coverage Change Notice',
      'premium_increase': 'Premium Increase Notice',
      'cancellation': 'Cancellation Notice',
      'welcome': 'Welcome Letter',
      'general': 'General Correspondence'
    };
    
    return typeMap[type] || 'Letter';
  };

  const handlePrint = () => {
    window.print();
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(editedContent);
    // You could add a toast notification here
  };

  // Auto-save functionality
  const handleContentUpdate = useCallback((newContent: string) => {
    setEditedContent(newContent);
    setSaveStatus('saving');

    // Clear existing timer
    if (saveTimer) {
      clearTimeout(saveTimer);
    }

    // Set new timer for debounced save
    const timer = setTimeout(() => {
      if (letter.document_id) {
        const success = LetterHistoryService.update(letter.document_id, {
          letter_content: newContent
        });
        
        if (success) {
          setSaveStatus('saved');
          // Reset to idle after 2 seconds
          setTimeout(() => setSaveStatus('idle'), 2000);
        } else {
          setSaveStatus('idle');
        }
      }
    }, 1000); // 1 second debounce

    setSaveTimer(timer);
  }, [letter.document_id, saveTimer]);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (saveTimer) {
        clearTimeout(saveTimer);
      }
    };
  }, [saveTimer]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {editMode && saveStatus !== 'idle' && (
              <span className="inline-flex items-center text-sm">
                {saveStatus === 'saving' && (
                  <>
                    <CloudArrowUpIcon className="h-4 w-4 mr-1 text-gray-400 animate-pulse" />
                    <span className="text-gray-500 dark:text-gray-400">Saving...</span>
                  </>
                )}
                {saveStatus === 'saved' && (
                  <>
                    <CheckCircleIcon className="h-4 w-4 mr-1 text-green-500" />
                    <span className="text-green-600 dark:text-green-400">Saved</span>
                  </>
                )}
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Primary Action - Only show if there are placeholders */}
            {hasPlaceholders && (
              <button
                onClick={() => setEditMode(!editMode)}
                className={`inline-flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  editMode 
                    ? 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600' 
                    : 'bg-primary-600 text-white hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600'
                } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
              >
                <PencilSquareIcon className="h-4 w-4 mr-2" />
                {editMode ? 'View Mode' : 'Edit Placeholders'}
              </button>
            )}
            
            {/* Secondary Actions Dropdown */}
            <div className="relative inline-block text-left">
              <button
                onClick={() => setShowActionsMenu(!showActionsMenu)}
                onBlur={() => setTimeout(() => setShowActionsMenu(false), 200)}
                className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Actions
                <svg className="ml-2 -mr-1 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
              
              {showActionsMenu && (
                <div className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
                  <div className="py-1">
                    <button
                      onClick={() => {
                        handleCopy();
                        setShowActionsMenu(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                    >
                      <DocumentDuplicateIcon className="h-4 w-4 mr-3" />
                      Copy to Clipboard
                    </button>
                    
                    <button
                      onClick={() => {
                        handlePrint();
                        setShowActionsMenu(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                    >
                      <PrinterIcon className="h-4 w-4 mr-3" />
                      Print Letter
                    </button>
                    
                    {letter.agent_conversation && letter.agent_conversation.length > 0 && (
                      <>
                        <div className="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                        <button
                          onClick={() => {
                            setShowConversation(true);
                            setShowActionsMenu(false);
                          }}
                          className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                        >
                          <ChatBubbleLeftRightIcon className="h-4 w-4 mr-3" />
                          View Conversation
                        </button>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Letter Content */}
        <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg overflow-hidden">
          <div className="px-8 py-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
                <DocumentTextIcon className="h-6 w-6 mr-2" />
                {formatLetterType(letter.letterType)}
              </h1>
              {letter.approval_status?.overall_approved && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                  <CheckCircleIcon className="h-4 w-4 mr-1" />
                  Approved
                </span>
              )}
            </div>
            {letter.document_id && (
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Document ID: {letter.document_id}
              </p>
            )}
          </div>
          
          <div className="px-8 py-8">
            {editMode ? (
              <LetterWithPlaceholders
                content={editedContent}
                onContentUpdate={handleContentUpdate}
                readOnly={false}
              />
            ) : (
              <div className="prose prose-lg dark:prose-invert max-w-none">
                <div className="whitespace-pre-wrap font-serif text-gray-900 dark:text-gray-100 leading-relaxed">
                  {editedContent.split('\n').map((line, index, lines) => {
                    // Style the letterhead
                    if (index === 0 && line.includes('[Insurance Company Letterhead]')) {
                      return (
                        <div key={index} className="text-center text-gray-600 dark:text-gray-400 italic mb-6">
                          {line}
                        </div>
                      );
                    }
                    
                    // Style the date
                    if (line.startsWith('Date:')) {
                      return (
                        <div key={index} className="mb-6">
                          {line}
                        </div>
                      );
                    }
                    
                    // Style the recipient info
                    if (line.startsWith('Policy Number:') || (index < 5 && line.trim() && !line.includes('Dear'))) {
                      return (
                        <div key={index} className="mb-1">
                          {line}
                        </div>
                      );
                    }
                    
                    // Style the greeting
                    if (line.startsWith('Dear')) {
                      return (
                        <div key={index} className="mb-4 mt-6">
                          {line}
                        </div>
                      );
                    }
                    
                    // Style the subject
                    if (line.startsWith('Subject:')) {
                      return (
                        <div key={index} className="font-semibold mb-4">
                          {line}
                        </div>
                      );
                    }
                    
                    // Check if we're in the signature block
                    const signatureStartIndex = lines.findIndex(l => 
                      l.includes('Sincerely,') || 
                      l.includes('Best regards,') || 
                      l.includes('Warm regards,') ||
                      l.includes('Kind regards,') ||
                      l.includes('Regards,')
                    );
                    const isSignatureLine = signatureStartIndex !== -1 && index >= signatureStartIndex;
                    
                    // Check if this is the footer separator
                    const isFooterSeparator = line.trim() === '---';
                    
                    // Style the signature block
                    if (isSignatureLine && !isFooterSeparator) {
                      // Closing (Sincerely, Best regards, etc.)
                      if (line.includes('Sincerely,') || 
                          line.includes('Best regards,') || 
                          line.includes('Warm regards,') ||
                          line.includes('Kind regards,') ||
                          line.includes('Regards,')) {
                        return (
                          <div key={index} className="mt-6 mb-2">
                            {line}
                          </div>
                        );
                      }
                      
                      // Empty lines in signature should be completely hidden
                      if (!line.trim()) {
                        return null;
                      }
                      
                      // Signature lines (name, title, company, etc.)
                      return (
                        <div key={index} className="leading-tight">
                          {line}
                        </div>
                      );
                    }
                    
                    // Style the footer separator with extra space above
                    if (isFooterSeparator) {
                      return (
                        <div key={index} className="mt-8 mb-4 text-gray-400">
                          {line}
                        </div>
                      );
                    }
                    
                    // Regular paragraphs
                    if (line.trim()) {
                      return (
                        <p key={index} className="mb-4">
                          {line}
                        </p>
                      );
                    }
                    
                    // Empty lines
                    return <div key={index} className="mb-4" />;
                  })}
                </div>
              </div>
            )}
          </div>
          
          {/* Footer */}
          <div className="px-8 py-4 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Generated on {new Date(letter.timestamp || Date.now()).toLocaleString()}
            </p>
          </div>
        </div>
      </div>
      
      {/* Agent Conversation Modal */}
      <AgentConversationModal
        isOpen={showConversation}
        onClose={() => setShowConversation(false)}
        conversation={letter.agent_conversation || []}
        totalRounds={letter.total_rounds}
      />
    </div>
  );
};