import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { AuthProvider } from './auth/AuthProvider';
import { OptionalProtectedRoute } from './auth/OptionalProtectedRoute';
import { Layout } from './components/Layout';
import { GenerateLetter } from './pages/GenerateLetter';
import { LetterHistory } from './pages/LetterHistory';
import { ViewLetter } from './pages/ViewLetter';
import { CompanySettings } from './pages/CompanySettings';

// Main App Content
const AppContent: React.FC = () => {
  const { toggleTheme, isDarkMode } = useTheme();

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout onThemeToggle={toggleTheme} isDarkMode={isDarkMode} />}>
          <Route index element={<Navigate to="/generate" replace />} />
          <Route path="generate" element={
            <OptionalProtectedRoute>
              <GenerateLetter />
            </OptionalProtectedRoute>
          } />
          <Route path="history" element={
            <OptionalProtectedRoute>
              <LetterHistory />
            </OptionalProtectedRoute>
          } />
          <Route path="letter/view" element={
            <OptionalProtectedRoute>
              <ViewLetter />
            </OptionalProtectedRoute>
          } />
          <Route path="settings" element={
            <OptionalProtectedRoute>
              <CompanySettings />
            </OptionalProtectedRoute>
          } />
        </Route>
      </Routes>
    </Router>
  );
};

// Main App Component with Providers
function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
