#!/usr/bin/env python3
"""
Insurance Letter Drafting CLI Tool

A comprehensive command-line interface for testing the insurance letter
drafting API with multi-agent orchestration.
"""

import argparse
import json
import os
import sys
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Initialize Rich console
console = Console()

# Default API configuration
DEFAULT_BASE_URL = "http://localhost:7071/api"
DEFAULT_FUNCTION_KEY = os.getenv("FUNCTION_KEY", "")


class InsuranceCLI:
    """CLI for testing insurance letter drafting functionality."""
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL, function_key: str = DEFAULT_FUNCTION_KEY):
        self.base_url = base_url.rstrip('/')
        self.function_key = function_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if function_key:
            self.headers["x-functions-key"] = function_key
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "unhealthy"}
    
    def draft_letter(self, customer_info: Dict[str, str], letter_type: str, user_prompt: str, 
                    include_conversation: bool = False) -> Dict[str, Any]:
        """Generate a letter using the API."""
        payload = {
            "customer_info": customer_info,
            "letter_type": letter_type,
            "user_prompt": user_prompt,
            "include_conversation": include_conversation
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/draft-letter",
                json=payload,
                headers=self.headers,
                timeout=120  # 2 minutes for multi-agent processing
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def suggest_letter_type(self, prompt: str) -> Dict[str, Any]:
        """Get letter type suggestion from API."""
        payload = {"prompt": prompt}
        
        try:
            response = requests.post(
                f"{self.base_url}/suggest-letter-type",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def validate_letter(self, letter_content: str, letter_type: str) -> Dict[str, Any]:
        """Validate a letter using the API."""
        payload = {
            "letter_content": letter_content,
            "letter_type": letter_type
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/validate-letter",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


def display_health_status(health_data: Dict[str, Any]):
    """Display health check results in a formatted table."""
    if "error" in health_data:
        console.print(f"[red]Health check failed: {health_data['error']}[/red]")
        return
    
    table = Table(title="API Health Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in health_data.items():
        if key == "endpoints":
            value = ", ".join(value)
        table.add_row(key, str(value))
    
    console.print(table)


def display_conversation(conversation: list):
    """Display the agent conversation in a formatted way."""
    if not conversation:
        return
    
    console.print("\n[bold cyan]🤝 Agent Conversation[/bold cyan]")
    console.print("=" * 80)
    
    current_round = 0
    
    for entry in conversation:
        # Print round header if it's a new round
        if entry['round'] != current_round:
            current_round = entry['round']
            console.print(f"\n[bold yellow]━━━ Round {current_round} ━━━[/bold yellow]")
        
        # Color-code agents
        agent_colors = {
            "LetterWriter": "blue",
            "ComplianceReviewer": "yellow", 
            "CustomerServiceReviewer": "green"
        }
        agent_color = agent_colors.get(entry['agent'], "white")
        
        # Print agent name
        console.print(f"\n[bold {agent_color}]📝 {entry['agent']}[/bold {agent_color}]")
        
        # Extract and format the message
        message = entry['message']
        
        # Check for approval keywords and split message
        approval_keywords = {
            "WRITER_APPROVED": ("✅", "green"),
            "WRITER_NEEDS_IMPROVEMENT": ("🔄", "yellow"),
            "COMPLIANCE_APPROVED": ("✅", "green"),
            "COMPLIANCE_REJECTED": ("❌", "red"),
            "CUSTOMER_SERVICE_APPROVED": ("✅", "green"),
            "CUSTOMER_SERVICE_REJECTED": ("❌", "red")
        }
        
        # Find and remove approval keyword from message
        status_display = None
        for keyword, (icon, color) in approval_keywords.items():
            if keyword in message:
                message = message.replace(keyword, "").strip()
                status_display = f"[{color}]{icon} {keyword}[/{color}]"
                break
        
        # Display the message content
        if len(message) > 200:
            # For long messages, show in a panel
            console.print(Panel(message, border_style=agent_color))
        else:
            console.print(f"   {message}")
        
        # Display status if found
        if status_display:
            console.print(f"   {status_display}")
        
        # Display timestamp in gray
        console.print(f"   [dim]⏰ {entry['timestamp']}[/dim]")
    
    console.print("\n" + "=" * 80)


def display_letter_result(result: Dict[str, Any], show_conversation: bool = False):
    """Display letter generation result."""
    if "error" in result:
        console.print(f"[red]Error: {result['error']}[/red]")
        return
    
    # Display approval status
    approval_status = result.get("approval_status", {})
    
    # Create approval status table
    table = Table(title="Approval Status")
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="green")
    
    table.add_row("Letter Writer", "✅ Approved" if approval_status.get("writer_approved") else "❌ Needs Work")
    table.add_row("Compliance", "✅ Approved" if approval_status.get("compliance_approved") else "❌ Rejected")
    table.add_row("Customer Service", "✅ Approved" if approval_status.get("customer_service_approved") else "❌ Needs Improvement")
    
    console.print(table)
    
    # Display metadata
    console.print(f"\n[bold]Total Rounds:[/bold] {result.get('total_rounds', 'N/A')}")
    console.print(f"[bold]Document ID:[/bold] {result.get('document_id', 'Not saved')}")
    console.print(f"[bold]Timestamp:[/bold] {result.get('timestamp', 'N/A')}")
    
    # Display the letter content
    letter_content = result.get("letter_content", "No letter content found")
    console.print("\n[bold]Generated Letter:[/bold]")
    console.print(Panel(letter_content, title="Letter Content", border_style="blue"))
    
    # Display conversation if requested and available
    if show_conversation and "agent_conversation" in result:
        display_conversation(result["agent_conversation"])


def interactive_mode(cli: InsuranceCLI):
    """Run the CLI in interactive mode."""
    console.print("[bold cyan]Insurance Letter Drafting CLI - Interactive Mode[/bold cyan]")
    console.print("Type 'help' for available commands or 'exit' to quit.\n")
    
    while True:
        command = Prompt.ask("\n[bold]Command[/bold]", 
                           choices=["draft", "suggest", "validate", "health", "help", "exit"])
        
        if command == "exit":
            console.print("[yellow]Goodbye![/yellow]")
            break
        
        elif command == "help":
            console.print("\n[bold]Available Commands:[/bold]")
            console.print("  draft    - Generate a new insurance letter")
            console.print("  suggest  - Get letter type suggestions")
            console.print("  validate - Validate an existing letter")
            console.print("  health   - Check API health status")
            console.print("  exit     - Exit the program")
        
        elif command == "health":
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Checking API health...", total=None)
                health_data = cli.health_check()
            
            display_health_status(health_data)
        
        elif command == "draft":
            # Collect customer information
            console.print("\n[bold]Customer Information:[/bold]")
            customer_info = {
                "name": Prompt.ask("Customer Name"),
                "policy_number": Prompt.ask("Policy Number"),
                "address": Prompt.ask("Address (optional)", default=""),
                "phone": Prompt.ask("Phone (optional)", default=""),
                "email": Prompt.ask("Email (optional)", default=""),
                "agent_name": Prompt.ask("Agent Name (optional)", default="")
            }
            
            # Select letter type
            letter_types = ["claim_denial", "claim_approval", "policy_renewal", 
                          "coverage_change", "premium_increase", "cancellation", 
                          "welcome", "general"]
            
            console.print("\n[bold]Letter Types:[/bold]")
            for i, lt in enumerate(letter_types, 1):
                console.print(f"  {i}. {lt}")
            
            type_choice = Prompt.ask("Select letter type (1-8)", default="8")
            letter_type = letter_types[int(type_choice) - 1]
            
            # Get user prompt
            user_prompt = Prompt.ask("\n[bold]Describe the letter requirements[/bold]")
            
            # Ask if user wants to see conversation
            show_conversation = Confirm.ask("\n[bold]Show agent conversation?[/bold]", default=False)
            
            # Generate letter
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Generating letter with multi-agent review...", total=None)
                result = cli.draft_letter(customer_info, letter_type, user_prompt, show_conversation)
            
            display_letter_result(result, show_conversation)
            
            # Offer to save the letter
            if "letter_content" in result and Confirm.ask("\nSave letter to file?"):
                filename = f"letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w') as f:
                    f.write(result["letter_content"])
                console.print(f"[green]Letter saved to {filename}[/green]")
        
        elif command == "suggest":
            prompt = Prompt.ask("\n[bold]Describe the situation[/bold]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Getting letter type suggestion...", total=None)
                suggestion = cli.suggest_letter_type(prompt)
            
            if "error" in suggestion:
                console.print(f"[red]Error: {suggestion['error']}[/red]")
            else:
                console.print(f"\n[bold]Suggested Type:[/bold] {suggestion.get('suggested_type', 'Unknown')}")
                console.print(f"[bold]Confidence:[/bold] {suggestion.get('confidence', 0):.0%}")
                console.print(f"[bold]Reasoning:[/bold] {suggestion.get('reasoning', 'N/A')}")
                
                alternatives = suggestion.get('alternative_types', [])
                if alternatives:
                    console.print(f"[bold]Alternatives:[/bold] {', '.join(alternatives)}")
        
        elif command == "validate":
            # Get letter content
            file_path = Prompt.ask("\n[bold]Letter file path (or 'paste' to enter manually)[/bold]")
            
            if file_path.lower() == 'paste':
                console.print("Paste the letter content (press Ctrl+D when done):")
                lines = []
                try:
                    while True:
                        lines.append(input())
                except EOFError:
                    pass
                letter_content = '\n'.join(lines)
            else:
                try:
                    with open(file_path, 'r') as f:
                        letter_content = f.read()
                except FileNotFoundError:
                    console.print("[red]File not found![/red]")
                    continue
            
            # Get letter type
            letter_type = Prompt.ask("Letter type", default="general")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Validating letter...", total=None)
                validation = cli.validate_letter(letter_content, letter_type)
            
            if "error" in validation:
                console.print(f"[red]Error: {validation['error']}[/red]")
            else:
                is_valid = validation.get("is_valid", False)
                console.print(f"\n[bold]Validation Result:[/bold] {'✅ Valid' if is_valid else '❌ Invalid'}")
                console.print(f"[bold]Compliance Score:[/bold] {validation.get('compliance_score', 0):.0%}")
                
                issues = validation.get("compliance_issues", [])
                if issues:
                    console.print("\n[bold]Compliance Issues:[/bold]")
                    for issue in issues:
                        console.print(f"  • {issue}")
                
                suggestions = validation.get("suggestions", [])
                if suggestions:
                    console.print("\n[bold]Suggestions:[/bold]")
                    for suggestion in suggestions:
                        console.print(f"  • {suggestion}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Insurance Letter Drafting CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python insurance_cli.py --interactive

  # Direct letter generation
  python insurance_cli.py --customer-name "John Doe" --policy-number "POL-123456" \\
      --letter-type "welcome" --prompt "Welcome new customer to auto insurance"

  # Letter generation with agent conversation display
  python insurance_cli.py --customer-name "Jane Smith" --policy-number "POL-789012" \\
      --letter-type "claim_denial" --prompt "Deny claim with empathy" --show-conversation

  # Letter type suggestion
  python insurance_cli.py --suggest --prompt "Customer claim was denied due to late filing"

  # Letter validation
  python insurance_cli.py --validate letter.txt --letter-type "claim_denial"

  # Health check
  python insurance_cli.py --health-check
        """
    )
    
    # Connection options
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL,
                       help="API base URL (default: http://localhost:7071/api)")
    parser.add_argument("--function-key", default=DEFAULT_FUNCTION_KEY,
                       help="Azure Function key for authentication")
    
    # Mode options
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run in interactive mode")
    
    # Letter generation options
    parser.add_argument("--customer-name", help="Customer name")
    parser.add_argument("--policy-number", help="Policy number")
    parser.add_argument("--address", default="", help="Customer address")
    parser.add_argument("--phone", default="", help="Customer phone")
    parser.add_argument("--email", default="", help="Customer email")
    parser.add_argument("--agent-name", default="", help="Agent name")
    parser.add_argument("--letter-type", default="general",
                       choices=["claim_denial", "claim_approval", "policy_renewal",
                               "coverage_change", "premium_increase", "cancellation",
                               "welcome", "general"],
                       help="Type of letter to generate")
    parser.add_argument("--prompt", help="Letter requirements or description")
    
    # Other operations
    parser.add_argument("--suggest", action="store_true",
                       help="Suggest letter type based on description")
    parser.add_argument("--validate", metavar="FILE",
                       help="Validate a letter from file")
    parser.add_argument("--health-check", action="store_true",
                       help="Check API health status")
    
    # Output options
    parser.add_argument("--output", "-o", help="Save output to file")
    parser.add_argument("--json", action="store_true",
                       help="Output raw JSON response")
    parser.add_argument("--show-conversation", action="store_true",
                       help="Show the agent conversation during letter generation")
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = InsuranceCLI(base_url=args.base_url, function_key=args.function_key)
    
    # Handle different modes
    if args.interactive:
        interactive_mode(cli)
    
    elif args.health_check:
        health_data = cli.health_check()
        if args.json:
            console.print_json(data=health_data)
        else:
            display_health_status(health_data)
    
    elif args.suggest:
        if not args.prompt:
            console.print("[red]Error: --prompt is required for suggestions[/red]")
            sys.exit(1)
        
        suggestion = cli.suggest_letter_type(args.prompt)
        if args.json:
            console.print_json(data=suggestion)
        else:
            if "error" in suggestion:
                console.print(f"[red]Error: {suggestion['error']}[/red]")
            else:
                console.print(f"[bold]Suggested Type:[/bold] {suggestion.get('suggested_type', 'Unknown')}")
                console.print(f"[bold]Confidence:[/bold] {suggestion.get('confidence', 0):.0%}")
                console.print(f"[bold]Reasoning:[/bold] {suggestion.get('reasoning', 'N/A')}")
    
    elif args.validate:
        try:
            with open(args.validate, 'r') as f:
                letter_content = f.read()
        except FileNotFoundError:
            console.print(f"[red]Error: File '{args.validate}' not found[/red]")
            sys.exit(1)
        
        validation = cli.validate_letter(letter_content, args.letter_type)
        if args.json:
            console.print_json(data=validation)
        else:
            if "error" in validation:
                console.print(f"[red]Error: {validation['error']}[/red]")
            else:
                is_valid = validation.get("is_valid", False)
                console.print(f"[bold]Valid:[/bold] {'Yes' if is_valid else 'No'}")
                console.print(f"[bold]Score:[/bold] {validation.get('compliance_score', 0):.0%}")
    
    elif args.customer_name and args.policy_number and args.prompt:
        # Direct letter generation
        customer_info = {
            "name": args.customer_name,
            "policy_number": args.policy_number,
            "address": args.address,
            "phone": args.phone,
            "email": args.email,
            "agent_name": args.agent_name
        }
        
        with console.status("Generating letter..."):
            result = cli.draft_letter(customer_info, args.letter_type, args.prompt, args.show_conversation)
        
        if args.json:
            console.print_json(data=result)
        else:
            display_letter_result(result, args.show_conversation)
        
        # Save output if requested
        if args.output and "letter_content" in result:
            with open(args.output, 'w') as f:
                f.write(result["letter_content"])
            console.print(f"\n[green]Letter saved to {args.output}[/green]")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()