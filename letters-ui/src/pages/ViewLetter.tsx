import React from 'react';
import { useLocation, Navigate } from 'react-router-dom';
import { LetterDisplay } from '../components/Letters';
import { LetterResponse } from '../types';

export const ViewLetter: React.FC = () => {
  const location = useLocation();
  const letter = location.state?.letter as LetterResponse;

  if (!letter) {
    return <Navigate to="/generate" replace />;
  }

  return <LetterDisplay letter={letter} />;
};