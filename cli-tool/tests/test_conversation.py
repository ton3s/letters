#!/usr/bin/env python3
"""
Test script to demonstrate CLI conversation display feature.
"""

import subprocess
import sys
import os
from pathlib import Path

# Get the path to the CLI script
cli_path = Path(__file__).parent.parent / "insurance_cli.py"

def run_cli_command(args):
    """Run a CLI command and return the output."""
    cmd = [sys.executable, str(cli_path)] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def test_direct_mode_with_conversation():
    """Test direct mode with conversation display."""
    print("=" * 80)
    print("TEST 1: Direct Mode WITH Conversation Display")
    print("=" * 80)
    
    args = [
        "--customer-name", "Alice Johnson",
        "--policy-number", "POL-2024-CONV-001",
        "--letter-type", "claim_denial",
        "--prompt", "Deny water damage claim due to lack of maintenance. Be empathetic.",
        "--show-conversation"  # This enables conversation display
    ]
    
    print(f"Running: python {cli_path.name} {' '.join(args)}")
    print()
    
    returncode, stdout, stderr = run_cli_command(args)
    
    if returncode == 0:
        print(stdout)
        if "Agent Conversation" in stdout:
            print("✅ SUCCESS: Conversation was displayed")
        else:
            print("❌ FAILED: Conversation was not displayed")
    else:
        print(f"❌ Command failed with return code {returncode}")
        print(f"Error: {stderr}")

def test_direct_mode_without_conversation():
    """Test direct mode without conversation display."""
    print("\n" + "=" * 80)
    print("TEST 2: Direct Mode WITHOUT Conversation Display")
    print("=" * 80)
    
    args = [
        "--customer-name", "Bob Smith",
        "--policy-number", "POL-2024-NOCONV-001",
        "--letter-type", "policy_renewal",
        "--prompt", "Renewal reminder with 5% loyalty discount"
        # Note: --show-conversation is NOT included
    ]
    
    print(f"Running: python {cli_path.name} {' '.join(args)}")
    print()
    
    returncode, stdout, stderr = run_cli_command(args)
    
    if returncode == 0:
        print(stdout)
        if "Agent Conversation" not in stdout:
            print("✅ SUCCESS: Conversation was NOT displayed (as expected)")
        else:
            print("❌ FAILED: Conversation was displayed when it shouldn't be")
    else:
        print(f"❌ Command failed with return code {returncode}")
        print(f"Error: {stderr}")

def test_json_output_with_conversation():
    """Test JSON output mode with conversation."""
    print("\n" + "=" * 80)
    print("TEST 3: JSON Output Mode WITH Conversation")
    print("=" * 80)
    
    args = [
        "--customer-name", "Charlie Davis",
        "--policy-number", "POL-2024-JSON-001",
        "--letter-type", "welcome",
        "--prompt", "Welcome new customer to home insurance",
        "--show-conversation",
        "--json"
    ]
    
    print(f"Running: python {cli_path.name} {' '.join(args)}")
    print()
    
    returncode, stdout, stderr = run_cli_command(args)
    
    if returncode == 0:
        try:
            import json
            data = json.loads(stdout)
            if "agent_conversation" in data:
                print("✅ SUCCESS: JSON output includes agent_conversation field")
                print(f"   Conversation entries: {len(data['agent_conversation'])}")
            else:
                print("❌ FAILED: JSON output missing agent_conversation field")
        except json.JSONDecodeError:
            print("❌ FAILED: Invalid JSON output")
            print(stdout)
    else:
        print(f"❌ Command failed with return code {returncode}")
        print(f"Error: {stderr}")

def test_help_output():
    """Test that help shows the new option."""
    print("\n" + "=" * 80)
    print("TEST 4: Help Output")
    print("=" * 80)
    
    args = ["--help"]
    
    returncode, stdout, stderr = run_cli_command(args)
    
    if returncode == 0:
        if "--show-conversation" in stdout:
            print("✅ SUCCESS: Help includes --show-conversation option")
            # Extract and show the relevant help line
            for line in stdout.split('\n'):
                if "--show-conversation" in line:
                    print(f"   Help text: {line.strip()}")
        else:
            print("❌ FAILED: Help missing --show-conversation option")
    else:
        print(f"❌ Command failed with return code {returncode}")

def main():
    """Run all tests."""
    print("CLI Conversation Display Feature Tests")
    print("=====================================\n")
    
    # Check if we're in the right directory
    if not cli_path.exists():
        print(f"❌ Error: CLI script not found at {cli_path}")
        print("Please run this script from the project root directory")
        return
    
    # Check if API is running
    print("Note: Make sure the API is running at http://localhost:7071")
    print("      Run: func start\n")
    
    # Run tests
    test_help_output()
    
    # These tests require the API to be running
    print("\n" + "=" * 80)
    print("The following tests require the API to be running...")
    print("=" * 80)
    
    # Check if running in interactive mode
    if sys.stdin.isatty():
        confirm = input("\nIs the API running? (y/n): ")
        run_api_tests = confirm.lower() == 'y'
    else:
        print("\nRunning in non-interactive mode. Skipping API tests.")
        print("To run API tests, execute this script directly in a terminal.")
        run_api_tests = False
    
    if run_api_tests:
        test_direct_mode_with_conversation()
        test_direct_mode_without_conversation()
        test_json_output_with_conversation()
    else:
        print("\nSkipping API tests. Start the API with 'func start' and run again.")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()