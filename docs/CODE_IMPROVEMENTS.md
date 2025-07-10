# Code Improvement Recommendations

Based on a comprehensive code review, here are the recommended improvements organized by priority and component.

## Priority 1: Critical Improvements

### 1.1 Security Enhancements

#### API Security
```python
# Add rate limiting middleware
from functools import wraps
import time

class RateLimiter:
    def __init__(self, max_calls=100, window=3600):
        self.max_calls = max_calls
        self.window = window
        self.calls = {}
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(req, *args, **kwargs):
            user_id = get_user_id(req)
            now = time.time()
            
            # Clean old entries
            self.calls = {k: v for k, v in self.calls.items() 
                         if now - v[-1] < self.window}
            
            # Check rate limit
            if user_id in self.calls:
                if len(self.calls[user_id]) >= self.max_calls:
                    return func.HttpResponse(
                        json.dumps({"error": "Rate limit exceeded"}),
                        status_code=429
                    )
            
            # Record call
            if user_id not in self.calls:
                self.calls[user_id] = []
            self.calls[user_id].append(now)
            
            return await func(req, *args, **kwargs)
        return wrapper

# Usage
rate_limiter = RateLimiter(max_calls=100, window=3600)

@app.route(route="draft-letter", methods=["POST"])
@require_auth
@rate_limiter
async def draft_letter(req: func.HttpRequest) -> func.HttpResponse:
    # Implementation
```

#### Input Validation
```python
# api/middleware/validation.py
from pydantic import BaseModel, ValidationError
from functools import wraps

def validate_request(model_class: BaseModel):
    def decorator(func):
        @wraps(func)
        async def wrapper(req: func.HttpRequest):
            try:
                body = req.get_json()
                validated_data = model_class(**body)
                req.validated_data = validated_data
                return await func(req)
            except ValidationError as e:
                return func.HttpResponse(
                    json.dumps({
                        "error": "Validation failed",
                        "details": e.errors()
                    }),
                    status_code=400,
                    mimetype="application/json"
                )
        return wrapper
    return decorator
```

### 1.2 Error Handling Standardization

#### Create Error Classes
```python
# api/services/errors.py
class APIError(Exception):
    """Base API error class"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 400, details)

class AuthenticationError(APIError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)

class AuthorizationError(APIError):
    """Authorization error"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, 403)

class NotFoundError(APIError):
    """Resource not found error"""
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", 404)

class RateLimitError(APIError):
    """Rate limit exceeded error"""
    def __init__(self, retry_after: int = 60):
        super().__init__("Rate limit exceeded", 429, {"retry_after": retry_after})
```

#### Global Error Handler
```python
# api/middleware/error_handler.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def create_error_response(error: Exception, request_id: str = None) -> func.HttpResponse:
    """Create standardized error response"""
    
    if isinstance(error, APIError):
        response_data = {
            "error": error.message,
            "details": error.details,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }
        status_code = error.status_code
    else:
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        response_data = {
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }
        status_code = 500
    
    return func.HttpResponse(
        json.dumps(response_data),
        status_code=status_code,
        mimetype="application/json"
    )
```

### 1.3 Testing Coverage

#### Add Missing UI Tests
```typescript
// ui/src/pages/__tests__/GenerateLetter.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { GenerateLetter } from '../GenerateLetter';
import { ApiService } from '../../services/api';

jest.mock('../../services/api');

describe('GenerateLetter Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('submits form with correct data', async () => {
    const mockGenerate = jest.spyOn(ApiService, 'generateLetter')
      .mockResolvedValue({
        letter_content: 'Test letter',
        approval_status: { overall_approved: true },
        document_id: 'test-123'
      });

    render(<GenerateLetter />);
    
    // Fill form
    fireEvent.change(screen.getByLabelText(/Customer Name/i), {
      target: { value: 'John Doe' }
    });
    fireEvent.change(screen.getByLabelText(/Policy Number/i), {
      target: { value: 'POL-123' }
    });
    
    // Submit
    fireEvent.click(screen.getByText(/Generate Letter/i));
    
    await waitFor(() => {
      expect(mockGenerate).toHaveBeenCalledWith({
        customer_info: expect.objectContaining({
          name: 'John Doe',
          policy_number: 'POL-123'
        })
      });
    });
  });

  test('shows loading state during generation', async () => {
    jest.spyOn(ApiService, 'generateLetter')
      .mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<GenerateLetter />);
    
    fireEvent.click(screen.getByText(/Generate Letter/i));
    
    expect(screen.getByText(/Generating/i)).toBeInTheDocument();
  });

  test('handles API errors gracefully', async () => {
    jest.spyOn(ApiService, 'generateLetter')
      .mockRejectedValue(new Error('API Error'));

    render(<GenerateLetter />);
    
    fireEvent.click(screen.getByText(/Generate Letter/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Error generating letter/i)).toBeInTheDocument();
    });
  });
});
```

