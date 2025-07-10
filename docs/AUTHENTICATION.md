# Authentication Setup Guide

This guide walks you through setting up Single Sign-On (SSO) authentication using Microsoft Entra ID (formerly Azure Active Directory) with the Insurance Letter Generator application.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Microsoft Entra ID Setup](#microsoft-entra-id-setup)
4. [Application Configuration](#application-configuration)
5. [Testing Authentication](#testing-authentication)
6. [Troubleshooting](#troubleshooting)

## Overview

The application uses OAuth 2.0 / OpenID Connect (OIDC) for authentication through Microsoft Entra ID. This provides:

- Single Sign-On (SSO) experience
- Secure token-based authentication
- User profile information
- Multi-tenant support (optional)

### Architecture

```
User → React App → MSAL.js → Microsoft Entra ID
                     ↓
                Access Token
                     ↓
              API Calls with Bearer Token → Azure Functions
                                                  ↓
                                           JWT Validation
```

## Prerequisites

Before starting, ensure you have:

- Azure subscription with permissions to create App Registrations
- Access to Microsoft Entra ID (Azure AD) tenant
- Admin consent privileges (for API permissions)
- The application running locally or deployed

## Microsoft Entra ID Setup

### Step 1: Create App Registration

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Go to **Microsoft Entra ID** (or Azure Active Directory)
3. Select **App registrations** from the left menu
4. Click **New registration**

Fill in the registration form:
- **Name**: `Insurance Letter Generator`
- **Supported account types**: Choose based on your needs:
  - Single tenant (your organization only)
  - Multitenant (any Azure AD organization)
  - Multitenant + personal Microsoft accounts
- **Redirect URI**: 
  - Platform: `Single-page application`
  - URI: `http://localhost:3000` (for local development)

Click **Register**

### Step 2: Configure Authentication

After registration, you'll be redirected to the app overview. Note down:
- **Application (client) ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Directory (tenant) ID**: `yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy`

1. Go to **Authentication** in the left menu
2. Under **Single-page application**, add redirect URIs:
   ```
   http://localhost:3000
   https://your-production-domain.com
   ```
3. Under **Implicit grant and hybrid flows**:
   - Check: ✓ Access tokens
   - Check: ✓ ID tokens
4. Under **Supported account types**, confirm your selection
5. Click **Save**

### Step 3: Configure API Permissions

1. Go to **API permissions** in the left menu
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Choose **Delegated permissions**
5. Add these permissions:
   - `User.Read` (Sign in and read user profile)
   - `openid` (Sign users in)
   - `profile` (View users' basic profile)
   - `email` (View users' email address)
6. Click **Add permissions**

**Important**: Click **Grant admin consent for [Your Organization]** if you have admin privileges.

### Step 4: Expose an API (For Backend)

1. Go to **Expose an API** in the left menu
2. Click **Set** next to Application ID URI
3. Accept the default: `api://[your-client-id]` or customize
4. Click **Save**
5. Click **Add a scope**:
   - **Scope name**: `access_as_user`
   - **Who can consent**: Admins and users
   - **Admin consent display name**: Access Insurance Letter API
   - **Admin consent description**: Allows the app to access the Insurance Letter API as the signed-in user
   - **User consent display name**: Access Insurance Letter API
   - **User consent description**: Allows the app to access the Insurance Letter API on your behalf
   - **State**: Enabled
6. Click **Add scope**

### Step 5: Create Client Secret (Optional - for server-side flows)

If you need server-side authentication:

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Add description: `Insurance Letter API Secret`
4. Select expiration period
5. Click **Add**
6. **Important**: Copy the secret value immediately (you won't see it again)

## Application Configuration

### Frontend Configuration (React)

Create a `.env.local` file in the `ui` directory:

```bash
# Microsoft Entra ID Configuration
REACT_APP_AZURE_AD_CLIENT_ID=your-client-id-here
REACT_APP_AZURE_AD_TENANT_ID=your-tenant-id-here
REACT_APP_AZURE_AD_REDIRECT_URI=http://localhost:3000

# API Configuration
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_API_SCOPE=api://your-client-id-here/access_as_user

# For production, use your API Management URL
# REACT_APP_API_URL=https://your-apim.azure-api.net/api
```

### Backend Configuration (Azure Functions)

Update `api/local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_AD_TENANT_ID": "your-tenant-id-here",
    "AZURE_AD_CLIENT_ID": "your-client-id-here",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "your-gpt4-deployment",
    "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
    "AZURE_OPENAI_API_KEY": "your-openai-key",
    "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
    "COSMOS_ENDPOINT": "https://your-cosmos.documents.azure.com:443/",
    "COSMOS_KEY": "your-cosmos-key"
  },
  "Host": {
    "CORS": "http://localhost:3000,https://your-production-domain.com"
  }
}
```

## Testing Authentication

### Local Testing

1. **Start the Backend**:
   ```bash
   cd api
   func start
   ```

2. **Start the Frontend**:
   ```bash
   cd ui
   npm install
   npm start
   ```

3. **Test Authentication Flow**:
   - Navigate to http://localhost:3000
   - You should be redirected to Microsoft login
   - Sign in with your Microsoft account
   - After successful login, you'll be redirected back to the app
   - Your name should appear in the top-right corner

### Testing API Authentication

Use tools like Postman or curl to test authenticated API calls:

1. **Get an Access Token**:
   - Sign in to the app
   - Open browser DevTools (F12)
   - Go to Application → Session Storage
   - Find the token under your domain
   - Or use the Network tab to see Authorization headers

2. **Make Authenticated API Call**:
   ```bash
   curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
        http://localhost:7071/api/health
   ```

### Creating Test Users

1. In Azure Portal, go to **Microsoft Entra ID**
2. Select **Users** → **New user** → **Create new user**
3. Fill in:
   - User principal name: `testuser@yourdomain.onmicrosoft.com`
   - Display name: `Test User`
   - Password: Auto-generate or create
4. Click **Create**
5. Assign necessary roles/permissions if needed

## Troubleshooting

### Common Issues

#### 1. CORS Errors
**Error**: "Access to fetch at 'login.microsoftonline.com' from origin 'http://localhost:3000' has been blocked by CORS"

**Solution**: This is normal - authentication redirects, not AJAX calls. Ensure redirect URIs are correctly configured.

#### 2. Invalid Client Error
**Error**: "AADSTS700016: Application with identifier 'xxx' was not found"

**Solution**: 
- Verify REACT_APP_AZURE_AD_CLIENT_ID is correct
- Ensure you're using the right tenant

#### 3. Token Validation Failures
**Error**: "JWT validation failed"

**Solution**:
- Ensure backend AZURE_AD_TENANT_ID and AZURE_AD_CLIENT_ID match frontend
- Check token hasn't expired
- Verify the audience claim in the token

#### 4. Consent Required
**Error**: "AADSTS65001: The user or administrator has not consented"

**Solution**:
- Grant admin consent in Azure Portal
- Or have users consent individually on first sign-in

#### 5. Redirect URI Mismatch
**Error**: "AADSTS50011: The reply URL specified in the request does not match"

**Solution**:
- Add exact redirect URI to app registration
- Include protocol (http/https) and port
- No trailing slashes

### Debug Mode

Enable verbose logging in the browser console:

```javascript
// In authConfig.ts
logLevel: LogLevel.Verbose
```

Check Azure Functions logs:
```bash
func start --verbose
```

### Token Inspection

Decode JWT tokens for debugging at [jwt.ms](https://jwt.ms) to verify:
- Issuer (iss)
- Audience (aud)
- Expiration (exp)
- User claims

## Security Best Practices

1. **Never commit credentials**:
   - Use environment variables
   - Add `.env.local` to `.gitignore`

2. **Use least privilege**:
   - Only request necessary API permissions
   - Remove unused permissions

3. **Token handling**:
   - Store tokens in sessionStorage (not localStorage)
   - Clear tokens on logout
   - Implement token refresh

4. **Production considerations**:
   - Use HTTPS everywhere
   - Implement proper CSP headers
   - Regular security reviews
   - Monitor failed authentication attempts

## Next Steps

- [Deploy to Production](DEPLOYMENT.md)
- [Configure API Management](DEPLOYMENT.md#api-management)
- [Set up monitoring](DEPLOYMENT.md#monitoring)