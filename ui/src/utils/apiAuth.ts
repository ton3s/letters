import { msalInstance, apiRequest } from '../auth/authConfig';

/**
 * Get access token for API calls
 * @returns Promise<string | null> - The access token or null if unable to acquire
 */
export async function getApiAccessToken(): Promise<string | null> {
  const accounts = msalInstance.getAllAccounts();
  
  if (accounts.length === 0) {
    return null;
  }

  const request = {
    ...apiRequest,
    account: accounts[0],
  };

  try {
    // Try to acquire token silently first
    const response = await msalInstance.acquireTokenSilent(request);
    return response.accessToken;
  } catch (error) {
    console.error('Silent token acquisition failed:', error);
    
    try {
      // Fall back to interactive method
      const response = await msalInstance.acquireTokenPopup(request);
      return response.accessToken;
    } catch (popupError) {
      console.error('Interactive token acquisition failed:', popupError);
      return null;
    }
  }
}

/**
 * Create authorization header for API requests
 * @returns Promise<{ Authorization: string } | {}> - Authorization header or empty object
 */
export async function getAuthHeader(): Promise<{ Authorization: string } | {}> {
  const token = await getApiAccessToken();
  
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  
  return {};
}