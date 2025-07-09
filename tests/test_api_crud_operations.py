import unittest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import azure.functions as func
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from function_app import app


class TestAPICRUDOperations(unittest.TestCase):
    """Test CRUD operations through API endpoints with Cosmos DB."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cosmos_patcher = patch('function_app.cosmos_service')
        self.mock_cosmos = self.cosmos_patcher.start()
        
        # In-memory storage to simulate Cosmos DB
        self.letter_storage = {}
        self.next_id = 1
        
        # Mock Cosmos methods
        self.mock_cosmos.health_check.return_value = True
        self.mock_cosmos.save_letter.side_effect = self._mock_save_letter
        self.mock_cosmos.get_letter.side_effect = self._mock_get_letter
        self.mock_cosmos.get_letters_by_customer.side_effect = self._mock_get_letters_by_customer
        self.mock_cosmos.get_letters_by_type.side_effect = self._mock_get_letters_by_type
        self.mock_cosmos.get_recent_letters.side_effect = self._mock_get_recent_letters
        self.mock_cosmos.update_letter_status.side_effect = self._mock_update_letter_status
        self.mock_cosmos.delete_letter.side_effect = self._mock_delete_letter
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.cosmos_patcher.stop()
        
    def _mock_save_letter(self, letter_doc):
        """Mock saving a letter to Cosmos DB."""
        if 'id' not in letter_doc:
            letter_doc['id'] = f'letter_{self.next_id}'
            self.next_id += 1
        self.letter_storage[letter_doc['id']] = letter_doc.copy()
        return letter_doc
    
    def _mock_get_letter(self, letter_id, partition_key='letter'):
        """Mock getting a letter from Cosmos DB."""
        letter = self.letter_storage.get(letter_id)
        if letter and not letter.get('deleted', False):
            return letter
        return None
    
    def _mock_get_letters_by_customer(self, customer_name, limit=10):
        """Mock getting letters by customer."""
        letters = [
            letter for letter in self.letter_storage.values()
            if letter.get('customer_name') == customer_name and not letter.get('deleted', False)
        ]
        return sorted(letters, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
    
    def _mock_get_letters_by_type(self, letter_type, limit=10):
        """Mock getting letters by type."""
        letters = [
            letter for letter in self.letter_storage.values()
            if letter.get('letter_type') == letter_type and not letter.get('deleted', False)
        ]
        return sorted(letters, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
    
    def _mock_get_recent_letters(self, limit=20):
        """Mock getting recent letters."""
        letters = [
            letter for letter in self.letter_storage.values()
            if not letter.get('deleted', False)
        ]
        return sorted(letters, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
    
    def _mock_update_letter_status(self, letter_id, status, partition_key='letter'):
        """Mock updating letter status."""
        if letter_id in self.letter_storage:
            self.letter_storage[letter_id]['compliance_status'] = status
            self.letter_storage[letter_id]['updated_at'] = datetime.now().isoformat()
            return self.letter_storage[letter_id]
        return None
    
    def _mock_delete_letter(self, letter_id, partition_key='letter'):
        """Mock deleting a letter (soft delete)."""
        if letter_id in self.letter_storage:
            self.letter_storage[letter_id]['deleted'] = True
            self.letter_storage[letter_id]['deleted_at'] = datetime.now().isoformat()
            return True
        return False
    
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
    
    # ============= CREATE Tests =============
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_create_multiple_letters(self, mock_generate):
        """Test creating multiple letters and verifying storage."""
        # Create first letter
        mock_generate.return_value = {
            "letter_content": "First letter content",
            "approval_status": {"overall_approved": True},
            "total_rounds": 1
        }
        
        req_body1 = {
            "customer_info": {
                "name": "Customer One",
                "policy_number": "POL001"
            },
            "letter_type": "welcome",
            "user_prompt": "Welcome letter"
        }
        
        req1 = self._create_http_request('POST', body=req_body1)
        
        # Import draft_letter directly
        from function_app import draft_letter
        
        loop = asyncio.new_event_loop()
        response1 = loop.run_until_complete(draft_letter(req1))
        
        self.assertEqual(response1.status_code, 200)
        response_data1 = json.loads(response1.get_body())
        letter_id1 = response_data1.get('document_id')
        
        # Create second letter
        mock_generate.return_value = {
            "letter_content": "Second letter content",
            "approval_status": {"overall_approved": False},
            "total_rounds": 3
        }
        
        req_body2 = {
            "customer_info": {
                "name": "Customer Two",
                "policy_number": "POL002"
            },
            "letter_type": "claim_denial",
            "user_prompt": "Claim denial letter"
        }
        
        req2 = self._create_http_request('POST', body=req_body2)
        response2 = loop.run_until_complete(draft_letter(req2))
        loop.close()
        
        self.assertEqual(response2.status_code, 200)
        response_data2 = json.loads(response2.get_body())
        letter_id2 = response_data2.get('document_id')
        
        # Verify both letters are stored
        self.assertNotEqual(letter_id1, letter_id2)
        self.assertEqual(len(self.letter_storage), 2)
        
        # Verify letter properties
        letter1 = self.letter_storage[letter_id1]
        self.assertEqual(letter1['customer_name'], 'Customer One')
        self.assertEqual(letter1['compliance_status'], 'approved')
        
        letter2 = self.letter_storage[letter_id2]
        self.assertEqual(letter2['customer_name'], 'Customer Two')
        self.assertEqual(letter2['compliance_status'], 'needs_review')
    
    # ============= READ Tests =============
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_read_operations_after_create(self, mock_generate):
        """Test various read operations after creating letters."""
        # Create multiple letters
        customers = [
            ("John Doe", "POL100", "policy_renewal"),
            ("John Doe", "POL101", "claim_approval"),
            ("Jane Smith", "POL200", "policy_renewal"),
            ("Bob Johnson", "POL300", "cancellation")
        ]
        
        from function_app import draft_letter
        loop = asyncio.new_event_loop()
        
        for customer_name, policy_number, letter_type in customers:
            mock_generate.return_value = {
                "letter_content": f"Letter for {customer_name}",
                "approval_status": {"overall_approved": True},
                "total_rounds": 1
            }
            
            req_body = {
                "customer_info": {
                    "name": customer_name,
                    "policy_number": policy_number
                },
                "letter_type": letter_type,
                "user_prompt": f"Generate {letter_type} letter"
            }
            
            req = self._create_http_request('POST', body=req_body)
            loop.run_until_complete(draft_letter(req))
        
        loop.close()
        
        # Test get_letters_by_customer
        john_letters = self.mock_cosmos.get_letters_by_customer("John Doe")
        self.assertEqual(len(john_letters), 2)
        self.assertTrue(all(l['customer_name'] == "John Doe" for l in john_letters))
        
        # Test get_letters_by_type
        renewal_letters = self.mock_cosmos.get_letters_by_type("policy_renewal")
        self.assertEqual(len(renewal_letters), 2)
        self.assertTrue(all(l['letter_type'] == "policy_renewal" for l in renewal_letters))
        
        # Test get_recent_letters
        recent_letters = self.mock_cosmos.get_recent_letters(limit=3)
        self.assertEqual(len(recent_letters), 3)
        
        # Test get specific letter
        first_letter_id = list(self.letter_storage.keys())[0]
        letter = self.mock_cosmos.get_letter(first_letter_id)
        self.assertIsNotNone(letter)
        self.assertEqual(letter['id'], first_letter_id)
    
    # ============= UPDATE Tests =============
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_update_letter_status_workflow(self, mock_generate):
        """Test updating letter status through workflow."""
        # Create a letter that needs review
        mock_generate.return_value = {
            "letter_content": "Letter needing review",
            "approval_status": {"overall_approved": False},
            "total_rounds": 5
        }
        
        req_body = {
            "customer_info": {
                "name": "Review Customer",
                "policy_number": "REV001"
            },
            "letter_type": "claim_denial",
            "user_prompt": "Deny claim"
        }
        
        from function_app import draft_letter
        req = self._create_http_request('POST', body=req_body)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        response_data = json.loads(response.get_body())
        letter_id = response_data.get('document_id')
        
        # Verify initial status
        letter = self.mock_cosmos.get_letter(letter_id)
        self.assertEqual(letter['compliance_status'], 'needs_review')
        
        # Update status to approved
        updated_letter = self.mock_cosmos.update_letter_status(letter_id, 'approved')
        self.assertIsNotNone(updated_letter)
        self.assertEqual(updated_letter['compliance_status'], 'approved')
        self.assertIn('updated_at', updated_letter)
        
        # Verify the update persisted
        letter_after_update = self.mock_cosmos.get_letter(letter_id)
        self.assertEqual(letter_after_update['compliance_status'], 'approved')
    
    # ============= DELETE Tests =============
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_delete_letter_workflow(self, mock_generate):
        """Test soft delete functionality."""
        # Create a letter
        mock_generate.return_value = {
            "letter_content": "Letter to be deleted",
            "approval_status": {"overall_approved": True},
            "total_rounds": 1
        }
        
        req_body = {
            "customer_info": {
                "name": "Delete Test",
                "policy_number": "DEL001"
            },
            "letter_type": "general",
            "user_prompt": "Test letter"
        }
        
        from function_app import draft_letter
        req = self._create_http_request('POST', body=req_body)
        
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(draft_letter(req))
        loop.close()
        
        response_data = json.loads(response.get_body())
        letter_id = response_data.get('document_id')
        
        # Verify letter exists
        letter = self.mock_cosmos.get_letter(letter_id)
        self.assertIsNotNone(letter)
        
        # Delete the letter
        deleted = self.mock_cosmos.delete_letter(letter_id)
        self.assertTrue(deleted)
        
        # Verify soft delete - letter should not be returned by get_letter
        deleted_letter = self.mock_cosmos.get_letter(letter_id)
        self.assertIsNone(deleted_letter)
        
        # But it should still exist in storage with deleted flag
        stored_letter = self.letter_storage.get(letter_id)
        self.assertIsNotNone(stored_letter)
        self.assertTrue(stored_letter['deleted'])
        self.assertIn('deleted_at', stored_letter)
        
        # Verify deleted letters don't appear in queries
        customer_letters = self.mock_cosmos.get_letters_by_customer("Delete Test")
        self.assertEqual(len(customer_letters), 0)
    
    # ============= Complex Workflow Tests =============
    
    @patch('function_app.generate_letter_with_approval_workflow')
    def test_complete_crud_lifecycle(self, mock_generate):
        """Test complete CRUD lifecycle with multiple operations."""
        from function_app import draft_letter
        loop = asyncio.new_event_loop()
        
        # 1. Create multiple letters for same customer
        letter_ids = []
        for i in range(3):
            mock_generate.return_value = {
                "letter_content": f"Letter {i+1} content",
                "approval_status": {"overall_approved": i % 2 == 0},
                "total_rounds": i + 1
            }
            
            req_body = {
                "customer_info": {
                    "name": "Lifecycle Customer",
                    "policy_number": f"LIFE{i:03d}"
                },
                "letter_type": ["welcome", "policy_renewal", "claim_denial"][i],
                "user_prompt": f"Letter {i+1}"
            }
            
            req = self._create_http_request('POST', body=req_body)
            response = loop.run_until_complete(draft_letter(req))
            response_data = json.loads(response.get_body())
            letter_ids.append(response_data.get('document_id'))
        
        loop.close()
        
        # 2. Read all letters for customer
        customer_letters = self.mock_cosmos.get_letters_by_customer("Lifecycle Customer")
        self.assertEqual(len(customer_letters), 3)
        
        # 3. Update the needs_review letter to approved
        needs_review_letter = [l for l in customer_letters if l['compliance_status'] == 'needs_review'][0]
        updated = self.mock_cosmos.update_letter_status(needs_review_letter['id'], 'approved')
        self.assertEqual(updated['compliance_status'], 'approved')
        
        # 4. Delete one letter
        self.mock_cosmos.delete_letter(letter_ids[0])
        
        # 5. Verify final state
        remaining_letters = self.mock_cosmos.get_letters_by_customer("Lifecycle Customer")
        self.assertEqual(len(remaining_letters), 2)
        
        # All remaining letters should be approved
        self.assertTrue(all(l['compliance_status'] == 'approved' for l in remaining_letters))
    
    def test_concurrent_operations(self):
        """Test handling concurrent CRUD operations."""
        # This test simulates concurrent operations on the same data
        initial_count = len(self.letter_storage)
        
        # Simulate concurrent saves
        letters = []
        for i in range(5):
            letter = {
                "id": f"concurrent_{i}",
                "type": "letter",
                "customer_name": f"Customer {i}",
                "letter_type": "general",
                "created_at": datetime.now().isoformat()
            }
            saved = self.mock_cosmos.save_letter(letter)
            letters.append(saved)
        
        # Verify all saves succeeded
        self.assertEqual(len(self.letter_storage), initial_count + 5)
        
        # Simulate concurrent updates
        for letter in letters[:3]:
            self.mock_cosmos.update_letter_status(letter['id'], 'approved')
        
        # Simulate concurrent deletes
        for letter in letters[3:]:
            self.mock_cosmos.delete_letter(letter['id'])
        
        # Verify final state
        active_letters = [l for l in self.letter_storage.values() if not l.get('deleted', False)]
        self.assertEqual(len(active_letters), initial_count + 3)
        
        # Verify all active letters are approved
        active_concurrent = [l for l in active_letters if l['id'].startswith('concurrent_')]
        self.assertTrue(all(l['compliance_status'] == 'approved' for l in active_concurrent))


if __name__ == '__main__':
    unittest.main()