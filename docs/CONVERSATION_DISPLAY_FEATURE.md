# Agent Conversation Display Feature

## Overview
The insurance letter generation system now supports displaying the full conversation between AI agents during the review process. This feature provides transparency into how the agents collaborate and iterate to produce compliant, customer-friendly letters.

## How It Works

### 1. Request Parameter
Add `include_conversation: true` to your API request to include the agent conversation in the response.

```json
{
  "customer_info": {
    "name": "John Doe",
    "policy_number": "POL123456"
  },
  "letter_type": "claim_denial",
  "user_prompt": "Deny water damage claim",
  "include_conversation": true  // ← Enable conversation display
}
```

### 2. Response Format
When enabled, the response includes an `agent_conversation` array with the full dialogue:

```json
{
  "letter_content": "Dear John Doe...",
  "approval_status": {
    "overall_approved": true,
    "compliance_approved": true,
    "legal_approved": true
  },
  "total_rounds": 2,
  "agent_conversation": [
    {
      "round": 1,
      "agent": "LetterWriter",
      "message": "I'll draft a claim denial letter. Dear John Doe... WRITER_APPROVED",
      "timestamp": "2024-01-15T10:00:00"
    },
    {
      "round": 1,
      "agent": "ComplianceReviewer",
      "message": "The letter meets regulatory requirements. COMPLIANCE_APPROVED",
      "timestamp": "2024-01-15T10:00:15"
    },
    {
      "round": 1,
      "agent": "CustomerServiceReviewer",
      "message": "The tone is empathetic and clear. CUSTOMER_SERVICE_APPROVED",
      "timestamp": "2024-01-15T10:00:30"
    }
  ]
}
```

## Agent Roles

### 1. **LetterWriter**
- Creates and refines the letter content
- Ends messages with: `WRITER_APPROVED` or `WRITER_NEEDS_IMPROVEMENT`

### 2. **ComplianceReviewer**
- Ensures regulatory compliance and legal requirements
- Ends messages with: `COMPLIANCE_APPROVED` or `COMPLIANCE_REJECTED`

### 3. **CustomerServiceReviewer**
- Reviews tone, clarity, and customer experience
- Ends messages with: `CUSTOMER_SERVICE_APPROVED` or `CUSTOMER_SERVICE_REJECTED`

## Approval Process

### Iterative Refinement
The agents work in rounds:
1. LetterWriter creates/refines the letter
2. ComplianceReviewer checks regulations
3. CustomerServiceReviewer evaluates customer experience

This continues until:
- All agents approve (ending keywords: `*_APPROVED`)
- OR maximum 5 rounds are reached

### Example Multi-Round Conversation

**Round 1:**
- LetterWriter: "Initial draft... WRITER_NEEDS_IMPROVEMENT"
- ComplianceReviewer: "Missing required disclosures. COMPLIANCE_REJECTED"
- CustomerServiceReviewer: "Tone too harsh. CUSTOMER_SERVICE_REJECTED"

**Round 2:**
- LetterWriter: "Added disclosures and softened tone... WRITER_APPROVED"
- ComplianceReviewer: "All requirements met. COMPLIANCE_APPROVED"
- CustomerServiceReviewer: "Much better tone. CUSTOMER_SERVICE_APPROVED"

## Use Cases

### 1. **Debugging & Quality Assurance**
- See exactly why a letter was rejected or approved
- Understand which compliance rules were applied
- Track how many iterations were needed

### 2. **Training & Documentation**
- Show new employees how the system works
- Document the review process for audits
- Create examples of good vs. problematic letters

### 3. **Customer Transparency**
- Demonstrate the care taken in letter creation
- Show compliance with regulations
- Build trust through process visibility

## API Examples

### Request WITH Conversation
```bash
curl -X POST http://localhost:7071/api/draft-letter \
  -H "Content-Type: application/json" \
  -d '{
    "customer_info": {
      "name": "Sarah Johnson",
      "policy_number": "POL-2024-001"
    },
    "letter_type": "policy_renewal",
    "user_prompt": "Renewal due in 30 days with 5% discount",
    "include_conversation": true
  }'
```

### Request WITHOUT Conversation (Default)
```bash
curl -X POST http://localhost:7071/api/draft-letter \
  -H "Content-Type: application/json" \
  -d '{
    "customer_info": {
      "name": "Sarah Johnson",
      "policy_number": "POL-2024-001"
    },
    "letter_type": "policy_renewal",
    "user_prompt": "Renewal due in 30 days with 5% discount"
  }'
```

## Performance Considerations

- Including conversation adds ~10-50KB to response size
- No impact on letter generation time
- Conversation is generated during normal workflow
- Storage in Cosmos DB is optional (not included by default)

## Testing

Run the conversation display tests:
```bash
python -m pytest tests/test_conversation_display.py -v
```

Run the interactive demo:
```bash
python demo_conversation_display.py
```

## Best Practices

1. **Production Use**: Consider excluding conversation in production for smaller payloads
2. **Development**: Always include during development for debugging
3. **Auditing**: Store conversations for compliance audits when needed
4. **UI Display**: Format conversations for easy reading in your frontend

## Future Enhancements

- [ ] Filter conversation by agent type
- [ ] Summarize key decision points
- [ ] Export conversation to different formats
- [ ] Real-time streaming of agent messages
- [ ] Conversation analytics and insights