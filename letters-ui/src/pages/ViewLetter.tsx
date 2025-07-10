import React from 'react';
import { useLocation, Navigate } from 'react-router-dom';
import { LetterDisplay, AgentConversation } from '../components/Letters';
import { LetterResponse } from '../types';

export const ViewLetter: React.FC = () => {
  const location = useLocation();
  const letter = location.state?.letter as LetterResponse;

  if (!letter) {
    return <Navigate to="/generate" replace />;
  }

  return (
    <div>
      <LetterDisplay letter={letter} />
      {letter.agent_conversation && letter.agent_conversation.length > 0 && (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
          <AgentConversation 
            conversation={letter.agent_conversation} 
            totalRounds={letter.total_rounds}
          />
        </div>
      )}
    </div>
  );
};