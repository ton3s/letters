# API Tests

Comprehensive test suite for the Insurance Letter Drafting API.

## Test Structure

```
tests/
├── conftest.py          # Pytest configuration and shared fixtures
├── test_models.py       # Unit tests for data models
├── test_agent_system.py # Unit tests for multi-agent system
├── test_cosmos_service.py # Unit tests for Cosmos DB service
├── test_function_app.py # Unit tests for API endpoints
├── test_integration.py  # Integration tests for complete workflows
└── run_tests.py        # Test runner script
```

## Running Tests

### Quick Start

```bash
# Run all tests
cd api
python -m pytest tests/

# Or use the test runner
python tests/run_tests.py
```

### Test Runner Options

```bash
# Run with coverage report
python tests/run_tests.py --coverage

# Run only unit tests
python tests/run_tests.py --unit

# Run only integration tests
python tests/run_tests.py --integration

# Run specific test
python tests/run_tests.py -k "test_generate_letter"

# Verbose output
python tests/run_tests.py -v

# Stop on first failure
python tests/run_tests.py --failfast
```

### Direct Pytest Commands

```bash
# Run all tests with coverage
pytest --cov=services --cov=function_app --cov-report=html

# Run specific test file
pytest tests/test_agent_system.py

# Run tests matching pattern
pytest -k "validation"

# Run with verbose output
pytest -v

# Run async tests
pytest -v tests/test_function_app.py::TestDraftLetterEndpoint
```

## Test Categories

### Unit Tests

1. **Model Tests** (`test_models.py`)
   - Data validation
   - Serialization/deserialization
   - Enum values
   - Required/optional fields

2. **Agent System Tests** (`test_agent_system.py`)
   - Letter generation workflow
   - Multi-agent approval process
   - Letter type suggestions
   - Validation logic
   - Error handling

3. **Cosmos Service Tests** (`test_cosmos_service.py`)
   - CRUD operations
   - Connection handling
   - Query building
   - Error scenarios

4. **Function App Tests** (`test_function_app.py`)
   - HTTP endpoint handlers
   - Request/response formatting
   - Error responses
   - Input validation

### Integration Tests

**Complete Workflows** (`test_integration.py`)
- End-to-end letter generation
- Error propagation
- Concurrent request handling
- Malformed request handling

## Test Fixtures

Key fixtures defined in `conftest.py`:

- `mock_env`: Sets up test environment variables
- `mock_cosmos_client`: Mocked Cosmos DB client
- `mock_semantic_kernel`: Mocked AI kernel
- `sample_customer_info`: Test customer data
- `sample_letter_request`: Test API request
- `mock_http_request`: Azure Functions HTTP request mock

## Coverage Goals

Target coverage: 80%+

Current coverage areas:
- ✅ All API endpoints
- ✅ Agent system workflows
- ✅ Data models
- ✅ Cosmos DB operations
- ✅ Error handling paths
- ✅ Edge cases

## Writing New Tests

### Test Structure

```python
class TestFeatureName:
    """Tests for specific feature."""
    
    @pytest.fixture
    def setup_data(self):
        """Test-specific setup."""
        return {...}
    
    def test_happy_path(self, setup_data):
        """Test normal operation."""
        # Arrange
        # Act
        # Assert
    
    def test_error_case(self):
        """Test error handling."""
        with pytest.raises(ExpectedException):
            # Trigger error
    
    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async operations."""
        result = await async_function()
        assert result is not None
```

### Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what they test
3. **Coverage**: Test both success and failure paths
4. **Mocking**: Mock external dependencies
5. **Assertions**: Use specific assertions
6. **Fixtures**: Share common setup via fixtures

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the api directory
   cd api
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Async Test Failures**
   ```bash
   # Ensure pytest-asyncio is installed
   pip install pytest-asyncio
   ```

3. **Coverage Not Working**
   ```bash
   # Install coverage tools
   pip install pytest-cov
   ```

4. **Module Not Found**
   ```bash
   # Run from api directory
   cd api
   python -m pytest tests/
   ```

## CI/CD Integration

Example GitHub Actions configuration:

```yaml
- name: Run API Tests
  run: |
    cd api
    pip install -r requirements.txt
    python -m pytest tests/ --cov=services --cov=function_app
```