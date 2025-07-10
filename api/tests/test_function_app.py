"""
Tests for Azure Functions endpoints.
"""
import pytest
import json
from unittest.mock import patch, Mock, AsyncMock
import azure.functions as func


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_env, mock_http_request):
        """Test successful health check with Cosmos DB connected."""
        request = mock_http_request(method="GET")
        
        with patch('services.cosmos_service.CosmosService') as mock_cosmos:
            mock_cosmos_instance = mock_cosmos.return_value
            mock_cosmos_instance.test_connection = AsyncMock(return_value=True)
            
            # Import function_app after mocking
            from function_app import health_check
            
            response = await health_check(request)
            
            assert response.status_code == 200
            response_data = json.loads(response.get_body())
            assert response_data["status"] == "healthy"
            assert response_data["cosmos_db"]["connected"] is True
            assert "endpoints" in response_data
    
    @pytest.mark.asyncio
    async def test_health_check_cosmos_not_connected(self, mock_env, mock_http_request):
        """Test health check when Cosmos DB is not connected."""
        request = mock_http_request(method="GET")
        
        with patch('services.cosmos_service.CosmosService') as mock_cosmos:
            mock_cosmos_instance = mock_cosmos.return_value
            mock_cosmos_instance.test_connection = AsyncMock(return_value=False)
            
            from function_app import health_check
            
            response = await health_check(request)
            
            assert response.status_code == 200
            response_data = json.loads(response.get_body())
            assert response_data["status"] == "healthy"
            assert response_data["cosmos_db"]["connected"] is False


class TestDraftLetterEndpoint:
    """Tests for the draft letter endpoint."""
    
    @pytest.mark.asyncio
    async def test_draft_letter_success(self, mock_env, mock_http_request, sample_letter_request):
        """Test successful letter generation."""
        request = mock_http_request(body=sample_letter_request, method="POST")
        
        mock_letter_response = {
            "letter_content": "Dear John Doe, Welcome to our insurance...",
            "approval_status": {
                "writer_approved": True,
                "compliance_approved": True,
                "customer_service_approved": True,
                "overall_approved": True,
                "status": "fully_approved"
            },
            "total_rounds": 1,
            "agent_conversations": [
                {
                    "round": 1,
                    "agent": "LetterWriter",
                    "message": "Initial draft created"
                }
            ]
        }
        
        with patch('services.agent_system.InsuranceAgentSystem') as mock_agent:
            mock_agent_instance = mock_agent.return_value
            mock_agent_instance.generate_letter = AsyncMock(return_value=mock_letter_response)
            
            with patch('services.cosmos_service.CosmosService') as mock_cosmos:
                mock_cosmos_instance = mock_cosmos.return_value
                mock_cosmos_instance.save_letter = AsyncMock(return_value={
                    "id": "test-doc-id",
                    "status": "created"
                })
                
                from function_app import draft_letter
                
                response = await draft_letter(request)
                
                assert response.status_code == 200
                response_data = json.loads(response.get_body())
                assert "letter_content" in response_data
                assert response_data["approval_status"]["overall_approved"] is True
                assert "document_id" in response_data
    
    @pytest.mark.asyncio
    async def test_draft_letter_missing_fields(self, mock_env, mock_http_request):
        """Test draft letter with missing required fields."""
        request = mock_http_request(
            body={"letter_type": "welcome"},  # Missing customer_info and user_prompt
            method="POST"
        )
        
        from function_app import draft_letter
        
        response = await draft_letter(request)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body())
        assert response_data["error"] == "Missing required fields"
    
    @pytest.mark.asyncio
    async def test_draft_letter_invalid_json(self, mock_env, mock_http_request):
        """Test draft letter with invalid JSON."""
        request = mock_http_request(method="POST")
        request.get_body = lambda: b'{"invalid": json}'
        
        from function_app import draft_letter
        
        response = await draft_letter(request)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body())
        assert "error" in response_data
    
    @pytest.mark.asyncio
    async def test_draft_letter_agent_error(self, mock_env, mock_http_request, sample_letter_request):
        """Test draft letter when agent system fails."""
        request = mock_http_request(body=sample_letter_request, method="POST")
        
        with patch('services.agent_system.InsuranceAgentSystem') as mock_agent:
            mock_agent_instance = mock_agent.return_value
            mock_agent_instance.generate_letter = AsyncMock(
                side_effect=Exception("Agent system error")
            )
            
            from function_app import draft_letter
            
            response = await draft_letter(request)
            
            assert response.status_code == 500
            response_data = json.loads(response.get_body())
            assert "error" in response_data


