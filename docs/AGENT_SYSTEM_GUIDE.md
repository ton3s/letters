# Multi-Agent System Guide

## Overview

The Insurance Letter Generator uses a sophisticated multi-agent system powered by Azure OpenAI and Microsoft Semantic Kernel. This guide provides an in-depth look at how the agents work together to create high-quality, compliant insurance correspondence.

## Table of Contents

1. [Agent System Philosophy](#agent-system-philosophy)
2. [Agent Roles and Responsibilities](#agent-roles-and-responsibilities)
3. [Technical Implementation](#technical-implementation)
4. [Agent Collaboration Workflow](#agent-collaboration-workflow)
5. [Conversation Protocol](#conversation-protocol)
6. [Customizing Agents](#customizing-agents)
7. [Performance and Optimization](#performance-and-optimization)
8. [Troubleshooting](#troubleshooting)

## Agent System Philosophy

### Why Multi-Agent?

Traditional single-model approaches often struggle with complex tasks requiring different types of expertise. Our multi-agent system addresses this by:

1. **Specialization**: Each agent focuses on a specific domain
2. **Collaboration**: Agents work together, providing checks and balances
3. **Iteration**: Multiple review rounds ensure quality
4. **Transparency**: Full conversation history for audit trails

### Design Principles

- **Separation of Concerns**: Each agent has a clear, focused role
- **Iterative Refinement**: Quality improves through multiple passes
- **Fail-Safe Design**: Approval from all agents required
- **Human-in-the-Loop**: Results are editable by users

## Agent Roles and Responsibilities

### 1. Letter Writer Agent

**Primary Role**: Content Creation and Revision

**Responsibilities**:
- Draft initial letters based on requirements
- Incorporate feedback from other agents
- Ensure proper formatting and structure
- Maintain professional tone

**Key Instructions**:
```python
You are a professional insurance letter drafting specialist with expertise in:
- Creating clear, concise insurance correspondence
- Tailoring tone and language to the letter type
- Incorporating all necessary information
- Following insurance industry best practices
```

**Approval Criteria**:
- Letter contains all required information
- Appropriate tone for the letter type
- Clear and concise language
- Proper formatting

### 2. Compliance Reviewer Agent

**Primary Role**: Regulatory Compliance Verification

**Responsibilities**:
- Verify legal accuracy
- Check for required disclosures
- Ensure regulatory compliance
- Identify potential legal risks

**Key Instructions**:
```python
You are an insurance compliance expert specializing in:
- Insurance regulations and requirements
- State and federal compliance standards
- Required disclosures and legal language
- Risk assessment and mitigation
```

**Approval Criteria**:
- All required disclosures present
- No misleading statements
- Compliant with regulations
- Appropriate legal language

### 3. Customer Service Agent

**Primary Role**: Customer Experience Optimization

**Responsibilities**:
- Evaluate clarity and understanding
- Ensure appropriate empathy
- Check for jargon or complex terms
- Verify customer-friendly approach

**Key Instructions**:
```python
You are a customer service excellence expert focusing on:
- Clear, understandable communication
- Empathetic and respectful tone
- Customer satisfaction and experience
- Avoiding technical jargon
```

**Approval Criteria**:
- Easy to understand
- Appropriate empathy level
- No unnecessary jargon
- Positive customer experience

## Technical Implementation

### Core Architecture

The agent system is built on Microsoft Semantic Kernel, providing:

```python
# Agent System Initialization
kernel = Kernel()

# Add AI Service
kernel.add_service(AzureChatCompletion(
    deployment_name=deployment_name,
    endpoint=endpoint,
    api_key=api_key
))

# Create Agents
agents = [
    ChatCompletionAgent(
        id="letter_writer",
        kernel=kernel,
        name="LetterWriter",
        instructions=LETTER_WRITER_INSTRUCTIONS
    ),
    ChatCompletionAgent(
        id="compliance_reviewer",
        kernel=kernel,
        name="ComplianceReviewer",
        instructions=COMPLIANCE_REVIEWER_INSTRUCTIONS
    ),
    ChatCompletionAgent(
        id="customer_service",
        kernel=kernel,
        name="CustomerServiceAgent",
        instructions=CUSTOMER_SERVICE_INSTRUCTIONS
    )
]
```

### Agent Chat Implementation

```python
# Create Agent Chat
agent_chat = AgentGroupChat(
    agents=agents,
    termination_strategy=ApprovalTerminationStrategy(
        agents=agents,
        maximum_rounds=5
    ),
    execution_settings=AgentGroupChatSettings(
        execution_mode=ExecutionMode.SEQUENTIAL
    )
)
```

### Termination Strategy

The `ApprovalTerminationStrategy` manages workflow completion:

```python
class ApprovalTerminationStrategy(TerminationStrategy):
    def __init__(self, agents, maximum_rounds=5):
        self.maximum_rounds = maximum_rounds
        self.round_count = 0
        self.approval_tracker = {
            "writer": False,
            "compliance": False,
            "customer_service": False
        }
```

## Agent Collaboration Workflow

### Sequential Execution Flow

```
Round 1:
├── Letter Writer → Creates initial draft
├── Compliance Reviewer → Reviews for compliance
└── Customer Service → Reviews for customer experience

Round 2 (if needed):
├── Letter Writer → Incorporates feedback
├── Compliance Reviewer → Re-reviews
└── Customer Service → Final check

... (continues until all approve or max rounds reached)
```

### Decision Flow

```python
def should_terminate(self, history):
    # Check if all agents approved
    if all(self.approval_tracker.values()):
        return True
    
    # Check if max rounds exceeded
    if self.round_count >= self.maximum_rounds:
        return True
    
    return False
```

### Message Flow Example

```
User Request → "Generate welcome letter for new customer"
    ↓
Letter Writer → "I'll create a welcoming letter for the new policyholder..."
    ↓
Compliance → "The letter needs to include policy effective date..."
    ↓
Customer Service → "The tone could be warmer. Consider adding..."
    ↓
Letter Writer → "I've incorporated all feedback. Here's the revised..."
    ↓
All Approve → Letter Complete
```

## Conversation Protocol

### Message Structure

Each agent message includes:

```python
{
    "agent": "LetterWriter",
    "role": "assistant",
    "content": "Letter content and explanation...",
    "approval_status": "WRITER_APPROVED",
    "timestamp": "2025-01-01T10:00:00Z",
    "round": 1
}
```

### Approval Tags

Agents indicate approval using specific tags:

- `[WRITER_APPROVED]` - Letter writer approves
- `[COMPLIANCE_APPROVED]` - Compliance reviewer approves
- `[CUSTOMER_SERVICE_APPROVED]` - Customer service approves
- `[WRITER_NEEDS_IMPROVEMENT]` - Revision needed
- `[COMPLIANCE_REJECTED]` - Compliance issues found
- `[CUSTOMER_SERVICE_REJECTED]` - Customer experience issues

### Parsing Approval Status

```python
def _extract_approval_status(self, content: str, agent_type: str) -> bool:
    approval_patterns = {
        "writer": r'\[WRITER_APPROVED\]',
        "compliance": r'\[COMPLIANCE_APPROVED\]',
        "customer_service": r'\[CUSTOMER_SERVICE_APPROVED\]'
    }
    
    pattern = approval_patterns.get(agent_type)
    if pattern:
        return bool(re.search(pattern, content, re.IGNORECASE))
    return False
```

## Customizing Agents

### Modifying Agent Instructions

To customize agent behavior, modify the instruction templates:

```python
# In agent_system.py
LETTER_WRITER_INSTRUCTIONS = """
You are a professional insurance letter drafting specialist.

Your responsibilities:
1. Create clear, professional insurance letters
2. Incorporate feedback from other agents
3. Ensure all required information is included

Customization: Add your specific requirements here
- Use company-specific tone guidelines
- Include required company disclaimers
- Follow brand voice guidelines
"""
```

### Adding New Agents

To add a new agent (e.g., Legal Review):

```python
# 1. Define instructions
LEGAL_REVIEWER_INSTRUCTIONS = """
You are a legal expert specializing in insurance law...
"""

# 2. Create agent
legal_agent = ChatCompletionAgent(
    id="legal_reviewer",
    kernel=kernel,
    name="LegalReviewer",
    instructions=LEGAL_REVIEWER_INSTRUCTIONS
)

# 3. Update termination strategy
self.approval_tracker["legal"] = False

# 4. Add approval pattern
approval_patterns["legal"] = r'\[LEGAL_APPROVED\]'
```

### Configuring Agent Parameters

```python
# Adjust agent behavior
execution_settings = OpenAIPromptExecutionSettings(
    temperature=0.7,  # Creativity level (0-1)
    max_tokens=2000,  # Response length
    top_p=0.9,       # Nucleus sampling
    frequency_penalty=0.0,  # Reduce repetition
    presence_penalty=0.0    # Encourage new topics
)
```

## Performance and Optimization

### Response Time Optimization

1. **Parallel Processing** (Future Enhancement):
```python
execution_mode=ExecutionMode.PARALLEL  # Not yet implemented
```

2. **Caching Common Patterns**:
```python
# Cache frequently used letter templates
template_cache = {
    "welcome": base_welcome_template,
    "renewal": base_renewal_template
}
```

3. **Token Optimization**:
- Keep instructions concise
- Limit conversation history
- Use efficient prompts

### Cost Management

```python
# Monitor token usage
def calculate_tokens(text: str) -> int:
    # Rough estimation: 1 token ≈ 4 characters
    return len(text) // 4

# Set token limits
MAX_TOKENS_PER_LETTER = 8000  # Adjust based on needs
```

### Scaling Considerations

1. **Concurrent Requests**: Use connection pooling
2. **Rate Limiting**: Implement per-user quotas
3. **Circuit Breakers**: Handle API failures gracefully
4. **Monitoring**: Track agent performance metrics

## Troubleshooting

### Common Issues

#### 1. Agents Not Approving

**Symptoms**: Agents keep requesting changes
**Solutions**:
- Review agent instructions for conflicts
- Check approval criteria clarity
- Increase maximum rounds
- Add debug logging

```python
# Debug logging
logger.info(f"Agent {agent_name} approval status: {approved}")
logger.debug(f"Agent response: {content[:200]}...")
```

#### 2. Timeout Errors

**Symptoms**: Function times out before completion
**Solutions**:
- Reduce max rounds
- Optimize agent instructions
- Implement async timeout handling

```python
# Add timeout handling
async def generate_with_timeout(chat, prompt, timeout=120):
    try:
        return await asyncio.wait_for(
            chat.add_chat_message(prompt),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.error("Agent chat timed out")
        raise
```

#### 3. Inconsistent Results

**Symptoms**: Same input produces different outputs
**Solutions**:
- Reduce temperature setting
- Add more specific instructions
- Implement result validation

```python
# Validate results
def validate_letter_content(content: str) -> bool:
    required_elements = [
        "policy number",
        "customer name",
        "signature block"
    ]
    return all(elem in content.lower() for elem in required_elements)
```

### Debugging Tools

#### 1. Conversation Replay

```python
def replay_conversation(conversation_history):
    for message in conversation_history:
        print(f"\n{'='*50}")
        print(f"Agent: {message['agent']}")
        print(f"Round: {message['round']}")
        print(f"Content: {message['content'][:200]}...")
        print(f"Approved: {message.get('approved', 'N/A')}")
```

#### 2. Agent Performance Metrics

```python
def analyze_agent_performance(letters):
    metrics = {
        "avg_rounds": 0,
        "approval_rates": {},
        "common_issues": []
    }
    # Calculate metrics
    return metrics
```

#### 3. Test Mode

```python
# Run in test mode with deterministic responses
TEST_MODE = os.getenv("AGENT_TEST_MODE", "false").lower() == "true"

if TEST_MODE:
    execution_settings.temperature = 0  # Deterministic
    execution_settings.seed = 42       # Fixed seed
```

## Best Practices

1. **Clear Instructions**: Be specific about expectations
2. **Iterative Refinement**: Start simple, add complexity
3. **Monitor Performance**: Track metrics and costs
4. **User Feedback**: Incorporate user edits as training data
5. **Regular Updates**: Refine instructions based on results
6. **Error Handling**: Graceful degradation for failures
7. **Documentation**: Keep agent behaviors documented

## Future Enhancements

1. **Parallel Execution**: Run compliance and customer service reviews simultaneously
2. **Dynamic Agent Selection**: Choose agents based on letter type
3. **Learning Loop**: Incorporate user feedback into agent instructions
4. **A/B Testing**: Test different agent configurations
5. **Custom Plugins**: Add specialized knowledge domains
6. **Multi-Language Support**: Agents for different languages