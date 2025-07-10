"""
Tests for Cosmos DB service.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError
from services.cosmos_service import CosmosService
from services.models import StoredLetter, LetterType, CustomerInfo


class TestCosmosService:
    """Tests for the CosmosService class."""
    
    @pytest.fixture
    def cosmos_service(self, mock_cosmos_client):
        """Create a CosmosService instance with mocked client."""
        client, container = mock_cosmos_client
        
        with patch('services.cosmos_service.CosmosClient', return_value=client):
            service = CosmosService()
            service.container = container
            service.database_name = "test_db"
            service.container_name = "test_container"
            return service
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, cosmos_service):
        """Test successful connection test."""
        cosmos_service.container.read = AsyncMock()
        
        result = await cosmos_service.test_connection()
        
        assert result is True
        cosmos_service.container.read.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, cosmos_service):
        """Test connection test failure."""
        cosmos_service.container.read = AsyncMock(
            side_effect=Exception("Connection failed")
        )
        
        result = await cosmos_service.test_connection()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_save_letter_success(self, cosmos_service, sample_customer_info):
        """Test successful letter saving."""
        letter_content = "Dear John, Welcome to our insurance..."
        approval_status = {
            "overall_approved": True,
            "writer_approved": True,
            "compliance_approved": True,
            "customer_service_approved": True
        }
        agent_conversations = [
            {"round": 1, "agent": "writer", "message": "Draft created"}
        ]
        
        expected_doc = {
            "id": Mock(),
            "type": "letter",
            "created_at": Mock(),
            "letter_content": letter_content
        }
        
        cosmos_service.container.create_item = AsyncMock(return_value=expected_doc)
        
        result = await cosmos_service.save_letter(
            letter_content=letter_content,
            customer_info=CustomerInfo(**sample_customer_info),
            letter_type=LetterType.WELCOME,
            user_prompt="Welcome new customer",
            approval_status=approval_status,
            agent_conversations=agent_conversations,
            total_rounds=1
        )
        
        assert result == expected_doc
        
        # Verify the document structure
        call_args = cosmos_service.container.create_item.call_args[0][0]
        assert call_args["type"] == "letter"
        assert call_args["letter_content"] == letter_content
        assert call_args["customer_info"]["name"] == "John Doe"
        assert call_args["letter_type"] == "welcome"
        assert call_args["approval_status"]["overall_approved"] is True
    
    @pytest.mark.asyncio
    async def test_save_letter_with_error(self, cosmos_service, sample_customer_info):
        """Test letter saving with Cosmos DB error."""
        cosmos_service.container.create_item = AsyncMock(
            side_effect=CosmosHttpResponseError(
                status_code=429,
                message="Request rate too high"
            )
        )
        
        with pytest.raises(CosmosHttpResponseError):
            await cosmos_service.save_letter(
                letter_content="Test content",
                customer_info=CustomerInfo(**sample_customer_info),
                letter_type=LetterType.WELCOME,
                user_prompt="Test prompt",
                approval_status={},
                agent_conversations=[],
                total_rounds=1
            )
    
    @pytest.mark.asyncio
    async def test_get_letter_success(self, cosmos_service):
        """Test successful letter retrieval."""
        letter_id = "test-letter-id"
        expected_letter = {
            "id": letter_id,
            "type": "letter",
            "letter_content": "Test letter content",
            "created_at": "2025-01-01T00:00:00Z"
        }
        
        cosmos_service.container.read_item = AsyncMock(return_value=expected_letter)
        
        result = await cosmos_service.get_letter(letter_id)
        
        assert result == expected_letter
        cosmos_service.container.read_item.assert_called_once_with(
            item=letter_id,
            partition_key="letter"
        )
    
    @pytest.mark.asyncio
    async def test_get_letter_not_found(self, cosmos_service):
        """Test letter retrieval when letter doesn't exist."""
        cosmos_service.container.read_item = AsyncMock(
            side_effect=CosmosResourceNotFoundError()
        )
        
        result = await cosmos_service.get_letter("non-existent-id")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_list_letters_success(self, cosmos_service):
        """Test listing letters with filters."""
        mock_letters = [
            {
                "id": "1",
                "letter_type": "welcome",
                "created_at": "2025-01-01T00:00:00Z",
                "customer_info": {"name": "John Doe"}
            },
            {
                "id": "2",
                "letter_type": "claim_denial",
                "created_at": "2025-01-02T00:00:00Z",
                "customer_info": {"name": "Jane Smith"}
            }
        ]
        
        cosmos_service.container.query_items = Mock(return_value=mock_letters)
        
        # Test with no filters
        result = await cosmos_service.list_letters()
        assert len(result) == 2
        
        # Test with letter type filter
        result = await cosmos_service.list_letters(letter_type="welcome")
        query_call = cosmos_service.container.query_items.call_args[1]
        assert "WHERE c.type = @type" in query_call["query"]
        assert "AND c.letter_type = @letter_type" in query_call["query"]
    
    @pytest.mark.asyncio
    async def test_list_letters_with_date_range(self, cosmos_service):
        """Test listing letters with date range filter."""
        cosmos_service.container.query_items = Mock(return_value=[])
        
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31)
        
        await cosmos_service.list_letters(
            start_date=start_date,
            end_date=end_date
        )
        
        query_call = cosmos_service.container.query_items.call_args[1]
        assert "AND c.created_at >= @start_date" in query_call["query"]
        assert "AND c.created_at <= @end_date" in query_call["query"]
        assert query_call["parameters"][2]["value"] == start_date.isoformat() + "Z"
        assert query_call["parameters"][3]["value"] == end_date.isoformat() + "Z"
    
    @pytest.mark.asyncio
    async def test_delete_letter_success(self, cosmos_service):
        """Test successful letter deletion."""
        letter_id = "test-letter-id"
        cosmos_service.container.delete_item = AsyncMock()
        
        result = await cosmos_service.delete_letter(letter_id)
        
        assert result is True
        cosmos_service.container.delete_item.assert_called_once_with(
            item=letter_id,
            partition_key="letter"
        )
    
    @pytest.mark.asyncio
    async def test_delete_letter_not_found(self, cosmos_service):
        """Test deleting non-existent letter."""
        cosmos_service.container.delete_item = AsyncMock(
            side_effect=CosmosResourceNotFoundError()
        )
        
        result = await cosmos_service.delete_letter("non-existent-id")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_update_letter_success(self, cosmos_service):
        """Test successful letter update."""
        letter_id = "test-letter-id"
        updates = {
            "letter_content": "Updated content",
            "modified_at": datetime.utcnow().isoformat() + "Z"
        }
        
        existing_letter = {
            "id": letter_id,
            "type": "letter",
            "letter_content": "Original content",
            "created_at": "2025-01-01T00:00:00Z"
        }
        
        cosmos_service.container.read_item = AsyncMock(return_value=existing_letter)
        cosmos_service.container.replace_item = AsyncMock(
            return_value={**existing_letter, **updates}
        )
        
        result = await cosmos_service.update_letter(letter_id, updates)
        
        assert result is not None
        assert result["letter_content"] == "Updated content"
        assert "modified_at" in result
    
    @pytest.mark.asyncio
    async def test_batch_operations(self, cosmos_service):
        """Test batch operations for multiple letters."""
        letter_ids = ["id1", "id2", "id3"]
        mock_letters = [
            {"id": id, "type": "letter", "content": f"Letter {id}"}
            for id in letter_ids
        ]
        
        # Mock batch read
        cosmos_service.container.read_item = AsyncMock(
            side_effect=mock_letters
        )
        
        # Test batch retrieval
        results = []
        for letter_id in letter_ids:
            letter = await cosmos_service.get_letter(letter_id)
            results.append(letter)
        
        assert len(results) == 3
        assert all(letter is not None for letter in results)
    
    def test_cosmos_service_initialization_without_credentials(self):
        """Test CosmosService initialization without credentials."""
        with patch.dict('os.environ', {}, clear=True):
            service = CosmosService()
            assert service.container is None
            assert service.is_cosmos_configured is False
    
    def test_stored_letter_model(self):
        """Test StoredLetter model creation and validation."""
        letter = StoredLetter(
            id="test-id",
            type="letter",
            letter_content="Test content",
            customer_info=CustomerInfo(
                name="John Doe",
                policy_number="POL-123",
                address="123 Main St",
                phone="555-1234",
                email="john@example.com"
            ),
            letter_type=LetterType.WELCOME,
            user_prompt="Welcome message",
            approval_status={
                "overall_approved": True,
                "writer_approved": True,
                "compliance_approved": True,
                "customer_service_approved": True
            },
            agent_conversations=[],
            total_rounds=1,
            created_at=datetime.utcnow().isoformat() + "Z"
        )
        
        assert letter.id == "test-id"
        assert letter.type == "letter"
        assert letter.letter_type == LetterType.WELCOME