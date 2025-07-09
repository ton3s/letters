#!/usr/bin/env python3
"""
Manual test script for Cosmos DB integration.
This script tests the actual Cosmos DB connection and operations.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.cosmos_service import CosmosService

# Load environment variables
load_dotenv()

def test_cosmos_connection():
    """Test Cosmos DB connection and basic operations."""
    print("=== Testing Cosmos DB Connection ===")
    
    # Initialize service
    cosmos_service = CosmosService()
    
    # Test 1: Health Check
    print("\n1. Testing health check...")
    try:
        result = cosmos_service.health_check()
        print(f"✓ Health check passed: {result}")
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return
    
    # Test 2: Save a letter
    print("\n2. Testing letter save...")
    test_letter = {
        "customer_name": "Test Customer",
        "policy_number": "TEST-" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "letter_type": "test_type",
        "content": "This is a test letter created by the manual test script.",
        "prompt": "Generate a test letter",
        "compliance_status": "pending",
        "is_compliant": False
    }
    
    try:
        saved_letter = cosmos_service.save_letter(test_letter)
        letter_id = saved_letter["id"]
        print(f"✓ Letter saved successfully with ID: {letter_id}")
    except Exception as e:
        print(f"✗ Failed to save letter: {str(e)}")
        return
    
    # Test 3: Retrieve the letter
    print("\n3. Testing letter retrieval...")
    try:
        retrieved_letter = cosmos_service.get_letter(letter_id, "letter")
        if retrieved_letter:
            print(f"✓ Letter retrieved successfully")
            print(f"   Customer: {retrieved_letter.get('customer_name')}")
            print(f"   Policy: {retrieved_letter.get('policy_number')}")
        else:
            print("✗ Letter not found")
    except Exception as e:
        print(f"✗ Failed to retrieve letter: {str(e)}")
    
    # Test 4: Query letters by customer
    print("\n4. Testing query by customer...")
    try:
        customer_letters = cosmos_service.get_letters_by_customer("Test Customer")
        print(f"✓ Found {len(customer_letters)} letters for 'Test Customer'")
    except Exception as e:
        print(f"✗ Failed to query by customer: {str(e)}")
    
    # Test 5: Query letters by type
    print("\n5. Testing query by type...")
    try:
        type_letters = cosmos_service.get_letters_by_type("test_type")
        print(f"✓ Found {len(type_letters)} letters of type 'test_type'")
    except Exception as e:
        print(f"✗ Failed to query by type: {str(e)}")
    
    # Test 6: Get recent letters
    print("\n6. Testing recent letters query...")
    try:
        recent_letters = cosmos_service.get_recent_letters(limit=5)
        print(f"✓ Found {len(recent_letters)} recent letters")
        if recent_letters:
            print("   Most recent letters:")
            for letter in recent_letters[:3]:
                created_at = letter.get('created_at', 'Unknown')
                customer = letter.get('customer_name', 'Unknown')
                print(f"   - {customer} ({created_at})")
    except Exception as e:
        print(f"✗ Failed to get recent letters: {str(e)}")
    
    # Test 7: Update letter status
    print("\n7. Testing letter status update...")
    try:
        updated_letter = cosmos_service.update_letter_status(letter_id, "approved", "letter")
        if updated_letter:
            print(f"✓ Letter status updated to: {updated_letter.get('compliance_status')}")
        else:
            print("✗ Failed to update letter status")
    except Exception as e:
        print(f"✗ Failed to update letter: {str(e)}")
    
    # Test 8: Delete letter (soft delete)
    print("\n8. Testing letter deletion...")
    try:
        deleted = cosmos_service.delete_letter(letter_id, "letter")
        if deleted:
            print("✓ Letter marked as deleted")
            
            # Verify soft delete
            deleted_letter = cosmos_service.get_letter(letter_id, "letter")
            if deleted_letter and deleted_letter.get("deleted"):
                print("✓ Confirmed: Letter is marked as deleted")
            else:
                print("✗ Letter deletion verification failed")
        else:
            print("✗ Failed to delete letter")
    except Exception as e:
        print(f"✗ Failed to delete letter: {str(e)}")
    
    print("\n=== All tests completed ===")


def test_error_scenarios():
    """Test error handling scenarios."""
    print("\n=== Testing Error Scenarios ===")
    
    cosmos_service = CosmosService()
    
    # Test 1: Get non-existent letter
    print("\n1. Testing retrieval of non-existent letter...")
    result = cosmos_service.get_letter("non-existent-id", "letter")
    if result is None:
        print("✓ Correctly returned None for non-existent letter")
    else:
        print("✗ Unexpected result for non-existent letter")
    
    # Test 2: Delete non-existent letter
    print("\n2. Testing deletion of non-existent letter...")
    result = cosmos_service.delete_letter("non-existent-id", "letter")
    if result is False:
        print("✓ Correctly returned False for non-existent letter deletion")
    else:
        print("✗ Unexpected result for non-existent letter deletion")
    
    print("\n=== Error scenario tests completed ===")


if __name__ == "__main__":
    print("Cosmos DB Manual Test Script")
    print("============================")
    
    # Check if credentials are configured
    if not os.getenv("COSMOS_ENDPOINT") or not os.getenv("COSMOS_KEY"):
        print("\n⚠️  Warning: Cosmos DB credentials not found in environment variables.")
        print("Please ensure COSMOS_ENDPOINT and COSMOS_KEY are set in your .env file.")
        sys.exit(1)
    
    print(f"\nEndpoint: {os.getenv('COSMOS_ENDPOINT')}")
    print(f"Database: {os.getenv('COSMOS_DATABASE_NAME', 'insurance_letters')}")
    print(f"Container: {os.getenv('COSMOS_CONTAINER_NAME', 'letters')}")
    
    # Run tests
    test_cosmos_connection()
    test_error_scenarios()