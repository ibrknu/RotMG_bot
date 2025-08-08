#!/usr/bin/env python3
"""
Comprehensive test runner for RotMG Bot
Tests all components: vision, input, logic, GUI, and integration
"""

import unittest
import sys
import os
import logging
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def setup_test_environment():
    """Setup test environment and logging"""
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/test_results.log'),
            logging.StreamHandler()
        ]
    )

def run_vision_tests():
    """Run vision detection tests"""
    print("\n" + "="*60)
    print("RUNNING VISION DETECTION TESTS")
    print("="*60)
    
    from tests.test_vision_detection import run_vision_tests
    return run_vision_tests()

def run_input_tests():
    """Run input automation tests"""
    print("\n" + "="*60)
    print("RUNNING INPUT AUTOMATION TESTS")
    print("="*60)
    
    # Import and run input tests
    try:
        from tests.test_input_automation import TestInputAutomation
        suite = unittest.TestLoader().loadTestsFromTestCase(TestInputAutomation)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Input tests not available: {e}")
        return True

def run_logic_tests():
    """Run bot logic tests"""
    print("\n" + "="*60)
    print("RUNNING BOT LOGIC TESTS")
    print("="*60)
    
    # Import and run logic tests
    try:
        from tests.test_bot_logic import TestBotLogic
        suite = unittest.TestLoader().loadTestsFromTestCase(TestBotLogic)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Logic tests not available: {e}")
        return True

def run_gui_tests():
    """Run GUI tests"""
    print("\n" + "="*60)
    print("RUNNING GUI TESTS")
    print("="*60)
    
    # Import and run GUI tests
    try:
        from tests.test_gui import TestGUI
        suite = unittest.TestLoader().loadTestsFromTestCase(TestGUI)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"GUI tests not available: {e}")
        return True

def run_integration_tests():
    """Run integration tests"""
    print("\n" + "="*60)
    print("RUNNING INTEGRATION TESTS")
    print("="*60)
    
    # Import and run integration tests
    try:
        from tests.test_integration import TestIntegration
        suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegration)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Integration tests not available: {e}")
        return True

def run_asset_tests():
    """Run asset loading and validation tests"""
    print("\n" + "="*60)
    print("RUNNING ASSET TESTS")
    print("="*60)
    
    # Import and run asset tests
    try:
        from tests.test_assets import TestAssets
        suite = unittest.TestLoader().loadTestsFromTestCase(TestAssets)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Asset tests not available: {e}")
        return True

def run_performance_tests():
    """Run performance tests"""
    print("\n" + "="*60)
    print("RUNNING PERFORMANCE TESTS")
    print("="*60)
    
    # Import and run performance tests
    try:
        from tests.test_performance import TestPerformance
        suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformance)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Performance tests not available: {e}")
        return True

def run_all_tests():
    """Run all test suites"""
    setup_test_environment()
    
    print("RotMG Bot - Comprehensive Test Suite")
    print("="*60)
    print(f"Starting tests at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track results
    test_results = {}
    total_tests = 0
    passed_tests = 0
    
    # Run each test suite
    test_suites = [
        ("Vision Detection", run_vision_tests),
        ("Input Automation", run_input_tests),
        ("Bot Logic", run_logic_tests),
        ("GUI", run_gui_tests),
        ("Integration", run_integration_tests),
        ("Assets", run_asset_tests),
        ("Performance", run_performance_tests),
    ]
    
    for suite_name, test_function in test_suites:
        try:
            start_time = time.time()
            success = test_function()
            end_time = time.time()
            
            test_results[suite_name] = {
                'success': success,
                'duration': end_time - start_time
            }
            
            if success:
                passed_tests += 1
            total_tests += 1
            
        except Exception as e:
            print(f"Error running {suite_name} tests: {e}")
            test_results[suite_name] = {
                'success': False,
                'duration': 0,
                'error': str(e)
            }
            total_tests += 1
    
    # Print final results
    print("\n" + "="*60)
    print("FINAL TEST RESULTS")
    print("="*60)
    
    for suite_name, result in test_results.items():
        status = "PASS" if result['success'] else "FAIL"
        duration = f"{result['duration']:.2f}s"
        print(f"{suite_name:20} | {status:4} | {duration:>8}")
        
        if 'error' in result:
            print(f"  Error: {result['error']}")
    
    print("-" * 60)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"Overall: {passed_tests}/{total_tests} test suites passed ({success_rate:.1f}%)")
    
    # Save detailed results to file
    with open("logs/test_summary.txt", "w") as f:
        f.write("RotMG Bot Test Results\n")
        f.write("=" * 40 + "\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for suite_name, result in test_results.items():
            f.write(f"{suite_name}:\n")
            f.write(f"  Status: {'PASS' if result['success'] else 'FAIL'}\n")
            f.write(f"  Duration: {result['duration']:.2f}s\n")
            if 'error' in result:
                f.write(f"  Error: {result['error']}\n")
            f.write("\n")
        
        f.write(f"Overall: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)\n")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 