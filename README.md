# Insurance Letter Drafting Application

A basic insurance letter drafting application using Azure Functions v2 with multi-agent Azure Semantic Kernel orchestration and Cosmos DB for persistent storage.

## Features

- **Multi-Agent System**: Three specialized AI agents collaborate to create professional insurance letters
  - Letter Drafting Agent: Creates professional insurance letters
  - Compliance Agent: Reviews letters for regulatory compliance
  - Customer Service Agent: Ensures customer-friendly tone and clarity
- **Approval-Based Workflow**: Iterative refinement until all agents approve
- **Letter Types**: Support for 8 different insurance letter types
- **Azure Functions v2**: Modern serverless architecture
- **Cosmos DB Integration**: Persistent storage for generated letters
- **Comprehensive CLI**: Full-featured command-line tool for testing

## API Status

✅ **All endpoints are fully functional and tested:**

| Endpoint                        | Status     | Description                                |
| ------------------------------- | ---------- | ------------------------------------------ |
| `GET /api/health`               | ✅ Working | Health check with Cosmos DB status         |
| `POST /api/draft-letter`        | ✅ Working | Generate letters with multi-agent review   |
| `POST /api/suggest-letter-type` | ✅ Working | AI-powered letter type suggestions         |
| `POST /api/validate-letter`     | ✅ Working | Compliance validation for existing letters |

### Performance

- Letter generation typically completes in 15-30 seconds
- Multi-agent approval usually achieved in 1-2 rounds
- All agents work with Azure OpenAI GPT-4 models

## Prerequisites

- Python 3.8 or higher
- Azure Functions Core Tools v4
- Azure OpenAI resource with GPT-4 deployment
- Azure Cosmos DB account (optional for local development)
- Azure Storage Emulator or Azurite (for local development)

## Azure Cosmos DB Setup

When creating your Cosmos DB container, use these exact settings:

### Container Configuration

1. **Database ID**: `insurance_letters` (Create new)
2. **Container ID**: `letters`
3. **Partition key**: `/type` (⚠️ CRITICAL - must be exactly `/type`)
4. **Unique keys**: Not required
5. **Analytical Store**: Off
6. **Throughput**:
   - **Recommended**: Serverless (pay per request)
   - **Alternative**: 400 RU/s provisioned throughput

### Important Notes

- The partition key `/type` is hardcoded in the application and must match exactly
- All documents will have `"type": "letter"` as their partition key value
- The application will automatically create the database and container if they don't exist (when using provisioned throughput)

### Portal Setup Steps

1. Navigate to your Cosmos DB account in Azure Portal
2. Click "Data Explorer" → "New Container"
3. Enter the settings exactly as shown above
4. Click "OK" to create

## Quick Start

1. **Clone and setup**:

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure Azure credentials**:
   Copy `local.settings.json.example` to `local.settings.json` and update with your Azure credentials:

   ```bash
   cp local.settings.json.example local.settings.json
   ```

   Update the following:

   - `AZURE_OPENAI_DEPLOYMENT_NAME`: Your GPT-4 deployment name
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
   - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
   - `AZURE_OPENAI_API_VERSION`: API version (e.g., "2024-02-15-preview")
   - `COSMOS_ENDPOINT`: Your Cosmos DB endpoint
   - `COSMOS_KEY`: Your Cosmos DB key

3. **Start the Azure Functions app**:

   ```bash
   source venv/bin/activate  # Activate virtual environment
   func start
   ```

   The API will be available at `http://localhost:7071`

4. **Test the API**:

   ```bash
   # Health check
   python cli/insurance_cli.py --health-check

   # Interactive mode
   python cli/insurance_cli.py --interactive

   # Direct letter generation
   python cli/insurance_cli.py \
     --customer-name "John Doe" \
     --policy-number "POL-123456" \
     --letter-type "welcome" \
     --prompt "Welcome new customer to our auto insurance policy"
   ```

## API Endpoints

