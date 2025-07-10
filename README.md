# Insurance Letter Drafting Application

A comprehensive insurance letter drafting application with a React UI, Azure Functions API, and CLI tool. Features multi-agent AI orchestration for professional letter generation with compliance review.

## Features

- **Single Sign-On (SSO)**: Secure authentication with Microsoft Entra ID (Azure AD)
- **React Web Interface**: Modern, responsive UI for letter generation and management
- **Multi-Agent System**: Three specialized AI agents collaborate to create professional insurance letters
  - Letter Writer Agent: Creates professional insurance letters
  - Compliance Reviewer Agent: Reviews letters for regulatory compliance
  - Customer Service Agent: Ensures customer-friendly tone and clarity
- **Company Profile Management**: Pre-fill common information across all letters
- **Placeholder System**: Smart detection and editing of placeholder values
- **Letter History**: Save and retrieve generated letters with full audit trail
- **Real-time Progress Tracking**: See which agent is working during letter generation
- **Auto-save**: Automatic saving of edits to letter content
- **API Management**: Production-ready with Azure API Management integration
- **CLI Tool**: Full-featured command-line interface for testing and automation
- **Comprehensive Test Suite**: 80%+ code coverage with unit and integration tests

## Project Structure

```
letters/
├── api/                         # Azure Functions Backend
│   ├── function_app.py         # Main Azure Functions app
│   ├── services/               # Backend services
│   │   ├── agent_system.py     # Multi-agent Semantic Kernel system
│   │   ├── cosmos_service.py   # Cosmos DB integration
│   │   └── models.py           # Data models
│   ├── tests/                  # API unit and integration tests
│   │   ├── test_*.py          # Test files
│   │   ├── run_tests.py       # Test runner
│   │   └── manual/            # Manual testing scripts
│   ├── deployment/            # Deployment configurations
│   ├── middleware/            # Authentication middleware
│   ├── host.json              # Azure Functions configuration
│   ├── local.settings.json    # Local development settings
│   └── requirements.txt       # Python dependencies
├── ui/                         # React Frontend
│   ├── src/
│   │   ├── auth/              # Authentication components
│   │   ├── components/        # React components
│   │   │   └── __tests__/     # Component tests
│   │   ├── pages/             # Page components
│   │   ├── services/          # Frontend services
│   │   ├── App.tsx            # Main React app
│   │   └── App.test.tsx       # App tests
│   ├── package.json           # Node dependencies
│   └── .env.example           # Environment variables example
├── cli-tool/                   # Command Line Interface
│   ├── insurance_cli.py       # CLI testing tool
│   └── tests/                 # CLI tests
│       ├── test_*.py         # Test files
│       └── README.md         # Test documentation
├── docs/                       # Documentation
│   ├── AUTHENTICATION.md      # SSO setup guide
│   └── DEPLOYMENT.md          # Production deployment guide
├── setup.sh                    # Setup script
├── CHANGELOG.md               # Version history
└── README.md                  # This file
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Azure Functions Core Tools v4
- Azure OpenAI resource with GPT-4 deployment
- Azure Cosmos DB account (optional for local development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd letters
chmod +x setup.sh
./setup.sh
```

### 2. Configure Authentication and Azure Services

#### Set up Microsoft Entra ID (Required for UI)
Follow the [Authentication Setup Guide](docs/AUTHENTICATION.md) to configure SSO.

#### Configure Backend Services
Copy the example settings file and update with your Azure credentials:

```bash
cp api/local.settings.json.example api/local.settings.json
```

Update the following in `api/local.settings.json`:
- `AZURE_AD_TENANT_ID`: Your Azure AD tenant ID
- `AZURE_AD_CLIENT_ID`: Your Azure AD application (client) ID
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your GPT-4 deployment name
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_API_VERSION`: API version (e.g., "2024-02-15-preview")
- `COSMOS_ENDPOINT`: Your Cosmos DB endpoint (optional)
- `COSMOS_KEY`: Your Cosmos DB key (optional)

#### Configure Frontend
Create a `.env.local` file in the `ui` directory:

```bash
cp ui/.env.example ui/.env.local
```

Update with your Microsoft Entra ID configuration.

### 3. Start the Backend API

```bash
cd api
source ../venv/bin/activate  # Activate virtual environment
func start
```

The API will be available at `http://localhost:7071`

