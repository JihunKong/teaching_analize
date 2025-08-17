#!/usr/bin/env python3
"""
Monitoring Dashboard for YouTube Integration
Real-time monitoring of transcript extraction performance
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = None

@dataclass
class RequestMetric:
    """Request-level metrics"""
    timestamp: datetime
    url: str
    method: str
    success: bool
    duration: float
    error: Optional[str] = None
    transcript_length: int = 0
    proxy_used: Optional[str] = None

class MetricsCollector:
    """Collect and store metrics for monitoring"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_metrics: deque = deque(maxlen=max_history)
        self.system_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.lock = threading.Lock()
        
        # Counters
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Method tracking
        self.method_stats = defaultdict(lambda: {"count": 0, "success": 0, "total_time": 0})
        
    def record_request(self, metric: RequestMetric):
        """Record a request metric"""
        with self.lock:
            self.request_metrics.append(metric)
            self.total_requests += 1
            
            if metric.success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1
            
            # Update method stats
            self.method_stats[metric.method]["count"] += 1
            self.method_stats[metric.method]["total_time"] += metric.duration
            if metric.success:
                self.method_stats[metric.method]["success"] += 1
    
    def record_system_metric(self, name: str, value: float, metadata: Dict[str, Any] = None):
        """Record a system metric"""
        with self.lock:
            metric = MetricPoint(datetime.now(), value, metadata or {})
            self.system_metrics[name].append(metric)
    
    def get_success_rate(self, time_window: timedelta = None) -> float:
        """Get success rate over time window"""
        with self.lock:
            if not self.request_metrics:
                return 0.0
            
            cutoff = datetime.now() - time_window if time_window else None
            relevant_requests = [
                r for r in self.request_metrics 
                if cutoff is None or r.timestamp > cutoff
            ]
            
            if not relevant_requests:
                return 0.0
            
            successful = sum(1 for r in relevant_requests if r.success)
            return successful / len(relevant_requests)
    
    def get_average_response_time(self, time_window: timedelta = None) -> float:
        """Get average response time over time window"""
        with self.lock:
            if not self.request_metrics:
                return 0.0
            
            cutoff = datetime.now() - time_window if time_window else None
            relevant_requests = [
                r for r in self.request_metrics 
                if (cutoff is None or r.timestamp > cutoff) and r.success
            ]
            
            if not relevant_requests:
                return 0.0
            
            total_time = sum(r.duration for r in relevant_requests)
            return total_time / len(relevant_requests)
    
    def get_error_breakdown(self, time_window: timedelta = None) -> Dict[str, int]:
        """Get breakdown of error types"""
        with self.lock:
            cutoff = datetime.now() - time_window if time_window else None
            error_counts = defaultdict(int)
            
            for request in self.request_metrics:
                if (cutoff is None or request.timestamp > cutoff) and not request.success:
                    error_type = request.error or "Unknown error"
                    error_counts[error_type] += 1
            
            return dict(error_counts)
    
    def get_method_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance stats by method"""
        with self.lock:
            performance = {}
            
            for method, stats in self.method_stats.items():
                if stats["count"] > 0:
                    performance[method] = {
                        "total_requests": stats["count"],
                        "successful_requests": stats["success"],
                        "success_rate": stats["success"] / stats["count"],
                        "average_time": stats["total_time"] / stats["count"],
                        "requests_per_hour": self._calculate_requests_per_hour(method)
                    }
            
            return performance
    
    def _calculate_requests_per_hour(self, method: str) -> float:
        """Calculate requests per hour for a specific method"""
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_requests = [
            r for r in self.request_metrics 
            if r.timestamp > hour_ago and r.method == method
        ]
        return len(recent_requests)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all data for monitoring dashboard"""
        with self.lock:
            # Time windows for analysis
            last_hour = timedelta(hours=1)
            last_day = timedelta(days=1)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "overview": {
                    "total_requests": self.total_requests,
                    "successful_requests": self.successful_requests,
                    "failed_requests": self.failed_requests,
                    "overall_success_rate": self.successful_requests / max(self.total_requests, 1)
                },
                "performance": {
                    "success_rate_1h": self.get_success_rate(last_hour),
                    "success_rate_24h": self.get_success_rate(last_day),
                    "avg_response_time_1h": self.get_average_response_time(last_hour),
                    "avg_response_time_24h": self.get_average_response_time(last_day),
                },
                "errors": {
                    "last_hour": self.get_error_breakdown(last_hour),
                    "last_day": self.get_error_breakdown(last_day)
                },
                "methods": self.get_method_performance(),
                "system_metrics": {
                    name: list(metrics)[-10:]  # Last 10 data points
                    for name, metrics in self.system_metrics.items()
                }
            }