### Health Check

```
GET /api/health
```

Returns API health status and Cosmos DB connection status.

### Generate Letter

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
  "user_prompt": "Welcome new customer to auto insurance policy with comprehensive coverage"
}
```

### Suggest Letter Type

```
POST /api/suggest-letter-type
Content-Type: application/json

{
  "prompt": "Customer's claim was denied due to late filing"
}
```

### Validate Letter

```
POST /api/validate-letter
Content-Type: application/json

{
  "letter_content": "Dear Mr. Doe...",
  "letter_type": "claim_denial"
}
```

## Letter Types

- `claim_denial` - For denying insurance claims
- `claim_approval` - For approving insurance claims
- `policy_renewal` - For policy renewal notifications
- `coverage_change` - For changes in coverage
- `premium_increase` - For premium rate increases
- `cancellation` - For policy cancellations
- `welcome` - For welcoming new customers
- `general` - For general correspondence

## CLI Usage

### Interactive Mode

The easiest way to use the CLI is in interactive mode:

```bash
python cli/insurance_cli.py --interactive
```

### Command Line Options

```bash
# Generate a letter
python cli/insurance_cli.py \
  --customer-name "Jane Smith" \
  --policy-number "POL-789012" \
  --letter-type "policy_renewal" \
  --prompt "Renewal reminder with 10% loyalty discount" \
  --output renewal_letter.txt

# Suggest letter type
python cli/insurance_cli.py \
  --suggest \
  --prompt "Customer wants to cancel policy due to high premiums"

# Validate existing letter
python cli/insurance_cli.py \
  --validate letter.txt \
  --letter-type "cancellation"

# JSON output
python cli/insurance_cli.py \
  --health-check \
  --json
```

## Multi-Agent Approval Workflow

The system uses an iterative approval process:

1. **Round 1**: Letter Writer creates initial draft
2. **Review**: Compliance and Customer Service agents review
3. **Refinement**: Letter Writer incorporates feedback
4. **Iteration**: Process continues until all agents approve or max 5 rounds

Each agent provides approval status:

- `WRITER_APPROVED` / `WRITER_NEEDS_IMPROVEMENT`
- `COMPLIANCE_APPROVED` / `COMPLIANCE_REJECTED`
- `CUSTOMER_SERVICE_APPROVED` / `CUSTOMER_SERVICE_REJECTED`

### Example Output

When generating a letter, you'll see the approval status:

```json
{
	"approval_status": {
		"writer_approved": true,
		"compliance_approved": true,
		"customer_service_approved": true,
		"overall_approved": true,
		"status": "fully_approved"
	},
	"total_rounds": 2
}
```

## Local Development

1. **Install Azurite** (Azure Storage Emulator):

   ```bash
   npm install -g azurite
   azurite --silent --location azurite --debug azurite/debug.log
   ```

2. **Run Azure Functions locally**:

   ```bash
   func start
   ```

3. **Test with CLI**:
   ```bash
   python cli/insurance_cli.py --interactive
   ```

## Testing with cURL

You can test the API endpoints directly using cURL:

### Health Check

```bash
curl http://localhost:7071/api/health
```

### Suggest Letter Type

```bash
curl -X POST http://localhost:7071/api/suggest-letter-type \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Customer wants to cancel policy due to high premiums"}'
```

### Validate Letter

```bash
curl -X POST http://localhost:7071/api/validate-letter \
  -H "Content-Type: application/json" \
  -d '{
    "letter_content": "Dear Customer, Your claim has been denied...",
    "letter_type": "claim_denial"
  }'
```

### Generate Letter

```bash
curl -X POST http://localhost:7071/api/draft-letter \
  -H "Content-Type: application/json" \
  -d '{
    "customer_info": {
      "name": "John Doe",
      "policy_number": "POL-123456",
      "address": "123 Main St",
      "phone": "555-1234",
      "email": "john@example.com"
    },
    "letter_type": "welcome",
    "user_prompt": "Welcome new customer to auto insurance"
  }'
