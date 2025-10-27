"""
Utility Functions
Helper functions for the Google Assistant AI service
"""

import logging
from typing import Dict, Any, Optional
from functools import wraps
import time

logger = logging.getLogger(__name__)


def log_execution_time(func):
    """Decorator to log function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.debug(
            f"{func.__name__} executed in {execution_time:.4f}s"
        )
        return result
    return wrapper


def sanitize_session_id(session_id: str) -> str:
    """
    Sanitize session ID for logging
    
    Args:
        session_id: Raw session ID
        
    Returns:
        Sanitized session ID (first 20 chars + ...)
    """
    if not session_id:
        return "unknown"
    return session_id[:20] + "..." if len(session_id) > 20 else session_id


def extract_intent_name(request_data: Dict[str, Any]) -> str:
    """
    Extract intent name from Google Assistant request
    
    Args:
        request_data: Request JSON from Google
        
    Returns:
        Intent display name or 'unknown'
    """
    try:
        return request_data.get('queryResult', {}).get('intent', {}).get('displayName', 'unknown')
    except Exception:
        return 'unknown'


def extract_query_text(request_data: Dict[str, Any]) -> str:
    """
    Extract user's query text from request
    
    Args:
        request_data: Request JSON from Google
        
    Returns:
        Query text or empty string
    """
    try:
        return request_data.get('queryResult', {}).get('queryText', '')
    except Exception:
        return ''


def validate_google_request(request_data: Dict[str, Any]) -> bool:
    """
    Validate that request has required Google Assistant fields
    
    Args:
        request_data: Request JSON
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['session', 'queryResult']
    
    for field in required_fields:
        if field not in request_data:
            logger.warning(f"Missing required field: {field}")
            return False
    
    return True


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    # Truncate at word boundary
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + '...'

