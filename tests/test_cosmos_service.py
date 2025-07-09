import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.cosmos_service import CosmosService
from azure.cosmos import exceptions


class TestCosmosService(unittest.TestCase):
    
    def setUp(self):
        self.mock_cosmos_client = Mock()
        self.mock_database = Mock()
        self.mock_container = Mock()
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'COSMOS_ENDPOINT': 'https://test.documents.azure.com:443/',
            'COSMOS_KEY': 'test-key',
            'COSMOS_DATABASE_NAME': 'test-db',
            'COSMOS_CONTAINER_NAME': 'test-container'
        })
        self.env_patcher.start()
        
        # Mock the CosmosClient constructor
        self.cosmos_patcher = patch('services.cosmos_service.CosmosClient')
        mock_cosmos_class = self.cosmos_patcher.start()
        mock_cosmos_class.return_value = self.mock_cosmos_client
        
        # Set up the mock client behavior
        self.mock_cosmos_client.create_database.side_effect = exceptions.CosmosResourceExistsError(
            status_code=409, message="Database exists"
        )
        self.mock_cosmos_client.get_database_client.return_value = self.mock_database
        
        self.mock_database.create_container.side_effect = exceptions.CosmosResourceExistsError(
            status_code=409, message="Container exists"
        )
        self.mock_database.get_container_client.return_value = self.mock_container
        
        # Create the service
        self.cosmos_service = CosmosService()
        
    def tearDown(self):
        self.cosmos_patcher.stop()
        self.env_patcher.stop()
    
    def test_health_check_success(self):
        self.mock_database.read.return_value = {"_self": "test"}
        result = self.cosmos_service.health_check()
        self.assertTrue(result)
        self.mock_database.read.assert_called_once()
    
    def test_health_check_failure(self):
        self.mock_database.read.side_effect = Exception("Connection failed")
        with self.assertRaises(Exception) as context:
            self.cosmos_service.health_check()
        self.assertIn("Connection failed", str(context.exception))
    
    def test_save_letter_success(self):
        test_letter_data = {
            "customer_name": "John Doe",
            "policy_number": "POL123",
            "letter_type": "renewal",
            "content": "Test letter content",
            "prompt": "Generate renewal letter",
            "is_compliant": True,
            "approved_by": "manager@test.com"
        }
        
        expected_item = {
            "id": "test-id-123",
            **test_letter_data,
            "type": "letter",
            "created_at": "2024-01-01T00:00:00",
        }
        
        self.mock_container.create_item.return_value = expected_item
        
        result = self.cosmos_service.save_letter(test_letter_data)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["customer_name"], "John Doe")
        self.assertEqual(result["type"], "letter")
        self.mock_container.create_item.assert_called_once()
    
    def test_save_letter_with_auto_generated_fields(self):
        test_letter_data = {
            "customer_name": "John Doe",
            "content": "Test content"
        }
        
        self.mock_container.create_item.return_value = {
            **test_letter_data,
            "id": "auto-generated-id",
            "type": "letter",
            "created_at": datetime.now().isoformat()
        }
        
        result = self.cosmos_service.save_letter(test_letter_data)
        
        # Check that the letter data passed to create_item has required fields
        call_args = self.mock_container.create_item.call_args
        letter_body = call_args.kwargs['body']
        self.assertIn('id', letter_body)
        self.assertEqual(letter_body['type'], 'letter')
        self.assertIn('created_at', letter_body)
    
    def test_get_letter_success(self):
        test_letter = {
            "id": "letter123",
            "type": "letter",
            "content": "Test content",
            "deleted": False
        }
        
        self.mock_container.read_item.return_value = test_letter
        
        result = self.cosmos_service.get_letter("letter123", "letter")
        
        self.assertEqual(result, test_letter)
        self.mock_container.read_item.assert_called_once_with(
            item="letter123",
            partition_key="letter"
        )
    
    def test_get_letter_not_found(self):
        self.mock_container.read_item.side_effect = exceptions.CosmosResourceNotFoundError(
            status_code=404,
            message="Item not found"
        )
        
        result = self.cosmos_service.get_letter("nonexistent", "letter")
        self.assertIsNone(result)
    
    def test_get_letters_by_customer(self):
        test_letters = [
            {"id": "1", "customer_name": "John Doe", "type": "letter"},
            {"id": "2", "customer_name": "John Doe", "type": "letter"}
        ]
        
        mock_query_items = MagicMock()
        mock_query_items.__iter__ = Mock(return_value=iter(test_letters))
        self.mock_container.query_items.return_value = mock_query_items
        
        result = self.cosmos_service.get_letters_by_customer("John Doe")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["customer_name"], "John Doe")
        
    def test_get_letters_by_type(self):
        test_letters = [
            {"id": "1", "letter_type": "renewal", "type": "letter"},
            {"id": "2", "letter_type": "renewal", "type": "letter"}
        ]
        
        mock_query_items = MagicMock()
        mock_query_items.__iter__ = Mock(return_value=iter(test_letters))
        self.mock_container.query_items.return_value = mock_query_items
        
        result = self.cosmos_service.get_letters_by_type("renewal", limit=5)
        
        self.assertEqual(len(result), 2)
        self.assertTrue(all(letter["letter_type"] == "renewal" for letter in result))
    
    def test_get_recent_letters(self):
        test_letters = [
            {"id": "1", "created_at": "2024-01-02", "type": "letter"},
            {"id": "2", "created_at": "2024-01-01", "type": "letter"}
        ]
        
        mock_query_items = MagicMock()
        mock_query_items.__iter__ = Mock(return_value=iter(test_letters))
        self.mock_container.query_items.return_value = mock_query_items
        
        result = self.cosmos_service.get_recent_letters(limit=10)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "1")
    
    def test_update_letter_status_success(self):
        existing_letter = {
            "id": "letter123",
            "type": "letter",
            "compliance_status": "pending",
            "updated_at": "2024-01-01"
        }
        
        self.mock_container.read_item.return_value = existing_letter
        self.mock_container.replace_item.return_value = {
            **existing_letter,
            "compliance_status": "approved",
            "updated_at": datetime.now().isoformat()
        }
        
        result = self.cosmos_service.update_letter_status("letter123", "approved", "letter")
        
        self.assertEqual(result["compliance_status"], "approved")
        self.assertIn("updated_at", result)
    
    def test_delete_letter_success(self):
        existing_letter = {
            "id": "letter123",
            "type": "letter",
            "deleted": False
        }
        
        self.mock_container.read_item.return_value = existing_letter
        self.mock_container.replace_item.return_value = {
            **existing_letter,
            "deleted": True,
            "deleted_at": datetime.now().isoformat()
        }
        
        result = self.cosmos_service.delete_letter("letter123", "letter")
        
        self.assertTrue(result)
        self.mock_container.replace_item.assert_called_once()
    
    def test_delete_letter_not_found(self):
        self.mock_container.read_item.side_effect = exceptions.CosmosResourceNotFoundError(
            status_code=404,
            message="Item not found"
        )
        
        result = self.cosmos_service.delete_letter("nonexistent", "letter")
        
        self.assertFalse(result)
        self.mock_container.replace_item.assert_not_called()
    
    def test_no_container_initialized(self):
        # Test behavior when container is not initialized
        self.cosmos_service.container = None
        
        # Test save_letter
        result = self.cosmos_service.save_letter({"test": "data"})
        self.assertEqual(result, {"test": "data"})
        
        # Test get_letter
        result = self.cosmos_service.get_letter("test", "letter")
        self.assertIsNone(result)
        
        # Test get_letters_by_customer
        result = self.cosmos_service.get_letters_by_customer("test")
        self.assertEqual(result, [])
        
        # Test get_letters_by_type
        result = self.cosmos_service.get_letters_by_type("test")
        self.assertEqual(result, [])
        
        # Test get_recent_letters
        result = self.cosmos_service.get_recent_letters()
        self.assertEqual(result, [])
        
        # Test update_letter_status
        result = self.cosmos_service.update_letter_status("test", "approved")
        self.assertIsNone(result)
        
        # Test delete_letter
        result = self.cosmos_service.delete_letter("test")
        self.assertFalse(result)


