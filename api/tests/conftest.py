"""
Pytest configuration and fixtures for API tests.
"""
import pytest
import os
import json
from unittest.mock import Mock, AsyncMock, patch
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError


@pytest.fixture
def mock_env(monkeypatch):
    """Set up environment variables for testing."""
    test_env = {
        "AZURE_OPENAI_DEPLOYMENT_NAME": "test-gpt4",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "COSMOS_ENDPOINT": "https://test.documents.azure.com:443/",
        "COSMOS_KEY": "test-cosmos-key",
        "COSMOS_DATABASE_NAME": "test_db",
        "COSMOS_CONTAINER_NAME": "test_container",
    }
    
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    
    return test_env


@pytest.fixture
def mock_cosmos_client():
    """Mock Cosmos DB client."""
    mock_client = Mock(spec=CosmosClient)
    mock_database = Mock()
    mock_container = Mock()
    
    # Set up the chain of mocks
    mock_client.get_database_client.return_value = mock_database
    mock_database.get_container_client.return_value = mock_container
    
    # Mock container operations
    mock_container.create_item = AsyncMock(return_value={
        "id": "test-id",
        "type": "letter",
        "letter_content": "Test letter content",
        "created_at": "2025-01-01T00:00:00Z"
    })
    
    mock_container.read_item = AsyncMock(return_value={
        "id": "test-id",
        "type": "letter",
        "letter_content": "Test letter content"
    })
    
    mock_container.query_items = Mock(return_value=[
        {"id": "1", "letter_content": "Letter 1"},
        {"id": "2", "letter_content": "Letter 2"}
    ])
    
    return mock_client, mock_container


@pytest.fixture
def mock_semantic_kernel():
    """Mock Semantic Kernel for agent testing."""
    mock_kernel = Mock()
    mock_agent = Mock()
    
    # Mock agent responses
    mock_agent.invoke = AsyncMock(return_value=Mock(
        value="Mocked agent response"
    ))
    
    return mock_kernel, mock_agent


@pytest.fixture
def sample_customer_info():
    """Sample customer information for testing."""
    return {
        "name": "John Doe",
        "policy_number": "POL-123456",
        "address": "123 Main St, City, State 12345",
        "phone": "555-1234",
        "email": "john.doe@example.com",
        "agent_name": "Jane Smith"
    }


@pytest.fixture
def sample_letter_request(sample_customer_info):
    """Sample letter generation request."""
    return {
        "customer_info": sample_customer_info,
        "letter_type": "welcome",
        "user_prompt": "Welcome new customer to auto insurance policy"
    }


@pytest.fixture
def mock_http_request():
    """Mock Azure Functions HTTP request."""
    class MockHttpRequest:
        def __init__(self, body=None, params=None, route_params=None, method="GET"):
            self.body = body
            self.params = params or {}
            self.route_params = route_params or {}
            self.method = method
            self.url = "http://localhost:7071/api/test"
            self.headers = {"Content-Type": "application/json"}
        
        def get_body(self):
            if isinstance(self.body, dict):
                return json.dumps(self.body).encode('utf-8')
            elif isinstance(self.body, str):
                return self.body.encode('utf-8')
            return self.body or b''
        
        def get_json(self):
            if self.body:
                if isinstance(self.body, dict):
                    return self.body
                return json.loads(self.body)
            return None
    
    return MockHttpRequest


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    mock_completion = Mock()
    
    # Mock chat completion
    mock_completion.choices = [
        Mock(message=Mock(content="Mocked AI response"))
    ]
    
    mock_client.chat.completions.create = AsyncMock(
        return_value=mock_completion
    )
    
    return mock_client


@pytest.fixture(autouse=True)
def reset_imports():
    """Reset imports between tests to ensure clean state."""
    import sys
    modules_to_remove = [
        module for module in sys.modules 
        if module.startswith('services') or module == 'function_app'
    ]
    for module in modules_to_remove:
        del sys.modules[module]
    yield