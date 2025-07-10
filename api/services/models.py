from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class LetterType(Enum):
    """Supported insurance letter types."""
    CLAIM_DENIAL = "claim_denial"
    CLAIM_APPROVAL = "claim_approval"
    POLICY_RENEWAL = "policy_renewal"
    COVERAGE_CHANGE = "coverage_change"
    PREMIUM_INCREASE = "premium_increase"
    CANCELLATION = "cancellation"
    WELCOME = "welcome"
    GENERAL = "general"


@dataclass
class CustomerInfo:
    """Customer information for letter generation."""
    name: str
    policy_number: str
    address: str = ""
    phone: str = ""
    email: str = ""
    agent_name: str = ""
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "policy_number": self.policy_number,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "agent_name": self.agent_name
        }


@dataclass
class LetterRequest:
    """Request model for letter generation."""
    customer_info: CustomerInfo
    letter_type: str
    user_prompt: str
    additional_context: str = ""
    
    def validate(self) -> bool:
        """Validate the letter request."""
        if not self.customer_info.name or not self.customer_info.policy_number:
            return False
        
        try:
            LetterType(self.letter_type)
        except ValueError:
            return False
        
        return bool(self.user_prompt)


@dataclass
class ApprovalStatus:
    """Track approval status from all agents."""
    writer_approved: bool = False
    compliance_approved: bool = False
    customer_service_approved: bool = False
    overall_approved: bool = False
    status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "writer_approved": self.writer_approved,
            "compliance_approved": self.compliance_approved,
            "customer_service_approved": self.customer_service_approved,
            "overall_approved": self.overall_approved,
            "status": self.status
        }


@dataclass
class LetterGenerationResult:
    """Result from letter generation process."""
    letter_content: str
    approval_status: ApprovalStatus
    total_rounds: int
    orchestration_type: str
    agents_used: list[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    letter_type: str = ""
    customer_name: str = ""
    quality_assurance: str = ""
    document_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "letter_content": self.letter_content,
            "approval_status": self.approval_status.to_dict(),
            "total_rounds": self.total_rounds,
            "orchestration_type": self.orchestration_type,
            "agents_used": self.agents_used,
            "timestamp": self.timestamp,
            "letter_type": self.letter_type,
            "customer_name": self.customer_name,
            "quality_assurance": self.quality_assurance,
            "document_id": self.document_id
        }


@dataclass
class ValidationResult:
    """Result from letter validation."""
    is_valid: bool
    compliance_issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    compliance_score: float = 0.0
    validated_by: str = "ComplianceReviewer"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "is_valid": self.is_valid,
            "compliance_issues": self.compliance_issues,
            "suggestions": self.suggestions,
            "compliance_score": self.compliance_score,
            "validated_by": self.validated_by,
            "timestamp": self.timestamp
        }


@dataclass
class LetterTypeSuggestion:
    """Suggestion for letter type based on user input."""
    suggested_type: LetterType
    confidence: float
    reasoning: str
    alternative_types: list[LetterType] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "suggested_type": self.suggested_type.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "alternative_types": [t.value for t in self.alternative_types]
        }