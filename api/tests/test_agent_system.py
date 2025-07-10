"""
Tests for the multi-agent insurance letter system.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from services.agent_system import InsuranceAgentSystem
from services.models import CustomerInfo, LetterType


class TestInsuranceAgentSystem:
    """Tests for the InsuranceAgentSystem class."""
    
    @pytest.fixture
    def mock_kernel(self):
        """Create a mock semantic kernel."""
        kernel = Mock()
        kernel.add_service = Mock()
        kernel.add_function = Mock()
        kernel.add_plugin = Mock()
        return kernel
    
    @pytest.fixture
    def agent_system(self, mock_kernel):
        """Create an agent system with mocked kernel."""
        with patch('semantic_kernel.Kernel', return_value=mock_kernel):
            with patch('services.agent_system.AzureChatCompletion'):
                system = InsuranceAgentSystem()
                system.kernel = mock_kernel
                return system
    
    @pytest.mark.asyncio
    async def test_generate_letter_success(self, agent_system, sample_customer_info):
        """Test successful letter generation with all agents approving."""
        # Mock agent responses
        writer_response = Mock(value="""Dear John Doe,

Welcome to our insurance family! We're delighted to have you as a new policyholder.

Your policy POL-123456 is now active and provides comprehensive coverage.

Sincerely,
Jane Smith
[WRITER_APPROVED]""")
        
        compliance_response = Mock(value="Letter meets all compliance requirements. [COMPLIANCE_APPROVED]")
        customer_response = Mock(value="Tone is friendly and professional. [CUSTOMER_SERVICE_APPROVED]")
        
        # Set up mock function calls
        agent_system.kernel.invoke = AsyncMock(side_effect=[
            writer_response,      # Round 1: Initial draft
            compliance_response,  # Round 1: Compliance review
            customer_response,    # Round 1: Customer service review
        ])
        
        result = await agent_system.generate_letter(
            CustomerInfo(**sample_customer_info),
            LetterType.WELCOME,
            "Welcome new customer to auto insurance"
        )
        
        assert result["letter_content"] is not None
        assert "Dear John Doe" in result["letter_content"]
        assert result["approval_status"]["overall_approved"] is True
        assert result["approval_status"]["writer_approved"] is True
        assert result["approval_status"]["compliance_approved"] is True
        assert result["approval_status"]["customer_service_approved"] is True
        assert result["total_rounds"] == 1
    
    @pytest.mark.asyncio
    async def test_generate_letter_with_revisions(self, agent_system, sample_customer_info):
        """Test letter generation requiring revisions."""
        # Mock responses for multiple rounds
        writer_draft1 = Mock(value="Initial draft [WRITER_APPROVED]")
        compliance_reject = Mock(value="Missing required disclosures [COMPLIANCE_REJECTED]")
        customer_reject = Mock(value="Tone too formal [CUSTOMER_SERVICE_REJECTED]")
        
        writer_draft2 = Mock(value="Revised draft with disclosures [WRITER_APPROVED]")
        compliance_approve = Mock(value="All requirements met [COMPLIANCE_APPROVED]")
        customer_approve = Mock(value="Much better tone [CUSTOMER_SERVICE_APPROVED]")
        
        agent_system.kernel.invoke = AsyncMock(side_effect=[
            writer_draft1,       # Round 1: Initial draft
            compliance_reject,   # Round 1: Compliance review
            customer_reject,     # Round 1: Customer service review
            writer_draft2,       # Round 2: Revised draft
            compliance_approve,  # Round 2: Compliance review
            customer_approve,    # Round 2: Customer service review
        ])
        
        result = await agent_system.generate_letter(
            CustomerInfo(**sample_customer_info),
            LetterType.CLAIM_DENIAL,
            "Deny claim due to policy exclusion"
        )
        
        assert result["approval_status"]["overall_approved"] is True
        assert result["total_rounds"] == 2
        assert len(result["agent_conversations"]) == 6  # 3 agents × 2 rounds
    
    @pytest.mark.asyncio
    async def test_generate_letter_max_rounds_exceeded(self, agent_system, sample_customer_info):
        """Test letter generation when max rounds are exceeded."""
        # Mock responses that never approve
        writer_response = Mock(value="Draft [WRITER_APPROVED]")
        compliance_reject = Mock(value="Issues found [COMPLIANCE_REJECTED]")
        customer_reject = Mock(value="Tone issues [CUSTOMER_SERVICE_REJECTED]")
        
        # Repeat rejections for all rounds
        responses = []
        for _ in range(5):  # MAX_ROUNDS = 5
            responses.extend([writer_response, compliance_reject, customer_reject])
        
        agent_system.kernel.invoke = AsyncMock(side_effect=responses)
        
        result = await agent_system.generate_letter(
            CustomerInfo(**sample_customer_info),
            LetterType.CLAIM_DENIAL,
            "Deny claim"
        )
        
        assert result["approval_status"]["overall_approved"] is False
        assert result["approval_status"]["status"] == "max_rounds_exceeded"
        assert result["total_rounds"] == 5
    
    @pytest.mark.asyncio
    async def test_suggest_letter_type(self, agent_system):
        """Test letter type suggestion."""
        mock_response = Mock(value="""Based on the prompt, this is about a customer wanting to cancel their policy.

