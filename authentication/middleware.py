"""
Security middleware for authentication
"""
from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings
from .utils import get_client_ip
import time


class RateLimitMiddleware:
    """
    Rate limiting middleware to prevent brute force attacks
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rate limiting settings
        self.rate_limits = {
            'login': {'requests': 5, 'window': 300},  # 5 requests per 5 minutes
            'register': {'requests': 3, 'window': 600},  # 3 requests per 10 minutes
            'password_reset': {'requests': 3, 'window': 600},  # 3 requests per 10 minutes
        }

    def __call__(self, request):
        # Check rate limits for specific endpoints
        if self.should_rate_limit(request):
            if self.is_rate_limited(request):
                response = HttpResponse(
                    "Too many requests. Please try again later.",
                    status=429
                )
                response['Retry-After'] = '300'  # 5 minutes
                return response
        
        response = self.get_response(request)
        return response

    def should_rate_limit(self, request):
        """Check if this request should be rate limited"""
        path = request.path.lower()
        method = request.method
        
        # Only rate limit POST requests to auth endpoints
        if method != 'POST':
            return False
            
        rate_limited_paths = [
            '/auth/login/',
            '/auth/register/',
            '/auth/forgot-password/',
        ]
        
        return any(path.startswith(rl_path) for rl_path in rate_limited_paths)

    def is_rate_limited(self, request):
        """Check if the client has exceeded rate limits"""
        ip_address = get_client_ip(request)
        path = request.path.lower()
        
        # Determine rate limit type
        if '/login/' in path:
            limit_type = 'login'
        elif '/register/' in path:
            limit_type = 'register'
        elif '/forgot-password/' in path:
            limit_type = 'password_reset'
        else:
            return False
        
        # Get rate limit settings
        limit_config = self.rate_limits.get(limit_type)
        if not limit_config:
            return False
        
        # Create cache key
        cache_key = f"rate_limit:{limit_type}:{ip_address}"
        
        # Get current request count
        current_requests = cache.get(cache_key, [])
        now = time.time()
        
        # Remove old requests outside the window
        window_start = now - limit_config['window']
        current_requests = [req_time for req_time in current_requests if req_time > window_start]
        
        # Check if limit exceeded
        if len(current_requests) >= limit_config['requests']:
            return True
        
        # Add current request
        current_requests.append(now)
        cache.set(cache_key, current_requests, limit_config['window'])
        
        return False


class SecurityHeadersMiddleware:
    """
    Add security headers to responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add CSP header for auth pages
        if request.path.startswith('/auth/'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self';"
            )
        
        return response
