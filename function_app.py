import azure.functions as func
import logging
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import asyncio

# Load environment variables locally
load_dotenv(override=True)

# Import our services (to be created)
from services.agent_system import (
    generate_letter_with_approval_workflow,
    suggest_letter_type,
    validate_letter_content
)
from services.cosmos_service import CosmosService
from services.models import LetterRequest, CustomerInfo, LetterType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Functions App with v2 model
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Initialize Cosmos DB service
cosmos_service = CosmosService()

@app.route(route="health")
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint to verify the service is running."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Insurance Letter Drafting API",
            "version": "1.0.0",
            "endpoints": [
                "/api/health",
                "/api/draft-letter",
                "/api/suggest-letter-type",
                "/api/validate-letter"
            ]
        }
        
        # Check Cosmos DB connection
        try:
            cosmos_service.health_check()
            health_status["cosmos_db"] = "connected"
        except Exception as e:
            health_status["cosmos_db"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        return func.HttpResponse(
            json.dumps(health_status, indent=2),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "unhealthy", "error": str(e)}),
            status_code=503,
            mimetype="application/json"
        )

@app.route(route="draft-letter", methods=["POST"])
async def draft_letter(req: func.HttpRequest) -> func.HttpResponse:
    """Generate an insurance letter using multi-agent review workflow."""
    try:
        # Parse request body
        req_body = req.get_json()
        
        # Validate required fields
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Extract customer info
        customer_info = req_body.get("customer_info", {})
        if not customer_info.get("name") or not customer_info.get("policy_number"):
            return func.HttpResponse(
                json.dumps({"error": "Customer name and policy number are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Extract letter details
        letter_type = req_body.get("letter_type", "general")
        user_prompt = req_body.get("user_prompt", "")
        
        if not user_prompt:
            return func.HttpResponse(
                json.dumps({"error": "User prompt is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate letter type
        try:
            letter_type_enum = LetterType(letter_type)
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": f"Invalid letter type: {letter_type}"}),
                status_code=400,
                mimetype="application/json"
            )
        
        logger.info(f"Generating {letter_type} letter for {customer_info.get('name')}")
        
        # Run async letter generation
        result = await generate_letter_with_approval_workflow(
            customer_info=customer_info,
            letter_type=letter_type,
            user_prompt=user_prompt
        )
        
        # Store letter in Cosmos DB
        try:
            letter_doc = {
                "id": f"letter_{datetime.now().timestamp()}",
                "type": "letter",
                "customer_name": customer_info.get("name"),
                "policy_number": customer_info.get("policy_number"),
                "letter_type": letter_type,
                "content": result.get("letter_content", ""),
                "compliance_status": "approved" if result.get("approval_status", {}).get("overall_approved") else "needs_review",
                "created_at": datetime.now().isoformat(),
                "user_prompt": user_prompt,
                "approval_details": result.get("approval_status", {}),
                "total_rounds": result.get("total_rounds", 0)
            }
            
            cosmos_service.save_letter(letter_doc)
            result["document_id"] = letter_doc["id"]
        except Exception as e:
            logger.error(f"Failed to save letter to Cosmos DB: {str(e)}")
            result["storage_error"] = str(e)
        
        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error generating letter: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="suggest-letter-type", methods=["POST"])
async def suggest_letter_type_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """AI-powered letter type suggestion based on user description."""
    try:
        req_body = req.get_json()
        
        if not req_body or not req_body.get("prompt"):
            return func.HttpResponse(
                json.dumps({"error": "Prompt is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        user_prompt = req_body.get("prompt")
        logger.info(f"Suggesting letter type for prompt: {user_prompt[:50]}...")
        
        # Run async suggestion
        suggestion = await suggest_letter_type(user_prompt)
        
        return func.HttpResponse(
            json.dumps(suggestion, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error suggesting letter type: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="validate-letter", methods=["POST"])
async def validate_letter_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Validate an existing letter for compliance."""
    try:
        req_body = req.get_json()
        
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        letter_content = req_body.get("letter_content", "")
        letter_type = req_body.get("letter_type", "general")
        
        if not letter_content:
            return func.HttpResponse(
                json.dumps({"error": "Letter content is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        logger.info(f"Validating {letter_type} letter")
        
        # Run async validation
        validation_result = await validate_letter_content(letter_content, letter_type)
        
        return func.HttpResponse(
            json.dumps(validation_result, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error validating letter: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )