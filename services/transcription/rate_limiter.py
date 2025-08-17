#!/usr/bin/env python3
"""
Rate Limiter and Retry Logic for YouTube Access
Implements intelligent rate limiting and retry mechanisms to avoid bot detection
"""

import time
import asyncio
import random
import logging
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass
from functools import wraps
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    max_requests_per_minute: int = 10
    max_requests_per_hour: int = 60
    min_interval_seconds: float = 2.0
    max_interval_seconds: float = 10.0
    burst_limit: int = 3
    cooldown_after_error: float = 30.0

@dataclass
class RetryConfig:
    """Retry configuration"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    backoff_multiplier: float = 1.5

class RateLimiter:
    """Thread-safe rate limiter with multiple time windows"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._requests_history: list = []
        self._last_request_time: float = 0
        self._error_count: int = 0
        self._last_error_time: float = 0
        self._lock = threading.Lock()
    
    def can_make_request(self) -> bool:
        """Check if a request can be made now"""
        with self._lock:
            current_time = time.time()
            
            # Check cooldown after errors
            if self._error_count > 0 and (current_time - self._last_error_time) < self.config.cooldown_after_error:
                return False
            
            # Clean old requests from history
            cutoff_time = current_time - 3600  # Keep 1 hour of history
            self._requests_history = [t for t in self._requests_history if t > cutoff_time]
            
            # Check hourly limit
            if len(self._requests_history) >= self.config.max_requests_per_hour:
                return False
            
            # Check minute limit
            minute_cutoff = current_time - 60
            recent_requests = [t for t in self._requests_history if t > minute_cutoff]
            if len(recent_requests) >= self.config.max_requests_per_minute:
                return False
            
            # Check minimum interval
            if (current_time - self._last_request_time) < self.config.min_interval_seconds:
                return False
            
            return True
    
    def wait_time(self) -> float:
        """Calculate how long to wait before next request"""
        with self._lock:
            current_time = time.time()
            
            # Wait for cooldown after errors
            if self._error_count > 0:
                cooldown_remaining = self.config.cooldown_after_error - (current_time - self._last_error_time)
                if cooldown_remaining > 0:
                    return cooldown_remaining
            
            # Wait for minimum interval
            interval_remaining = self.config.min_interval_seconds - (current_time - self._last_request_time)
            if interval_remaining > 0:
                return interval_remaining
            
            # Check if we need to wait for minute/hour limits
            minute_cutoff = current_time - 60
            recent_requests = [t for t in self._requests_history if t > minute_cutoff]
            
            if len(recent_requests) >= self.config.max_requests_per_minute:
                # Wait until oldest request in the minute is older than 60 seconds
                oldest_in_minute = min(recent_requests)
                return 60 - (current_time - oldest_in_minute)
            
            return 0
    
    async def wait_if_needed(self):
        """Async wait if rate limiting is needed"""
        wait_seconds = self.wait_time()
        if wait_seconds > 0:
            # Add some jitter to avoid thundering herd
            jitter = random.uniform(0, min(wait_seconds * 0.1, 2.0))
            total_wait = wait_seconds + jitter
            logger.info(f"Rate limiting: waiting {total_wait:.2f} seconds")
            await asyncio.sleep(total_wait)
    
    def wait_if_needed_sync(self):
        """Synchronous wait if rate limiting is needed"""
        wait_seconds = self.wait_time()
        if wait_seconds > 0:
            # Add some jitter
            jitter = random.uniform(0, min(wait_seconds * 0.1, 2.0))
            total_wait = wait_seconds + jitter
            logger.info(f"Rate limiting: waiting {total_wait:.2f} seconds")
            time.sleep(total_wait)
    
    def record_request(self):
        """Record a successful request"""
        with self._lock:
            current_time = time.time()
            self._requests_history.append(current_time)
            self._last_request_time = current_time
            # Reset error count on successful request
            if self._error_count > 0:
                logger.info("Request successful - resetting error count")
                self._error_count = 0
    
    def record_error(self):
        """Record a failed request"""
        with self._lock:
            current_time = time.time()
            self._error_count += 1
            self._last_error_time = current_time
            logger.warning(f"Request failed - error count: {self._error_count}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        with self._lock:
            current_time = time.time()
            
            # Count recent requests
            minute_requests = len([t for t in self._requests_history if t > current_time - 60])
            hour_requests = len([t for t in self._requests_history if t > current_time - 3600])
            
            return {
                "requests_last_minute": minute_requests,
                "requests_last_hour": hour_requests,
                "max_per_minute": self.config.max_requests_per_minute,
                "max_per_hour": self.config.max_requests_per_hour,
                "error_count": self._error_count,
                "last_error_time": self._last_error_time,
                "can_make_request": self.can_make_request(),
                "wait_time": self.wait_time()
            }

class RetryHandler:
    """Intelligent retry handler with exponential backoff"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        if attempt <= 0:
            return 0
        
        # Exponential backoff
        delay = self.config.base_delay * (self.config.exponential_base ** (attempt - 1))
        delay = min(delay, self.config.max_delay)
        
        # Apply backoff multiplier
        delay *= self.config.backoff_multiplier
        
        # Add jitter if enabled
        if self.config.jitter:
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter
        
        return delay
    
    async def retry_async(self, func: Callable, *args, **kwargs) -> Any:
        """Async retry wrapper"""
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                if attempt > 1:
                    delay = self.calculate_delay(attempt - 1)
                    logger.info(f"Retry attempt {attempt}/{self.config.max_attempts} after {delay:.2f}s delay")
                    await asyncio.sleep(delay)
                
                return await func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} failed: {e}")
                
                if attempt == self.config.max_attempts:
                    logger.error(f"All {self.config.max_attempts} attempts failed")
                    break
        
        raise last_exception
    
    def retry_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Synchronous retry wrapper"""
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                if attempt > 1:
                    delay = self.calculate_delay(attempt - 1)
                    logger.info(f"Retry attempt {attempt}/{self.config.max_attempts} after {delay:.2f}s delay")
                    time.sleep(delay)
                
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} failed: {e}")
                
                if attempt == self.config.max_attempts:
                    logger.error(f"All {self.config.max_attempts} attempts failed")
                    break
        
        raise last_exception

