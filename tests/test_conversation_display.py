import unittest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import azure.functions as func
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from function_app import draft_letter


class TestConversationDisplay(unittest.TestCase):
    """Test the agent conversation display feature."""
    
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
    
    def _create_http_request(self, body=None):
        """Helper to create mock HTTP request."""
        req = Mock(spec=func.HttpRequest)
        req.method = 'POST'
        req.url = 'http://localhost:7071/api/draft-letter'
        req.headers = {'Content-Type': 'application/json'}
        req.get_json.return_value = body
        return req
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_conversation_included_when_requested(self, mock_generate):
        """Test that conversation is included when include_conversation is True."""
        # Mock response with conversation
        mock_generate.return_value = {
            "letter_content": "Dear Customer, Your policy renewal is due...",
            "approval_status": {
                "overall_approved": True,
                "compliance_approved": True,
                "legal_approved": True
            },
            "total_rounds": 2,
            "agent_conversation": [
                {
                    "round": 1,
                    "agent": "LetterWriter",
                    "message": "I'll draft a renewal letter. Dear Customer, Your policy renewal is due next month. WRITER_APPROVED",
                    "timestamp": "2024-01-01T10:00:00"
                },
                {
                    "round": 1,
                    "agent": "ComplianceReviewer",
                    "message": "The letter meets all regulatory requirements. COMPLIANCE_APPROVED",
                    "timestamp": "2024-01-01T10:01:00"
                },
                {
                    "round": 1,
                    "agent": "CustomerServiceReviewer",
                    "message": "The tone is professional and clear. CUSTOMER_SERVICE_APPROVED",
                    "timestamp": "2024-01-01T10:02:00"
                }
            ]
        }
        
        req_body = {
            "customer_info": {
                "name": "John Doe",
                "policy_number": "POL123456"
            },
            "letter_type": "policy_renewal",
            "user_prompt": "Generate renewal letter",
            "include_conversation": True
        }
        
        req = self._create_http_request(body=req_body)
        
        # Run the async function
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_body())
        
        # Verify conversation is included
        self.assertIn('agent_conversation', response_data)
        self.assertEqual(len(response_data['agent_conversation']), 3)
        
        # Verify conversation structure
        first_message = response_data['agent_conversation'][0]
        self.assertEqual(first_message['agent'], 'LetterWriter')
        self.assertEqual(first_message['round'], 1)
        self.assertIn('message', first_message)
        self.assertIn('timestamp', first_message)
        
        # Verify the function was called with include_conversation=True
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args.kwargs
        self.assertTrue(call_kwargs['include_conversation'])
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_conversation_excluded_when_not_requested(self, mock_generate):
        """Test that conversation is excluded when include_conversation is False or not provided."""
        # Mock response without conversation
        mock_generate.return_value = {
            "letter_content": "Dear Customer, Your policy renewal is due...",
            "approval_status": {
                "overall_approved": True,
                "compliance_approved": True,
                "legal_approved": True
            },
            "total_rounds": 2
        }
        
        req_body = {
            "customer_info": {
                "name": "Jane Smith",
                "policy_number": "POL789012"
            },
            "letter_type": "policy_renewal",
            "user_prompt": "Generate renewal letter",
            "include_conversation": False
        }
        
        req = self._create_http_request(body=req_body)
        
        # Run the async function
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_body())
        
        # Verify conversation is NOT included
        self.assertNotIn('agent_conversation', response_data)
        
        # Verify the function was called with include_conversation=False
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args.kwargs
        self.assertFalse(call_kwargs['include_conversation'])
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_conversation_default_behavior(self, mock_generate):
        """Test that conversation is excluded by default when parameter is not provided."""
        mock_generate.return_value = {
            "letter_content": "Test letter",
            "approval_status": {"overall_approved": True},
            "total_rounds": 1
        }
        
        req_body = {
            "customer_info": {
                "name": "Default Test",
                "policy_number": "DEF123"
            },
            "letter_type": "general",
            "user_prompt": "Test default behavior"
            # Note: include_conversation is not provided
        }
        
        req = self._create_http_request(body=req_body)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_body())
        
        # Verify conversation is NOT included by default
        self.assertNotIn('agent_conversation', response_data)
        
        # Verify the function was called with include_conversation=False (default)
        call_kwargs = mock_generate.call_args.kwargs
        self.assertFalse(call_kwargs['include_conversation'])
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_conversation_with_multiple_rounds(self, mock_generate):
        """Test conversation display with multiple approval rounds."""
        mock_generate.return_value = {
            "letter_content": "Final approved letter content",
            "approval_status": {
                "overall_approved": True,
                "compliance_approved": True,
                "legal_approved": True
            },
            "total_rounds": 3,
            "agent_conversation": [
                # Round 1
                {
                    "round": 1,
                    "agent": "LetterWriter",
                    "message": "Initial draft. WRITER_NEEDS_IMPROVEMENT",
                    "timestamp": "2024-01-01T10:00:00"
                },
                {
                    "round": 1,
                    "agent": "ComplianceReviewer",
                    "message": "Missing required disclosures. COMPLIANCE_REJECTED",
                    "timestamp": "2024-01-01T10:01:00"
                },
                {
                    "round": 1,
                    "agent": "CustomerServiceReviewer",
                    "message": "Tone needs adjustment. CUSTOMER_SERVICE_REJECTED",
                    "timestamp": "2024-01-01T10:02:00"
                },
                # Round 2
                {
                    "round": 2,
                    "agent": "LetterWriter",
                    "message": "Revised draft with disclosures. WRITER_NEEDS_IMPROVEMENT",
                    "timestamp": "2024-01-01T10:03:00"
                },
                {
                    "round": 2,
                    "agent": "ComplianceReviewer",
                    "message": "Disclosures added. COMPLIANCE_APPROVED",
                    "timestamp": "2024-01-01T10:04:00"
                },
                {
                    "round": 2,
                    "agent": "CustomerServiceReviewer",
                    "message": "Still needs softer tone. CUSTOMER_SERVICE_REJECTED",
                    "timestamp": "2024-01-01T10:05:00"
                },
                # Round 3
                {
                    "round": 3,
                    "agent": "LetterWriter",
                    "message": "Final draft with improved tone. WRITER_APPROVED",
                    "timestamp": "2024-01-01T10:06:00"
                },
                {
                    "round": 3,
                    "agent": "ComplianceReviewer",
                    "message": "All requirements met. COMPLIANCE_APPROVED",
                    "timestamp": "2024-01-01T10:07:00"
                },
                {
                    "round": 3,
                    "agent": "CustomerServiceReviewer",
                    "message": "Perfect tone and clarity. CUSTOMER_SERVICE_APPROVED",
                    "timestamp": "2024-01-01T10:08:00"
                }
            ]
        }
        
        req_body = {
            "customer_info": {
                "name": "Multi Round Test",
                "policy_number": "MRT123"
            },
            "letter_type": "claim_denial",
            "user_prompt": "Deny claim with empathy",
            "include_conversation": True
        }
        
        req = self._create_http_request(body=req_body)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_body())
        
        # Verify conversation has all rounds
        self.assertIn('agent_conversation', response_data)
        self.assertEqual(len(response_data['agent_conversation']), 9)  # 3 agents * 3 rounds
        
        # Verify rounds are properly tracked
        round_1_messages = [m for m in response_data['agent_conversation'] if m['round'] == 1]
        round_2_messages = [m for m in response_data['agent_conversation'] if m['round'] == 2]
        round_3_messages = [m for m in response_data['agent_conversation'] if m['round'] == 3]
        
        self.assertEqual(len(round_1_messages), 3)
        self.assertEqual(len(round_2_messages), 3)
        self.assertEqual(len(round_3_messages), 3)
        
        # Verify final round has all approvals
        final_round_approvals = [
            'WRITER_APPROVED' in m['message'] or
            'COMPLIANCE_APPROVED' in m['message'] or
            'CUSTOMER_SERVICE_APPROVED' in m['message']
            for m in round_3_messages
        ]
        self.assertTrue(all(final_round_approvals))


if __name__ == '__main__':
    unittest.main()