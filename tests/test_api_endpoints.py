import unittest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
import azure.functions as func
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from function_app import app, health_check, draft_letter, suggest_letter_type_endpoint, validate_letter_endpoint


class TestAPIEndpoints(unittest.TestCase):
    """Comprehensive tests for all API endpoints including Cosmos DB operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cosmos_patcher = patch('function_app.cosmos_service')
        self.mock_cosmos = self.cosmos_patcher.start()
        
        # Mock Cosmos DB methods
        self.mock_cosmos.health_check.return_value = True
        self.mock_cosmos.save_letter.return_value = {"id": "test-letter-id"}
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.cosmos_patcher.stop()
    
    def _create_http_request(self, method='GET', body=None, params=None):
        """Helper to create mock HTTP request."""
        req = Mock(spec=func.HttpRequest)
        req.method = method
        req.url = 'http://localhost:7071/api/test'
        req.headers = {'Content-Type': 'application/json'}
        req.params = params or {}
        
        if body:
            req.get_json.return_value = body
        else:
            req.get_json.return_value = None
            
        return req
    
    # ============= Health Check Tests =============
    
    def test_health_check_success(self):
        """Test successful health check with Cosmos DB connection."""
        req = self._create_http_request()
        
        response = health_check(req)
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.get_body())
        self.assertEqual(response_data['status'], 'healthy')
        self.assertEqual(response_data['cosmos_db'], 'connected')
        self.assertIn('timestamp', response_data)
        self.assertIn('endpoints', response_data)
        
    def test_health_check_cosmos_failure(self):
        """Test health check when Cosmos DB is down."""
        req = self._create_http_request()
        self.mock_cosmos.health_check.side_effect = Exception("Cosmos DB connection failed")
        
        response = health_check(req)
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.get_body())
        self.assertEqual(response_data['status'], 'degraded')
        self.assertIn('error', response_data['cosmos_db'])
    
    def test_health_check_complete_failure(self):
        """Test health check when everything fails."""
        req = self._create_http_request()
        
        with patch('function_app.datetime') as mock_datetime:
            mock_datetime.now.side_effect = Exception("System failure")
            
            response = health_check(req)
            
            self.assertEqual(response.status_code, 503)
            response_data = json.loads(response.get_body())
            self.assertEqual(response_data['status'], 'unhealthy')
    
    # ============= Draft Letter Tests =============
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_draft_letter_success(self, mock_generate):
        """Test successful letter generation with Cosmos DB save."""
        # Set up async mock
        mock_generate.return_value = {
            "letter_content": "Dear Customer, This is your renewal letter...",
            "approval_status": {
                "overall_approved": True,
                "compliance_approved": True,
                "legal_approved": True
            },
            "total_rounds": 2
        }
        
        req_body = {
            "customer_info": {
                "name": "John Doe",
                "policy_number": "POL123456"
            },
            "letter_type": "policy_renewal",
            "user_prompt": "Generate renewal letter for policy expiring next month"
        }
        
        req = self._create_http_request('POST', body=req_body)
        
        # Run the async function
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_body())
        
        # Verify response
        self.assertIn('letter_content', response_data)
        self.assertIn('approval_status', response_data)
        self.assertIn('document_id', response_data)
        
        # Verify Cosmos DB save was called
        self.mock_cosmos.save_letter.assert_called_once()
        saved_letter = self.mock_cosmos.save_letter.call_args[0][0]
        self.assertEqual(saved_letter['customer_name'], 'John Doe')
        self.assertEqual(saved_letter['policy_number'], 'POL123456')
        self.assertEqual(saved_letter['letter_type'], 'policy_renewal')
        self.assertEqual(saved_letter['compliance_status'], 'approved')
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_draft_letter_not_approved(self, mock_generate):
        """Test letter generation when not approved."""
        mock_generate.return_value = {
            "letter_content": "Dear Customer...",
            "approval_status": {
                "overall_approved": False,
                "compliance_approved": False,
                "legal_approved": True
            },
            "total_rounds": 5
        }
        
        req_body = {
            "customer_info": {
                "name": "Jane Smith",
                "policy_number": "POL789012"
            },
            "letter_type": "claim_denial",
            "user_prompt": "Deny claim for water damage"
        }
        
        req = self._create_http_request('POST', body=req_body)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        self.assertEqual(response.status_code, 200)
        
        # Verify Cosmos DB save with needs_review status
        saved_letter = self.mock_cosmos.save_letter.call_args[0][0]
        self.assertEqual(saved_letter['compliance_status'], 'needs_review')
    
    def test_draft_letter_missing_body(self):
        """Test draft letter with missing request body."""
        req = self._create_http_request('POST', body=None)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.get_body())
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Request body is required')
    
    def test_draft_letter_missing_customer_info(self):
        """Test draft letter with missing customer information."""
        req_body = {
            "letter_type": "policy_renewal",
            "user_prompt": "Generate renewal letter"
        }
        
        req = self._create_http_request('POST', body=req_body)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.get_body())
        self.assertIn('Customer name and policy number are required', response_data['error'])
    
    def test_draft_letter_invalid_letter_type(self):
        """Test draft letter with invalid letter type."""
        req_body = {
            "customer_info": {
                "name": "John Doe",
                "policy_number": "POL123"
            },
            "letter_type": "invalid_type",
            "user_prompt": "Generate letter"
        }
        
        req = self._create_http_request('POST', body=req_body)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.get_body())
        self.assertIn('Invalid letter type', response_data['error'])
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_draft_letter_cosmos_save_failure(self, mock_generate):
        """Test handling of Cosmos DB save failure."""
        mock_generate.return_value = {
            "letter_content": "Test content",
            "approval_status": {"overall_approved": True}
        }
        
        self.mock_cosmos.save_letter.side_effect = Exception("Cosmos DB error")
        
        req_body = {
            "customer_info": {
                "name": "Test User",
                "policy_number": "TEST123"
            },
            "letter_type": "policy_renewal",
            "user_prompt": "Test prompt"
        }
        
        req = self._create_http_request('POST', body=req_body)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_body())
        self.assertIn('storage_error', response_data)
    
    # ============= Suggest Letter Type Tests =============
    
    @patch('function_app.suggest_letter_type')
    def test_suggest_letter_type_success(self, mock_suggest):
        """Test successful letter type suggestion."""
        mock_suggest.return_value = {
            "suggested_type": "renewal",
            "confidence": 0.95,
            "reasoning": "User mentioned policy expiration"
        }
        
        req_body = {
            "prompt": "I need to notify customer about policy expiration"
        }
        
        req = self._create_http_request('POST', body=req_body)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(suggest_letter_type_endpoint(req))
        loop.close()
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_body())
        self.assertEqual(response_data['suggested_type'], 'renewal')
        self.assertIn('confidence', response_data)
    
    def test_suggest_letter_type_missing_prompt(self):
        """Test suggest letter type with missing prompt."""
        req_body = {}
        req = self._create_http_request('POST', body=req_body)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(suggest_letter_type_endpoint(req))
        loop.close()
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.get_body())
        self.assertEqual(response_data['error'], 'Prompt is required')
    
    # ============= Validate Letter Tests =============
    
    @patch('function_app.validate_letter_content')
    def test_validate_letter_success(self, mock_validate):
        """Test successful letter validation."""
        mock_validate.return_value = {
            "is_compliant": True,
            "issues": [],
            "score": 98
        }
        
        req_body = {
            "letter_content": "Dear Customer, Your policy is expiring...",
            "letter_type": "policy_renewal"
        }
        
        req = self._create_http_request('POST', body=req_body)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(validate_letter_endpoint(req))
        loop.close()
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_body())
        self.assertTrue(response_data['is_compliant'])
        self.assertEqual(response_data['score'], 98)
    
    def test_validate_letter_missing_content(self):
        """Test validate letter with missing content."""
        req_body = {
            "letter_type": "policy_renewal"
        }
        
        req = self._create_http_request('POST', body=req_body)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(validate_letter_endpoint(req))
        loop.close()
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.get_body())
        self.assertEqual(response_data['error'], 'Letter content is required')


class TestCosmosDBIntegration(unittest.TestCase):
    """Test Cosmos DB CRUD operations through API endpoints."""
    
    def setUp(self):
        """Set up test fixtures for Cosmos DB integration tests."""
        self.cosmos_patcher = patch('function_app.cosmos_service')
        self.mock_cosmos = self.cosmos_patcher.start()
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.cosmos_patcher.stop()
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_create_letter_document(self, mock_generate):
        """Test creating a letter document in Cosmos DB."""
        mock_generate.return_value = {
            "letter_content": "Test letter content",
            "approval_status": {"overall_approved": True},
            "total_rounds": 1
        }
        
        # Capture the document saved to Cosmos
        saved_document = None
        def save_letter_side_effect(doc):
            nonlocal saved_document
            saved_document = doc
            return {"id": "generated-id-123"}
        
        self.mock_cosmos.save_letter.side_effect = save_letter_side_effect
        
        req_body = {
            "customer_info": {
                "name": "Test Customer",
                "policy_number": "TEST-POL-123",
                "email": "test@example.com"
            },
            "letter_type": "policy_renewal",
            "user_prompt": "Generate renewal reminder"
        }
        
        req = Mock(spec=func.HttpRequest)
        req.method = 'POST'
        req.get_json.return_value = req_body
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        # Verify document structure
        self.assertIsNotNone(saved_document)
        self.assertEqual(saved_document['type'], 'letter')
        self.assertEqual(saved_document['customer_name'], 'Test Customer')
        self.assertEqual(saved_document['policy_number'], 'TEST-POL-123')
        self.assertEqual(saved_document['letter_type'], 'policy_renewal')
        self.assertEqual(saved_document['compliance_status'], 'approved')
        self.assertIn('created_at', saved_document)
        self.assertIn('user_prompt', saved_document)
        self.assertIn('approval_details', saved_document)
    
    def test_cosmos_db_connection_in_health_check(self):
        """Test Cosmos DB connection status in health check."""
        # Test successful connection
        self.mock_cosmos.health_check.return_value = True
        
        req = Mock(spec=func.HttpRequest)
        req.method = 'GET'
        
        response = health_check(req)
        response_data = json.loads(response.get_body())
        
        self.assertEqual(response_data['cosmos_db'], 'connected')
        
        # Test failed connection
        self.mock_cosmos.health_check.side_effect = Exception("Connection timeout")
        
        response = health_check(req)
        response_data = json.loads(response.get_body())
        
        self.assertEqual(response_data['status'], 'degraded')
        self.assertIn('Connection timeout', response_data['cosmos_db'])


class TestLetterLifecycle(unittest.TestCase):
    """Test complete letter lifecycle including CRUD operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cosmos_patcher = patch('function_app.cosmos_service')
        self.mock_cosmos = self.cosmos_patcher.start()
        
        # Store for simulating Cosmos DB
        self.letter_store = {}
        
        def save_letter(doc):
            doc_id = doc.get('id', f'letter_{len(self.letter_store)}')
            doc['id'] = doc_id
            self.letter_store[doc_id] = doc.copy()
            return doc
        
        def get_letter(letter_id, partition_key='letter'):
            return self.letter_store.get(letter_id)
        
        def update_letter_status(letter_id, status, partition_key='letter'):
            if letter_id in self.letter_store:
                self.letter_store[letter_id]['compliance_status'] = status
                self.letter_store[letter_id]['updated_at'] = datetime.now().isoformat()
                return self.letter_store[letter_id]
            return None
        
        def delete_letter(letter_id, partition_key='letter'):
            if letter_id in self.letter_store:
                self.letter_store[letter_id]['deleted'] = True
                self.letter_store[letter_id]['deleted_at'] = datetime.now().isoformat()
                return True
            return False
        
        self.mock_cosmos.save_letter.side_effect = save_letter
        self.mock_cosmos.get_letter.side_effect = get_letter
        self.mock_cosmos.update_letter_status.side_effect = update_letter_status
        self.mock_cosmos.delete_letter.side_effect = delete_letter
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.cosmos_patcher.stop()
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_complete_letter_lifecycle(self, mock_generate):
        """Test creating, reading, updating, and deleting a letter."""
        # 1. Create letter
        mock_generate.return_value = {
            "letter_content": "Complete lifecycle test",
            "approval_status": {"overall_approved": False},
            "total_rounds": 3
        }
        
        req_body = {
            "customer_info": {
                "name": "Lifecycle Test",
                "policy_number": "LIFE-123"
            },
            "letter_type": "claim_denial",
            "user_prompt": "Test lifecycle"
        }
        
        req = Mock(spec=func.HttpRequest)
        req.method = 'POST'
        req.get_json.return_value = req_body
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        response_data = json.loads(response.get_body())
        letter_id = response_data.get('document_id')
        
        # 2. Verify letter was created with needs_review status
        self.assertIsNotNone(letter_id)
        letter = self.mock_cosmos.get_letter(letter_id)
        self.assertEqual(letter['compliance_status'], 'needs_review')
        
        # 3. Update letter status to approved
        updated_letter = self.mock_cosmos.update_letter_status(letter_id, 'approved')
        self.assertEqual(updated_letter['compliance_status'], 'approved')
        self.assertIn('updated_at', updated_letter)
        
        # 4. Delete letter (soft delete)
        deleted = self.mock_cosmos.delete_letter(letter_id)
        self.assertTrue(deleted)
        
        # 5. Verify soft delete
        deleted_letter = self.mock_cosmos.get_letter(letter_id)
        self.assertTrue(deleted_letter['deleted'])
        self.assertIn('deleted_at', deleted_letter)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cosmos_patcher = patch('function_app.cosmos_service')
        self.mock_cosmos = self.cosmos_patcher.start()
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.cosmos_patcher.stop()
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_generation_failure(self, mock_generate):
        """Test handling of letter generation failure."""
        mock_generate.side_effect = Exception("AI service unavailable")
        
        req_body = {
            "customer_info": {
                "name": "Error Test",
                "policy_number": "ERR-123"
            },
            "letter_type": "policy_renewal",
            "user_prompt": "Test error"
        }
        
        req = Mock(spec=func.HttpRequest)
        req.method = 'POST'
        req.get_json.return_value = req_body
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.get_body())
        self.assertIn('AI service unavailable', response_data['error'])
    
    def test_malformed_json_request(self):
        """Test handling of malformed JSON in request."""
        req = Mock(spec=func.HttpRequest)
        req.method = 'POST'
        req.get_json.side_effect = ValueError("Invalid JSON")
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        self.assertEqual(response.status_code, 500)
    
    @patch('function_app.suggest_letter_type')
    def test_suggestion_service_timeout(self, mock_suggest):
        """Test handling of service timeout."""
        mock_suggest.side_effect = asyncio.TimeoutError("Service timeout")
        
        req_body = {"prompt": "Test timeout"}
        req = Mock(spec=func.HttpRequest)
        req.method = 'POST'
        req.get_json.return_value = req_body
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(suggest_letter_type_endpoint(req))
        loop.close()
        
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.get_body())
        self.assertIn('error', response_data)


if __name__ == '__main__':
    unittest.main()