## Priority 2: Performance Improvements

### 2.1 React Performance

#### Implement React.memo
```typescript
// ui/src/components/Common/LoadingSpinner.tsx
import React from 'react';

export const LoadingSpinner = React.memo<LoadingSpinnerProps>(({ 
  size = 'medium', 
  className = '' 
}) => {
  // Component implementation
});

// Add display name for debugging
LoadingSpinner.displayName = 'LoadingSpinner';
```

#### Use React Query
```typescript
// ui/src/hooks/useLetterGeneration.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ApiService } from '../services/api';

export const useLetterGeneration = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ApiService.generateLetter,
    onSuccess: (data) => {
      // Invalidate and refetch letter history
      queryClient.invalidateQueries({ queryKey: ['letterHistory'] });
    },
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};
```

### 2.2 API Performance

#### Implement Caching
```python
# api/services/cache.py
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Any

class InMemoryCache:
    def __init__(self):
        self.cache = {}
        self.expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            if datetime.now() < self.expiry[key]:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.expiry[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        self.cache[key] = value
        self.expiry[key] = datetime.now() + timedelta(seconds=ttl)
    
    def create_key(self, *args) -> str:
        """Create cache key from arguments"""
        key_string = json.dumps(args, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

# Usage in agent_system.py
cache = InMemoryCache()

async def suggest_letter_type(user_prompt: str) -> Dict[str, Any]:
    # Check cache
    cache_key = cache.create_key("suggest", user_prompt)
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Generate result
    result = await _generate_suggestion(user_prompt)
    
    # Cache result
    cache.set(cache_key, result, ttl=3600)  # 1 hour
    
    return result
```

## Priority 3: Code Organization

### 3.1 Extract Configuration

#### Agent Configuration
```yaml
# api/config/agents.yaml
agents:
  letter_writer:
    name: "LetterWriter"
    id: "letter_writer"
    instructions: |
      You are a professional insurance letter drafting specialist with expertise in:
      - Creating clear, concise insurance correspondence
      - Tailoring tone and language to the letter type
      - Incorporating all necessary information
      - Following insurance industry best practices
    
    temperature: 0.7
    max_tokens: 2000
    
  compliance_reviewer:
    name: "ComplianceReviewer"
    id: "compliance_reviewer"
    instructions: |
      You are an insurance compliance expert specializing in:
      - Insurance regulations and requirements
      - State and federal compliance standards
      - Required disclosures and legal language
      - Risk assessment and mitigation
    
    temperature: 0.3
    max_tokens: 1500
    
  customer_service:
    name: "CustomerServiceAgent"
    id: "customer_service"
    instructions: |
      You are a customer service excellence expert focusing on:
      - Clear, understandable communication
      - Empathetic and respectful tone
      - Customer satisfaction and experience
      - Avoiding technical jargon
    
    temperature: 0.5
    max_tokens: 1500

workflow:
  max_rounds: 5
  execution_mode: "sequential"
  timeout: 120
```

#### Load Configuration
```python
# api/services/config.py
import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    @property
    def agents(self) -> Dict[str, Any]:
        return self._config.get('agents', {})
    
    @property
    def workflow(self) -> Dict[str, Any]:
        return self._config.get('workflow', {})
    
    def get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        return self.agents.get(agent_id, {})
```

### 3.2 Improve Type Safety

#### Fix useApi Hook
```typescript
// ui/src/hooks/useApi.ts
import { useState, useCallback } from 'react';

interface UseApiState<T> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
}

interface UseApiReturn<T, TArgs extends any[]> extends UseApiState<T> {
  execute: (...args: TArgs) => Promise<T | null>;
  reset: () => void;
}

export function useApi<T, TArgs extends any[] = any[]>(
  apiFunction: (...args: TArgs) => Promise<T>
): UseApiReturn<T, TArgs> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    error: null,
    isLoading: false,
  });

  const execute = useCallback(
    async (...args: TArgs): Promise<T | null> => {
      setState({ data: null, error: null, isLoading: true });

      try {
        const result = await apiFunction(...args);
        setState({ data: result, error: null, isLoading: false });
        return result;
      } catch (error) {
        setState({
          data: null,
          error: error instanceof Error ? error : new Error('Unknown error'),
          isLoading: false,
        });
        return null;
      }
    },
    [apiFunction]
  );

  const reset = useCallback(() => {
    setState({ data: null, error: null, isLoading: false });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}
```