### 4. Start the React UI

In a new terminal:

```bash
cd ui
npm install
npm start
```

The UI will be available at `http://localhost:3000`

### 5. (Optional) Use the CLI Tool

```bash
cd cli-tool
python insurance_cli.py --interactive
```

## Web UI Guide

### Features

1. **Generate Letter**: Create new insurance letters with AI assistance
   - Select letter type from dropdown
   - Fill in customer information
   - Provide context/prompt for letter generation
   - View real-time progress as agents work

2. **Letter History**: View and manage previously generated letters
   - Search and filter letters
   - View full letter content and agent conversations
   - Edit placeholder values with auto-save
   - Download or print letters

3. **Company Settings**: Configure default information
   - Company name and details
   - Default agent information
   - Insurance license numbers
   - Contact information

### Letter Generation Process

1. Navigate to "Generate Letter"
2. Select the appropriate letter type
3. Fill in customer information
4. Provide a detailed prompt/context
5. Click "Generate Letter"
6. Watch progress as each agent reviews the letter
7. View the generated letter with all placeholders highlighted
8. Edit any placeholder values inline
9. Save or download the final letter

### Placeholder System

The application automatically detects and highlights placeholders in generated letters:
- **Yellow highlight**: Unfilled placeholders (e.g., [Customer Name])
- **Green highlight**: Filled placeholders (click to edit)
- **Auto-population**: Common placeholders are filled from Company Settings
- **Inline editing**: Click any placeholder to edit its value
- **Auto-save**: Changes are saved automatically after 1 second

## API Documentation

### Base URL

```
http://localhost:7071/api
```

### Endpoints

#### Health Check
```
GET /api/health
```

Returns API health status and Cosmos DB connection status.

#### Generate Letter
```
POST /api/draft-letter
Content-Type: application/json

{
  "customer_info": {
    "name": "John Doe",
    "policy_number": "POL-123456",
    "address": "123 Main St",
    "phone": "555-1234",
    "email": "john@example.com",
    "agent_name": "Jane Smith"
  },
  "letter_type": "welcome",
  "user_prompt": "Welcome new customer to auto insurance policy"
}
```

#### Suggest Letter Type
```
POST /api/suggest-letter-type
Content-Type: application/json

{
  "prompt": "Customer's claim was denied due to late filing"
}
```

#### Validate Letter
```
POST /api/validate-letter
Content-Type: application/json

{
  "letter_content": "Dear Mr. Doe...",
  "letter_type": "claim_denial"
}
```

### Letter Types

- `claim_denial` - For denying insurance claims
- `claim_approval` - For approving insurance claims
- `policy_renewal` - For policy renewal notifications
- `coverage_change` - For changes in coverage
- `premium_increase` - For premium rate increases
- `cancellation` - For policy cancellations
- `welcome` - For welcoming new customers
- `general` - For general correspondence

## CLI Tool Usage

### Interactive Mode

```bash
cd cli-tool
python insurance_cli.py --interactive
```

### Command Line Options

```bash
# Generate a letter
python insurance_cli.py \
  --customer-name "Jane Smith" \
  --policy-number "POL-789012" \
  --letter-type "policy_renewal" \
  --prompt "Renewal reminder with 10% loyalty discount" \
  --output renewal_letter.txt

# Suggest letter type
python insurance_cli.py \
  --suggest \
  --prompt "Customer wants to cancel policy"

# Validate existing letter
python insurance_cli.py \
  --validate letter.txt \
  --letter-type "cancellation"

# Health check with JSON output
python insurance_cli.py \
  --health-check \
  --json
```

## Development

### Running Tests

Tests are organized by project component for better maintainability:

