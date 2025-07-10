# Local Development Guide

This guide provides detailed instructions for setting up and running the Insurance Letter Generator on your local development workstation.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Azure Services Configuration](#azure-services-configuration)
4. [Running the Application](#running-the-application)
5. [Development Workflow](#development-workflow)
6. [Testing](#testing)
7. [Debugging](#debugging)
8. [Troubleshooting](#troubleshooting)
9. [Development Tools](#development-tools)

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Ubuntu 20.04+
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: At least 10GB free space
- **CPU**: Multi-core processor recommended

### Required Software

1. **Python 3.8 or higher**
   ```bash
   # Check Python version
   python --version  # or python3 --version
   
   # Install Python from https://www.python.org/downloads/
   ```

2. **Node.js 18+ and npm**
   ```bash
   # Check Node.js version
   node --version
   
   # Check npm version
   npm --version
   
   # Install from https://nodejs.org/
   ```

3. **Azure Functions Core Tools v4**
   ```bash
   # macOS
   brew tap azure/functions
   brew install azure-functions-core-tools@4
   
   # Windows (using Chocolatey)
   choco install azure-functions-core-tools
   
   # Ubuntu/Debian
   curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
   sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
   sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'
   sudo apt-get update
   sudo apt-get install azure-functions-core-tools-4
   ```

4. **Git**
   ```bash
   # Check Git version
   git --version
   
   # Install from https://git-scm.com/downloads
   ```

5. **Azure Storage Emulator or Azurite** (for local development)
   ```bash
   # Install Azurite globally
   npm install -g azurite
   ```

### Azure Account Requirements

- Azure subscription (free tier works for development)
- Access to create:
  - Azure OpenAI resource
  - Microsoft Entra ID app registration
  - Cosmos DB account (optional for local dev)

## Initial Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd letters
```

### 2. Run the Setup Script

```bash
# Make the setup script executable
chmod +x setup.sh

# Run the setup
./setup.sh
```

The setup script will:
- Check Python version
- Create a virtual environment
- Install Python dependencies
- Check for Azure Functions Core Tools
- Create configuration files from examples

### 3. Manual Setup (if setup.sh fails)

```bash
# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r api/requirements.txt

# Install UI dependencies
cd ui
npm install
cd ..
```

## Azure Services Configuration

### 1. Azure OpenAI Setup

1. **Create Azure OpenAI Resource**
   ```bash
   # Using Azure CLI
   az cognitiveservices account create \
     --name "your-openai-resource" \
     --resource-group "your-resource-group" \
     --kind "OpenAI" \
     --sku "S0" \
     --location "eastus" \
     --yes
   ```

2. **Deploy GPT-4 Model**
   - Go to Azure Portal → Your OpenAI resource
   - Click "Model deployments" → "Create"
   - Select "gpt-4" model
   - Name it (e.g., "gpt-4")
   - Note the deployment name

3. **Get Credentials**
   - In Azure Portal → Your OpenAI resource → "Keys and Endpoint"
   - Copy Key 1 and Endpoint

### 2. Microsoft Entra ID Setup

Follow the detailed guide in [AUTHENTICATION.md](AUTHENTICATION.md). Key steps:

1. **Create App Registration**
   - Name: "Insurance Letter Generator (Local)"
   - Redirect URI: `http://localhost:3000`
   - Note the Application (client) ID and Directory (tenant) ID

2. **Configure API Permissions**
   - Add `User.Read` permission
   - Grant admin consent

3. **Expose an API**
   - Set Application ID URI: `api://[your-client-id]`
   - Add scope: `access_as_user`

### 3. Configure Environment Variables

#### Backend Configuration (api/local.settings.json)

```bash
# Copy the example file
cp api/local.settings.json.example api/local.settings.json
```

Edit `api/local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_AD_TENANT_ID": "your-tenant-id",
    "AZURE_AD_CLIENT_ID": "your-client-id",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4",
    "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
    "AZURE_OPENAI_API_KEY": "your-openai-key",
    "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
    "COSMOS_ENDPOINT": "",  // Optional for local dev
    "COSMOS_KEY": ""        // Optional for local dev
  },
  "Host": {
    "CORS": "http://localhost:3000"
  }
}
```

#### Frontend Configuration (ui/.env.local)

```bash
# Copy the example file
cp ui/.env.example ui/.env.local
```

Edit `ui/.env.local`:
```env
# Microsoft Entra ID Configuration
REACT_APP_AZURE_AD_CLIENT_ID=your-client-id
REACT_APP_AZURE_AD_TENANT_ID=your-tenant-id
REACT_APP_AZURE_AD_REDIRECT_URI=http://localhost:3000

# API Configuration
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_API_SCOPE=api://your-client-id/access_as_user

# Environment
REACT_APP_ENVIRONMENT=development
```

### 4. Optional: Local Cosmos DB Emulator

If you want to test with local data persistence:

1. **Install Cosmos DB Emulator**
   - Windows: [Download here](https://aka.ms/cosmosdb-emulator)
   - macOS/Linux: Use Docker
     ```bash
     docker run -p 8081:8081 -p 10251:10251 -p 10252:10252 -p 10253:10253 -p 10254:10254 \
       --name cosmosdb-emulator \
       -e AZURE_COSMOS_EMULATOR_PARTITION_COUNT=10 \
       -e AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE=true \
       mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator
     ```

2. **Update Configuration**
   ```json
   {
     "COSMOS_ENDPOINT": "https://localhost:8081",
     "COSMOS_KEY": "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
   }
   ```

## Running the Application

### 1. Start Azurite (Storage Emulator)

```bash
# In a new terminal
azurite --silent --location azurite-data
```

### 2. Start the Backend API

```bash
# In a new terminal
cd api

# Activate Python virtual environment
# On macOS/Linux:
source ../venv/bin/activate
# On Windows:
..\venv\Scripts\activate

# Start Azure Functions
func start

# You should see:
# Functions:
#   health: [GET] http://localhost:7071/api/health
#   draft-letter: [POST] http://localhost:7071/api/draft-letter
#   suggest-letter-type: [POST] http://localhost:7071/api/suggest-letter-type
#   validate-letter: [POST] http://localhost:7071/api/validate-letter
```

### 3. Start the Frontend UI

```bash
# In a new terminal
cd ui

# Start the React development server
npm start

# The browser should open automatically to http://localhost:3000
```

### 4. Verify Everything Works

1. **Test Backend Health**
   ```bash
   curl http://localhost:7071/api/health
   ```

2. **Test Frontend**
   - Navigate to http://localhost:3000
   - You should see the login page
   - Click "Sign In" to authenticate with Microsoft

### 5. Using the CLI Tool (Optional)

```bash
cd cli-tool

# Activate Python virtual environment
source ../venv/bin/activate

# Run interactive mode
python insurance_cli.py --interactive

# Or run directly
python insurance_cli.py \
  --customer-name "John Doe" \
  --policy-number "POL-123456" \
  --letter-type "welcome" \
  --prompt "Welcome new customer to auto insurance"
```

## Development Workflow

### Making Code Changes

#### Backend Changes
- The Azure Functions runtime supports hot reload
- Changes to Python files are detected automatically
- If you add new dependencies, restart the Functions host

#### Frontend Changes
- React development server supports hot module replacement (HMR)
- Changes are reflected immediately in the browser
- CSS/Tailwind changes are applied instantly

### Git Workflow

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push to remote
git push origin feature/your-feature-name
```

### Code Style

#### Python (Backend)
```bash
# Format code with Black
black api/

# Lint with flake8
flake8 api/ --max-line-length=100

# Type checking with mypy
mypy api/
```

#### TypeScript/React (Frontend)
```bash
cd ui

# Format code
npm run format

# Lint
npm run lint

# Type checking
npm run type-check
```

## Testing

### Backend Tests

```bash
cd api

# Run all tests
python -m pytest

# Run with coverage
python tests/run_tests.py --coverage

# Run specific test file
python -m pytest tests/test_agent_system.py

# Run tests matching pattern
python -m pytest -k "test_generate_letter"

# Run with verbose output
python -m pytest -v
```

### Frontend Tests

```bash
cd ui

# Run all tests
npm test

# Run with coverage
npm test -- --coverage --watchAll=false

# Run specific test file
npm test -- --testPathPattern=App.test.tsx

# Run in watch mode
npm test -- --watchAll
```

### CLI Tests

```bash
cd cli-tool/tests

# Run conversation tests
python test_conversation.py

# Run demo
python demo_conversation.py
```

### Manual Testing

1. **Test Letter Generation**
   - Create different letter types
   - Test with various customer information
   - Verify agent conversations work

2. **Test Authentication**
   - Sign in/out flow
   - Token refresh
   - Protected route access

3. **Test Error Handling**
   - Invalid inputs
   - Network failures
   - API errors

## Debugging

### VS Code Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to Python Functions",
      "type": "python",
      "request": "attach",
      "port": 9091,
      "preLaunchTask": "func: host start"
    },
    {
      "name": "Debug React App",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/ui/src",
      "sourceMapPathOverrides": {
        "webpack:///src/*": "${webRoot}/*"
      }
    }
  ]
}
```

### Backend Debugging

1. **Enable Debug Mode**
   ```bash
   # Start Functions with debugging
   func start --debug
   ```

2. **Add Breakpoints**
   - Set breakpoints in VS Code
   - Use the "Attach to Python Functions" configuration

3. **View Logs**
   ```bash
   # Verbose logging
   func start --verbose
   ```

### Frontend Debugging

1. **Browser DevTools**
   - Use Chrome/Edge DevTools
   - React Developer Tools extension
   - Network tab for API calls

2. **Console Logging**
   ```typescript
   console.log('Component state:', state);
   console.debug('API response:', response);
   ```

3. **React Query DevTools** (if using React Query)
   ```typescript
   import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
   
   // Add to your app
   <ReactQueryDevtools initialIsOpen={false} />
   ```

## Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use

**Error**: "Port 7071 is already in use"

**Solution**:
```bash
# Find process using port
# macOS/Linux:
lsof -i :7071
kill -9 <PID>

# Windows:
netstat -ano | findstr :7071
taskkill /PID <PID> /F

# Or use different port:
func start --port 7072
```

#### 2. Authentication Errors

**Error**: "AADSTS700016: Application not found"

**Solutions**:
- Verify AZURE_AD_CLIENT_ID is correct in both frontend and backend
- Ensure redirect URI matches exactly (including trailing slashes)
- Check you're using the correct tenant

#### 3. CORS Errors

**Error**: "Access blocked by CORS policy"

**Solutions**:
- Ensure `local.settings.json` includes CORS configuration
- Verify frontend URL in CORS settings
- Check API URL in frontend `.env.local`

#### 4. Azure OpenAI Errors

**Error**: "Invalid API key" or "Resource not found"

**Solutions**:
- Verify API key and endpoint in `local.settings.json`
- Ensure deployment name matches your Azure OpenAI deployment
- Check API version is supported

#### 5. Module Not Found

**Error**: "ModuleNotFoundError" (Python) or "Module not found" (Node.js)

**Solutions**:
```bash
# Python
pip install -r api/requirements.txt

# Node.js
cd ui && npm install
```

#### 6. Functions Runtime Not Starting

**Error**: "No job functions found"

**Solutions**:
- Ensure you're in the `api` directory
- Check Python version compatibility
- Verify `function_app.py` exists
- Clear Functions cache: `func start --clear`

### Environment-Specific Issues

#### macOS
- If using M1/M2 Macs, ensure Rosetta 2 is installed
- Some Python packages may need `--no-binary :all:` flag

#### Windows
- Run terminals as Administrator if permission errors occur
- Use PowerShell instead of Command Prompt
- Ensure Windows Defender isn't blocking ports

#### Linux
- May need to install additional system packages:
  ```bash
  sudo apt-get install python3-dev build-essential
  ```

## Development Tools

### Recommended VS Code Extensions

```json
{
  "recommendations": [
    // Python
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    
    // Azure
    "ms-azuretools.vscode-azurefunctions",
    "ms-azuretools.vscode-azurestorage",
    
    // React/TypeScript
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    
    // General
    "eamodio.gitlens",
    "streetsidesoftware.code-spell-checker",
    "usernamehw.errorlens"
  ]
}
```

### API Testing Tools

1. **Postman**
   - Import the API collection from `docs/postman_collection.json`
   - Set up environment variables

2. **REST Client (VS Code)**
   Create `api.http`:
   ```http
   @baseUrl = http://localhost:7071/api
   @token = <your-jwt-token>

   ### Health Check
   GET {{baseUrl}}/health

   ### Generate Letter
   POST {{baseUrl}}/draft-letter
   Authorization: Bearer {{token}}
   Content-Type: application/json

   {
     "customer_info": {
       "name": "John Doe",
       "policy_number": "POL-123456"
     },
     "letter_type": "welcome",
     "user_prompt": "Welcome new customer"
   }
   ```

3. **cURL Examples**
   ```bash
   # Health check
   curl http://localhost:7071/api/health | jq

   # Generate letter (with token)
   curl -X POST http://localhost:7071/api/draft-letter \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d @letter-request.json | jq
   ```

### Performance Monitoring

1. **Backend Monitoring**
   ```python
   # Add to function_app.py for local profiling
   import cProfile
   import pstats
   
   profiler = cProfile.Profile()
   profiler.enable()
   # ... function code ...
   profiler.disable()
   stats = pstats.Stats(profiler)
   stats.sort_stats('cumulative').print_stats(10)
   ```

2. **Frontend Performance**
   - Use React DevTools Profiler
   - Chrome Performance tab
   - Lighthouse audits

### Database Tools

1. **Azure Storage Explorer**
   - View Azurite tables and queues
   - Download from [here](https://azure.microsoft.com/features/storage-explorer/)

2. **Cosmos DB Explorer**
   - For local emulator: https://localhost:8081/_explorer/index.html
   - For cloud: Use Azure Portal Data Explorer

## Next Steps

1. Review the [Architecture Guide](ARCHITECTURE.md) to understand the system design
2. Read the [Agent System Guide](AGENT_SYSTEM_GUIDE.md) to understand the AI components
3. Check [Code Improvements](CODE_IMPROVEMENTS.md) for enhancement ideas
4. Join the development community (if applicable)

## Additional Resources

- [Azure Functions Python Developer Guide](https://docs.microsoft.com/azure/azure-functions/functions-reference-python)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Microsoft Entra ID Documentation](https://learn.microsoft.com/entra/identity/)