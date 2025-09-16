import os
import hashlib
import hmac
from functools import wraps
from flask import request, jsonify

class APIKeyAuth:
    def __init__(self):
        # In production, these should be stored in a database
        # For now, we'll use environment variables
        self.valid_api_keys = self._load_api_keys()
    
    def _load_api_keys(self):
        """Load valid API keys from environment variables"""
        api_keys_env = os.environ.get('VALID_API_KEYS', '')
        if not api_keys_env:
            # No API keys configured - this will cause all requests to fail
            # This is intentional for security - you MUST configure VALID_API_KEYS
            raise ValueError(
                "CRITICAL SECURITY ERROR: No API keys configured! "
                "You must set the VALID_API_KEYS environment variable with valid API keys. "
                "Example: VALID_API_KEYS=your-secret-key-1,your-secret-key-2"
            )
        
        # Parse comma-separated API keys from environment
        api_keys = {}
        for key in api_keys_env.split(','):
            key = key.strip()
            if key:
                # Validate API key format for security
                if len(key) < 16:
                    raise ValueError(f"API key too short: {key[:8]}... (minimum 16 characters required)")
                api_keys[key] = {'name': 'Client', 'active': True}
        
        if not api_keys:
            raise ValueError("No valid API keys found in VALID_API_KEYS environment variable")
        
        return api_keys
    
    def is_valid_key(self, api_key):
        """Check if an API key is valid and active"""
        if not api_key:
            return False
        
        key_info = self.valid_api_keys.get(api_key)
        return key_info and key_info.get('active', False)
    
    def get_key_info(self, api_key):
        """Get information about an API key"""
        return self.valid_api_keys.get(api_key, {})

# Global instance
auth = APIKeyAuth()

def require_api_key(f):
    """Decorator to require valid API key for endpoint access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'API key required',
                'message': 'Please provide a valid API key in the X-API-Key header'
            }), 401
        
        if not auth.is_valid_key(api_key):
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid or inactive'
            }), 401
        
        # Add API key info to request context for use in the endpoint
        request.api_key_info = auth.get_key_info(api_key)
        
        return f(*args, **kwargs)
    
    return decorated_function

def generate_api_key(prefix='mk'):
    """Generate a new API key (utility function)"""
    import secrets
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}-{random_part}"