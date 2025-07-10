import React, { createContext, useContext, useEffect, useState } from 'react';
import { 
  MsalProvider, 
  useMsal, 
  useIsAuthenticated,
  AuthenticatedTemplate,
  UnauthenticatedTemplate
} from '@azure/msal-react';
import { InteractionStatus, AccountInfo, SilentRequest } from '@azure/msal-browser';
import { msalInstance, loginRequest, apiRequest } from './authConfig';

interface AuthContextType {
  isAuthenticated: boolean;
  user: AccountInfo | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  getAccessToken: () => Promise<string | null>;
  isLoading: boolean;
  error: Error | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Hook to access authentication context
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * Internal component that provides authentication functionality
 */
const AuthProviderInner: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { instance, accounts, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [user, setUser] = useState<AccountInfo | null>(null);

  useEffect(() => {
    if (accounts.length > 0) {
      setUser(accounts[0]);
    } else {
      setUser(null);
    }
  }, [accounts]);

  // Handle redirect response
  useEffect(() => {
    const handleRedirectPromise = async () => {
      try {
        const response = await instance.handleRedirectPromise();
        if (response && response.account) {
          instance.setActiveAccount(response.account);
          setUser(response.account);
        }
      } catch (error) {
        console.error('Error handling redirect:', error);
      }
    };

    handleRedirectPromise();
  }, [instance]);

  /**
   * Handles user login using redirect
   */
  const login = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Use redirect instead of popup to avoid hash issues
      await instance.loginRedirect({
        ...loginRequest,
        redirectStartPage: window.location.href
      });
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Login failed'));
      console.error('Login error:', err);
      setIsLoading(false);
    }
  };

  /**
   * Handles user logout
   */
  const logout = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      await instance.logoutRedirect({
        postLogoutRedirectUri: '/'
      });
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Logout failed'));
      console.error('Logout error:', err);
      setIsLoading(false);
    }
  };

  /**
   * Gets an access token for API calls
   */
  const getAccessToken = async (): Promise<string | null> => {
    if (!accounts.length) return null;

    const request: SilentRequest = {
      ...apiRequest,
      account: accounts[0],
    };

    try {
      // Try to acquire token silently first
      const response = await instance.acquireTokenSilent(request);
      return response.accessToken;
    } catch (error) {
      console.error('Silent token acquisition failed, attempting popup', error);
      
      try {
        // Fall back to interactive method
        const response = await instance.acquireTokenPopup(request);
        return response.accessToken;
      } catch (popupError) {
        console.error('Token acquisition failed:', popupError);
        return null;
      }
    }
  };

  const contextValue: AuthContextType = {
    isAuthenticated,
    user,
    login,
    logout,
    getAccessToken,
    isLoading: isLoading || inProgress !== InteractionStatus.None,
    error,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Main AuthProvider component that wraps the app with MSAL provider
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <MsalProvider instance={msalInstance}>
      <AuthProviderInner>
        {children}
      </AuthProviderInner>
    </MsalProvider>
  );
};

/**
 * Export authentication templates for conditional rendering
 */
export { AuthenticatedTemplate, UnauthenticatedTemplate };