#!/usr/bin/env python3
"""
Demo script to show agent conversation display feature.
This demonstrates how to use the include_conversation parameter.
"""

import json
import asyncio
from datetime import datetime
from services.agent_system import generate_letter_with_approval_workflow


async def demo_with_conversation():
    """Demo showing full agent conversation."""
    print("=" * 80)
    print("DEMO: Letter Generation WITH Agent Conversation")
    print("=" * 80)
    
    # Customer information
    customer_info = {
        "name": "Sarah Johnson",
        "policy_number": "POL-2024-12345",
        "address": "123 Main St, Anytown, USA 12345",
        "phone": "(555) 123-4567",
        "email": "sarah.johnson@email.com",
        "agent_name": "Michael Smith"
    }
    
    # Generate letter with conversation included
    result = await generate_letter_with_approval_workflow(
        customer_info=customer_info,
        letter_type="claim_denial",
        user_prompt="Deny water damage claim due to lack of maintenance. Be empathetic but firm.",
        include_conversation=True  # This includes the full agent conversation
    )
    
    # Display the final letter
    print("\n📄 FINAL LETTER:")
    print("-" * 40)
    print(result['letter_content'])
    print("-" * 40)
    
    # Display approval status
    print(f"\n✅ APPROVAL STATUS:")
    approval = result['approval_status']
    print(f"   Overall Approved: {approval['overall_approved']}")
    print(f"   Compliance Approved: {approval['compliance_approved']}")
    print(f"   Legal Approved: {approval.get('legal_approved', 'N/A')}")
    print(f"   Total Rounds: {result['total_rounds']}")
    
    # Display the agent conversation
    if 'agent_conversation' in result:
        print("\n💬 AGENT CONVERSATION:")
        print("=" * 80)
        
        current_round = 0
        for entry in result['agent_conversation']:
            # Print round header
            if entry['round'] != current_round:
                current_round = entry['round']
                print(f"\n--- Round {current_round} ---")
            
            # Print agent message
            print(f"\n[{entry['agent']}]:")
            
            # Format the message for better readability
            message = entry['message']
            
            # Split into content and approval status
            if "APPROVED" in message or "REJECTED" in message or "NEEDS_IMPROVEMENT" in message:
                # Find the approval keyword
                for keyword in ["WRITER_APPROVED", "WRITER_NEEDS_IMPROVEMENT", 
                               "COMPLIANCE_APPROVED", "COMPLIANCE_REJECTED",
                               "CUSTOMER_SERVICE_APPROVED", "CUSTOMER_SERVICE_REJECTED"]:
                    if keyword in message:
                        content = message.replace(keyword, "").strip()
                        print(f"{content}")
                        print(f"\n🔹 Status: {keyword}")
                        break
            else:
                print(message)
            
            print(f"⏰ Time: {entry['timestamp']}")
    else:
        print("\n❌ No conversation data available")


async def demo_without_conversation():
    """Demo showing letter generation without conversation."""
    print("\n\n" + "=" * 80)
    print("DEMO: Letter Generation WITHOUT Agent Conversation")
    print("=" * 80)
    
    customer_info = {
        "name": "John Doe",
        "policy_number": "POL-2024-67890",
        "email": "john.doe@email.com"
    }
    
    # Generate letter without conversation
    result = await generate_letter_with_approval_workflow(
        customer_info=customer_info,
        letter_type="policy_renewal",
        user_prompt="Remind about upcoming renewal in 30 days. Mention 5% loyalty discount.",
        include_conversation=False  # This excludes the conversation
    )
    
    # Display only the final result
    print("\n📄 FINAL LETTER:")
    print("-" * 40)
    print(result['letter_content'])
    print("-" * 40)
    
    print(f"\n✅ Letter generated in {result['total_rounds']} round(s)")
    print(f"   Approved: {result['approval_status']['overall_approved']}")
    
    # Verify no conversation is included
    if 'agent_conversation' not in result:
        print("\n✓ Agent conversation not included (as requested)")


async def main():
    """Run both demos."""
    print("Insurance Letter Generation - Agent Conversation Demo")
    print("This demo shows how to include/exclude agent conversations in the response\n")
    
    try:
        # Demo with conversation
        await demo_with_conversation()
        
        # Demo without conversation
        await demo_without_conversation()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure you have configured your Azure OpenAI credentials in .env file")


if __name__ == "__main__":
    # Check for required environment variables
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file")
    else:
        # Run the async main function
        asyncio.run(main())