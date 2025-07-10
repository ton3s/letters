"""
Tests for data models.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from services.models import (
    CustomerInfo, LetterType, LetterRequest, 
    SuggestLetterTypeRequest, ValidateLetterRequest,
    StoredLetter, ApprovalStatus, AgentConversation
)


class TestCustomerInfo:
    """Tests for CustomerInfo model."""
    
    def test_customer_info_valid(self):
        """Test creating valid CustomerInfo."""
        info = CustomerInfo(
            name="John Doe",
            policy_number="POL-123456",
            address="123 Main St",
            phone="555-1234",
            email="john@example.com",
            agent_name="Jane Smith"
        )
        
        assert info.name == "John Doe"
        assert info.policy_number == "POL-123456"
        assert info.agent_name == "Jane Smith"
    
    def test_customer_info_optional_fields(self):
        """Test CustomerInfo with optional fields."""
        info = CustomerInfo(
            name="John Doe",
            policy_number="POL-123456"
        )
        
        assert info.name == "John Doe"
        assert info.address is None
        assert info.phone is None
        assert info.email is None
        assert info.agent_name is None
    
    def test_customer_info_missing_required(self):
        """Test CustomerInfo with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            CustomerInfo(name="John Doe")  # Missing policy_number
        
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("policy_number",) for e in errors)


class TestLetterType:
    """Tests for LetterType enum."""
    
    def test_letter_type_values(self):
        """Test all letter type values."""
        expected_types = [
            "claim_denial", "claim_approval", "policy_renewal",
            "coverage_change", "premium_increase", "cancellation",
            "welcome", "general"
        ]
        
        actual_types = [lt.value for lt in LetterType]
        assert set(actual_types) == set(expected_types)
    
    def test_letter_type_from_string(self):
        """Test creating LetterType from string."""
        assert LetterType("welcome") == LetterType.WELCOME
        assert LetterType("claim_denial") == LetterType.CLAIM_DENIAL
    
    def test_invalid_letter_type(self):
        """Test invalid letter type."""
        with pytest.raises(ValueError):
            LetterType("invalid_type")


class TestLetterRequest:
    """Tests for LetterRequest model."""
    
    def test_letter_request_valid(self, sample_customer_info):
        """Test creating valid LetterRequest."""
        request = LetterRequest(
            customer_info=sample_customer_info,
            letter_type="welcome",
            user_prompt="Welcome new customer"
        )
        
        assert request.customer_info.name == "John Doe"
        assert request.letter_type == "welcome"
        assert request.user_prompt == "Welcome new customer"
    
    def test_letter_request_type_validation(self, sample_customer_info):
        """Test LetterRequest with invalid letter type."""
        with pytest.raises(ValidationError):
            LetterRequest(
                customer_info=sample_customer_info,
                letter_type="invalid_type",
                user_prompt="Test"
            )


class TestSuggestLetterTypeRequest:
    """Tests for SuggestLetterTypeRequest model."""
    
    def test_suggest_request_valid(self):
        """Test creating valid suggest request."""
        request = SuggestLetterTypeRequest(
            prompt="Customer wants to cancel policy"
        )
        
        assert request.prompt == "Customer wants to cancel policy"
    
    def test_suggest_request_empty_prompt(self):
        """Test suggest request with empty prompt."""
        with pytest.raises(ValidationError):
            SuggestLetterTypeRequest(prompt="")


class TestValidateLetterRequest:
    """Tests for ValidateLetterRequest model."""
    
    def test_validate_request_valid(self):
        """Test creating valid validate request."""
        request = ValidateLetterRequest(
            letter_content="Dear Customer, Your claim is approved...",
            letter_type="claim_approval"
        )
        
        assert "Your claim is approved" in request.letter_content
        assert request.letter_type == "claim_approval"
    
    def test_validate_request_optional_type(self):
        """Test validate request without letter type."""
        request = ValidateLetterRequest(
            letter_content="Test content"
        )
        
        assert request.letter_content == "Test content"
        assert request.letter_type is None


class TestApprovalStatus:
    """Tests for ApprovalStatus model."""
    
    def test_approval_status_all_approved(self):
        """Test ApprovalStatus with all approvals."""
        status = ApprovalStatus(
            writer_approved=True,
            compliance_approved=True,
            customer_service_approved=True,
            overall_approved=True,
            status="fully_approved"
        )
        
        assert status.overall_approved is True
        assert status.status == "fully_approved"
    
    def test_approval_status_partial(self):
        """Test ApprovalStatus with partial approvals."""
        status = ApprovalStatus(
            writer_approved=True,
            compliance_approved=False,
            customer_service_approved=True,
            overall_approved=False,
            status="compliance_rejected"
        )
        
        assert status.overall_approved is False
        assert status.compliance_approved is False
    
    def test_approval_status_defaults(self):
        """Test ApprovalStatus default values."""
        status = ApprovalStatus()
        
        assert status.writer_approved is False
        assert status.compliance_approved is False
        assert status.customer_service_approved is False
        assert status.overall_approved is False
        assert status.status == "pending"


class TestAgentConversation:
    """Tests for AgentConversation model."""
    
    def test_agent_conversation_valid(self):
        """Test creating valid AgentConversation."""
        conv = AgentConversation(
            round=1,
            agent="LetterWriter",
            role="writer",
            message="Initial draft created",
            timestamp="2025-01-01T00:00:00Z"
        )
        
        assert conv.round == 1
        assert conv.agent == "LetterWriter"
        assert conv.role == "writer"
    
    def test_agent_conversation_optional_fields(self):
        """Test AgentConversation with minimal fields."""
        conv = AgentConversation(
            round=2,
            agent="ComplianceReviewer",
            message="Letter approved"
        )
        
        assert conv.round == 2
        assert conv.role is None
        assert conv.timestamp is None


class TestStoredLetter:
    """Tests for StoredLetter model."""
    
    def test_stored_letter_complete(self, sample_customer_info):
        """Test creating complete StoredLetter."""
        letter = StoredLetter(
            id="test-123",
            type="letter",
            letter_content="Dear John Doe, Welcome...",
            customer_info=CustomerInfo(**sample_customer_info),
            letter_type=LetterType.WELCOME,
            user_prompt="Welcome new customer",
            approval_status=ApprovalStatus(
                writer_approved=True,
                compliance_approved=True,
                customer_service_approved=True,
                overall_approved=True,
                status="fully_approved"
            ),
            agent_conversations=[
                AgentConversation(
                    round=1,
                    agent="LetterWriter",
                    message="Draft created"
                )
            ],
            total_rounds=1,
            created_at=datetime.utcnow().isoformat() + "Z",
            modified_at=datetime.utcnow().isoformat() + "Z"
        )
        
        assert letter.id == "test-123"
        assert letter.type == "letter"
        assert letter.letter_type == LetterType.WELCOME
        assert letter.total_rounds == 1
        assert len(letter.agent_conversations) == 1
    
    def test_stored_letter_minimal(self, sample_customer_info):
        """Test creating StoredLetter with minimal fields."""
        letter = StoredLetter(
            id="test-123",
            type="letter",
            letter_content="Test content",
            customer_info=CustomerInfo(**sample_customer_info),
            letter_type=LetterType.GENERAL,
            user_prompt="Test",
            approval_status=ApprovalStatus(),
            agent_conversations=[],
            total_rounds=0,
            created_at=datetime.utcnow().isoformat() + "Z"
        )
        
        assert letter.id == "test-123"
        assert letter.modified_at is None
        assert len(letter.agent_conversations) == 0
    
    def test_stored_letter_type_validation(self, sample_customer_info):
        """Test StoredLetter with invalid type."""
        with pytest.raises(ValidationError):
            StoredLetter(
                id="test-123",
                type="invalid",  # Should be "letter"
                letter_content="Test",
                customer_info=CustomerInfo(**sample_customer_info),
                letter_type=LetterType.GENERAL,
                user_prompt="Test",
                approval_status=ApprovalStatus(),
                agent_conversations=[],
                total_rounds=0,
                created_at=datetime.utcnow().isoformat() + "Z"
            )


class TestModelSerialization:
    """Tests for model serialization/deserialization."""
    
    def test_customer_info_json_serialization(self):
        """Test CustomerInfo JSON serialization."""
        info = CustomerInfo(
            name="John Doe",
            policy_number="POL-123456",
            email="john@example.com"
        )
        
        json_data = info.model_dump_json()
        assert '"name":"John Doe"' in json_data
        assert '"policy_number":"POL-123456"' in json_data
        
        # Test deserialization
        info2 = CustomerInfo.model_validate_json(json_data)
        assert info2.name == info.name
        assert info2.policy_number == info.policy_number
    
    def test_letter_request_dict_serialization(self, sample_customer_info):
        """Test LetterRequest dict serialization."""
        request = LetterRequest(
            customer_info=sample_customer_info,
            letter_type="welcome",
            user_prompt="Welcome message"
        )
        
        dict_data = request.model_dump()
        assert dict_data["letter_type"] == "welcome"
        assert dict_data["customer_info"]["name"] == "John Doe"
        
        # Test creating from dict
        request2 = LetterRequest.model_validate(dict_data)
        assert request2.letter_type == request.letter_type