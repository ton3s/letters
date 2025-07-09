import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from semantic_kernel import Kernel
from semantic_kernel.agents import (
    ChatCompletionAgent,
    AgentGroupChat
)
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent, AuthorRole
from semantic_kernel.agents.strategies.termination.termination_strategy import TerminationStrategy
from semantic_kernel.agents.strategies.selection.sequential_selection_strategy import SequentialSelectionStrategy

from .models import (
    LetterType, 
    ApprovalStatus, 
    LetterGenerationResult,
    ValidationResult,
    LetterTypeSuggestion
)

# Configure logging
logger = logging.getLogger(__name__)


class ApprovalTerminationStrategy(TerminationStrategy):
    """Custom termination strategy based on agent approvals."""
    
    max_rounds: int = 5
    current_round: int = 0
    agents_per_round: int = 3  # Number of agents in the group
    
    async def should_agent_terminate(self, agent, history: List[ChatMessageContent]) -> bool:
        """Check if all agents have approved or max rounds reached."""
        # Calculate current round based on message count
        if len(history) > 0:
            self.current_round = (len(history) - 1) // self.agents_per_round + 1
        
        # Safety: Terminate if max rounds reached
        if self.current_round >= self.max_rounds:
            logger.info(f"Terminating: Max rounds ({self.max_rounds}) reached")
            return True
        
        # Need at least one complete round to check approvals
        if len(history) < self.agents_per_round:
            return False
        
        # Get the last round of messages
        last_round_start = ((self.current_round - 1) * self.agents_per_round)
        recent_messages = history[last_round_start:last_round_start + self.agents_per_round]
        
        # Check for approval keywords from all agents
        approvals = {
            "writer": False,
            "compliance": False,
            "customer_service": False
        }
        
        for message in recent_messages:
            if hasattr(message, 'name') and message.name and message.content:
                content = message.content.upper()
                if "LetterWriter" in message.name and "WRITER_APPROVED" in content:
                    approvals["writer"] = True
                elif "ComplianceReviewer" in message.name and "COMPLIANCE_APPROVED" in content:
                    approvals["compliance"] = True
                elif "CustomerServiceReviewer" in message.name and "CUSTOMER_SERVICE_APPROVED" in content:
                    approvals["customer_service"] = True
        
        # Terminate only if all agents approve
        all_approved = all(approvals.values())
        if all_approved:
            logger.info("Terminating: All agents approved")
        
        return all_approved


def get_kernel_with_azure_openai() -> Kernel:
    """Create and configure kernel with Azure OpenAI."""
    kernel = Kernel()
    
    # Configure Azure OpenAI service
    azure_chat_completion = AzureChatCompletion(
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        service_id="azure_openai_chat"
    )
    
    kernel.add_service(azure_chat_completion)
    return kernel


def get_insurance_agents(kernel: Kernel) -> List[ChatCompletionAgent]:
    """Create the three specialized insurance agents."""
    
    # Letter Drafting Agent
    letter_writer = ChatCompletionAgent(
        kernel=kernel,
        name="LetterWriter",
        instructions=(
            "You are a professional insurance letter drafting specialist with 15+ years of experience. "
            "Create and refine clear, professional, and compliant insurance letters. "
            "Guidelines: Use professional but warm tone, include required legal disclaimers, "
            "personalize with customer information, follow industry best practices, ensure clarity and avoid jargon. "
            "When refining, incorporate feedback from compliance and customer service reviews. "
            "At the end of your response, state: 'WRITER_APPROVED' if you believe the letter is complete and ready, "
            "or 'WRITER_NEEDS_IMPROVEMENT' if further refinement is needed."
        ),
    )
    
    # Compliance Reviewer Agent
    compliance_reviewer = ChatCompletionAgent(
        kernel=kernel,
        name="ComplianceReviewer",
        instructions=(
            "You are an insurance compliance specialist ensuring all letters meet regulatory requirements. "
            "Review letters for: legal compliance, required disclaimers, accuracy of information, "
            "professional tone, missing required elements, state-specific regulations. "
            "Provide specific feedback for improvements needed. "
            "At the end of your response, state: 'COMPLIANCE_APPROVED' if the letter meets all regulatory requirements, "
            "or 'COMPLIANCE_REJECTED' with specific issues that must be addressed."
        ),
    )
    
    # Customer Service Agent
    customer_service_reviewer = ChatCompletionAgent(
        kernel=kernel,
        name="CustomerServiceReviewer",
        instructions=(
            "You are a customer service specialist ensuring letters are customer-friendly and effective. "
            "Review for: clear communication, empathetic tone, easy to understand language, "
            "appropriate level of detail, customer satisfaction potential, emotional impact. "
            "Suggest improvements to enhance customer experience and reduce potential complaints. "
            "At the end of your response, state: 'CUSTOMER_SERVICE_APPROVED' if the letter provides excellent customer experience, "
            "or 'CUSTOMER_SERVICE_REJECTED' with specific improvements needed."
        ),
    )
    
    return [letter_writer, compliance_reviewer, customer_service_reviewer]


