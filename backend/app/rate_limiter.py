"""
Simple in-memory rate limiter for API endpoints.
For production, consider using Redis-based rate limiting.
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from threading import Lock


class RateLimiter:
    """
    Simple token bucket rate limiter.
    Thread-safe for basic use cases.
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Args:
            max_requests: Maximum requests allowed in the time window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, identifier: str) -> Tuple[bool, int]:
        """
        Check if a request is allowed.
        
        Args:
            identifier: Unique identifier (e.g., IP address, user ID)
        
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        current_time = time.time()
        
        with self.lock:
            # Clean old requests outside the window
            window_start = current_time - self.window_seconds
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
            
            # Check if limit exceeded
            if len(self.requests[identifier]) >= self.max_requests:
                remaining = 0
                return False, remaining
            
            # Add current request
            self.requests[identifier].append(current_time)
            remaining = self.max_requests - len(self.requests[identifier])
            
            return True, remaining
    
    def reset(self, identifier: str = None):
        """Reset rate limit for an identifier or all identifiers."""
        with self.lock:
            if identifier:
                self.requests.pop(identifier, None)
            else:
                self.requests.clear()


# Global rate limiters for different endpoints
detect_limiter = RateLimiter(max_requests=30, window_seconds=60)  # 30 requests per minute
logs_limiter = RateLimiter(max_requests=100, window_seconds=60)  # 100 requests per minute
images_limiter = RateLimiter(max_requests=200, window_seconds=60)  # 200 requests per minute


def get_client_identifier(request) -> str:
    """
    Get a unique identifier for rate limiting.
    Uses IP address by default.
    """
    # Try to get real IP (behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.remote_addr or "unknown"