class TestSuggestLetterTypeEndpoint:
    """Tests for the suggest letter type endpoint."""
    
    @pytest.mark.asyncio
    async def test_suggest_letter_type_success(self, mock_env, mock_http_request):
        """Test successful letter type suggestion."""
        request = mock_http_request(
            body={"prompt": "Customer wants to cancel policy"},
            method="POST"
        )
        
        with patch('services.agent_system.InsuranceAgentSystem') as mock_agent:
            mock_agent_instance = mock_agent.return_value
            mock_agent_instance.suggest_letter_type = AsyncMock(
                return_value={
                    "suggested_type": "cancellation",
                    "confidence": 0.95,
                    "reasoning": "Customer explicitly wants to cancel"
                }
            )
            
            from function_app import suggest_letter_type
            
            response = await suggest_letter_type(request)
            
            assert response.status_code == 200
            response_data = json.loads(response.get_body())
            assert response_data["suggested_type"] == "cancellation"
            assert "confidence" in response_data
    
    @pytest.mark.asyncio
    async def test_suggest_letter_type_missing_prompt(self, mock_env, mock_http_request):
        """Test suggest letter type with missing prompt."""
        request = mock_http_request(body={}, method="POST")
        
        from function_app import suggest_letter_type
        
        response = await suggest_letter_type(request)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body())
        assert response_data["error"] == "Missing required field: prompt"


class TestValidateLetterEndpoint:
    """Tests for the validate letter endpoint."""
    
    @pytest.mark.asyncio
    async def test_validate_letter_success(self, mock_env, mock_http_request):
        """Test successful letter validation."""
        request = mock_http_request(
            body={
                "letter_content": "Dear Customer, Your claim has been denied...",
                "letter_type": "claim_denial"
            },
            method="POST"
        )
        
        with patch('services.agent_system.InsuranceAgentSystem') as mock_agent:
            mock_agent_instance = mock_agent.return_value
            mock_agent_instance.validate_letter = AsyncMock(
                return_value={
                    "is_valid": True,
                    "compliance_score": 0.92,
                    "tone_score": 0.88,
                    "suggestions": []
                }
            )
            
            from function_app import validate_letter
            
            response = await validate_letter(request)
            
            assert response.status_code == 200
            response_data = json.loads(response.get_body())
            assert response_data["is_valid"] is True
            assert "compliance_score" in response_data
    
    @pytest.mark.asyncio
    async def test_validate_letter_missing_content(self, mock_env, mock_http_request):
        """Test validate letter with missing content."""
        request = mock_http_request(
            body={"letter_type": "claim_denial"},
            method="POST"
        )
        
        from function_app import validate_letter
        
        response = await validate_letter(request)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body())
        assert "error" in response_data
    
    @pytest.mark.asyncio
    async def test_validate_letter_invalid_type(self, mock_env, mock_http_request):
        """Test validate letter with invalid letter type."""
        request = mock_http_request(
            body={
                "letter_content": "Test content",
                "letter_type": "invalid_type"
            },
            method="POST"
        )
        
        with patch('services.agent_system.InsuranceAgentSystem') as mock_agent:
            mock_agent_instance = mock_agent.return_value
            mock_agent_instance.validate_letter = AsyncMock(
                return_value={
                    "is_valid": False,
                    "compliance_score": 0.0,
                    "tone_score": 0.0,
                    "suggestions": ["Invalid letter type"]
                }
            )
            
            from function_app import validate_letter
            
            response = await validate_letter(request)
            
            assert response.status_code == 200
            response_data = json.loads(response.get_body())
            assert response_data["is_valid"] is False