#### Backend API Tests

The API includes a comprehensive test suite with 80%+ code coverage:

```bash
# Run all backend tests
cd api
python -m pytest

# Run with coverage report
python tests/run_tests.py --coverage

# Run only unit tests
python tests/run_tests.py --unit

# Run specific test
python tests/run_tests.py -k "test_generate_letter"

# Run manual Cosmos DB test
python tests/manual/test_cosmos_manual.py
```

See `api/tests/README.md` for detailed testing documentation.

#### Frontend UI Tests

```bash
cd ui
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watchAll
```

#### CLI Tool Tests

```bash
cd cli-tool/tests

# Run conversation tests
python test_conversation.py

# Run demo
python demo_conversation.py
```

See `cli-tool/tests/README.md` for CLI testing documentation.

### Building for Production

```bash
# Build UI
cd ui
npm run build

# Package API
cd api
func azure functionapp publish <function-app-name>
```

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - Complete system architecture overview
- [Agent System Guide](docs/AGENT_SYSTEM_GUIDE.md) - In-depth guide to the multi-agent system
- [Authentication Setup Guide](docs/AUTHENTICATION.md) - Configure Microsoft Entra ID for SSO
- [Deployment Guide](docs/DEPLOYMENT.md) - Deploy to Azure with API Management
- [Code Improvements](docs/CODE_IMPROVEMENTS.md) - Recommended improvements and best practices
- [API Tests Documentation](api/tests/README.md) - Running and writing tests

## Azure Deployment

For production deployment with Azure API Management, see the [Deployment Guide](docs/DEPLOYMENT.md).

### Cosmos DB Setup

Create a Cosmos DB container with these exact settings:

1. **Database ID**: `insurance_letters`
2. **Container ID**: `letters`
3. **Partition key**: `/type` (must be exactly `/type`)
4. **Throughput**: Serverless recommended

### Deploy to Azure

1. Create Azure resources:
```bash
# Create resource group
az group create --name insurance-app-rg --location eastus

# Create Function App
az functionapp create \
  --resource-group insurance-app-rg \
  --name insurance-letters-app \
  --storage-account insurancestorage \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4

# Create Cosmos DB
az cosmosdb create \
  --name insurance-cosmos \
  --resource-group insurance-app-rg \
  --kind GlobalDocumentDB \
  --capabilities EnableServerless
```

2. Configure and deploy:
```bash
# Set app settings
az functionapp config appsettings set \
  --name insurance-letters-app \
  --resource-group insurance-app-rg \
  --settings @app-settings.json

# Deploy function app
cd api
func azure functionapp publish insurance-letters-app

# Deploy UI to Azure Static Web Apps or similar
```

## Troubleshooting

### UI Issues

1. **CORS errors**: Ensure API is running and CORS is configured in `local.settings.json`
2. **Blank page**: Check browser console for errors, ensure npm install completed
3. **API connection failed**: Verify API is running on port 7071

### API Issues

1. **"Cosmos DB not connected"**: Cosmos DB is optional for local development
2. **"Azure OpenAI timeout"**: Check your credentials and deployment name
3. **"Module not found"**: Run `pip install -r requirements.txt` in api directory

### Common Solutions

- Clear browser cache and localStorage if UI behaves unexpectedly
- Restart both API and UI servers after configuration changes
- Check that all required environment variables are set
- Ensure virtual environment is activated when running API

## Version History

- **v2.0.0** (2025-07-10): Added React UI with company profiles and placeholder management
- **v1.0.0** (2025-07-09): Initial release with API and CLI

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See [LICENSE](LICENSE) file for details

## Acknowledgments

- Built with [React](https://reactjs.org/) and [Tailwind CSS](https://tailwindcss.com/)
- Backend powered by [Azure Functions](https://azure.microsoft.com/en-us/products/functions/) and [Azure Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- AI capabilities via [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- Data persistence with [Azure Cosmos DB](https://azure.microsoft.com/en-us/products/cosmos-db/)