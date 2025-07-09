# CLI Conversation Display Feature

## Overview
The Insurance Letter CLI now supports displaying the full agent conversation during letter generation. This feature allows users to see how the AI agents collaborate and iterate to produce compliant, customer-friendly letters.

## Usage

### Command Line Mode

Add the `--show-conversation` flag to see agent conversations:

```bash
python cli/insurance_cli.py \
  --customer-name "John Doe" \
  --policy-number "POL-123456" \
  --letter-type "claim_denial" \
  --prompt "Deny water damage claim" \
  --show-conversation
```

### Interactive Mode

When using interactive mode (`-i` or `--interactive`), you'll be prompted:

```
Show agent conversation? (y/N): y
```

## Display Format

The conversation is displayed with:

### 🎨 Visual Elements
- **Round Headers**: `━━━ Round 1 ━━━` in yellow
- **Agent Names**: Color-coded for easy identification
  - 📝 **LetterWriter** (blue)
  - 📝 **ComplianceReviewer** (yellow)
  - 📝 **CustomerServiceReviewer** (green)
- **Status Icons**: 
  - ✅ Approved (green)
  - ❌ Rejected (red)
  - 🔄 Needs Improvement (yellow)
- **Timestamps**: Shown in gray for each message

### Example Output

```
🤝 Agent Conversation
================================================================================

━━━ Round 1 ━━━

📝 LetterWriter
   I'll draft a claim denial letter for water damage...
   [Letter content here]
   🔄 WRITER_NEEDS_IMPROVEMENT
   ⏰ 2024-01-15T10:00:00

📝 ComplianceReviewer
   Missing required disclosure about appeal process.
   ❌ COMPLIANCE_REJECTED
   ⏰ 2024-01-15T10:00:15

📝 CustomerServiceReviewer
   Tone is too harsh. Needs more empathy.
   ❌ CUSTOMER_SERVICE_REJECTED
   ⏰ 2024-01-15T10:00:30

━━━ Round 2 ━━━

📝 LetterWriter
   Revised letter with appeal information and softer tone...
   [Updated letter content]
   ✅ WRITER_APPROVED
   ⏰ 2024-01-15T10:01:00

[... continues until all agents approve]
```

## CLI Examples

### 1. Basic Usage
```bash
# Show conversation for a claim denial
python cli/insurance_cli.py \
  --customer-name "Alice Johnson" \
  --policy-number "POL-2024-001" \
  --letter-type "claim_denial" \
  --prompt "Deny claim due to late filing" \
  --show-conversation
```

### 2. Save Output with Conversation
```bash
# Generate and save both letter and conversation
python cli/insurance_cli.py \
  --customer-name "Bob Smith" \
  --policy-number "POL-2024-002" \
  --letter-type "policy_renewal" \
  --prompt "Renewal with discount" \
  --show-conversation \
  --output renewal_letter.txt
```

### 3. JSON Output with Conversation
```bash
# Get raw JSON including conversation data
python cli/insurance_cli.py \
  --customer-name "Carol White" \
  --policy-number "POL-2024-003" \
  --letter-type "welcome" \
  --prompt "Welcome to insurance" \
  --show-conversation \
  --json > output.json
```

## JSON Structure

When using `--json` with `--show-conversation`, the output includes:

```json
{
  "letter_content": "Dear Carol...",
  "approval_status": {
    "overall_approved": true,
    "compliance_approved": true,
    "customer_service_approved": true
  },
  "total_rounds": 2,
  "agent_conversation": [
    {
      "round": 1,
      "agent": "LetterWriter",
      "message": "Draft letter... WRITER_APPROVED",
      "timestamp": "2024-01-15T10:00:00"
    },
    // ... more conversation entries
  ]
}
```

## Benefits

1. **Transparency**: See exactly how the AI agents work together
2. **Learning**: Understand what makes a compliant letter
3. **Debugging**: Identify why letters might need multiple rounds
4. **Quality Assurance**: Verify the review process is thorough
5. **Audit Trail**: Document the complete generation process

## Performance Notes

- No impact on generation time
- Adds ~10-50KB to response size depending on rounds
- Conversation data is generated during normal workflow
- Only displayed when explicitly requested

## Testing

Run the test script to verify the feature:

```bash
python test_cli_conversation.py
```

This will test:
- Help text includes the new option
- Conversation displays with flag
- Conversation hidden without flag
- JSON output includes conversation data

## Tips

1. **Development**: Always use `--show-conversation` during development
2. **Production**: Consider omitting for cleaner output in production
3. **Debugging**: Use with `--json` to capture full conversation data
4. **Training**: Great for showing new employees the review process