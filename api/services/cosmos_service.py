import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential

# Configure logging
logger = logging.getLogger(__name__)


class CosmosService:
    """Service for interacting with Azure Cosmos DB."""
    
    def __init__(self):
        """Initialize Cosmos DB client and database/container references."""
        self.endpoint = os.getenv("COSMOS_ENDPOINT", "")
        self.key = os.getenv("COSMOS_KEY", "")
        self.database_name = os.getenv("COSMOS_DATABASE_NAME", "insurance_letters")
        self.container_name = os.getenv("COSMOS_CONTAINER_NAME", "letters")
        
        self.client = None
        self.database = None
        self.container = None
        
        if self.endpoint and self.key:
            self._initialize_client()
        else:
            logger.warning("Cosmos DB credentials not configured")
    
    def _initialize_client(self):
        """Initialize Cosmos DB client and create database/container if needed."""
        try:
            # Create Cosmos client
            self.client = CosmosClient(self.endpoint, self.key)
            
            # Create database if it doesn't exist
            try:
                self.database = self.client.create_database(id=self.database_name)
                logger.info(f"Created database: {self.database_name}")
            except exceptions.CosmosResourceExistsError:
                self.database = self.client.get_database_client(self.database_name)
                logger.info(f"Using existing database: {self.database_name}")
            
            # Create container if it doesn't exist
            try:
                self.container = self.database.create_container(
                    id=self.container_name,
                    partition_key=PartitionKey(path="/type")
                    # Note: Don't specify offer_throughput for serverless accounts
                )
                logger.info(f"Created container: {self.container_name}")
            except exceptions.CosmosResourceExistsError:
                self.container = self.database.get_container_client(self.container_name)
                logger.info(f"Using existing container: {self.container_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB: {str(e)}")
            raise
    
    def health_check(self) -> bool:
        """Check if Cosmos DB connection is healthy."""
        if not self.client:
            raise Exception("Cosmos DB client not initialized")
        
        try:
            # Try to read database properties
            if self.database:
                self.database.read()
            return True
        except Exception as e:
            logger.error(f"Cosmos DB health check failed: {str(e)}")
            raise
    
    def save_letter(self, letter_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Save a generated letter to Cosmos DB."""
        if not self.container:
            logger.error("Cosmos DB container not initialized")
            return letter_doc
        
        try:
            # Ensure required fields
            if "id" not in letter_doc:
                letter_doc["id"] = str(uuid.uuid4())
            
            if "type" not in letter_doc:
                letter_doc["type"] = "letter"
            
            if "created_at" not in letter_doc:
                letter_doc["created_at"] = datetime.now().isoformat()
            
            # Create the document
            created_doc = self.container.create_item(body=letter_doc)
            logger.info(f"Saved letter to Cosmos DB: {created_doc['id']}")
            
            return created_doc
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to save letter: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving letter: {str(e)}")
            raise
    
    def get_letter(self, letter_id: str, partition_key: str = "letter") -> Optional[Dict[str, Any]]:
        """Retrieve a letter by ID."""
        if not self.container:
            logger.error("Cosmos DB container not initialized")
            return None
        
        try:
            letter = self.container.read_item(
                item=letter_id,
                partition_key=partition_key
            )
            return letter
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Letter not found: {letter_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving letter: {str(e)}")
            raise
    
    def get_letters_by_customer(self, customer_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get letters for a specific customer."""
        if not self.container:
            logger.error("Cosmos DB container not initialized")
            return []
        
        try:
            query = """
                SELECT * FROM c 
                WHERE c.type = 'letter' 
                AND c.customer_name = @customer_name 
                ORDER BY c.created_at DESC
                OFFSET 0 LIMIT @limit
            """
            
            parameters = [
                {"name": "@customer_name", "value": customer_name},
                {"name": "@limit", "value": limit}
            ]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            return items
            
        except Exception as e:
            logger.error(f"Error querying letters: {str(e)}")
            return []
    
    def get_letters_by_type(self, letter_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get letters of a specific type."""
        if not self.container:
            logger.error("Cosmos DB container not initialized")
            return []
        
        try:
            query = """
                SELECT * FROM c 
                WHERE c.type = 'letter' 
                AND c.letter_type = @letter_type 
                ORDER BY c.created_at DESC
                OFFSET 0 LIMIT @limit
            """
            
            parameters = [
                {"name": "@letter_type", "value": letter_type},
                {"name": "@limit", "value": limit}
            ]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            return items
            
        except Exception as e:
            logger.error(f"Error querying letters by type: {str(e)}")
            return []
    
    def get_recent_letters(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most recent letters."""
        if not self.container:
            logger.error("Cosmos DB container not initialized")
            return []
        
        try:
            query = """
                SELECT * FROM c 
                WHERE c.type = 'letter' 
                ORDER BY c.created_at DESC
                OFFSET 0 LIMIT @limit
            """
            
            parameters = [
                {"name": "@limit", "value": limit}
            ]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            return items
            
        except Exception as e:
            logger.error(f"Error querying recent letters: {str(e)}")
            return []
    
    def update_letter_status(self, letter_id: str, status: str, partition_key: str = "letter") -> Optional[Dict[str, Any]]:
        """Update the status of a letter."""
        if not self.container:
            logger.error("Cosmos DB container not initialized")
            return None
        
        try:
            # Read the existing document
            letter = self.container.read_item(
                item=letter_id,
                partition_key=partition_key
            )
            
            # Update status
            letter["compliance_status"] = status
            letter["updated_at"] = datetime.now().isoformat()
            
            # Replace the document
            updated_letter = self.container.replace_item(
                item=letter_id,
                body=letter
            )
            
            logger.info(f"Updated letter status: {letter_id} -> {status}")
            return updated_letter
            
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Letter not found for update: {letter_id}")
            return None
        except Exception as e:
            logger.error(f"Error updating letter: {str(e)}")
            raise
    
    def delete_letter(self, letter_id: str, partition_key: str = "letter") -> bool:
        """Delete a letter (soft delete by marking as deleted)."""
        if not self.container:
            logger.error("Cosmos DB container not initialized")
            return False
        
        try:
            # Read the existing document
            letter = self.container.read_item(
                item=letter_id,
                partition_key=partition_key
            )
            
            # Mark as deleted (soft delete)
            letter["deleted"] = True
            letter["deleted_at"] = datetime.now().isoformat()
            
            # Replace the document
            self.container.replace_item(
                item=letter_id,
                body=letter
            )
            
            logger.info(f"Soft deleted letter: {letter_id}")
            return True
            
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Letter not found for deletion: {letter_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting letter: {str(e)}")
            return False
