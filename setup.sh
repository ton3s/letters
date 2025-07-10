#!/bin/bash

# Insurance Letter Drafting Application Setup Script

echo "Setting up Insurance Letter Drafting Application..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r api/requirements.txt

# Install Azure Functions Core Tools if not present
if ! command -v func &>/dev/null; then
    echo "Azure Functions Core Tools not found. Please install it from:"
    echo "https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local"
    echo ""
    echo "On macOS: brew tap azure/functions && brew install azure-functions-core-tools@4"
    echo "On Ubuntu: Follow instructions at the link above"
    echo "On Windows: Download the MSI installer from the link above"
else
    echo "Azure Functions Core Tools found: $(func --version)"
fi

# Copy example settings if needed
if [ ! -f api/local.settings.json ]; then
    if [ -f api/local.settings.json.example ]; then
        echo "Copying local.settings.json.example to local.settings.json..."
        cp api/local.settings.json.example api/local.settings.json
        echo "Please update api/local.settings.json with your actual Azure credentials"
    fi
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat >.env <<EOF
# Azure OpenAI Configuration
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Cosmos DB Configuration
COSMOS_ENDPOINT=https://your-cosmos-account.documents.azure.com:443/
COSMOS_KEY=your-cosmos-primary-key
COSMOS_DATABASE_NAME=insurance_letters
COSMOS_CONTAINER_NAME=letters

# Function App Configuration
FUNCTIONS_WORKER_RUNTIME=python
AzureWebJobsStorage=UseDevelopmentStorage=true
EOF
    echo "Please update .env with your actual Azure credentials"
fi

# Make CLI executable
chmod +x cli-tool/insurance_cli.py

echo ""
echo "Setup complete! Next steps:"
echo "1. Update api/local.settings.json with your Azure credentials"
echo "2. Start the Azure Functions app: cd api && func start"
echo "3. Start the React UI: cd ui && npm install && npm start"
echo "4. Or use the CLI: cd cli-tool && python insurance_cli.py --interactive"
echo ""
echo "For more information, see README.md"
