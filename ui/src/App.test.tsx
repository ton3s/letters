import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { PublicClientApplication } from '@azure/msal-browser';
import App from './App';

// Mock MSAL
jest.mock('@azure/msal-browser');

// Mock the auth config
jest.mock('./auth/authConfig', () => ({
  msalConfig: {
    auth: {
      clientId: 'test-client-id',
      authority: 'https://login.microsoftonline.com/test-tenant',
      redirectUri: 'http://localhost:3000'
    }
  },
  msalInstance: new PublicClientApplication({
    auth: {
      clientId: 'test-client-id',
      authority: 'https://login.microsoftonline.com/test-tenant',
      redirectUri: 'http://localhost:3000'
    }
  })
}));

// Mock MSAL React
jest.mock('@azure/msal-react', () => ({
  ...jest.requireActual('@azure/msal-react'),
  MsalProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useIsAuthenticated: () => false,
  useMsal: () => ({
    instance: {
      getAllAccounts: () => [],
      loginPopup: jest.fn(),
      logoutPopup: jest.fn(),
    },
    accounts: [],
    inProgress: 'none'
  })
}));

describe('App Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('renders without crashing', () => {
    render(<App />);
    // The app should render without errors
    expect(document.querySelector('div')).toBeInTheDocument();
  });

  test('displays app title', async () => {
    render(<App />);
    
    // Wait for the app to render and find the title
    await waitFor(() => {
      const titleElement = screen.getByText(/Insurance Letter Generator/i);
      expect(titleElement).toBeInTheDocument();
    });
  });

  test('shows login button when not authenticated', async () => {
    render(<App />);
    
    // When not authenticated, should show Sign In button
    await waitFor(() => {
      const loginButton = screen.getByText(/Sign In/i);
      expect(loginButton).toBeInTheDocument();
    });
  });

  test('redirects to login when accessing protected route', async () => {
    render(<App />);
    
    // The app should attempt to protect routes
    // Since we're not authenticated, it should show login UI
    await waitFor(() => {
      const loginButton = screen.getByText(/Sign In/i);
      expect(loginButton).toBeInTheDocument();
    });
  });
});

describe('App Component - Authenticated', () => {
  beforeEach(() => {
    // Mock authenticated state
    jest.mock('@azure/msal-react', () => ({
      ...jest.requireActual('@azure/msal-react'),
      MsalProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
      useIsAuthenticated: () => true,
      useMsal: () => ({
        instance: {
          getAllAccounts: () => [{
            username: 'test@example.com',
            name: 'Test User',
            localAccountId: 'test-id'
          }],
          loginPopup: jest.fn(),
          logoutPopup: jest.fn(),
        },
        accounts: [{
          username: 'test@example.com',
          name: 'Test User',
          localAccountId: 'test-id'
        }],
        inProgress: 'none'
      })
    }));
  });

  test('shows navigation when authenticated', async () => {
    render(<App />);
    
    // When authenticated, navigation should be visible
    await waitFor(() => {
      expect(screen.getByText(/Generate Letter/i)).toBeInTheDocument();
      expect(screen.getByText(/Letter History/i)).toBeInTheDocument();
    });
  });
});