class YouTubeIntegrationMonitor:
    """Main monitoring class for YouTube integration"""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.start_time = datetime.now()
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Component status
        self.component_status = {
            "youtube_handler": False,
            "mcp_client": False,
            "proxy_manager": False,
            "rate_limiter": False
        }
        
    def start_monitoring(self, interval: int = 60):
        """Start background monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"📊 Started monitoring with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("📊 Stopped monitoring")
    
    def _monitoring_loop(self, interval: int):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                self._collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # Check component health
            self._check_component_health()
            
            # Record system metrics
            import psutil
            
            # CPU and memory
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            self.metrics.record_system_metric("cpu_percent", cpu_percent)
            self.metrics.record_system_metric("memory_percent", memory_percent)
            
            # Request rate
            hour_ago = datetime.now() - timedelta(hours=1)
            recent_requests = sum(1 for r in self.metrics.request_metrics if r.timestamp > hour_ago)
            self.metrics.record_system_metric("requests_per_hour", recent_requests)
            
        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")
    
    def _check_component_health(self):
        """Check health of all components"""
        try:
            # YouTube handler
            from youtube_handler import YouTubeHandler
            handler = YouTubeHandler()
            self.component_status["youtube_handler"] = True
            
            # MCP client
            try:
                from mcp_youtube_client import MCPYouTubeClientSync
                client = MCPYouTubeClientSync()
                self.component_status["mcp_client"] = client.health_check()
            except:
                self.component_status["mcp_client"] = False
            
            # Proxy manager
            try:
                from proxy_manager import ProxyManager
                proxy_mgr = ProxyManager()
                self.component_status["proxy_manager"] = proxy_mgr.has_proxies()
            except:
                self.component_status["proxy_manager"] = False
            
            # Rate limiter
            try:
                from rate_limiter import youtube_rate_limiter
                youtube_rate_limiter.get_stats()
                self.component_status["rate_limiter"] = True
            except:
                self.component_status["rate_limiter"] = False
                
        except Exception as e:
            logger.error(f"Component health check failed: {e}")
    
    def record_transcript_request(self, url: str, method: str, success: bool, 
                                duration: float, error: str = None, 
                                transcript_length: int = 0, proxy_used: str = None):
        """Record a transcript extraction request"""
        metric = RequestMetric(
            timestamp=datetime.now(),
            url=url,
            method=method,
            success=success,
            duration=duration,
            error=error,
            transcript_length=transcript_length,
            proxy_used=proxy_used
        )
        
        self.metrics.record_request(metric)
        
        # Log significant events
        if not success:
            logger.warning(f"❌ Request failed: {method} - {error}")
        elif duration > 30:
            logger.warning(f"⏱️ Slow request: {method} - {duration:.1f}s")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        success_rate_1h = self.metrics.get_success_rate(timedelta(hours=1))
        avg_time_1h = self.metrics.get_average_response_time(timedelta(hours=1))
        
        # Determine overall health
        health = "healthy"
        if success_rate_1h < 0.8:
            health = "degraded"
        if success_rate_1h < 0.5:
            health = "unhealthy"
        
        return {
            "status": health,
            "timestamp": datetime.now().isoformat(),
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "components": self.component_status,
            "metrics": {
                "success_rate_1h": success_rate_1h,
                "avg_response_time_1h": avg_time_1h,
                "total_requests": self.metrics.total_requests
            }
        }
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts based on metrics"""
        alerts = []
        
        # Success rate alerts
        success_rate_1h = self.metrics.get_success_rate(timedelta(hours=1))
        if success_rate_1h < 0.5:
            alerts.append({
                "severity": "critical",
                "message": f"Success rate critically low: {success_rate_1h:.1%}",
                "metric": "success_rate",
                "value": success_rate_1h
            })
        elif success_rate_1h < 0.8:
            alerts.append({
                "severity": "warning", 
                "message": f"Success rate below threshold: {success_rate_1h:.1%}",
                "metric": "success_rate",
                "value": success_rate_1h
            })
        
        # Response time alerts
        avg_time_1h = self.metrics.get_average_response_time(timedelta(hours=1))
        if avg_time_1h > 60:
            alerts.append({
                "severity": "warning",
                "message": f"High average response time: {avg_time_1h:.1f}s",
                "metric": "response_time",
                "value": avg_time_1h
            })
        
        # Component health alerts
        for component, status in self.component_status.items():
            if not status and component in ["youtube_handler"]:  # Critical components
                alerts.append({
                    "severity": "critical",
                    "message": f"Critical component unhealthy: {component}",
                    "metric": "component_health",
                    "component": component
                })
        
        return alerts
    
    def export_metrics(self, filepath: str = None) -> str:
        """Export metrics to JSON file"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"youtube_metrics_{timestamp}.json"
        
        data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "uptime": (datetime.now() - self.start_time).total_seconds(),
                "version": "1.0"
            },
            "dashboard": self.metrics.get_dashboard_data(),
            "health": self.get_health_status(),
            "alerts": self.get_alerts()
        }
        
        # Convert datetime objects to strings for JSON serialization
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object {obj} is not JSON serializable")
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=serialize_datetime)
            
            logger.info(f"📄 Metrics exported to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return ""

# Global monitor instance
youtube_monitor = YouTubeIntegrationMonitor()

def create_monitoring_endpoints(app):
    """Add monitoring endpoints to FastAPI app"""
    
    @app.get("/api/monitoring/health")
    async def monitoring_health():
        """Health check endpoint"""
        return youtube_monitor.get_health_status()
    
    @app.get("/api/monitoring/metrics")
    async def monitoring_metrics():
        """Get current metrics"""
        return youtube_monitor.metrics.get_dashboard_data()
    
    @app.get("/api/monitoring/alerts")
    async def monitoring_alerts():
        """Get current alerts"""
        return {"alerts": youtube_monitor.get_alerts()}
    
    @app.post("/api/monitoring/export")
    async def export_monitoring_data():
        """Export monitoring data"""
        filepath = youtube_monitor.export_metrics()
        return {"success": bool(filepath), "filepath": filepath}

if __name__ == "__main__":
    # Test monitoring
    monitor = YouTubeIntegrationMonitor()
    monitor.start_monitoring(interval=10)
    
    # Simulate some requests
    import random
    import time
    
    for i in range(10):
        success = random.random() > 0.2  # 80% success rate
        duration = random.uniform(1, 10)
        error = None if success else "Bot detection error"
        
        monitor.record_transcript_request(
            url=f"https://youtube.com/watch?v=test{i}",
            method="mcp_client",
            success=success,
            duration=duration,
            error=error,
            transcript_length=random.randint(1000, 5000) if success else 0
        )
        
        time.sleep(1)
    
    # Show results
    print("Dashboard Data:")
    print(json.dumps(monitor.metrics.get_dashboard_data(), indent=2, default=str))
    
    print("\nHealth Status:")
    print(json.dumps(monitor.get_health_status(), indent=2, default=str))
    
    print("\nAlerts:")
    print(json.dumps(monitor.get_alerts(), indent=2, default=str))
    
    monitor.stop_monitoring()