#!/usr/bin/env python3
"""
Comprehensive YouTube Integration Test Suite
Tests all implemented methods for YouTube caption extraction
"""

import sys
import os
import json
import time
import logging
from typing import Dict, List, Any
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from youtube_handler import YouTubeHandler
from mcp_youtube_client import MCPYouTubeClientSync
from proxy_manager import ProxyManager
from rate_limiter import youtube_rate_limiter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('youtube_integration_test.log')
    ]
)
logger = logging.getLogger(__name__)

class YouTubeIntegrationTester:
    """Comprehensive tester for YouTube integration"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        
        # Test URLs with known captions
        self.test_urls = [
            {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "name": "Rick Roll (Famous video)",
                "expected_languages": ["en"],
                "description": "Popular video that should have English captions"
            },
            {
                "url": "https://youtu.be/dQw4w9WgXcQ", 
                "name": "Rick Roll (Short URL)",
                "expected_languages": ["en"],
                "description": "Same video with youtu.be format"
            },
            {
                "url": "https://www.youtube.com/watch?v=fJ9rUzIMcZQ",
                "name": "TED Talk Example",
                "expected_languages": ["en"],
                "description": "TED talk that typically has captions"
            }
        ]
        
        # Initialize components
        self.youtube_handler = None
        self.mcp_client = None
        self.proxy_manager = None
        
    def setup_components(self):
        """Initialize all components for testing"""
        logger.info("🔧 Setting up test components...")
        
        try:
            self.youtube_handler = YouTubeHandler()
            logger.info("✅ YouTube handler initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize YouTube handler: {e}")
            return False
        
        try:
            self.mcp_client = MCPYouTubeClientSync()
            if self.mcp_client.health_check():
                logger.info("✅ MCP client connected and healthy")
            else:
                logger.warning("⚠️ MCP client not healthy")
                self.mcp_client = None
        except Exception as e:
            logger.warning(f"⚠️ MCP client not available: {e}")
            self.mcp_client = None
        
        try:
            self.proxy_manager = ProxyManager()
            if self.proxy_manager.has_proxies():
                logger.info(f"✅ Proxy manager initialized with {len(self.proxy_manager.proxies)} proxies")
            else:
                logger.info("ℹ️ No proxies configured")
        except Exception as e:
            logger.warning(f"⚠️ Proxy manager not available: {e}")
            self.proxy_manager = None
        
        return True
    
    def test_component_health(self) -> Dict[str, Any]:
        """Test health of all components"""
        logger.info("🏥 Testing component health...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "youtube_handler": False,
            "mcp_client": False,
            "proxy_manager": False,
            "rate_limiter": False
        }
        
        # Test YouTube handler
        if self.youtube_handler:
            try:
                # Test video ID extraction
                test_id = self.youtube_handler._extract_video_id(self.test_urls[0]["url"])
                results["youtube_handler"] = test_id is not None
                logger.info(f"✅ YouTube handler: Video ID extraction {'works' if results['youtube_handler'] else 'failed'}")
            except Exception as e:
                logger.error(f"❌ YouTube handler health check failed: {e}")
        
        # Test MCP client
        if self.mcp_client:
            try:
                results["mcp_client"] = self.mcp_client.health_check()
                logger.info(f"✅ MCP client: {'Healthy' if results['mcp_client'] else 'Unhealthy'}")
            except Exception as e:
                logger.error(f"❌ MCP client health check failed: {e}")
        
        # Test proxy manager
        if self.proxy_manager:
            try:
                results["proxy_manager"] = self.proxy_manager.has_proxies()
                logger.info(f"✅ Proxy manager: {len(self.proxy_manager.proxies) if results['proxy_manager'] else 0} proxies")
            except Exception as e:
                logger.error(f"❌ Proxy manager health check failed: {e}")
        
        # Test rate limiter
        try:
            stats = youtube_rate_limiter.get_stats()
            results["rate_limiter"] = True
            logger.info("✅ Rate limiter: Operational")
        except Exception as e:
            logger.error(f"❌ Rate limiter health check failed: {e}")
        
        return results
    
    def test_single_method(self, method_name: str, method_func, url_info: Dict[str, Any], 
                          timeout: int = 60) -> Dict[str, Any]:
        """Test a single extraction method"""
        url = url_info["url"]
        start_time = time.time()
        
        result = {
            "method": method_name,
            "url": url,
            "url_name": url_info["name"],
            "success": False,
            "transcript_length": 0,
            "execution_time": 0,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            logger.info(f"🔄 Testing {method_name} with {url_info['name']}...")
            
            transcript = method_func(url, "en")
            execution_time = time.time() - start_time
            
            if transcript:
                result.update({
                    "success": True,
                    "transcript_length": len(transcript),
                    "execution_time": execution_time,
                    "preview": transcript[:150] + "..." if len(transcript) > 150 else transcript
                })
                logger.info(f"✅ {method_name}: {len(transcript)} characters in {execution_time:.2f}s")
            else:
                result.update({
                    "success": False,
                    "execution_time": execution_time,
                    "error": "No transcript returned"
                })
                logger.warning(f"⚠️ {method_name}: No transcript returned")
        
        except Exception as e:
            execution_time = time.time() - start_time
            result.update({
                "success": False,
                "execution_time": execution_time,
                "error": str(e)
            })
            logger.error(f"❌ {method_name}: {str(e)}")
        
        return result
    
    def test_all_methods(self) -> List[Dict[str, Any]]:
        """Test all available extraction methods"""
        logger.info("🧪 Testing all extraction methods...")
        
        all_results = []
        
        for url_info in self.test_urls:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing URL: {url_info['name']}")
            logger.info(f"URL: {url_info['url']}")
            logger.info(f"{'='*60}")
            
            # Test MCP client if available
            if self.mcp_client:
                result = self.test_single_method(
                    "MCP Client", 
                    self.mcp_client.get_transcript, 
                    url_info
                )
                all_results.append(result)
            
            # Test YouTube handler (all methods)
            if self.youtube_handler:
                # Test complete get_captions method
                result = self.test_single_method(
                    "YouTube Handler (Complete)",
                    self.youtube_handler.get_captions,
                    url_info
                )
                all_results.append(result)
                
                # Test individual methods
                result = self.test_single_method(
                    "YouTube Transcript API",
                    self.youtube_handler.get_transcript_via_api,
                    url_info
                )
                all_results.append(result)
            
            # Add delay between URLs to respect rate limits
            time.sleep(3)
        
        return all_results
    
    def test_proxy_functionality(self) -> Dict[str, Any]:
        """Test proxy functionality if available"""
        logger.info("🌐 Testing proxy functionality...")
        
        if not self.proxy_manager or not self.proxy_manager.has_proxies():
            return {"available": False, "message": "No proxies configured"}
        
        results = {
            "available": True,
            "proxy_count": len(self.proxy_manager.proxies),
            "test_results": []
        }
        
        # Test each proxy
        for i, proxy in enumerate(self.proxy_manager.proxies):
            logger.info(f"Testing proxy {i+1}/{len(self.proxy_manager.proxies)}: {proxy.host}:{proxy.port}")
            
            test_result = {
                "proxy_index": i,
                "host": proxy.host,
                "port": proxy.port,
                "working": False,
                "response_time": 0,
                "error": None
            }
            
            start_time = time.time()
            try:
                working = self.proxy_manager.test_proxy(proxy)
                test_result.update({
                    "working": working,
                    "response_time": time.time() - start_time
                })
                
                if working:
                    logger.info(f"✅ Proxy {i+1} working")
                else:
                    logger.warning(f"⚠️ Proxy {i+1} not responding")
                    
            except Exception as e:
                test_result.update({
                    "working": False,
                    "response_time": time.time() - start_time,
                    "error": str(e)
                })
                logger.error(f"❌ Proxy {i+1} failed: {e}")
            
            results["test_results"].append(test_result)
            time.sleep(2)  # Rate limit proxy tests
        
        working_proxies = sum(1 for r in results["test_results"] if r["working"])
        logger.info(f"📊 Proxy test summary: {working_proxies}/{len(self.proxy_manager.proxies)} working")
        
        return results
    
    def test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting functionality"""
        logger.info("⏱️ Testing rate limiting...")
        
        try:
            stats_before = youtube_rate_limiter.get_stats()
            
            # Make a few rapid requests to test rate limiting
            logger.info("Making rapid requests to test rate limiting...")
            
            start_time = time.time()
            for i in range(3):
                try:
                    # Simulate a request that would be rate limited
                    if youtube_rate_limiter.rate_limiter.can_make_request():
                        youtube_rate_limiter.rate_limiter.record_request()
                        logger.info(f"Request {i+1} allowed")
                    else:
                        wait_time = youtube_rate_limiter.rate_limiter.wait_time()
                        logger.info(f"Request {i+1} rate limited, wait time: {wait_time:.2f}s")
                        time.sleep(wait_time)
                        youtube_rate_limiter.rate_limiter.record_request()
                        logger.info(f"Request {i+1} completed after wait")
                except Exception as e:
                    logger.error(f"Request {i+1} failed: {e}")
            
            total_time = time.time() - start_time
            stats_after = youtube_rate_limiter.get_stats()
            
            return {
                "available": True,
                "total_test_time": total_time,
                "stats_before": stats_before,
                "stats_after": stats_after,
                "rate_limiting_working": total_time > 5  # Should take some time due to rate limiting
            }
            
        except Exception as e:
            logger.error(f"Rate limiting test failed: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    def generate_report(self, health_results: Dict[str, Any], 
                       method_results: List[Dict[str, Any]],
                       proxy_results: Dict[str, Any],
                       rate_limit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        total_tests = len(method_results)
        successful_tests = sum(1 for r in method_results if r["success"])
        
        # Group results by method
        method_summary = {}
        for result in method_results:
            method = result["method"]
            if method not in method_summary:
                method_summary[method] = {"total": 0, "successful": 0, "avg_time": 0}
            
            method_summary[method]["total"] += 1
            if result["success"]:
                method_summary[method]["successful"] += 1
            method_summary[method]["avg_time"] += result["execution_time"]
        
        # Calculate averages
        for method_data in method_summary.values():
            if method_data["total"] > 0:
                method_data["avg_time"] /= method_data["total"]
                method_data["success_rate"] = method_data["successful"] / method_data["total"]
        
        report = {
            "test_info": {
                "timestamp": datetime.now().isoformat(),
                "duration": (datetime.now() - self.start_time).total_seconds(),
                "test_urls": len(self.test_urls),
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0
            },
            "component_health": health_results,
            "method_summary": method_summary,
            "detailed_results": method_results,
            "proxy_testing": proxy_results,
            "rate_limiting": rate_limit_results,
            "recommendations": self._generate_recommendations(
                health_results, method_summary, proxy_results, rate_limit_results
            )
        }
        
        return report
    
    def _generate_recommendations(self, health: Dict[str, Any], methods: Dict[str, Any], 
                                 proxies: Dict[str, Any], rate_limiting: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check component health
        if not health.get("mcp_client", False):
            recommendations.append("🔧 Consider setting up MCP server for better bot detection bypass")
        
        if not health.get("proxy_manager", False):
            recommendations.append("🌐 Configure residential proxies (e.g., Webshare) for server deployment")
        
        # Check method success rates
        for method, stats in methods.items():
            if stats["success_rate"] < 0.5:
                recommendations.append(f"⚠️ {method} has low success rate ({stats['success_rate']:.1%}) - check configuration")
        
        # Check proxy results
        if proxies.get("available", False):
            working_proxies = sum(1 for r in proxies["test_results"] if r["working"])
            total_proxies = len(proxies["test_results"])
            if working_proxies == 0:
                recommendations.append("❌ No working proxies found - check proxy credentials")
            elif working_proxies < total_proxies:
                recommendations.append(f"⚠️ Only {working_proxies}/{total_proxies} proxies working - review proxy configuration")
        
        # Overall recommendations
        if not recommendations:
            recommendations.append("✅ All systems operational - ready for production use")
        
        recommendations.append("📊 Monitor logs for rate limiting and proxy rotation")
        recommendations.append("🔄 Run this test periodically to ensure continued functionality")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save test report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_integration_test_report_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"📄 Test report saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return None
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report"""
        logger.info("🚀 Starting comprehensive YouTube integration test...")
        logger.info(f"Start time: {self.start_time}")
        
        # Setup components
        if not self.setup_components():
            logger.error("❌ Failed to setup components - aborting test")
            return {}
        
        # Run tests
        health_results = self.test_component_health()
        method_results = self.test_all_methods()
        proxy_results = self.test_proxy_functionality()
        rate_limit_results = self.test_rate_limiting()
        
        # Generate report
        report = self.generate_report(health_results, method_results, proxy_results, rate_limit_results)
        
        # Save report
        report_file = self.save_report(report)
        
        # Print summary
        self.print_summary(report)
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print test summary to console"""
        print(f"\n{'='*80}")
        print("🧪 YOUTUBE INTEGRATION TEST SUMMARY")
        print(f"{'='*80}")
        
        test_info = report["test_info"]
        print(f"📊 Test Results:")
        print(f"   • Duration: {test_info['duration']:.1f} seconds")
        print(f"   • URLs tested: {test_info['test_urls']}")
        print(f"   • Total tests: {test_info['total_tests']}")
        print(f"   • Successful: {test_info['successful_tests']}")
        print(f"   • Success rate: {test_info['success_rate']:.1%}")
        
        print(f"\n🏥 Component Health:")
        health = report["component_health"]
        for component, status in health.items():
            if component != "timestamp":
                icon = "✅" if status else "❌"
                print(f"   • {component}: {icon}")
        
        print(f"\n🎯 Method Performance:")
        for method, stats in report["method_summary"].items():
            success_rate = stats["success_rate"]
            avg_time = stats["avg_time"]
            icon = "✅" if success_rate > 0.7 else "⚠️" if success_rate > 0.3 else "❌"
            print(f"   • {method}: {icon} {success_rate:.1%} success, {avg_time:.1f}s avg")
        
        if report["proxy_testing"]["available"]:
            proxy_results = report["proxy_testing"]["test_results"]
            working = sum(1 for r in proxy_results if r["working"])
            total = len(proxy_results)
            print(f"\n🌐 Proxy Status: {working}/{total} working")
        
        print(f"\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   {rec}")
        
        print(f"\n{'='*80}")

def main():
    """Main test execution"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("YouTube Integration Test Suite")
            print("Usage: python test_youtube_integration.py [--quick] [--proxy-only] [--health-only]")
            print("  --quick      : Run only health checks and one URL test")
            print("  --proxy-only : Test only proxy functionality")
            print("  --health-only: Test only component health")
            return
    
    tester = YouTubeIntegrationTester()
    
    if "--health-only" in sys.argv:
        tester.setup_components()
        health = tester.test_component_health()
        print(json.dumps(health, indent=2))
    elif "--proxy-only" in sys.argv:
        tester.setup_components()
        proxy_results = tester.test_proxy_functionality()
        print(json.dumps(proxy_results, indent=2))
    else:
        report = tester.run_comprehensive_test()

if __name__ == "__main__":
    main()