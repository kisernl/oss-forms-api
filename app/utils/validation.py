import re
from typing import Dict, Any, List

def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email or not isinstance(email, str):
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def validate_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate form submission data"""
    if not isinstance(form_data, dict):
        return {
            'valid': False,
            'message': 'Form data must be a JSON object'
        }
    
    # Required fields
    required_fields = ['to_email', 'fields']
    missing_fields = []
    
    for field in required_fields:
        if field not in form_data or not form_data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        return {
            'valid': False,
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }
    
    # Validate to_email
    to_email = form_data.get('to_email')
    if not validate_email(str(to_email) if to_email else ''):
        return {
            'valid': False,
            'message': 'Invalid to_email format'
        }
    
    # Validate from_email if provided
    from_email = form_data.get('from_email')
    if from_email and not validate_email(str(from_email)):
        return {
            'valid': False,
            'message': 'Invalid from_email format'
        }
    
    # Validate fields
    fields = form_data.get('fields')
    if not isinstance(fields, dict):
        return {
            'valid': False,
            'message': 'Fields must be a JSON object'
        }
    
    if not fields:
        return {
            'valid': False,
            'message': 'At least one form field is required'
        }
    
    # Validate field content
    for field_name, field_value in fields.items():
        if not isinstance(field_name, str):
            return {
                'valid': False,
                'message': 'Field names must be strings'
            }
        
        # Check for potentially dangerous content
        if _contains_suspicious_content(str(field_value)):
            return {
                'valid': False,
                'message': f'Suspicious content detected in field: {field_name}'
            }
    
    # Validate subject if provided
    subject = form_data.get('subject', '')
    if subject and len(subject) > 200:
        return {
            'valid': False,
            'message': 'Subject line too long (max 200 characters)'
        }
    
    # Validate source_url if provided
    source_url = form_data.get('source_url')
    if source_url and not _validate_url(source_url):
        return {
            'valid': False,
            'message': 'Invalid source_url format'
        }
    
    return {
        'valid': True,
        'message': 'Validation passed'
    }

def _contains_suspicious_content(content: str) -> bool:
    """Check for potentially malicious content"""
    if not isinstance(content, str):
        return False
    
    # Check for common injection patterns
    suspicious_patterns = [
        r'<script[^>]*>',
        r'javascript:',
        r'on\w+\s*=',
        r'eval\s*\(',
        r'document\.',
        r'window\.',
        r'<iframe',
        r'<object',
        r'<embed'
    ]
    
    content_lower = content.lower()
    
    for pattern in suspicious_patterns:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return True
    
    return False

def _validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url or not isinstance(url, str):
        return False
    
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(url_pattern, url) is not None

def sanitize_field_value(value: Any) -> str:
    """Sanitize field value for safe email inclusion"""
    if value is None:
        return ''
    
    # Convert to string and limit length
    str_value = str(value)[:1000]  # Limit to 1000 characters
    
    # Remove potentially dangerous HTML tags
    str_value = re.sub(r'<[^>]+>', '', str_value)
    
    # Remove null bytes and control characters
    str_value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', str_value)
    
    return str_value.strip()