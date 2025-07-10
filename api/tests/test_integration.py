"""
Integration tests for the complete API workflow.
"""
import pytest
import json
from unittest.mock import patch, Mock, AsyncMock
from datetime import datetime
import azure.functions as func


class TestAPIIntegration:
    """Integration tests for complete API workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_letter_generation_workflow(
        self, mock_env, mock_http_request, sample_letter_request
    ):
        """Test complete workflow from request to saved letter."""
        request = mock_http_request(body=sample_letter_request, method="POST")
        
        # Mock the complete response
        mock_letter_response = {
            "letter_content": """Dear John Doe,

Welcome to State Farm Insurance! We're thrilled to have you as a new member of our insurance family.

Your auto insurance policy POL-123456 is now active and provides comprehensive coverage for your vehicle.

If you have any questions, please don't hesitate to contact your agent, Jane Smith, at 555-1234.

Sincerely,
Jane Smith
State Farm Insurance Agent""",
            "approval_status": {
                "writer_approved": True,
                "compliance_approved": True,
                "customer_service_approved": True,
                "overall_approved": True,
                "status": "fully_approved"
            },
            "total_rounds": 2,
            "agent_conversations": [
                {
                    "round": 1,
                    "agent": "LetterWriter",
                    "role": "writer",
                    "message": "Initial welcome letter drafted",
                    "timestamp": "2025-01-01T10:00:00Z"
                },
                {
                    "round": 1,
                    "agent": "ComplianceReviewer",
                    "role": "compliance",
                    "message": "Missing policy effective date",
                    "timestamp": "2025-01-01T10:01:00Z"
                },
                {
                    "round": 2,
                    "agent": "LetterWriter",
                    "role": "writer",
                    "message": "Added policy effective date",
                    "timestamp": "2025-01-01T10:02:00Z"
                },
                {
                    "round": 2,
                    "agent": "ComplianceReviewer",
                    "role": "compliance",
                    "message": "All compliance requirements met",
                    "timestamp": "2025-01-01T10:03:00Z"
                },
                {
                    "round": 2,
                    "agent": "CustomerServiceAgent",
                    "role": "customer_service",
                    "message": "Tone is friendly and welcoming",
                    "timestamp": "2025-01-01T10:04:00Z"
                }
            ]
        }
        
        mock_cosmos_response = {
            "id": "doc-123-456",
            "type": "letter",
            "created_at": "2025-01-01T10:05:00Z",
            "_etag": "etag-123",
            "_ts": 1704103500
        }
        
        with patch('services.agent_system.InsuranceAgentSystem') as mock_agent:
            mock_agent_instance = mock_agent.return_value
            mock_agent_instance.generate_letter = AsyncMock(
                return_value=mock_letter_response
            )
            
            with patch('services.cosmos_service.CosmosService') as mock_cosmos:
                mock_cosmos_instance = mock_cosmos.return_value
                mock_cosmos_instance.save_letter = AsyncMock(
                    return_value=mock_cosmos_response
                )
                
                from function_app import draft_letter
                
                response = await draft_letter(request)
                
                # Verify response
                assert response.status_code == 200
                response_data = json.loads(response.get_body())
                
                # Check all expected fields
                assert "letter_content" in response_data
                assert "Welcome to State Farm Insurance" in response_data["letter_content"]
                assert response_data["document_id"] == "doc-123-456"
                assert response_data["approval_status"]["overall_approved"] is True
                assert response_data["total_rounds"] == 2
                assert len(response_data["agent_conversations"]) == 5
                
                # Verify agent system was called correctly
                mock_agent_instance.generate_letter.assert_called_once()
                call_args = mock_agent_instance.generate_letter.call_args
                assert call_args[0][0].name == "John Doe"
                assert call_args[0][1].value == "welcome"
                assert call_args[0][2] == "Welcome new customer to auto insurance policy"
                
                # Verify Cosmos save was called
                mock_cosmos_instance.save_letter.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_letter_validation_workflow(self, mock_env, mock_http_request):
        """Test complete letter validation workflow."""
        validation_request = {
            "letter_content": """Dear Mr. Smith,

We regret to inform you that your claim #CLM-789 has been denied.

The reason for denial is that the incident occurred outside the coverage period.

