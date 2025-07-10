import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { Layout } from './components/Layout';
import { GenerateLetter } from './pages/GenerateLetter';
import { LetterHistory } from './pages/LetterHistory';
import { ViewLetter } from './pages/ViewLetter';

// Main App Content
const AppContent: React.FC = () => {
  const { toggleTheme, isDarkMode } = useTheme();

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout onThemeToggle={toggleTheme} isDarkMode={isDarkMode} />}>
          <Route index element={<Navigate to="/generate" replace />} />
          <Route path="generate" element={<GenerateLetter />} />
          <Route path="history" element={<LetterHistory />} />
          <Route path="letter/view" element={<ViewLetter />} />
        </Route>
      </Routes>
    </Router>
  );
};

// Main App Component with Providers
function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
