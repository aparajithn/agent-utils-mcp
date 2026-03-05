"""Rate limiting middleware for free tier tracking."""
import time
from collections import defaultdict
from typing import Dict
from fastapi import Request, HTTPException


class RateLimiter:
    """Simple in-memory rate limiter with TTL."""
    
    def __init__(self, free_limit: int = 100, ttl_seconds: int = 86400):
        """
        Initialize rate limiter.
        
        Args:
            free_limit: Number of free requests per IP
            ttl_seconds: Time to live for rate limit counters (default 24h)
        """
        self.free_limit = free_limit
        self.ttl_seconds = ttl_seconds
        self.counters: Dict[str, Dict] = defaultdict(lambda: {"count": 0, "reset_at": 0})
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check X-Forwarded-For header (from proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        return request.client.host if request.client else "unknown"
    
    def check_limit(self, request: Request) -> tuple[bool, int, int]:
        """
        Check if request is within free tier limit.
        
        Returns:
            (allowed, remaining, reset_at)
        """
        ip = self.get_client_ip(request)
        now = time.time()
        
        # Get or initialize counter
        counter = self.counters[ip]
        
        # Reset if TTL expired
        if counter["reset_at"] < now:
            counter["count"] = 0
            counter["reset_at"] = now + self.ttl_seconds
        
        # Check limit
        if counter["count"] >= self.free_limit:
            return False, 0, int(counter["reset_at"])
        
        # Increment counter
        counter["count"] += 1
        remaining = self.free_limit - counter["count"]
        
        return True, remaining, int(counter["reset_at"])
    
    def cleanup_expired(self):
        """Remove expired counters (should be called periodically)."""
        now = time.time()
        expired = [ip for ip, counter in self.counters.items() if counter["reset_at"] < now]
        for ip in expired:
            del self.counters[ip]
