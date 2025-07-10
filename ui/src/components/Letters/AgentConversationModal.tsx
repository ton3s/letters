import React, { useState } from 'react';
import { XMarkIcon, ChatBubbleLeftRightIcon, DocumentTextIcon, ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import { ConversationEntry } from '../../types';

interface AgentConversationModalProps {
  isOpen: boolean;
  onClose: () => void;
  conversation: ConversationEntry[];
  totalRounds: number;
}

export const AgentConversationModal: React.FC<AgentConversationModalProps> = ({
  isOpen,
  onClose,
  conversation,
  totalRounds,
}) => {
  const [expandedEntries, setExpandedEntries] = useState<Set<number>>(new Set());

  if (!isOpen) return null;

  // Format agent names to add spaces between words
  const formatAgentName = (name: string): string => {
    // Add spaces before capital letters (except the first one)
    return name.replace(/([A-Z])/g, ' $1').trim();
  };

  // Extract the agent's feedback/comments from the full message
  const extractAgentFeedback = (message: string, agent: string): string => {
    // For Letter Writer, we want to extract just the status
    if (agent === 'LetterWriter') {
      const statusMatch = message.match(/(WRITER_APPROVED|WRITER_REJECTED)/);
      return statusMatch ? `Status: ${statusMatch[1]}` : 'Letter drafted';
    }
    
    // For other agents, remove the letter content and keep their feedback
    const lines = message.split('\n');
    const feedbackLines: string[] = [];
    let isLetterContent = false;
    
    for (const line of lines) {
      // Skip email addresses and letter headers
      if (line.includes('@') && line.includes('.com')) {
        isLetterContent = true;
        continue;
      }
      
      // Stop when we hit the letter content markers
      if (line.includes('Dear ') || line.includes('Subject:')) {
        isLetterContent = true;
        continue;
      }
      
      // Resume after finding agent status
      if (line.includes('_APPROVED') || line.includes('_REJECTED')) {
        isLetterContent = false;
        feedbackLines.push(line);
        continue;
      }
      
      // Add non-letter content lines
      if (!isLetterContent && line.trim()) {
        feedbackLines.push(line);
      }
    }
    
    return feedbackLines.join('\n').trim();
  };

  // Extract the letter content from the message
  const extractLetterContent = (message: string): string => {
    const lines = message.split('\n');
    const letterLines: string[] = [];
    let isLetterContent = false;
    
    for (const line of lines) {
      // Start capturing at email or Dear
      if ((line.includes('@') && line.includes('.com')) || line.includes('Dear ')) {
        isLetterContent = true;
      }
      
      // Stop at status markers
      if (line.includes('_APPROVED') || line.includes('_REJECTED')) {
        break;
      }
      
      if (isLetterContent) {
        letterLines.push(line);
      }
    }
    
    return letterLines.join('\n').trim();
  };

  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedEntries);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedEntries(newExpanded);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />
      
      {/* Modal */}
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-5xl max-h-[85vh] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center">
              <ChatBubbleLeftRightIcon className="h-5 w-5 mr-2" />
              Agent Review Process - Audit Trail
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          
          {/* Content */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            {conversation && conversation.length > 0 ? (
              <div className="space-y-4">
                {conversation.map((entry, index) => {
                  const feedback = extractAgentFeedback(entry.message, entry.agent);
                  const letterContent = extractLetterContent(entry.message);
                  const isExpanded = expandedEntries.has(index);
                  const hasLetterContent = letterContent.length > 0;
                  
                  // Determine status color
                  const isApproved = entry.message.includes('_APPROVED');
                  const isRejected = entry.message.includes('_REJECTED');
                  
                  return (
                    <div key={index} className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                      {/* Agent Header */}
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <span className="text-sm font-bold text-primary-600 dark:text-primary-400">
                            {formatAgentName(entry.agent)}
                          </span>
                          {isApproved && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                              Approved
                            </span>
                          )}
                          {isRejected && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400">
                              Rejected
                            </span>
                          )}
                        </div>
                        <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                          <span>Round {entry.round}</span>
                          {entry.timestamp && (
                            <>
                              <span>•</span>
                              <span>{new Date(entry.timestamp).toLocaleString()}</span>
                            </>
                          )}
                        </div>
                      </div>
                      
                      {/* Agent Feedback */}
                      <div className="text-sm text-gray-700 dark:text-gray-300">
                        {feedback.split('\n').map((line, lineIndex) => {
                          // Format bullet points
                          if (line.trim().startsWith('•') || line.trim().startsWith('-') || /^\d+\./.test(line.trim())) {
                            return (
                              <p key={lineIndex} className="ml-4 my-1">
                                {line}
                              </p>
                            );
                          }
                          
                          // Format recommendations/headers
                          if (line.includes('Recommended') || line.includes('Important') || line.endsWith(':')) {
                            return (
                              <p key={lineIndex} className="font-semibold text-gray-900 dark:text-white mt-3 mb-1">
                                {line}
                              </p>
                            );
                          }
                          
                          // Regular text
                          return line.trim() ? (
                            <p key={lineIndex} className="my-1">
                              {line}
                            </p>
                          ) : null;
                        })}
                      </div>
                      
                      {/* Letter Content Toggle */}
                      {hasLetterContent && (
                        <div className="mt-4">
                          <button
                            onClick={() => toggleExpanded(index)}
                            className="flex items-center space-x-2 text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                          >
                            {isExpanded ? (
                              <ChevronDownIcon className="h-4 w-4" />
                            ) : (
                              <ChevronRightIcon className="h-4 w-4" />
                            )}
                            <DocumentTextIcon className="h-4 w-4" />
                            <span>View Letter State at Round {entry.round}</span>
                          </button>
                          
                          {/* Expanded Letter Content */}
                          {isExpanded && (
                            <div className="mt-3 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                              <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider mb-2">
                                Letter Content - Round {entry.round}
                              </h4>
                              <pre className="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-mono">
                                {letterContent}
                              </pre>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 dark:text-gray-400">
                  No agent conversation available for this letter.
                </p>
              </div>
            )}
          </div>
          
          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Total review rounds: {totalRounds || 0}
              </p>
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};