Sincerely,
Claims Department""",
            "letter_type": "claim_denial"
        }
        
        request = mock_http_request(body=validation_request, method="POST")
        
        mock_validation_response = {
            "is_valid": False,
            "compliance_score": 0.65,
            "tone_score": 0.45,
            "suggestions": [
                "Include specific policy clause reference",
                "Add appeal process information",
                "Tone is too abrupt - soften the language",
                "Include agent contact information"
            ]
        }
        
        with patch('services.agent_system.InsuranceAgentSystem') as mock_agent:
            mock_agent_instance = mock_agent.return_value
            mock_agent_instance.validate_letter = AsyncMock(
                return_value=mock_validation_response
            )
            
            from function_app import validate_letter
            
            response = await validate_letter(request)
            
            assert response.status_code == 200
            response_data = json.loads(response.get_body())
            
            assert response_data["is_valid"] is False
            assert response_data["compliance_score"] == 0.65
            assert response_data["tone_score"] == 0.45
            assert len(response_data["suggestions"]) == 4
            assert "appeal process" in response_data["suggestions"][1]
    
    @pytest.mark.asyncio
    async def test_error_handling_cascade(self, mock_env, mock_http_request, sample_letter_request):
        """Test error handling through the full stack."""
        request = mock_http_request(body=sample_letter_request, method="POST")
        
        # Test various error scenarios
        error_scenarios = [
            {
                "name": "AI Service Error",
                "error": Exception("Azure OpenAI service unavailable"),
                "expected_status": 500,
                "expected_message": "Internal server error"
            },
            {
                "name": "Cosmos Connection Error",
                "error": Exception("Cosmos DB connection failed"),
                "expected_status": 500,
                "expected_message": "Internal server error"
            },
            {
                "name": "Rate Limit Error",
                "error": Exception("Rate limit exceeded"),
                "expected_status": 500,
                "expected_message": "Internal server error"
            }
        ]
        
        for scenario in error_scenarios:
            with patch('services.agent_system.InsuranceAgentSystem') as mock_agent:
                if "AI Service" in scenario["name"]:
                    mock_agent_instance = mock_agent.return_value
                    mock_agent_instance.generate_letter = AsyncMock(
                        side_effect=scenario["error"]
                    )
                else:
                    # Normal AI response, error in Cosmos
                    mock_agent_instance = mock_agent.return_value
                    mock_agent_instance.generate_letter = AsyncMock(
                        return_value={"letter_content": "Test", "approval_status": {}}
                    )
                
                with patch('services.cosmos_service.CosmosService') as mock_cosmos:
                    if "Cosmos" in scenario["name"]:
                        mock_cosmos_instance = mock_cosmos.return_value
                        mock_cosmos_instance.save_letter = AsyncMock(
                            side_effect=scenario["error"]
                        )
                    
                    from function_app import draft_letter
                    
                    response = await draft_letter(request)
                    
                    assert response.status_code == scenario["expected_status"]
                    response_data = json.loads(response.get_body())
                    assert scenario["expected_message"] in response_data["error"]
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mock_env, mock_http_request):
        """Test handling of concurrent API requests."""
        import asyncio
        
        # Create multiple different requests
        requests = [
            mock_http_request(
                body={
                    "customer_info": {
                        "name": f"Customer {i}",
                        "policy_number": f"POL-{i:06d}"
                    },
                    "letter_type": "welcome",
                    "user_prompt": f"Welcome customer {i}"
                },
                method="POST"
            )
            for i in range(5)
        ]
        
        with patch('services.agent_system.InsuranceAgentSystem') as mock_agent:
            mock_agent_instance = mock_agent.return_value
            
            # Mock different responses for each request
            async def mock_generate(customer_info, letter_type, prompt):
                await asyncio.sleep(0.1)  # Simulate processing time
                return {
                    "letter_content": f"Dear {customer_info.name}, Welcome!",
                    "approval_status": {
                        "overall_approved": True,
                        "writer_approved": True,
                        "compliance_approved": True,
                        "customer_service_approved": True
                    },
                    "total_rounds": 1,
                    "agent_conversations": []
                }
            
            mock_agent_instance.generate_letter = mock_generate
            
            with patch('services.cosmos_service.CosmosService') as mock_cosmos:
                mock_cosmos_instance = mock_cosmos.return_value
                
                async def mock_save(letter_content, **kwargs):
                    await asyncio.sleep(0.05)  # Simulate save time
                    return {"id": f"doc-{kwargs['customer_info'].name}"}
                
                mock_cosmos_instance.save_letter = mock_save
                
                from function_app import draft_letter
                
                # Execute requests concurrently
                responses = await asyncio.gather(
                    *[draft_letter(req) for req in requests]
                )
                
                # Verify all succeeded
                assert all(r.status_code == 200 for r in responses)
                
                # Verify each got unique response
                response_ids = [
                    json.loads(r.get_body())["document_id"] 
                    for r in responses
                ]
                assert len(set(response_ids)) == 5  # All unique
    
    @pytest.mark.asyncio
    async def test_malformed_request_handling(self, mock_env, mock_http_request):
        """Test handling of various malformed requests."""
        test_cases = [
            {
                "name": "Empty body",
                "body": {},
                "expected_error": "Missing required fields"
            },
            {
                "name": "Missing customer info",
                "body": {
                    "letter_type": "welcome",
                    "user_prompt": "Test"
                },
                "expected_error": "Missing required fields"
            },
            {
                "name": "Invalid letter type",
                "body": {
                    "customer_info": {"name": "Test", "policy_number": "123"},
                    "letter_type": "invalid_type",
                    "user_prompt": "Test"
                },
                "expected_error": "Missing required fields"
            },
            {
                "name": "Null values",
                "body": {
                    "customer_info": None,
                    "letter_type": None,
                    "user_prompt": None
                },
                "expected_error": "Missing required fields"
            }
        ]
        
        from function_app import draft_letter
        
        for test_case in test_cases:
            request = mock_http_request(body=test_case["body"], method="POST")
            response = await draft_letter(request)
            
            assert response.status_code == 400
            response_data = json.loads(response.get_body())
            assert test_case["expected_error"] in response_data["error"]