```

## Deployment to Azure

1. **Create Azure resources**:

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

   # Create database
   az cosmosdb sql database create \
     --account-name insurance-cosmos \
     --resource-group insurance-app-rg \
     --name insurance_letters

   # Create container with correct partition key
   az cosmosdb sql container create \
     --account-name insurance-cosmos \
     --resource-group insurance-app-rg \
     --database-name insurance_letters \
     --name letters \
     --partition-key-path "/type"
   ```

2. **Configure app settings**:

   ```bash
   az functionapp config appsettings set \
     --name insurance-letters-app \
     --resource-group insurance-app-rg \
     --settings @app-settings.json
   ```

3. **Deploy the function app**:
   ```bash
   func azure functionapp publish insurance-letters-app
   ```

## Project Structure

```
letters/
├── function_app.py              # Main Azure Functions app
├── services/
│   ├── agent_system.py         # Multi-agent Semantic Kernel system
│   ├── cosmos_service.py       # Cosmos DB integration
│   └── models.py               # Data models
├── cli/
│   └── insurance_cli.py        # CLI testing tool
├── requirements.txt            # Python dependencies
├── local.settings.json         # Local development settings
├── host.json                  # Azure Functions configuration
├── setup.sh                   # Setup script
└── README.md                  # This file
```

## Troubleshooting

### Common Issues

1. **"Cosmos DB not connected"**

   - Cosmos DB is optional for local development
   - The app will work without it but won't persist letters
   - Update credentials in `.env` to enable persistence

2. **"Azure OpenAI timeout"**

   - Ensure your Azure OpenAI credentials are correct
   - Check that your deployment name matches
   - Verify API version is supported

3. **"Module not found"**

   - Run `pip install -r requirements.txt`
   - Ensure virtual environment is activated

4. **"Partition key mismatch" or "Resource Not Found" errors**

   - Ensure your Cosmos DB container uses `/type` as the partition key
   - The partition key is case-sensitive and must be exactly `/type`
   - If you created the container with a different partition key, delete and recreate it
   - All documents created by the app will have `"type": "letter"` field

5. **"Cannot run the event loop while another loop is running"**

   - This occurs when using older versions of the code
   - Ensure you're using the latest version where async endpoints use `await` directly
   - Don't use `asyncio.run()` or `loop.run_until_complete()` in Azure Functions

6. **"Setting offer throughput on container is not supported for serverless accounts"**

   - This happens when trying to create a container with throughput on a serverless Cosmos DB
   - The code automatically handles this - no throughput is specified for serverless accounts
   - If you see this error, pull the latest code

7. **"Port 7071 is unavailable"**
   - Kill the existing process: `lsof -ti:7071 | xargs kill -9`
   - Or use a different port: `func start --port 7072`

### Debug Mode

Enable detailed logging:

```bash
export AZURE_FUNCTIONS_ENVIRONMENT=Development
func start --verbose
```

## Next Steps

This is a basic implementation that can be extended with:

- Authentication and authorization
- Letter history and retrieval endpoints
- React frontend application
- Enhanced letter templates
- Batch processing capabilities
- Email integration
- Document generation (PDF)

## Project Status

This application is **production-ready** with the following completed features:

- ✅ All API endpoints tested and working
- ✅ Multi-agent orchestration with approval workflow
- ✅ Cosmos DB integration for data persistence
- ✅ Comprehensive error handling
- ✅ Full CLI tool for testing
- ✅ Complete documentation

### Version

Current version: 1.0.0 (2025-07-09)

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See [LICENSE](LICENSE) file for details

## Acknowledgments

- Built with [Azure Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- Powered by [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- Serverless architecture using [Azure Functions](https://azure.microsoft.com/en-us/products/functions/)
- Data persistence with [Azure Cosmos DB](https://azure.microsoft.com/en-us/products/cosmos-db/)