class RateLimitedRetryHandler:
    """Combined rate limiting and retry handler"""
    
    def __init__(self, 
                 rate_config: Optional[RateLimitConfig] = None,
                 retry_config: Optional[RetryConfig] = None):
        self.rate_limiter = RateLimiter(rate_config or RateLimitConfig())
        self.retry_handler = RetryHandler(retry_config or RetryConfig())
    
    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with rate limiting and retry"""
        
        async def rate_limited_func(*args, **kwargs):
            await self.rate_limiter.wait_if_needed()
            
            try:
                result = await func(*args, **kwargs)
                self.rate_limiter.record_request()
                return result
            except Exception as e:
                self.rate_limiter.record_error()
                raise
        
        return await self.retry_handler.retry_async(rate_limited_func, *args, **kwargs)
    
    def execute_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with rate limiting and retry (synchronous)"""
        
        def rate_limited_func(*args, **kwargs):
            self.rate_limiter.wait_if_needed_sync()
            
            try:
                result = func(*args, **kwargs)
                self.rate_limiter.record_request()
                return result
            except Exception as e:
                self.rate_limiter.record_error()
                raise
        
        return self.retry_handler.retry_sync(rate_limited_func, *args, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get combined statistics"""
        return {
            "rate_limiter": self.rate_limiter.get_stats(),
            "retry_config": {
                "max_attempts": self.retry_handler.config.max_attempts,
                "base_delay": self.retry_handler.config.base_delay,
                "max_delay": self.retry_handler.config.max_delay
            }
        }

# Decorators for easy use
def rate_limited_retry(rate_config: Optional[RateLimitConfig] = None,
                      retry_config: Optional[RetryConfig] = None):
    """Decorator for automatic rate limiting and retry"""
    handler = RateLimitedRetryHandler(rate_config, retry_config)
    
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await handler.execute_async(func, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return handler.execute_sync(func, *args, **kwargs)
            return sync_wrapper
    
    return decorator

# Global handler instance for YouTube operations
youtube_rate_limiter = RateLimitedRetryHandler(
    rate_config=RateLimitConfig(
        max_requests_per_minute=8,
        max_requests_per_hour=50,
        min_interval_seconds=3.0,
        cooldown_after_error=60.0
    ),
    retry_config=RetryConfig(
        max_attempts=3,
        base_delay=2.0,
        max_delay=120.0
    )
)

if __name__ == "__main__":
    # Test the rate limiter
    import sys
    
    async def test_async():
        print("Testing async rate limiter...")
        
        async def mock_request(request_id: int):
            print(f"Making request {request_id}")
            if request_id % 4 == 0:  # Simulate failures
                raise Exception(f"Mock error for request {request_id}")
            return f"Success {request_id}"
        
        handler = RateLimitedRetryHandler()
        
        # Make several requests
        for i in range(10):
            try:
                result = await handler.execute_async(mock_request, i)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Final failure: {e}")
            
            # Show stats periodically
            if i % 3 == 0:
                stats = handler.get_stats()
                print(f"Stats: {stats['rate_limiter']['requests_last_minute']} requests/min")
    
    def test_sync():
        print("Testing sync rate limiter...")
        
        def mock_request(request_id: int):
            print(f"Making request {request_id}")
            if request_id % 4 == 0:  # Simulate failures
                raise Exception(f"Mock error for request {request_id}")
            return f"Success {request_id}"
        
        handler = RateLimitedRetryHandler()
        
        for i in range(5):
            try:
                result = handler.execute_sync(mock_request, i)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Final failure: {e}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "async":
        asyncio.run(test_async())
    else:
        test_sync()