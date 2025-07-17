# Insurance Letters Application - Terraform Deployment

This Terraform configuration deploys the complete infrastructure for the Insurance Letters application on Azure, including:

- Azure Function App (Serverless)
- Azure Cosmos DB (Serverless)
- Azure Static Web Apps (Frontend)
- Azure API Management (Optional)
- Application Insights
- All necessary networking and security configurations

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Static Web App │────▶│ API Management   │────▶│  Function App   │
│    (React UI)   │     │  (Optional)      │     │   (Python API)  │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                           │
                              ┌────────────────────────────┼────────┐
                              │                            │        │
                        ┌─────▼──────┐            ┌────────▼────┐   │
                        │ Cosmos DB  │            │ Azure       │   │
                        │ (Serverless)│            │ OpenAI      │   │
                        └────────────┘            └─────────────┘   │
                                                                    │
                                                  ┌─────────────────▼┐
                                                  │ App Insights     │
                                                  └─────────────────┘
```

## Prerequisites

1. **Azure CLI** installed and authenticated
   ```bash
   az login
   az account set --subscription "your-subscription-id"
   ```

2. **Terraform** v1.3 or higher
   ```bash
   terraform --version
   ```

3. **Azure OpenAI Service** with a GPT-4 deployment

4. **Azure AD App Registration** for authentication

## Quick Start

1. **Clone and navigate to terraform directory**
   ```bash
   cd terraform
   ```

2. **Copy and configure variables**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

3. **Initialize Terraform**
   ```bash
   terraform init
   ```

4. **Review the deployment plan**
   ```bash
   terraform plan
   ```

5. **Deploy the infrastructure**
   ```bash
   terraform apply
   ```

## Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `azure_subscription_id` | Your Azure subscription ID | `12345678-1234-1234-1234-123456789012` |
| `openai_deployment_name` | Azure OpenAI deployment name | `gpt-4` |
| `openai_endpoint` | Azure OpenAI endpoint URL | `https://myopenai.openai.azure.com/` |
| `openai_api_key` | Azure OpenAI API key | `your-api-key` |
| `azure_ad_tenant_id` | Azure AD tenant ID | `12345678-1234-1234-1234-123456789012` |
| `azure_ad_client_id` | Azure AD app client ID | `12345678-1234-1234-1234-123456789012` |
| `apim_publisher_email` | Email for API Management | `admin@company.com` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `project_name` | Base name for resources | `insuranceletters` |
| `environment` | Environment name | `dev` |
| `location` | Azure region | `eastus` |
| `deploy_apim` | Deploy API Management | `true` |
| `cosmos_database_name` | Cosmos DB database name | `insurance_letters` |
| `additional_cors_origins` | Additional CORS origins | `["http://localhost:3000"]` |

## Post-Deployment Steps

### 1. Deploy Function App Code

```bash
cd ../api
func azure functionapp publish $(terraform output -raw function_app_name)
```

### 2. Deploy Frontend Application

```bash
cd ../ui

# Set environment variables
export REACT_APP_AZURE_AD_CLIENT_ID=$(terraform output -raw azure_ad_client_id)
export REACT_APP_AZURE_AD_TENANT_ID=$(terraform output -raw azure_ad_tenant_id)
export REACT_APP_AZURE_AD_REDIRECT_URI=$(terraform output -raw static_web_app_url)/redirect
export REACT_APP_API_URL=$(terraform output -raw api_management_gateway_url)
export REACT_APP_API_SCOPE="api://$(terraform output -raw azure_ad_client_id)/user_impersonation"

# Build the application
npm install
npm run build

# Deploy to Static Web Apps
az staticwebapp deployment token show \
  --name $(terraform output -raw static_web_app_name) \
  --resource-group $(terraform output -raw resource_group_name)
# Use the token with your preferred deployment method
```

### 3. Configure Azure AD

1. Go to Azure Portal > Azure Active Directory > App registrations
2. Find your application registration
3. Add redirect URIs:
   - `https://<static-web-app-url>/redirect`
   - `http://localhost:3000/redirect` (for local development)
4. Configure API permissions if needed
5. Expose an API and add scope `user_impersonation`

### 4. Verify Deployment

1. **Check Function App Health**
   ```bash
   curl https://$(terraform output -raw function_app_default_hostname)/api/health
   ```

2. **Access the application**
   - Frontend: Visit the URL from `terraform output static_web_app_url`
   - API Management Portal: Visit the URL from `terraform output api_management_developer_portal_url`

## Cost Optimization

This deployment uses serverless/consumption tiers where possible:

- **Function App**: Consumption plan (pay per execution)
- **Cosmos DB**: Serverless (pay per request)
- **API Management**: Consumption tier (pay per call)
- **Static Web Apps**: Free tier

Estimated monthly cost for light usage: $20-50

## Security Features

- JWT token validation at API Management layer
- Rate limiting (100 calls/hour, 1000 calls/day per user)
- CORS configuration for frontend domain
- Managed identities for Azure services
- Application Insights for monitoring
- Security headers in API responses

## Monitoring

Application Insights is automatically configured. View metrics:

1. Go to Azure Portal > Application Insights
2. Select your Application Insights instance
3. View:
   - Live Metrics
   - Failures
   - Performance
   - Usage Analytics

## Troubleshooting

### Common Issues

1. **Authentication errors**
   - Verify Azure AD configuration
   - Check redirect URIs match exactly
   - Ensure API scope is exposed

2. **CORS errors**
   - Add your domain to `additional_cors_origins`
   - Run `terraform apply` to update

3. **Function App not responding**
   - Check Application Insights for errors
   - Verify all app settings are correct
   - Check function app logs

### Useful Commands

```bash
# View all outputs
terraform output

# View specific output
terraform output function_app_name

# View sensitive outputs
terraform output -json cosmos_db_primary_key

# Destroy all resources
terraform destroy
```

## Maintenance

### Updating Infrastructure

```bash
# Pull latest changes
git pull

# Review changes
terraform plan

# Apply updates
terraform apply
```

### Backup and Recovery

Cosmos DB automatically handles backups in serverless mode. For additional backup:

```bash
# Export Cosmos DB data
az cosmosdb sql container export \
  --account-name $(terraform output -raw cosmos_db_account_name) \
  --database-name insurance_letters \
  --container-name letters \
  --output-file backup.json
```

## Support

For issues or questions:
1. Check Application Insights for errors
2. Review function app logs
3. Verify all configuration values
4. Check Azure service health status