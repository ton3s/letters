# Deployment Guide

This guide covers deploying the Insurance Letter Generator application to Azure, including setting up Azure API Management (APIM) for production use.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Deploy Azure Functions](#deploy-azure-functions)
4. [Deploy React Frontend](#deploy-react-frontend)
5. [Configure API Management](#configure-api-management)
6. [Environment Configuration](#environment-configuration)
7. [Testing & Validation](#testing--validation)
8. [Monitoring & Maintenance](#monitoring--maintenance)

## Architecture Overview

### Production Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│  React App      │────▶│  Azure APIM      │────▶│ Azure Functions │
│  (Static Web)   │     │  (API Gateway)   │     │  (Backend API)  │
│                 │     │                  │     │                 │
└────────┬────────┘     └──────────────────┘     └────────┬────────┘
         │                                                  │
         │              ┌──────────────────┐                │
         └─────────────▶│                  │                │
                       │ Microsoft Entra   │                │
                       │      (Auth)       │◀───────────────┘
                       └──────────────────┘

                       ┌──────────────────┐
                       │   Cosmos DB      │
                       │  (Data Store)    │
                       └──────────────────┘
```

### Key Components

- **Azure Static Web Apps**: Hosts the React frontend
- **Azure API Management**: API gateway with authentication, rate limiting, and policies
- **Azure Functions**: Serverless backend API
- **Microsoft Entra ID**: Authentication provider
- **Azure Cosmos DB**: NoSQL database for letter storage
- **Azure OpenAI**: AI service for letter generation

## Prerequisites

Before deploying, ensure you have:

1. **Azure Resources**:
   - Azure subscription with appropriate permissions
   - Resource group created
   - Azure OpenAI service deployed with GPT-4 model

2. **Tools**:
   - Azure CLI installed and logged in
   - Node.js 18+ and npm
   - Python 3.8+
   - Azure Functions Core Tools v4

3. **Configuration**:
   - Microsoft Entra ID app registration completed (see [AUTHENTICATION.md](AUTHENTICATION.md))
   - API keys and connection strings ready

## Deploy Azure Functions

### 1. Create Function App

```bash
# Set variables
RESOURCE_GROUP="insurance-letter-rg"
LOCATION="eastus"
FUNCTION_APP_NAME="insurance-letter-api"
STORAGE_ACCOUNT="insuranceletterstorage"

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --name $FUNCTION_APP_NAME \
  --storage-account $STORAGE_ACCOUNT \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --os-type Linux
```

### 2. Configure App Settings

```bash
# Set environment variables
az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    "AZURE_AD_TENANT_ID=your-tenant-id" \
    "AZURE_AD_CLIENT_ID=your-client-id" \
    "AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt4-deployment" \
    "AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/" \
    "AZURE_OPENAI_API_KEY=your-api-key" \
    "AZURE_OPENAI_API_VERSION=2024-02-15-preview" \
    "COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com:443/" \
    "COSMOS_KEY=your-cosmos-key"
```

### 3. Deploy Function Code

```bash
cd api

# Build and deploy
func azure functionapp publish $FUNCTION_APP_NAME --python
```

### 4. Enable CORS (if not using APIM)

```bash
az functionapp cors add \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --allowed-origins "https://your-frontend-domain.com"
```

## Deploy React Frontend

### 1. Create Static Web App

```bash
STATIC_APP_NAME="insurance-letter-ui"

# Create Static Web App
az staticwebapp create \
  --name $STATIC_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --source "https://github.com/your-repo/insurance-letter" \
  --location $LOCATION \
  --branch main \
  --app-location "ui" \
  --output-location "build" \
  --sku Free
```

### 2. Configure Environment Variables

Create `ui/.env.production`:

```env
REACT_APP_AZURE_AD_CLIENT_ID=your-client-id
REACT_APP_AZURE_AD_TENANT_ID=your-tenant-id
REACT_APP_AZURE_AD_REDIRECT_URI=https://your-app.azurestaticapps.net
REACT_APP_API_URL=https://your-apim.azure-api.net/api
REACT_APP_API_SCOPE=api://your-client-id/access_as_user
REACT_APP_ENVIRONMENT=production
```

### 3. Build and Deploy

```bash
cd ui

# Install dependencies
npm install

# Build for production
npm run build

# Deploy (if not using GitHub Actions)
swa deploy ./build --env production
```

### 4. Configure Custom Domain (Optional)

```bash
az staticwebapp hostname add \
  --name $STATIC_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --hostname "letters.yourdomain.com"
```

## Configure API Management

### 1. Create APIM Instance

```bash
APIM_NAME="insurance-letter-apim"
PUBLISHER_EMAIL="admin@yourdomain.com"
PUBLISHER_NAME="Your Organization"

# Create APIM (this takes 30-40 minutes)
az apim create \
  --name $APIM_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --publisher-email $PUBLISHER_EMAIL \
  --publisher-name "$PUBLISHER_NAME" \
  --sku-name Consumption
```

### 2. Import API Definition

```bash
# Deploy API configuration
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file api/deployment/apim-config.json \
  --parameters \
    apimServiceName=$APIM_NAME \
    functionAppName=$FUNCTION_APP_NAME \
    functionAppKey=$(az functionapp keys list -g $RESOURCE_GROUP -n $FUNCTION_APP_NAME --query functionKeys.default -o tsv) \
    azureAdTenantId=your-tenant-id \
    azureAdClientId=your-client-id
```

### 3. Apply Policies

1. Go to Azure Portal → API Management → APIs
2. Select "Insurance Letter API"
3. Click on "All operations"
4. In the Inbound processing section, click "</>"
5. Replace with content from `api/deployment/apim-policies.xml`
6. Update placeholders:
   - `{tenant-id}` → Your Azure AD tenant ID
   - `{client-id}` → Your Azure AD client ID
   - `{function-app-key}` → Your function app key

### 4. Create Products and Subscriptions

```bash
# Create a product
az apim product create \
  --resource-group $RESOURCE_GROUP \
  --service-name $APIM_NAME \
  --product-id "insurance-letter-product" \
  --display-name "Insurance Letter API" \
  --description "Access to Insurance Letter Generation API" \
  --state published \
  --requires-subscription true

# Add API to product
az apim product api add \
  --resource-group $RESOURCE_GROUP \
  --service-name $APIM_NAME \
  --product-id "insurance-letter-product" \
  --api-id "insurance-letter-api"
```

## Environment Configuration

### Development vs Production

| Setting | Development | Production |
|---------|------------|------------|
| API URL | `http://localhost:7071/api` | `https://apim.azure-api.net/api` |
| Auth Redirect | `http://localhost:3000` | `https://your-app.com` |
| CORS Origins | `http://localhost:3000` | `https://your-app.com` |
| Function Auth | Anonymous + JWT | Anonymous + JWT |
| APIM | Not used | Required |

### Security Checklist

- [ ] Enable HTTPS only
- [ ] Configure CORS properly
- [ ] Set up API rate limiting
- [ ] Enable Application Insights
- [ ] Configure backup for Cosmos DB
- [ ] Set up key rotation reminders
- [ ] Enable Azure AD conditional access
- [ ] Configure network restrictions

## Testing & Validation

### 1. Test Authentication Flow

```bash
# Test health endpoint (no auth required)
curl https://your-apim.azure-api.net/api/health

# Get access token (use browser or Postman)
# Then test authenticated endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://your-apim.azure-api.net/api/draft-letter
```

### 2. Validate CORS

```javascript
// In browser console
fetch('https://your-apim.azure-api.net/api/health', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### 3. Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Test rate limiting
ab -n 1000 -c 10 -H "Authorization: Bearer TOKEN" \
   https://your-apim.azure-api.net/api/health
```

## Monitoring & Maintenance

### 1. Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app "insurance-letter-insights" \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web

# Link to Function App
INSIGHTS_KEY=$(az monitor app-insights component show \
  --app "insurance-letter-insights" \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey -o tsv)

az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings "APPINSIGHTS_INSTRUMENTATIONKEY=$INSIGHTS_KEY"
```

### 2. Set Up Alerts

```bash
# Create action group
az monitor action-group create \
  --name "insurance-letter-alerts" \
  --resource-group $RESOURCE_GROUP \
  --short-name "InsLetters" \
  --email admin "admin@yourdomain.com"

# Create metric alert for high error rate
az monitor metrics alert create \
  --name "high-error-rate" \
  --resource-group $RESOURCE_GROUP \
  --scopes "/subscriptions/{subscription-id}/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$FUNCTION_APP_NAME" \
  --condition "avg requests/failed > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action "insurance-letter-alerts"
```

### 3. Backup Strategy

```bash
# Enable Cosmos DB continuous backup
az cosmosdb update \
  --name "your-cosmos-account" \
  --resource-group $RESOURCE_GROUP \
  --backup-policy-type Continuous
```

### 4. Regular Maintenance Tasks

- **Weekly**:
  - Review Application Insights for errors
  - Check API usage and rate limit hits
  - Monitor Cosmos DB performance

- **Monthly**:
  - Review and rotate API keys
  - Update dependencies
  - Review security logs

- **Quarterly**:
  - Performance testing
  - Disaster recovery drill
  - Security audit

## Troubleshooting

### Common Issues

1. **CORS errors in production**
   - Verify APIM CORS policy includes your frontend domain
   - Check Function App CORS settings

2. **Authentication failures**
   - Verify redirect URIs in Azure AD match exactly
   - Check token audience in APIM policy

3. **Rate limiting issues**
   - Review APIM analytics
   - Adjust rate limits if needed
   - Consider implementing caching

4. **Function timeouts**
   - Check Application Insights for slow queries
   - Optimize Cosmos DB queries
   - Consider Premium Function plan

### Support Resources

- [Azure Functions Documentation](https://docs.microsoft.com/azure/azure-functions/)
- [API Management Documentation](https://docs.microsoft.com/azure/api-management/)
- [Static Web Apps Documentation](https://docs.microsoft.com/azure/static-web-apps/)

## Cost Optimization

### Estimated Monthly Costs

| Service | Tier | Estimated Cost |
|---------|------|----------------|
| Static Web App | Free | $0 |
| Function App | Consumption | $0-20 |
| API Management | Consumption | $3.50 per million calls |
| Cosmos DB | Serverless | $0.25 per million RUs |
| Application Insights | Basic | $2.30 per GB |

### Cost Saving Tips

1. Use consumption plans for sporadic usage
2. Enable auto-pause for Cosmos DB
3. Set up budget alerts
4. Review and remove unused resources
5. Use reserved capacity for predictable workloads