## Priority 4: Observability

### 4.1 Structured Logging

```python
# api/services/logger.py
import structlog
import os
from datetime import datetime

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Usage
logger = structlog.get_logger()

# In function_app.py
@app.route(route="draft-letter", methods=["POST"])
@require_auth
async def draft_letter(req: func.HttpRequest) -> func.HttpResponse:
    request_id = str(uuid.uuid4())
    logger = structlog.get_logger().bind(
        request_id=request_id,
        user_id=get_user_id(req),
        endpoint="draft-letter"
    )
    
    logger.info("letter_generation_started")
    
    try:
        # Implementation
        logger.info("letter_generation_completed", 
                   letter_type=letter_type,
                   rounds=result.get("total_rounds"))
    except Exception as e:
        logger.error("letter_generation_failed", 
                    error=str(e),
                    exc_info=True)
        raise
```

### 4.2 Metrics Collection

```python
# api/services/metrics.py
from datetime import datetime
from typing import Dict, Any
import time

class MetricsCollector:
    def __init__(self):
        self.metrics = {}
    
    def record_duration(self, metric_name: str, duration: float):
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append({
            "value": duration,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def record_counter(self, metric_name: str, value: int = 1):
        if metric_name not in self.metrics:
            self.metrics[metric_name] = 0
        self.metrics[metric_name] += value
    
    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics.copy()

# Context manager for timing
class Timer:
    def __init__(self, metrics: MetricsCollector, metric_name: str):
        self.metrics = metrics
        self.metric_name = metric_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        duration = time.time() - self.start_time
        self.metrics.record_duration(self.metric_name, duration)

# Usage
metrics = MetricsCollector()

async def generate_letter_with_metrics(...):
    with Timer(metrics, "letter_generation_time"):
        result = await generate_letter(...)
    
    metrics.record_counter(f"letter_type_{letter_type}")
    metrics.record_counter(f"approval_rounds_{result['total_rounds']}")
    
    return result
```

## Priority 5: Developer Experience

### 5.1 Development Tools

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.9
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100']
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
        
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.42.0
    hooks:
      - id: eslint
        files: \.[jt]sx?$
        types: [file]
        additional_dependencies:
          - eslint@8.42.0
          - eslint-config-react-app
```

### 5.2 Documentation

#### API Documentation
```python
# api/docs/openapi.py
from typing import Dict, Any

def generate_openapi_spec() -> Dict[str, Any]:
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Insurance Letter Generator API",
            "version": "1.0.0",
            "description": "API for generating compliant insurance letters using AI"
        },
        "servers": [
            {"url": "http://localhost:7071/api", "description": "Local development"},
            {"url": "https://api.example.com/api", "description": "Production"}
        ],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health Check",
                    "operationId": "healthCheck",
                    "responses": {
                        "200": {
                            "description": "API is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HealthStatus"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/draft-letter": {
                "post": {
                    "summary": "Generate Letter",
                    "operationId": "generateLetter",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/LetterRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Letter generated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/LetterResponse"
                                    }
                                }
                            }
                        },
                        "401": {
                            "$ref": "#/components/responses/Unauthorized"
                        }
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            },
            "schemas": {
                # Define schemas here
            }
        }
    }
```

## Implementation Priority

1. **Week 1-2**: Security enhancements and error handling
2. **Week 3-4**: Testing coverage and performance improvements
3. **Week 5-6**: Code organization and type safety
4. **Week 7-8**: Observability and developer experience

## Monitoring Success

Track these metrics to measure improvement:

1. **Code Quality**
   - Test coverage: Target 80%+
   - Type coverage: Target 95%+
   - Linting errors: Target 0

2. **Performance**
   - API response time: < 2s for letter generation
   - UI load time: < 3s
   - Error rate: < 0.1%

3. **Security**
   - No critical vulnerabilities
   - All inputs validated
   - Rate limiting effective

4. **Developer Experience**
   - Build time: < 30s
   - Test execution: < 2 minutes
   - Documentation coverage: 100%