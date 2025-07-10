"""
Middleware package for Azure Functions
"""
from .auth import require_auth, get_user_id, get_user_email, get_user_name, AuthError

__all__ = ['require_auth', 'get_user_id', 'get_user_email', 'get_user_name', 'AuthError']