class TestCosmosServiceIntegration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Set test database/container names
        cls.original_db = os.getenv("COSMOS_DATABASE_NAME")
        cls.original_container = os.getenv("COSMOS_CONTAINER_NAME")
        os.environ["COSMOS_DATABASE_NAME"] = "test_insurance_letters"
        os.environ["COSMOS_CONTAINER_NAME"] = "test_letters"
        
        cls.cosmos_service = CosmosService()
    
    @unittest.skipIf(not os.getenv("COSMOS_ENDPOINT") or not os.getenv("COSMOS_KEY"), 
                     "Cosmos DB credentials not available")
    def test_full_letter_lifecycle(self):
        letter_data = {
            "customer_name": "Test Customer",
            "policy_number": "TEST123",
            "letter_type": "test_letter", 
            "content": "This is a test letter for integration testing",
            "prompt": "Generate test letter",
            "compliance_status": "pending"
        }
        
        created_letter = self.cosmos_service.save_letter(letter_data)
        self.assertIsNotNone(created_letter)
        letter_id = created_letter["id"]
        
        retrieved_letter = self.cosmos_service.get_letter(letter_id, "letter")
        self.assertIsNotNone(retrieved_letter)
        self.assertEqual(retrieved_letter["customer_name"], "Test Customer")
        
        updated_letter = self.cosmos_service.update_letter_status(letter_id, "approved", "letter")
        self.assertEqual(updated_letter["compliance_status"], "approved")
        self.assertIn("updated_at", updated_letter)
        
        customer_letters = self.cosmos_service.get_letters_by_customer("Test Customer")
        self.assertTrue(any(l["id"] == letter_id for l in customer_letters))
        
        type_letters = self.cosmos_service.get_letters_by_type("test_letter")
        self.assertTrue(any(l["id"] == letter_id for l in type_letters))
        
        deleted = self.cosmos_service.delete_letter(letter_id, "letter")
        self.assertTrue(deleted)
        
        # After soft delete, the letter should still be retrievable but marked as deleted
        deleted_letter = self.cosmos_service.get_letter(letter_id, "letter")
        self.assertIsNotNone(deleted_letter)
        self.assertTrue(deleted_letter.get("deleted", False))
    
    @classmethod
    def tearDownClass(cls):
        # Clean up test database/container
        try:
            if cls.cosmos_service.client:
                database = cls.cosmos_service.client.get_database_client("test_insurance_letters")
                database.delete_container("test_letters")
                cls.cosmos_service.client.delete_database("test_insurance_letters")
        except:
            pass
        
        # Restore original environment variables
        if cls.original_db:
            os.environ["COSMOS_DATABASE_NAME"] = cls.original_db
        else:
            os.environ.pop("COSMOS_DATABASE_NAME", None)
            
        if cls.original_container:
            os.environ["COSMOS_CONTAINER_NAME"] = cls.original_container
        else:
            os.environ.pop("COSMOS_CONTAINER_NAME", None)


if __name__ == "__main__":
    unittest.main()