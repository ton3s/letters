import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { AuthProvider } from './auth/AuthProvider';
import { ProtectedRoute } from './auth/ProtectedRoute';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
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
        {/* Login Route */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected App Routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout onThemeToggle={toggleTheme} isDarkMode={isDarkMode} />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/generate" replace />} />
          <Route path="generate" element={<GenerateLetter />} />
          <Route path="history" element={<LetterHistory />} />
          <Route path="letter/view" element={<ViewLetter />} />
          <Route path="settings" element={<CompanySettings />} />
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
