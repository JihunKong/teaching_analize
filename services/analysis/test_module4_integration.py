#!/usr/bin/env python3
"""
Module 4 Integration Test
Tests the new advanced report generation components
"""

import sys
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all Module 4 components can be imported"""
    logger.info("Testing imports...")

    try:
        from advanced_pdf_generator import AdvancedPDFGenerator
        logger.info("✓ AdvancedPDFGenerator imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import AdvancedPDFGenerator: {e}")
        return False

    try:
        from visualization import Matrix3DVisualizer
        logger.info("✓ Matrix3DVisualizer imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import Matrix3DVisualizer: {e}")
        return False

    try:
        from exporters import ExcelReportExporter
        logger.info("✓ ExcelReportExporter imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import ExcelReportExporter: {e}")
        return False

    return True

def test_generator_initialization():
    """Test that generators can be initialized"""
    logger.info("\nTesting generator initialization...")

    try:
        from advanced_pdf_generator import AdvancedPDFGenerator
        pdf_gen = AdvancedPDFGenerator()
        logger.info("✓ AdvancedPDFGenerator initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize AdvancedPDFGenerator: {e}")
        return False

    try:
        from visualization import Matrix3DVisualizer
        viz = Matrix3DVisualizer()
        logger.info("✓ Matrix3DVisualizer initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize Matrix3DVisualizer: {e}")
        return False

    try:
        from exporters import ExcelReportExporter
        exporter = ExcelReportExporter()
        logger.info("✓ ExcelReportExporter initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize ExcelReportExporter: {e}")
        return False

    return True

def test_3d_visualization():
    """Test 3D visualization with sample data"""
    logger.info("\nTesting 3D visualization with sample data...")

    try:
        from visualization import Matrix3DVisualizer
        viz = Matrix3DVisualizer()

        # Create sample matrix data
        sample_data = {
            "matrix": {
                "introduction": {
                    "explanation": {"l1": 5, "l2": 3, "l3": 1},
                    "question": {"l1": 2, "l2": 4, "l3": 2},
                    "feedback": {"l1": 1, "l2": 2, "l3": 1},
                    "facilitation": {"l1": 0, "l2": 1, "l3": 0},
                    "management": {"l1": 1, "l2": 0, "l3": 0}
                },
                "development": {
                    "explanation": {"l1": 8, "l2": 6, "l3": 4},
                    "question": {"l1": 5, "l2": 7, "l3": 5},
                    "feedback": {"l1": 3, "l2": 5, "l3": 3},
                    "facilitation": {"l1": 2, "l2": 3, "l3": 2},
                    "management": {"l1": 1, "l2": 1, "l3": 1}
                },
                "closing": {
                    "explanation": {"l1": 2, "l2": 1, "l3": 1},
                    "question": {"l1": 1, "l2": 2, "l3": 1},
                    "feedback": {"l1": 1, "l2": 1, "l3": 1},
                    "facilitation": {"l1": 0, "l2": 1, "l3": 0},
                    "management": {"l1": 0, "l2": 0, "l3": 0}
                }
            },
            "statistics": {
                "stage_distribution": {
                    "introduction": {"count": 20, "percentage": 25.0},
                    "development": {"count": 50, "percentage": 62.5},
                    "closing": {"count": 10, "percentage": 12.5}
                },
                "context_distribution": {
                    "explanation": {"count": 35, "percentage": 43.75},
                    "question": {"count": 25, "percentage": 31.25},
                    "feedback": {"count": 15, "percentage": 18.75},
                    "facilitation": {"count": 10, "percentage": 12.5},
                    "management": {"count": 5, "percentage": 6.25}
                },
                "level_distribution": {
                    "l1": {"count": 40, "percentage": 50.0},
                    "l2": {"count": 30, "percentage": 37.5},
                    "l3": {"count": 10, "percentage": 12.5}
                }
            }
        }

        # Test 3D heatmap generation
        html = viz.generate_3d_heatmap(sample_data)
        if html and len(html) > 1000:  # Check if HTML is generated
            logger.info("✓ 3D heatmap generated successfully")
        else:
            logger.error("✗ 3D heatmap generation produced insufficient output")
            return False

        # Test 2D heatmaps
        html = viz.generate_2d_heatmaps(sample_data)
        if html and len(html) > 1000:
            logger.info("✓ 2D heatmaps generated successfully")
        else:
            logger.error("✗ 2D heatmaps generation produced insufficient output")
            return False

        # Test distribution charts
        html = viz.generate_distribution_charts(sample_data)
        if html and len(html) > 1000:
            logger.info("✓ Distribution charts generated successfully")
        else:
            logger.error("✗ Distribution charts generation produced insufficient output")
            return False

        return True

    except Exception as e:
        logger.error(f"✗ 3D visualization test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_excel_export():
    """Test Excel export with sample data"""
    logger.info("\nTesting Excel export with sample data...")

    try:
        from exporters import ExcelReportExporter
        exporter = ExcelReportExporter()

        # Create sample cbil_comprehensive result
        sample_result = {
            "framework": "cbil_comprehensive",
            "analysis_id": "test-001",
            "created_at": "2025-01-10T12:00:00",
            "cbil_scores": {
                "engage": {"score": 2.5, "max_score": 3.0, "percentage": 83.3},
                "focus": {"score": 2.0, "max_score": 3.0, "percentage": 66.7},
                "investigate": {"score": 2.5, "max_score": 3.0, "percentage": 83.3},
                "organize": {"score": 2.0, "max_score": 3.0, "percentage": 66.7},
                "generalize": {"score": 1.5, "max_score": 3.0, "percentage": 50.0},
                "transfer": {"score": 1.0, "max_score": 3.0, "percentage": 33.3},
                "reflect": {"score": 1.5, "max_score": 3.0, "percentage": 50.0}
            },
            "module3_result": {
                "quantitative_metrics": {
                    "question_frequency": {"value": 45, "status": "optimal"},
                    "wait_time_average": {"value": 3.5, "status": "optimal"},
                    "student_talk_ratio": {"value": 65, "status": "optimal"}
                }
            }
        }

        # Test Excel generation
        excel_bytes = exporter.export_to_excel(sample_result)
        if excel_bytes and len(excel_bytes) > 5000:  # Check if Excel file is generated
            logger.info(f"✓ Excel export generated successfully ({len(excel_bytes)} bytes)")
            return True
        else:
            logger.error("✗ Excel export produced insufficient output")
            return False

    except Exception as e:
        logger.error(f"✗ Excel export test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all integration tests"""
    print("=" * 70)
    print("Module 4 Integration Test Suite")
    print("=" * 70)

    tests = [
        ("Import Test", test_imports),
        ("Initialization Test", test_generator_initialization),
        ("3D Visualization Test", test_3d_visualization),
        ("Excel Export Test", test_excel_export)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
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

    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