Suggested type: cancellation
Confidence: 0.95
Reasoning: The customer explicitly wants to cancel their policy, which matches the cancellation letter type.""")
        
        agent_system.kernel.invoke = AsyncMock(return_value=mock_response)
        
        result = await agent_system.suggest_letter_type("Customer wants to cancel policy")
        
        assert result["suggested_type"] == "cancellation"
        assert result["confidence"] == 0.95
        assert "explicitly wants to cancel" in result["reasoning"]
    
    @pytest.mark.asyncio
    async def test_suggest_letter_type_parsing_error(self, agent_system):
        """Test letter type suggestion with parsing error."""
        mock_response = Mock(value="Invalid response format")
        
        agent_system.kernel.invoke = AsyncMock(return_value=mock_response)
        
        result = await agent_system.suggest_letter_type("Test prompt")
        
        assert result["suggested_type"] == "general"
        assert result["confidence"] == 0.5
        assert "Could not parse" in result["reasoning"]
    
    @pytest.mark.asyncio
    async def test_validate_letter(self, agent_system):
        """Test letter validation."""
        mock_response = Mock(value="""Letter validation complete.

Compliance Score: 0.92
Tone Score: 0.88
Overall Valid: Yes

Suggestions:
- Consider adding policy effective date
- Ensure contact information is prominently displayed""")
        
        agent_system.kernel.invoke = AsyncMock(return_value=mock_response)
        
        result = await agent_system.validate_letter(
            "Dear Customer, Your policy is active...",
            LetterType.WELCOME
        )
        
        assert result["is_valid"] is True
        assert result["compliance_score"] == 0.92
        assert result["tone_score"] == 0.88
        assert len(result["suggestions"]) == 2
    
    @pytest.mark.asyncio
    async def test_validate_letter_invalid(self, agent_system):
        """Test validation of invalid letter."""
        mock_response = Mock(value="""Letter validation complete.

Compliance Score: 0.45
Tone Score: 0.62
Overall Valid: No

Suggestions:
- Missing required regulatory disclosures
- Tone is too aggressive
- Policy number not included""")
        
        agent_system.kernel.invoke = AsyncMock(return_value=mock_response)
        
        result = await agent_system.validate_letter(
            "Your claim is denied. End of story.",
            LetterType.CLAIM_DENIAL
        )
        
        assert result["is_valid"] is False
        assert result["compliance_score"] == 0.45
        assert result["tone_score"] == 0.62
        assert len(result["suggestions"]) == 3
    
    @pytest.mark.asyncio
    async def test_extract_approval_status(self, agent_system):
        """Test approval status extraction from agent responses."""
        test_cases = [
            ("Letter looks good [WRITER_APPROVED]", "writer", True),
            ("Issues found [COMPLIANCE_REJECTED]", "compliance", False),
            ("[CUSTOMER_SERVICE_APPROVED] Great tone!", "customer_service", True),
            ("No explicit approval tag", "writer", False),
        ]
        
        for text, agent_type, expected in test_cases:
            status = agent_system._extract_approval_status(text, agent_type)
            assert status == expected
    
    def test_letter_type_validation(self, agent_system):
        """Test that all letter types are properly configured."""
        for letter_type in LetterType:
            assert letter_type.value in [
                "claim_denial", "claim_approval", "policy_renewal",
                "coverage_change", "premium_increase", "cancellation",
                "welcome", "general"
            ]
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self, agent_system, sample_customer_info):
        """Test error handling when agent fails."""
        agent_system.kernel.invoke = AsyncMock(
            side_effect=Exception("AI service unavailable")
        )
        
        with pytest.raises(Exception) as exc_info:
            await agent_system.generate_letter(
                CustomerInfo(**sample_customer_info),
                LetterType.WELCOME,
                "Test prompt"
            )
        
        assert "AI service unavailable" in str(exc_info.value)