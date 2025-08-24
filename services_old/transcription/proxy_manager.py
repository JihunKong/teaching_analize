#!/usr/bin/env python3
"""
Proxy Manager for YouTube Access
Handles rotating proxies to bypass bot detection
"""

import os
import random
import logging
import time
import requests
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from urllib.parse import urlparse
import json

logger = logging.getLogger(__name__)

@dataclass
class ProxyConfig:
    """Proxy configuration"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"
    
    def to_url(self) -> str:
        """Convert to proxy URL format"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        else:
            return f"{self.protocol}://{self.host}:{self.port}"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to requests-compatible proxy dict"""
        proxy_url = self.to_url()
        return {
            "http": proxy_url,
            "https": proxy_url
        }

class ProxyManager:
    """Manage proxy rotation for YouTube access"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), "proxy_config.json")
        self.proxies: List[ProxyConfig] = []
        self.current_proxy_index = 0
        self.last_rotation_time = 0
        self.rotation_interval = 300  # Rotate every 5 minutes
        self.proxy_stats = {}  # Track success rates
        
        # Load proxy configuration
        self._load_proxies()
        
    def _load_proxies(self):
        """Load proxy configuration from environment and config file"""
        
        # Load from environment variables (Webshare format)
        webshare_username = os.getenv("WEBSHARE_PROXY_USERNAME")
        webshare_password = os.getenv("WEBSHARE_PROXY_PASSWORD")
        webshare_endpoint = os.getenv("WEBSHARE_PROXY_ENDPOINT")
        
        if all([webshare_username, webshare_password, webshare_endpoint]):
            # Parse Webshare endpoint (format: hostname:port)
            if ":" in webshare_endpoint:
                host, port = webshare_endpoint.split(":", 1)
                proxy = ProxyConfig(
                    host=host,
                    port=int(port),
                    username=webshare_username,
                    password=webshare_password,
                    protocol="http"
                )
                self.proxies.append(proxy)
                logger.info(f"Loaded Webshare proxy: {host}:{port}")
        
        # Load from generic HTTP proxy environment
        http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
        if http_proxy:
            proxy = self._parse_proxy_url(http_proxy)
            if proxy:
                self.proxies.append(proxy)
                logger.info(f"Loaded HTTP proxy: {proxy.host}:{proxy.port}")
        
        # Load from config file
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                for proxy_config in config.get("proxies", []):
                    proxy = ProxyConfig(**proxy_config)
                    self.proxies.append(proxy)
                    logger.info(f"Loaded proxy from config: {proxy.host}:{proxy.port}")
                    
            except Exception as e:
                logger.error(f"Error loading proxy config file: {e}")
        
        if not self.proxies:
            logger.warning("No proxies configured")
        else:
            logger.info(f"Total proxies loaded: {len(self.proxies)}")
            
        # Initialize stats
        for i, proxy in enumerate(self.proxies):
            self.proxy_stats[i] = {
                "success_count": 0,
                "error_count": 0,
                "last_used": 0
            }
    
    def _parse_proxy_url(self, proxy_url: str) -> Optional[ProxyConfig]:
        """Parse proxy URL into ProxyConfig"""
        try:
            parsed = urlparse(proxy_url)
            return ProxyConfig(
                host=parsed.hostname,
                port=parsed.port or 8080,
                username=parsed.username,
                password=parsed.password,
                protocol=parsed.scheme or "http"
            )
        except Exception as e:
            logger.error(f"Error parsing proxy URL {proxy_url}: {e}")
            return None
    
    def has_proxies(self) -> bool:
        """Check if any proxies are configured"""
        return len(self.proxies) > 0
    
    def get_current_proxy(self) -> Optional[ProxyConfig]:
        """Get current proxy"""
        if not self.proxies:
            return None
        
        # Auto-rotate if interval has passed
        current_time = time.time()
        if current_time - self.last_rotation_time > self.rotation_interval:
            self.rotate_proxy()
        
        return self.proxies[self.current_proxy_index]
    
    def rotate_proxy(self):
        """Rotate to next proxy"""
        if len(self.proxies) <= 1:
            return
        
        # Find best proxy based on success rate
        best_proxy_index = self._find_best_proxy()
        
        if best_proxy_index != self.current_proxy_index:
            old_proxy = self.proxies[self.current_proxy_index]
            self.current_proxy_index = best_proxy_index
            new_proxy = self.proxies[self.current_proxy_index]
            logger.info(f"Rotated proxy: {old_proxy.host}:{old_proxy.port} -> {new_proxy.host}:{new_proxy.port}")
        
        self.last_rotation_time = time.time()
    
    def _find_best_proxy(self) -> int:
        """Find proxy with best success rate"""
        if not self.proxy_stats:
            return 0
        
        best_index = 0
        best_score = -1
        
        for index, stats in self.proxy_stats.items():
            total_requests = stats["success_count"] + stats["error_count"]
            if total_requests == 0:
                # Prefer untested proxies
                success_rate = 1.0
            else:
                success_rate = stats["success_count"] / total_requests
            
            # Factor in recency (prefer recently used proxies that worked)
            time_factor = max(0.1, 1.0 - (time.time() - stats["last_used"]) / 3600)
            score = success_rate * time_factor
            
            if score > best_score:
                best_score = score
                best_index = index
        
        return best_index
    
    def mark_proxy_success(self, proxy_index: Optional[int] = None):
        """Mark current proxy as successful"""
        if proxy_index is None:
            proxy_index = self.current_proxy_index
        
        if proxy_index in self.proxy_stats:
            self.proxy_stats[proxy_index]["success_count"] += 1
            self.proxy_stats[proxy_index]["last_used"] = time.time()
    
    def mark_proxy_error(self, proxy_index: Optional[int] = None):
        """Mark current proxy as having an error"""
        if proxy_index is None:
            proxy_index = self.current_proxy_index
        
        if proxy_index in self.proxy_stats:
            self.proxy_stats[proxy_index]["error_count"] += 1
            self.proxy_stats[proxy_index]["last_used"] = time.time()
        
        # Rotate to next proxy after error
        if len(self.proxies) > 1:
            self.rotate_proxy()
    
    def get_proxy_for_requests(self) -> Optional[Dict[str, str]]:
        """Get proxy dict for requests library"""
        proxy = self.get_current_proxy()
        return proxy.to_dict() if proxy else None
    
    def get_proxy_for_yt_dlp(self) -> Optional[str]:
        """Get proxy URL for yt-dlp"""
        proxy = self.get_current_proxy()
        return proxy.to_url() if proxy else None
    
    def test_proxy(self, proxy: ProxyConfig, timeout: int = 10) -> bool:
        """Test if a proxy is working"""
        try:
            proxy_dict = proxy.to_dict()
            response = requests.get(
                "https://httpbin.org/ip",
                proxies=proxy_dict,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Proxy {proxy.host}:{proxy.port} working, IP: {result.get('origin')}")
                return True
            else:
                logger.warning(f"Proxy {proxy.host}:{proxy.port} returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Proxy {proxy.host}:{proxy.port} test failed: {e}")
            return False
    
    def test_all_proxies(self) -> Dict[int, bool]:
        """Test all configured proxies"""
        results = {}
        
        for i, proxy in enumerate(self.proxies):
            logger.info(f"Testing proxy {i+1}/{len(self.proxies)}: {proxy.host}:{proxy.port}")
            results[i] = self.test_proxy(proxy)
            time.sleep(1)  # Rate limit proxy tests
        
        return results
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get detailed status of proxy configuration"""
        return {
            "total_proxies": len(self.proxies),
            "current_proxy_index": self.current_proxy_index,
            "current_proxy": self.get_current_proxy().to_url() if self.get_current_proxy() else None,
            "rotation_interval": self.rotation_interval,
            "last_rotation": self.last_rotation_time,
            "proxy_stats": self.proxy_stats,
            "proxies": [
                {
                    "host": proxy.host,
                    "port": proxy.port,
                    "protocol": proxy.protocol,
                    "has_auth": bool(proxy.username)
                }
                for proxy in self.proxies
            ]
        }

def create_proxy_config_template():
    """Create a template proxy configuration file"""
    config_template = {
        "proxies": [
            {
                "host": "proxy1.example.com",
                "port": 8080,
                "username": "your_username",
                "password": "your_password",
                "protocol": "http"
            },
            {
                "host": "proxy2.example.com", 
                "port": 3128,
                "protocol": "http"
            }
        ]
    }
    
    config_file = os.path.join(os.path.dirname(__file__), "proxy_config.json")
    
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(config_template, f, indent=2)
        logger.info(f"Created proxy config template: {config_file}")
    
    return config_file

# Global proxy manager instance
default_proxy_manager = ProxyManager()

if __name__ == "__main__":
    # CLI interface for proxy management
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        manager = ProxyManager()
        
        if command == "test":
            print("Testing all configured proxies...")
            results = manager.test_all_proxies()
            
            print("\nProxy Test Results:")
            for index, result in results.items():
                proxy = manager.proxies[index]
                status = "✅ WORKING" if result else "❌ FAILED"
                print(f"  {proxy.host}:{proxy.port} - {status}")
        
        elif command == "status":
            status = manager.get_status_report()
            print("Proxy Manager Status:")
            print(json.dumps(status, indent=2))
        
        elif command == "create-config":
            config_file = create_proxy_config_template()
            print(f"Created proxy config template: {config_file}")
        
        else:
            print("Usage: python proxy_manager.py [test|status|create-config]")
    else:
        # Default: show status
        manager = ProxyManager()
        if manager.has_proxies():
            print(f"Proxy Manager: {len(manager.proxies)} proxies configured")
            current = manager.get_current_proxy()
            if current:
                print(f"Current proxy: {current.host}:{current.port}")
        else:
            print("No proxies configured")
            print("Set environment variables or create proxy_config.json")