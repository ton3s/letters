/**
 * Authentication configuration for Microsoft Entra ID (Azure AD)
 * using MSAL (Microsoft Authentication Library)
 */

import { Configuration, LogLevel, PublicClientApplication } from '@azure/msal-browser';

/**
 * Configuration object to be passed to MSAL instance on creation.
 * For full configuration options visit:
 * https://github.com/AzureAD/microsoft-authentication-library-for-js/blob/dev/lib/msal-browser/docs/configuration.md
 */

// Get configuration from environment variables
const clientId = process.env.REACT_APP_AZURE_AD_CLIENT_ID || '';
const tenantId = process.env.REACT_APP_AZURE_AD_TENANT_ID || '';
const redirectUri = process.env.REACT_APP_AZURE_AD_REDIRECT_URI || window.location.origin;

// Validate required configuration
if (!clientId || !tenantId) {
  console.error('Missing required Azure AD configuration. Please set REACT_APP_AZURE_AD_CLIENT_ID and REACT_APP_AZURE_AD_TENANT_ID environment variables.');
}

export const msalConfig: Configuration = {
  auth: {
    clientId: clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri: redirectUri,
    postLogoutRedirectUri: redirectUri,
    navigateToLoginRequestUrl: false, // Changed to false to prevent navigation issues
  },
  cache: {
    cacheLocation: 'sessionStorage', // Use sessionStorage for better security
    storeAuthStateInCookie: true, // Changed to true to help with popup handling
  },
  system: {
    loggerOptions: {
      loggerCallback: (level: LogLevel, message: string, containsPii: boolean) => {
        if (containsPii) {
          return;
        }
        switch (level) {
          case LogLevel.Error:
            console.error(message);
            return;
          case LogLevel.Info:
            console.info(message);
            return;
          case LogLevel.Verbose:
            console.debug(message);
            return;
          case LogLevel.Warning:
            console.warn(message);
            return;
          default:
            return;
        }
      },
      logLevel: process.env.NODE_ENV === 'development' ? LogLevel.Verbose : LogLevel.Warning,
    },
  },
};

/**
 * Scopes you add here will be prompted for user consent during sign-in.
 * By default, MSAL.js will add OIDC scopes (openid, profile, email) to any login request.
 * For more information about OIDC scopes, visit:
 * https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-permissions-and-consent#openid-connect-scopes
 */
export const loginRequest = {
  scopes: ['User.Read'], // Add API scopes here
};

/**
 * Add here the endpoints and scopes when obtaining an access token for protected web APIs.
 * For the Insurance Letter API, we'll need to add the appropriate scope once the API is registered in Azure AD
 */
export const apiRequest = {
  scopes: [
    process.env.REACT_APP_API_SCOPE || `api://${clientId}/access_as_user`
  ],
};

/**
 * Instance of the MSAL PublicClientApplication
 */
export const msalInstance = new PublicClientApplication(msalConfig);

// Account selection logic is app dependent. Adjust as needed for different use cases.
const accounts = msalInstance.getAllAccounts();
if (accounts.length > 0) {
  msalInstance.setActiveAccount(accounts[0]);
}

msalInstance.addEventCallback((event) => {
  if (event.eventType === 'msal:loginSuccess' && event.payload && 'account' in event.payload) {
    const account = event.payload.account;
    if (account) {
      msalInstance.setActiveAccount(account);
    }
  }
});

/**
 * Graph API endpoints
 */
export const graphConfig = {
  graphMeEndpoint: 'https://graph.microsoft.com/v1.0/me',
};