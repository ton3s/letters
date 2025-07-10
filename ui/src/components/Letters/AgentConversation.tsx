import React from 'react';
import { ConversationEntry } from '../../types';
import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';

interface AgentConversationProps {
  conversation: ConversationEntry[];
  totalRounds: number;
}

export const AgentConversation: React.FC<AgentConversationProps> = ({ conversation, totalRounds }) => {
  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
        <ChatBubbleLeftRightIcon className="h-5 w-5 mr-2" />
        Agent Conversation
      </h3>
      
      <div className="space-y-4">
        {conversation.map((entry, index) => (
          <div key={index} className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-bold text-primary-500 dark:text-primary-400">
                {entry.agent}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Round {entry.round}
              </span>
            </div>
            
            <div className="text-sm text-gray-700 dark:text-gray-300 space-y-2">
              {entry.message.split('---').map((section, sectionIndex) => {
                if (section.includes('WRITER_APPROVED') || section.includes('COMPLIANCE_APPROVED')) {
                  return (
                    <div key={sectionIndex} className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                        {section.trim()}
                      </span>
                    </div>
                  );
                }
                
                // Parse the message content more intelligently
                const lines = section.trim().split('\n').filter(line => line.trim());
                
                return (
                  <div key={sectionIndex} className="space-y-2">
                    {lines.map((line, lineIndex) => {
                      // Format headers
                      if (line.includes('Subject:') || line.includes('Dear ') || line.includes('Next Steps:')) {
                        return (
                          <p key={lineIndex} className="font-medium text-gray-900 dark:text-white">
                            {line}
                          </p>
                        );
                      }
                      
                      // Format section headers
                      if (line.endsWith(':') && !line.includes('Subject:')) {
                        return (
                          <p key={lineIndex} className="font-medium text-gray-900 dark:text-white mt-3">
                            {line}
                          </p>
                        );
                      }
                      
                      // Format bullet points
                      if (line.trim().startsWith('-')) {
                        return (
                          <p key={lineIndex} className="ml-4">
                            • {line.substring(1).trim()}
                          </p>
                        );
                      }
                      
                      // Format legal disclaimer
                      if (line.includes('Legal Disclaimer:')) {
                        return (
                          <div key={lineIndex} className="mt-4 p-3 bg-gray-100 dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                            <p className="text-xs text-gray-600 dark:text-gray-400">
                              {line}
                            </p>
                          </div>
                        );
                      }
                      
                      // Regular paragraph
                      return (
                        <p key={lineIndex} className="text-gray-700 dark:text-gray-300">
                          {line}
                        </p>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
        Total rounds: {totalRounds}
      </div>
    </div>
  );
};