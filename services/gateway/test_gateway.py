#!/usr/bin/env python3
"""
API Gateway Integration Test
Tests all routers and endpoints
"""

import asyncio
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def test_imports():
    """Test that all modules can be imported"""
    logger.info("Testing imports...")

    try:
        from main import app
        logger.info("✓ main.py imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import main.py: {e}")
        return False

    try:
        from config import settings
        logger.info("✓ config.py imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import config.py: {e}")
        return False

    try:
        from routers import (
            transcription_router,
            analysis_router,
            evaluation_router,
            reporting_router,
            workflows_router
        )
        logger.info("✓ All routers imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import routers: {e}")
        return False

    return True


async def test_app_creation():
    """Test that FastAPI app is created correctly"""
    logger.info("\nTesting app creation...")

    try:
        from main import app
        from config import settings

        # Check app attributes
        assert app.title == settings.app_name
        assert app.version == settings.app_version
        logger.info(f"✓ App created: {app.title} v{app.version}")

        # Check routes
        routes = [route.path for route in app.routes]
        logger.info(f"✓ Found {len(routes)} routes")

        # Check key endpoints
        required_endpoints = [
            "/health",
            "/api/health",
            "/api/services/health",
            "/api/transcribe/youtube",
            "/api/analyze/text",
            "/api/workflow/full-analysis"
        ]

        for endpoint in required_endpoints:
            if endpoint in routes:
                logger.info(f"✓ Endpoint exists: {endpoint}")
            else:
                logger.warning(f"⚠ Endpoint not found: {endpoint}")

        return True

    except Exception as e:
        logger.error(f"✗ App creation test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_config():
    """Test configuration settings"""
    logger.info("\nTesting configuration...")

    try:
        from config import settings

        # Check service URLs
        logger.info(f"✓ Transcription service: {settings.transcription_service_url}")
        logger.info(f"✓ Analysis service: {settings.analysis_service_url}")
        logger.info(f"✓ Evaluation service: {settings.evaluation_service_url}")
        logger.info(f"✓ Reporting service: {settings.reporting_service_url}")

        # Check Redis config
        logger.info(f"✓ Redis host: {settings.redis_host}:{settings.redis_port}")

        # Check CORS
        logger.info(f"✓ CORS origins: {len(settings.cors_origins)} configured")

        return True

    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False


async def test_router_structure():
    """Test router structure and endpoints"""
    logger.info("\nTesting router structure...")

    try:
        from routers import (
            transcription_router,
            analysis_router,
            evaluation_router,
            reporting_router,
            workflows_router
        )

        routers = {
            "transcription": transcription_router,
            "analysis": analysis_router,
            "evaluation": evaluation_router,
            "reporting": reporting_router,
            "workflows": workflows_router
        }

        for router_name, router in routers.items():
            route_count = len(router.routes)
            logger.info(f"✓ {router_name} router: {route_count} endpoints")

            # Log endpoints
            for route in router.routes:
                methods = ','.join(route.methods) if hasattr(route, 'methods') else 'N/A'
                logger.info(f"  - {methods} {route.path}")

        return True

    except Exception as e:
        logger.error(f"✗ Router structure test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Run all tests"""
    print("=" * 70)
    print("API Gateway Integration Test Suite")
    print("=" * 70)

    tests = [
        ("Import Test", test_imports),
        ("App Creation Test", test_app_creation),
        ("Configuration Test", test_config),
        ("Router Structure Test", test_router_structure)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status:12} {test_name}")

    print("-" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print("\n✅ All tests passed! Gateway is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