def analyze_final_approvals(history: List[ChatMessageContent]) -> ApprovalStatus:
    """Analyze the final approval status from all agents."""
    if not history:
        return ApprovalStatus(status="failed")
    
    # Get last messages from each agent type
    approvals = ApprovalStatus()
    
    # Look through all messages to find the latest from each agent
    for message in reversed(history):
        if hasattr(message, 'name') and message.name and message.content:
            content = message.content.upper()
            
            if "LetterWriter" in message.name and not approvals.writer_approved:
                approvals.writer_approved = "WRITER_APPROVED" in content
            elif "ComplianceReviewer" in message.name and not approvals.compliance_approved:
                approvals.compliance_approved = "COMPLIANCE_APPROVED" in content
            elif "CustomerServiceReviewer" in message.name and not approvals.customer_service_approved:
                approvals.customer_service_approved = "CUSTOMER_SERVICE_APPROVED" in content
    
    approvals.overall_approved = all([
        approvals.writer_approved,
        approvals.compliance_approved,
        approvals.customer_service_approved
    ])
    
    approvals.status = "fully_approved" if approvals.overall_approved else "needs_improvement"
    
    return approvals


def extract_final_letter(history: List[ChatMessageContent]) -> str:
    """Extract the final letter content from the last LetterWriter response."""
    # Find the last message from LetterWriter
    for message in reversed(history):
        if hasattr(message, 'name') and message.name and "LetterWriter" in message.name and message.content:
            # Extract letter content (remove approval keywords)
            content = message.content
            content = content.replace("WRITER_APPROVED", "").replace("WRITER_NEEDS_IMPROVEMENT", "")
            return content.strip()
    
    return "No final letter found in conversation"


async def generate_letter_with_approval_workflow(
    customer_info: Dict[str, str],
    letter_type: str,
    user_prompt: str,
    include_conversation: bool = False
) -> Dict[str, Any]:
    """Generate insurance letter using iterative approval workflow.
    
    Args:
        customer_info: Customer information dict
        letter_type: Type of letter to generate
        user_prompt: User's requirements for the letter
        include_conversation: If True, includes the full agent conversation in the response
    """
    kernel = get_kernel_with_azure_openai()
    agents = get_insurance_agents(kernel)
    
    # Create termination strategy
    termination_strategy = ApprovalTerminationStrategy()
    
    # Create the agent group chat
    chat = AgentGroupChat(
        agents=agents,
        selection_strategy=SequentialSelectionStrategy(),
        termination_strategy=termination_strategy
    )
    
    # Create detailed task for iterative improvement
    task = f"""
    Create a professional {letter_type} insurance letter that meets all compliance and customer service standards:
    
    Customer Information:
    - Name: {customer_info.get('name')}
    - Policy Number: {customer_info.get('policy_number')}
    - Address: {customer_info.get('address', 'Not provided')}
    - Phone: {customer_info.get('phone', 'Not provided')}
    - Email: {customer_info.get('email', 'Not provided')}
    - Agent Name: {customer_info.get('agent_name', 'Not provided')}
    
    Letter Requirements: {user_prompt}
    
    PROCESS:
    1. LetterWriter: Create/refine the complete letter content
    2. ComplianceReviewer: Review for regulatory compliance and legal requirements
    3. CustomerServiceReviewer: Review for customer experience and clarity
    
    APPROVAL REQUIREMENTS:
    - LetterWriter must end with: "WRITER_APPROVED" (ready) or "WRITER_NEEDS_IMPROVEMENT" (continue)
    - ComplianceReviewer must end with: "COMPLIANCE_APPROVED" (compliant) or "COMPLIANCE_REJECTED" (fix issues)
    - CustomerServiceReviewer must end with: "CUSTOMER_SERVICE_APPROVED" (excellent) or "CUSTOMER_SERVICE_REJECTED" (improve)
    
    Continue refining until ALL agents approve or 5 rounds maximum.
    """
    
    # Add initial message to start the conversation
    await chat.add_chat_message(
        ChatMessageContent(
            role=AuthorRole.USER,
            content=task
        )
    )
    
    # Run the group chat and collect messages
    history = []
    conversation_log = []  # Store formatted conversation for display
    
    async for message in chat.invoke():
        if hasattr(message, 'content'):
            author = getattr(message, 'name', 'Unknown')
            content = str(message.content)
            logger.info(f"[Round {termination_strategy.current_round}] {author}: {content[:100]}...")
            history.append(message)
            
            # Format conversation entry
            conversation_entry = {
                "round": termination_strategy.current_round,
                "agent": author,
                "message": content,
                "timestamp": datetime.now().isoformat()
            }
            conversation_log.append(conversation_entry)
    
    # Get final results from chat history if empty
    if not history:
        async for msg in chat.get_chat_messages():
            history.append(msg)
            if hasattr(msg, 'content') and hasattr(msg, 'name'):
                conversation_entry = {
                    "round": termination_strategy.current_round,
                    "agent": getattr(msg, 'name', 'Unknown'),
                    "message": str(msg.content),
                    "timestamp": datetime.now().isoformat()
                }
                conversation_log.append(conversation_entry)
    
    # Analyze final approval status
    approval_status = analyze_final_approvals(history)
    
    # Extract final letter
    final_letter = extract_final_letter(history)
    
    # Create result
    result = LetterGenerationResult(
        letter_content=final_letter,
        approval_status=approval_status,
        total_rounds=termination_strategy.current_round,
        orchestration_type="approval_based_iterative",
        agents_used=["LetterWriter", "ComplianceReviewer", "CustomerServiceReviewer"],
        letter_type=letter_type,
        customer_name=customer_info.get('name', ''),
        quality_assurance="Multi-round approval process completed"
    )
    
    result_dict = result.to_dict()
    
    # Add conversation if requested
    if include_conversation:
        result_dict["agent_conversation"] = conversation_log
    
    return result_dict


