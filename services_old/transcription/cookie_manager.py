#!/usr/bin/env python3
"""
Cookie Manager for YouTube Access
Handles browser cookie extraction and management for yt-dlp
"""

import os
import subprocess
import logging
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class CookieManager:
    """Manage YouTube cookies for better API access"""
    
    def __init__(self, storage_dir: str = "/data"):
        self.storage_dir = storage_dir
        self.cookie_file = os.path.join(storage_dir, "youtube_cookies.txt")
        
    def extract_cookies_from_browser(self, browser: str = "chrome") -> bool:
        """
        Extract cookies from browser (only works if browser is available)
        
        Args:
            browser: Browser name (chrome, firefox, safari, edge)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure storage directory exists
            os.makedirs(self.storage_dir, exist_ok=True)
            
            # Try to extract cookies using yt-dlp
            cmd = [
                "yt-dlp",
                f"--cookies-from-browser", browser,
                "--cookies", self.cookie_file,
                "--no-download",
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Test video
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0 and os.path.exists(self.cookie_file):
                logger.info(f"Successfully extracted {browser} cookies to {self.cookie_file}")
                return True
            else:
                logger.error(f"Failed to extract cookies: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Cookie extraction timed out")
            return False
        except Exception as e:
            logger.error(f"Cookie extraction failed: {e}")
            return False
    
    def has_valid_cookies(self) -> bool:
        """Check if we have a valid cookie file"""
        if not os.path.exists(self.cookie_file):
            return False
            
        try:
            # Check if file is not empty and contains cookie data
            with open(self.cookie_file, 'r') as f:
                content = f.read().strip()
                # Simple check for Netscape cookie format
                return len(content) > 100 and ('youtube.com' in content.lower() or 'TRUE' in content)
        except Exception as e:
            logger.error(f"Error reading cookie file: {e}")
            return False
    
    def create_cookie_instructions(self) -> str:
        """Create instructions file for manual cookie setup"""
        instructions = f"""# YouTube Cookie Setup Instructions
# 
# To improve YouTube access and avoid bot detection, follow these steps:
#
# OPTION 1: Generate cookies on your local computer (RECOMMENDED)
# ============================================================
# 1. Install yt-dlp on your local computer:
#    pip install yt-dlp
#
# 2. Make sure you're logged into YouTube in your browser (Chrome recommended)
#
# 3. Run this command on your local computer:
#    yt-dlp --cookies-from-browser chrome --cookies cookies.txt "https://www.youtube.com"
#
# 4. Upload the generated cookies.txt file to this server at:
#    {self.cookie_file}
#
# OPTION 2: Manual cookie extraction
# ================================= 
# 1. Open Chrome DevTools (F12) while on YouTube
# 2. Go to Application > Storage > Cookies > https://www.youtube.com
# 3. Copy all cookies and format as Netscape cookies.txt format
# 4. Save to {self.cookie_file}
#
# OPTION 3: Use browser extensions
# ===============================
# Install "cookies.txt" browser extension and export YouTube cookies
#
# After setup, restart the transcription service for changes to take effect.
"""
        
        instructions_file = os.path.join(self.storage_dir, "cookie_setup_instructions.txt")
        
        try:
            os.makedirs(self.storage_dir, exist_ok=True)
            with open(instructions_file, 'w') as f:
                f.write(instructions)
            logger.info(f"Created cookie setup instructions at {instructions_file}")
            return instructions_file
        except Exception as e:
            logger.error(f"Failed to create instructions file: {e}")
            return ""
    
    def try_auto_extract(self) -> bool:
        """Try to automatically extract cookies from available browsers"""
        browsers = ["chrome", "firefox", "safari", "edge", "chromium"]
        
        for browser in browsers:
            logger.info(f"Attempting to extract cookies from {browser}...")
            if self.extract_cookies_from_browser(browser):
                return True
        
        logger.warning("Could not automatically extract cookies from any browser")
        return False
    
    def get_cookie_file_path(self) -> Optional[str]:
        """Get the path to cookie file if it exists and is valid"""
        if self.has_valid_cookies():
            return self.cookie_file
        return None
    
    def cleanup_old_cookies(self, max_age_days: int = 7) -> None:
        """Remove old cookie files"""
        try:
            if os.path.exists(self.cookie_file):
                # Check file age
                file_age = os.path.getctime(self.cookie_file)
                current_time = os.time.time()
                age_days = (current_time - file_age) / (24 * 3600)
                
                if age_days > max_age_days:
                    os.remove(self.cookie_file)
                    logger.info(f"Removed old cookie file (age: {age_days:.1f} days)")
        except Exception as e:
            logger.error(f"Error cleaning up cookies: {e}")
    
    def get_status_report(self) -> dict:
        """Get detailed status of cookie setup"""
        status = {
            "cookie_file_exists": os.path.exists(self.cookie_file),
            "cookie_file_path": self.cookie_file,
            "has_valid_cookies": self.has_valid_cookies(),
            "storage_dir": self.storage_dir,
            "storage_dir_writable": os.access(self.storage_dir, os.W_OK) if os.path.exists(self.storage_dir) else False
        }
        
        if status["cookie_file_exists"]:
            try:
                stat = os.stat(self.cookie_file)
                status["cookie_file_size"] = stat.st_size
                status["cookie_file_modified"] = stat.st_mtime
            except Exception as e:
                status["error"] = str(e)
        
        return status

# Global cookie manager instance
default_cookie_manager = CookieManager()

def setup_cookies_for_youtube() -> Optional[str]:
    """
    Setup cookies for YouTube access
    Returns cookie file path if successful, None otherwise
    """
    manager = default_cookie_manager
    
    # Create instructions file for manual setup
    manager.create_cookie_instructions()
    
    # Try to auto-extract if possible (likely to fail on server)
    if not manager.has_valid_cookies():
        logger.info("No valid cookies found, attempting auto-extraction...")
        manager.try_auto_extract()
    
    # Return cookie file path if available
    return manager.get_cookie_file_path()

if __name__ == "__main__":
    # CLI interface for cookie management
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        manager = CookieManager()
        
        if command == "extract":
            browser = sys.argv[2] if len(sys.argv) > 2 else "chrome"
            success = manager.extract_cookies_from_browser(browser)
            print(f"Cookie extraction: {'SUCCESS' if success else 'FAILED'}")
            
        elif command == "status":
            status = manager.get_status_report()
            print("Cookie Status Report:")
            for key, value in status.items():
                print(f"  {key}: {value}")
                
        elif command == "instructions":
            instructions_file = manager.create_cookie_instructions()
            print(f"Instructions created at: {instructions_file}")
            
        else:
            print("Usage: python cookie_manager.py [extract|status|instructions] [browser]")
    else:
        # Default: show status
        manager = CookieManager()
        status = manager.get_status_report()
        print("YouTube Cookie Manager")
        print("=" * 50)
        for key, value in status.items():
            print(f"{key}: {value}")