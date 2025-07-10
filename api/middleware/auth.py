"""
Azure AD authentication middleware for Azure Functions
"""
import os
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime
import jwt
import requests
from functools import wraps
import azure.functions as func
from jwt import PyJWKClient

logger = logging.getLogger(__name__)

class AuthError(Exception):
    """Authentication error exception"""
    def __init__(self, error: str, status_code: int = 401):
        self.error = error
        self.status_code = status_code
        super().__init__(self.error)

class AzureADAuth:
    """Azure AD authentication handler"""
    
    def __init__(self):
        self.tenant_id = os.environ.get('AZURE_AD_TENANT_ID', '')
        self.client_id = os.environ.get('AZURE_AD_CLIENT_ID', '')
        self.issuer = f'https://login.microsoftonline.com/{self.tenant_id}/v2.0'
        self.jwks_uri = f'{self.issuer}/.well-known/openid-configuration'
        self._jwks_client = None
        self._openid_config = None
        
        if not self.tenant_id or not self.client_id:
            logger.warning("Azure AD configuration not found. Authentication will be bypassed in development.")
    
    @property
    def jwks_client(self):
        """Lazy load JWKS client"""
        if self._jwks_client is None and self.tenant_id:
            # Get the JWKS URL from OpenID configuration
            openid_config = self.get_openid_config()
            if openid_config and 'jwks_uri' in openid_config:
                self._jwks_client = PyJWKClient(openid_config['jwks_uri'])
        return self._jwks_client
    
    def get_openid_config(self) -> Optional[Dict[str, Any]]:
        """Get OpenID configuration from Azure AD"""
        if self._openid_config is None and self.tenant_id:
            try:
                response = requests.get(self.jwks_uri)
                response.raise_for_status()
                self._openid_config = response.json()
            except Exception as e:
                logger.error(f"Failed to get OpenID configuration: {e}")
                return None
        return self._openid_config
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token from Azure AD
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            AuthError: If token validation fails
        """
        if not self.tenant_id or not self.client_id:
            # In development without Azure AD configured
            logger.warning("Azure AD not configured. Skipping authentication.")
            return {"sub": "dev-user", "name": "Development User", "oid": "dev-123"}
        
        try:
            # Get the signing key from Azure AD
            if not self.jwks_client:
                raise AuthError("Unable to fetch JWKS", 500)
            
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Decode and validate the token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=self.issuer,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "require": ["exp", "iat", "nbf", "iss", "aud"]
                }
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthError("Token has expired", 401)
        except jwt.InvalidTokenError as e:
            raise AuthError(f"Invalid token: {str(e)}", 401)
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise AuthError("Token validation failed", 401)
    
    def get_token_from_request(self, req: func.HttpRequest) -> Optional[str]:
        """
        Extract JWT token from request
        
        Args:
            req: Azure Functions HTTP request
            
        Returns:
            Token string or None
        """
        auth_header = req.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        return None

# Global auth instance
auth = AzureADAuth()

def require_auth(f):
    """
    Decorator to require authentication for Azure Functions
    
    Usage:
        @require_auth
        async def my_function(req: func.HttpRequest) -> func.HttpResponse:
            # Access user info from req.user
            user_id = req.user.get('oid')
            ...
    """
    @wraps(f)
    async def decorated_function(req: func.HttpRequest, *args, **kwargs) -> func.HttpResponse:
        try:
            # Extract token from request
            token = auth.get_token_from_request(req)
            
            if not token:
                return func.HttpResponse(
                    json.dumps({"error": "No authentication token provided"}),
                    status_code=401,
                    mimetype="application/json",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Validate token
            user_info = auth.validate_token(token)
            
            # Add user info to request object
            req.user = user_info
            
            # Call the original function
            if f.__name__.startswith('async_'):
                return await f(req, *args, **kwargs)
            else:
                return f(req, *args, **kwargs)
                
        except AuthError as e:
            return func.HttpResponse(
                json.dumps({"error": e.error}),
                status_code=e.status_code,
                mimetype="application/json",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Authentication failed"}),
                status_code=500,
                mimetype="application/json"
            )
    
    return decorated_function

def get_user_id(req: func.HttpRequest) -> Optional[str]:
    """
    Get user ID from authenticated request
    
    Args:
        req: Authenticated HTTP request with user info
        
    Returns:
        User ID (oid claim) or None
    """
    if hasattr(req, 'user') and isinstance(req.user, dict):
        return req.user.get('oid') or req.user.get('sub')
    return None

def get_user_email(req: func.HttpRequest) -> Optional[str]:
    """
    Get user email from authenticated request
    
    Args:
        req: Authenticated HTTP request with user info
        
    Returns:
        User email or None
    """
    if hasattr(req, 'user') and isinstance(req.user, dict):
        return req.user.get('preferred_username') or req.user.get('email')
    return None

def get_user_name(req: func.HttpRequest) -> Optional[str]:
    """
    Get user name from authenticated request
    
    Args:
        req: Authenticated HTTP request with user info
        
    Returns:
        User display name or None
    """
    if hasattr(req, 'user') and isinstance(req.user, dict):
        return req.user.get('name') or req.user.get('given_name')
    return None