async def suggest_letter_type(user_prompt: str) -> Dict[str, Any]:
    """Suggest appropriate letter type based on user description."""
    kernel = get_kernel_with_azure_openai()
    
    # Create a specialized agent for letter type suggestions
    suggestion_agent = ChatCompletionAgent(
        kernel=kernel,
        name="LetterTypeSuggestionAgent",
        instructions=(
            f"You are an insurance letter classification expert. Based on the user's description, "
            f"suggest the most appropriate letter type from these options: "
            f"{', '.join([lt.value for lt in LetterType])}. "
            f"Provide your suggestion with confidence level (0-1) and reasoning. "
            f"Also suggest 1-2 alternative types if applicable."
        ),
    )
    
    # Create the task
    task = f"""
    Based on this description, what type of insurance letter is most appropriate?
    
    Description: {user_prompt}
    
    Available letter types:
    - claim_denial: For denying insurance claims
    - claim_approval: For approving insurance claims
    - policy_renewal: For policy renewal notifications
    - coverage_change: For changes in coverage
    - premium_increase: For premium rate increases
    - cancellation: For policy cancellations
    - welcome: For welcoming new customers
    - general: For general correspondence
    
    Provide:
    1. The most appropriate letter type
    2. Confidence level (0-1)
    3. Brief reasoning
    4. Any alternative types that might also work
    """
    
    # Get suggestion
    response_content = ""
    async for response_item in suggestion_agent.invoke(task):
        # The response is the string representation of response_item
        response_content = str(response_item)
        break
    
    # Parse the response to extract structured data
    # This is a simplified parser - in production, you'd want more robust parsing
    suggested_type = LetterType.GENERAL  # Default
    confidence = 0.8
    reasoning = response_content if response_content else "Unable to determine letter type"
    alternatives = []
    
    # Try to extract the suggested type from the response
    content_lower = response_content.lower() if response_content else ""
    for letter_type in LetterType:
        if letter_type.value in content_lower:
            suggested_type = letter_type
            break
    
    suggestion = LetterTypeSuggestion(
        suggested_type=suggested_type,
        confidence=confidence,
        reasoning=reasoning,
        alternative_types=alternatives
    )
    
    return suggestion.to_dict()


async def validate_letter_content(letter_content: str, letter_type: str) -> Dict[str, Any]:
    """Validate an existing letter for compliance."""
    kernel = get_kernel_with_azure_openai()
    
    # Use the compliance reviewer agent
    compliance_agent = ChatCompletionAgent(
        kernel=kernel,
        name="ComplianceValidator",
        instructions=(
            "You are an insurance compliance specialist. Validate the provided letter for: "
            "1) Regulatory compliance, 2) Required legal disclaimers, 3) Accuracy and completeness, "
            "4) Professional tone, 5) Industry standards. "
            "Provide specific compliance issues found and suggestions for improvement. "
            "Rate compliance on a scale of 0-1."
        ),
    )
    
    # Create validation task
    task = f"""
    Validate this {letter_type} insurance letter for compliance:
    
    {letter_content}
    
    Check for:
    1. All required legal disclaimers
    2. Regulatory compliance
    3. Professional tone and language
    4. Completeness of information
    5. Industry best practices
    
    Provide:
    - List of compliance issues (if any)
    - Specific suggestions for improvement
    - Overall compliance score (0-1)
    - Whether the letter is valid for sending
    """
    
    # Get validation
    response_content = ""
    async for response_item in compliance_agent.invoke(task):
        # The response is the string representation of response_item
        response_content = str(response_item)
        break
    
    # Parse response (simplified - would be more robust in production)
    is_valid = "valid" in response_content.lower() if response_content else False
    compliance_score = 0.85 if is_valid else 0.5
    
    validation = ValidationResult(
        is_valid=is_valid,
        compliance_issues=["Review required disclaimers"] if not is_valid else [],
        suggestions=["Consider adding state-specific requirements"],
        compliance_score=compliance_score
    )
    
    return validation.to_dict()