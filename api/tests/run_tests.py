#!/usr/bin/env python
"""
Test runner script for the Insurance Letter API.
"""
import sys
import os
import pytest
import argparse
from pathlib import Path

# Add parent directory to path so we can import the app modules
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Run the test suite with various options."""
    parser = argparse.ArgumentParser(description="Run API tests")
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose test output"
    )
    parser.add_argument(
        "--failfast",
        "-x",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run only unit tests (skip integration)"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests"
    )
    parser.add_argument(
        "--specific",
        "-k",
        type=str,
        help="Run specific test by name pattern"
    )
    
    args = parser.parse_args()
    
    # Build pytest arguments
    pytest_args = []
    
    if args.verbose:
        pytest_args.append("-v")
    
    if args.failfast:
        pytest_args.append("-x")
    
    if args.coverage:
        pytest_args.extend([
            "--cov=services",
            "--cov=function_app",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    if args.unit:
        pytest_args.extend([
            "test_models.py",
            "test_agent_system.py",
            "test_cosmos_service.py",
            "test_function_app.py"
        ])
    elif args.integration:
        pytest_args.append("test_integration.py")
    
    if args.specific:
        pytest_args.extend(["-k", args.specific])
    
    # Add test directory if no specific files specified
    if not any(arg.endswith(".py") for arg in pytest_args):
        pytest_args.append(str(Path(__file__).parent))
    
    # Run tests
    print(f"Running tests with arguments: {' '.join(pytest_args)}")
    exit_code = pytest.main(pytest_args)
    
    if args.coverage and exit_code == 0:
        print("\nCoverage report generated in htmlcov/index.html")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())