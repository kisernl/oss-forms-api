import time
from typing import Dict, Tuple, Optional
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self):
        # Store request timestamps for each client (IP + API key combination)
        self.requests = defaultdict(deque)
        
        # Rate limiting configuration
        self.limits = {
            'per_minute': 10,    # 10 requests per minute per IP
            'per_hour': 100,     # 100 requests per hour per IP
            'per_day': 1000      # 1000 requests per day per IP
        }
        
        # Time windows in seconds
        self.windows = {
            'per_minute': 60,
            'per_hour': 3600,
            'per_day': 86400
        }
    
    def is_allowed(self, client_ip: str, api_key: Optional[str] = None) -> bool:
        """Check if a request is allowed based on rate limits"""
        if not client_ip:
            return False
        
        # Create a unique identifier combining IP and API key
        client_id = f"{client_ip}:{api_key}" if api_key else client_ip
        
        current_time = time.time()
        
        # Clean old requests and check limits
        return self._check_and_update_limits(client_id, current_time)
    
    def _check_and_update_limits(self, client_id: str, current_time: float) -> bool:
        """Check rate limits and update request log"""
        client_requests = self.requests[client_id]
        
        # Check each time window
        for limit_type, limit_count in self.limits.items():
            window_seconds = self.windows[limit_type]
            cutoff_time = current_time - window_seconds
            
            # Remove old requests outside the time window
            while client_requests and client_requests[0] < cutoff_time:
                client_requests.popleft()
            
            # Check if we've exceeded the limit
            if len(client_requests) >= limit_count:
                return False
        
        # If all limits are okay, record this request
        client_requests.append(current_time)
        
        # Keep memory usage reasonable by limiting stored requests
        max_stored_requests = max(self.limits.values())
        while len(client_requests) > max_stored_requests:
            client_requests.popleft()
        
        return True
    
    def get_remaining_requests(self, client_ip: str, api_key: Optional[str] = None) -> Dict[str, int]:
        """Get remaining requests for each time window"""
        if not client_ip:
            return {}
        
        client_id = f"{client_ip}:{api_key}" if api_key else client_ip
        current_time = time.time()
        client_requests = self.requests[client_id]
        
        remaining = {}
        
        for limit_type, limit_count in self.limits.items():
            window_seconds = self.windows[limit_type]
            cutoff_time = current_time - window_seconds
            
            # Count requests in this time window
            recent_requests = sum(1 for req_time in client_requests if req_time >= cutoff_time)
            remaining[limit_type] = max(0, limit_count - recent_requests)
        
        return remaining
    
    def get_reset_times(self, client_ip: str, api_key: Optional[str] = None) -> Dict[str, float]:
        """Get reset times for each rate limit window"""
        if not client_ip:
            return {}
        
        client_id = f"{client_ip}:{api_key}" if api_key else client_ip
        current_time = time.time()
        client_requests = self.requests[client_id]
        
        reset_times = {}
        
        for limit_type, window_seconds in self.windows.items():
            if client_requests:
                # Find the oldest request in this window
                cutoff_time = current_time - window_seconds
                oldest_in_window = None
                
                for req_time in client_requests:
                    if req_time >= cutoff_time:
                        oldest_in_window = req_time
                        break
                
                if oldest_in_window:
                    reset_times[limit_type] = oldest_in_window + window_seconds
                else:
                    reset_times[limit_type] = current_time
            else:
                reset_times[limit_type] = current_time
        
        return reset_times
    
    def cleanup_old_entries(self, max_age_hours: int = 24):
        """Clean up old entries to prevent memory leaks"""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        clients_to_remove = []
        
        for client_id, requests in self.requests.items():
            # Remove old requests
            while requests and requests[0] < cutoff_time:
                requests.popleft()
            
            # Remove client if no recent requests
            if not requests:
                clients_to_remove.append(client_id)
        
        for client_id in clients_to_remove:
            del self.requests[client_id]