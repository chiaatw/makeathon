#!/usr/bin/env python3
"""Final Integration Test Suite for Enhanced Compliance Agent.

This comprehensive test suite validates all aspects of the enhanced compliance
system including backward compatibility, enhanced features, data integration,
error handling, and performance.
"""

import sys
import time
import traceback
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Set up Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

class TestResult:
    """Container for test results."""

    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.duration = 0.0
        self.details = {}

    def success(self, details: Dict[str, Any] = None):
        """Mark test as successful."""
        self.passed = True
        self.details = details or {}

    def failure(self, error: str, details: Dict[str, Any] = None):
        """Mark test as failed."""
        self.passed = False
        self.error = error
        self.details = details or {}


class FinalIntegrationTestSuite:
    """Comprehensive test suite for the Enhanced Compliance Agent."""

    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()

    def run_test(self, test_name: str, test_func):
        """Run a single test and capture results."""
        print(f"\n{'='*60}")
        print(f"Running Test: {test_name}")
        print(f"{'='*60}")

        result = TestResult(test_name)
        start_time = time.time()

        try:
            test_func(result)
            result.duration = time.time() - start_time

            if result.passed:
                print(f"[PASS] PASSED: {test_name} ({result.duration:.2f}s)")
            else:
                print(f"[FAIL] FAILED: {test_name} ({result.duration:.2f}s)")
                if result.error:
                    print(f"   Error: {result.error}")

        except Exception as e:
            result.duration = time.time() - start_time
            result.failure(f"Exception: {str(e)}")
            print(f"❌ FAILED: {test_name} ({result.duration:.2f}s)")
            print(f"   Exception: {str(e)}")
            print(f"   Traceback: {traceback.format_exc()}")

        self.results.append(result)
        return result

    def test_data_availability(self, result: TestResult):
        """Test 1: Verify all required data files exist."""
        data_dir = Path("data")
        required_files = [
            "suppliers.csv",
            "customer_requirements.csv",
            "external_evidence.json"
        ]

        file_status = {}
        all_exist = True

        for file_name in required_files:
            file_path = data_dir / file_name
            exists = file_path.exists()
            file_status[file_name] = exists
            if not exists:
                all_exist = False

        if all_exist:
            result.success({"files_found": file_status})
        else:
            missing = [f for f, exists in file_status.items() if not exists]
            result.failure(f"Missing data files: {missing}", {"files_found": file_status})

    def test_backward_compatibility(self, result: TestResult):
        """Test 2: Verify backward compatibility with SimpleComplianceChecker."""
        try:
            from agents.enhanced_compliance_agent import call_compliance_agent

            # Test basic function call
            compliance_result = call_compliance_agent("Vitamin D3", "DSM", "PharmaCorp")

            # Verify return format matches original
            required_attrs = ["compliance_status", "confidence", "reasoning", "synergy_potential"]
            missing_attrs = []

            for attr in required_attrs:
                if not hasattr(compliance_result, attr):
                    missing_attrs.append(attr)

            if missing_attrs:
                result.failure(f"Missing attributes: {missing_attrs}")
                return

            # Verify data types
            if not isinstance(compliance_result.compliance_status, str):
                result.failure("compliance_status is not string")
                return

            if not isinstance(compliance_result.confidence, (int, float)):
                result.failure("confidence is not numeric")
                return

            # Test multiple suppliers
            test_cases = [
                ("DSM", "PharmaCorp"),
                ("BASF", "FoodSupplementCo"),
                ("Unknown", "PharmaCorp"),  # Should handle gracefully
            ]

            test_results = {}
            for supplier, customer in test_cases:
                try:
                    res = call_compliance_agent("Vitamin D3", supplier, customer)
                    test_results[(supplier, customer)] = {
                        "status": res.compliance_status,
                        "confidence": res.confidence
                    }
                except Exception as e:
                    test_results[(supplier, customer)] = {"error": str(e)}

            result.success({
                "basic_call": {
                    "status": compliance_result.compliance_status,
                    "confidence": compliance_result.confidence
                },
                "test_cases": test_results
            })

        except ImportError as e:
            result.failure(f"Import error: {str(e)}")
        except Exception as e:
            result.failure(f"Unexpected error: {str(e)}")

    def test_enhanced_features(self, result: TestResult):
        """Test 3: Verify enhanced features work correctly."""
        try:
            from agents.enhanced_compliance_agent import EnhancedComplianceAgent

            # Test agent creation
            agent = EnhancedComplianceAgent(legacy_fallback=True)

            # Test system status
            status = agent.get_system_status()
            if "mode" not in status:
                result.failure("System status missing mode")
                return

            # Test enhanced compliance check
            enhanced_result = agent.check_compliance_enhanced("DSM", "PharmaCorp")

            # Verify enhanced result structure
            required_attrs = [
                "overall_score", "overall_confidence", "plugin_results",
                "reasoning_chain", "data_gaps", "recommendations"
            ]

            missing_attrs = []
            for attr in required_attrs:
                if not hasattr(enhanced_result, attr):
                    missing_attrs.append(attr)

            if missing_attrs:
                result.failure(f"Enhanced result missing attributes: {missing_attrs}")
                return

            # Test supplier ranking
            rankings = agent.rank_suppliers("PharmaCorp", limit=3)

            if not isinstance(rankings, list):
                result.failure("Rankings not returned as list")
                return

            # Test custom scoring configuration
            agent.configure_scoring(
                plugin_weights={"certificates": 0.8},
                aggregation_method="weighted_average"
            )

            configured_result = agent.check_compliance_enhanced("DSM", "PharmaCorp")

            result.success({
                "system_mode": status["mode"],
                "enhanced_score": enhanced_result.overall_score,
                "plugin_count": len(enhanced_result.plugin_results),
                "ranking_count": len(rankings),
                "configured_score": configured_result.overall_score
            })

        except Exception as e:
            result.failure(f"Enhanced features error: {str(e)}")

    def test_data_integration(self, result: TestResult):
        """Test 4: Verify data integration and multi-source loading."""
        try:
            from agents.integration.data_integration import LegacyDataAdapter

            # Test data validation
            adapter = LegacyDataAdapter(Path("data"))
            validation_report = adapter.validate_data_files()

            # Check validation results
            files_found = validation_report["files_found"]
            all_files_found = all(files_found.values())

            if not all_files_found:
                result.failure(f"Data validation failed: {validation_report['issues']}")
                return

            # Test integration setup
            enhanced_agent = adapter.create_enhanced_compliance_agent()
            system_status = enhanced_agent.get_system_status()

            # Test integration functionality
            integration_test_report = adapter.test_integration()

            if integration_test_report["integration_test"] != "completed":
                result.failure(f"Integration test failed: {integration_test_report['errors']}")
                return

            result.success({
                "files_validated": files_found,
                "system_status": system_status["mode"],
                "suppliers_loaded": system_status.get("data_status", {}).get("suppliers_loaded", 0),
                "customers_loaded": system_status.get("data_status", {}).get("customers_loaded", 0),
                "integration_test": integration_test_report["integration_test"]
            })

        except Exception as e:
            result.failure(f"Data integration error: {str(e)}")

    def test_plugin_system(self, result: TestResult):
        """Test 5: Verify plugin system functionality."""
        try:
            from agents.enhanced_compliance_agent import EnhancedComplianceAgent
            from agents.plugins.base import CompliancePlugin
            from agents.core.data_models import PluginResult

            # Create test plugin
            class TestPlugin(CompliancePlugin):
                @property
                def name(self) -> str:
                    return "test_plugin"

                @property
                def weight_default(self) -> float:
                    return 0.1

                @property
                def required_data_fields(self):
                    return ["name"]

                def check_compliance(self, supplier_data, customer_requirements, user_filters):
                    return PluginResult(
                        plugin_name=self.name,
                        score=0.75,
                        confidence=0.9,
                        reasoning="Test plugin executed successfully"
                    )

            # Test plugin registration
            agent = EnhancedComplianceAgent()
            if agent.enhanced_engine:
                agent.enhanced_engine.register_plugin(TestPlugin())

                # Test with custom plugin
                result_with_plugin = agent.check_compliance_enhanced("DSM", "PharmaCorp")

                # Verify plugin was executed
                plugin_names = [pr.plugin_name for pr in result_with_plugin.plugin_results]

                if "test_plugin" not in plugin_names:
                    result.failure("Custom plugin was not executed")
                    return

                # Find test plugin result
                test_plugin_result = None
                for pr in result_with_plugin.plugin_results:
                    if pr.plugin_name == "test_plugin":
                        test_plugin_result = pr
                        break

                if not test_plugin_result:
                    result.failure("Test plugin result not found")
                    return

                result.success({
                    "plugin_registered": True,
                    "plugin_executed": True,
                    "plugin_score": test_plugin_result.score,
                    "plugin_confidence": test_plugin_result.confidence,
                    "total_plugins": len(result_with_plugin.plugin_results)
                })
            else:
                result.failure("Enhanced engine not available for plugin testing")

        except Exception as e:
            result.failure(f"Plugin system error: {str(e)}")

    def test_error_handling(self, result: TestResult):
        """Test 6: Verify error handling and fallback mechanisms."""
        try:
            from agents.enhanced_compliance_agent import EnhancedComplianceAgent

            error_test_results = {}

            # Test 1: Invalid supplier
            try:
                agent = EnhancedComplianceAgent(legacy_fallback=True)
                invalid_result = agent.check_compliance("NonexistentSupplier", "PharmaCorp")
                error_test_results["invalid_supplier"] = {
                    "handled": True,
                    "status": invalid_result.compliance_status
                }
            except Exception as e:
                error_test_results["invalid_supplier"] = {
                    "handled": False,
                    "error": str(e)
                }

            # Test 2: Invalid customer
            try:
                invalid_customer_result = agent.check_compliance("DSM", "NonexistentCustomer")
                error_test_results["invalid_customer"] = {
                    "handled": True,
                    "status": invalid_customer_result.compliance_status
                }
            except Exception as e:
                error_test_results["invalid_customer"] = {
                    "handled": False,
                    "error": str(e)
                }

            # Test 3: Legacy fallback
            try:
                # Force enhanced mode with no data sources (should fall back)
                fallback_agent = EnhancedComplianceAgent(
                    data_sources=[],
                    use_enhanced_mode=True,
                    legacy_fallback=True
                )
                fallback_result = fallback_agent.check_compliance("DSM", "PharmaCorp")
                error_test_results["legacy_fallback"] = {
                    "handled": True,
                    "status": fallback_result.compliance_status
                }
            except Exception as e:
                error_test_results["legacy_fallback"] = {
                    "handled": False,
                    "error": str(e)
                }

            # Check if all error scenarios were handled
            all_handled = all(test["handled"] for test in error_test_results.values())

            if all_handled:
                result.success(error_test_results)
            else:
                failed_tests = [name for name, test in error_test_results.items() if not test["handled"]]
                result.failure(f"Error handling failed for: {failed_tests}", error_test_results)

        except Exception as e:
            result.failure(f"Error handling test error: {str(e)}")

    def test_performance_and_caching(self, result: TestResult):
        """Test 7: Verify performance characteristics and caching."""
        try:
            from agents.enhanced_compliance_agent import EnhancedComplianceAgent

            agent = EnhancedComplianceAgent()

            # Test 1: Basic performance
            start_time = time.time()
            first_result = agent.check_compliance_enhanced("DSM", "PharmaCorp")
            first_duration = time.time() - start_time

            # Test 2: Cached performance
            start_time = time.time()
            second_result = agent.check_compliance_enhanced("BASF", "PharmaCorp")
            second_duration = time.time() - start_time

            # Test 3: Batch processing
            start_time = time.time()
            batch_results = agent.batch_analyze_suppliers(
                ["DSM", "BASF"], "PharmaCorp"
            )
            batch_duration = time.time() - start_time

            # Test 4: Ranking performance
            start_time = time.time()
            rankings = agent.rank_suppliers("PharmaCorp", limit=3)
            ranking_duration = time.time() - start_time

            # Test 5: Cache status
            cache_info = agent.get_system_status().get("data_status", {}).get("cache_info", {})

            performance_acceptable = (
                first_duration < 5.0 and      # First run under 5 seconds
                second_duration < 2.0 and     # Second run under 2 seconds
                batch_duration < 3.0 and      # Batch under 3 seconds
                ranking_duration < 2.0        # Ranking under 2 seconds
            )

            if performance_acceptable:
                result.success({
                    "first_run_time": first_duration,
                    "second_run_time": second_duration,
                    "batch_time": batch_duration,
                    "ranking_time": ranking_duration,
                    "cache_active": bool(cache_info),
                    "batch_results_count": len(batch_results),
                    "ranking_count": len(rankings)
                })
            else:
                result.failure("Performance thresholds not met", {
                    "first_run_time": first_duration,
                    "second_run_time": second_duration,
                    "batch_time": batch_duration,
                    "ranking_time": ranking_duration,
                    "thresholds_met": performance_acceptable
                })

        except Exception as e:
            result.failure(f"Performance test error: {str(e)}")

    def test_end_to_end_workflow(self, result: TestResult):
        """Test 8: Complete end-to-end workflow."""
        try:
            from agents.enhanced_compliance_agent import EnhancedComplianceAgent

            # Step 1: Create agent with automatic data detection
            agent = EnhancedComplianceAgent()

            # Step 2: Check system is operational
            status = agent.get_system_status()
            if status["mode"] not in ["enhanced", "legacy"]:
                result.failure(f"Invalid system mode: {status['mode']}")
                return

            # Step 3: Perform comprehensive analysis
            analysis_results = {}

            # Single compliance check
            single_result = agent.check_compliance("DSM", "PharmaCorp")
            analysis_results["single_check"] = {
                "status": single_result.compliance_status,
                "confidence": single_result.confidence
            }

            # Enhanced analysis if available
            if status["mode"] == "enhanced":
                enhanced_result = agent.check_compliance_enhanced("DSM", "PharmaCorp")
                analysis_results["enhanced_check"] = {
                    "score": enhanced_result.overall_score,
                    "confidence": enhanced_result.overall_confidence,
                    "plugins": len(enhanced_result.plugin_results)
                }

                # Supplier ranking
                rankings = agent.rank_suppliers("PharmaCorp", limit=3)
                analysis_results["ranking"] = {
                    "count": len(rankings),
                    "top_supplier": rankings[0][0] if rankings else None
                }

                # Custom configuration
                agent.configure_scoring(plugin_weights={"certificates": 0.9})
                configured_result = agent.check_compliance_enhanced("DSM", "PharmaCorp")
                analysis_results["configured_check"] = {
                    "score": configured_result.overall_score
                }

            # Step 4: Validate results are consistent
            consistency_check = (
                single_result.compliance_status in ["COMPLIANT", "NON_COMPLIANT", "INSUFFICIENT_DATA"] and
                0.0 <= single_result.confidence <= 1.0
            )

            if status["mode"] == "enhanced" and "enhanced_check" in analysis_results:
                enhanced_consistency = (
                    0.0 <= enhanced_result.overall_score <= 1.0 and
                    0.0 <= enhanced_result.overall_confidence <= 1.0
                )
                consistency_check = consistency_check and enhanced_consistency

            if consistency_check:
                result.success({
                    "system_mode": status["mode"],
                    "analysis_results": analysis_results,
                    "workflow_complete": True
                })
            else:
                result.failure("Workflow consistency check failed", analysis_results)

        except Exception as e:
            result.failure(f"End-to-end workflow error: {str(e)}")

    def run_all_tests(self):
        """Run the complete test suite."""
        print("[STARTING] Enhanced Compliance Agent - Final Integration Test Suite")
        print("=" * 80)

        # Define all tests
        tests = [
            ("Data Availability", self.test_data_availability),
            ("Backward Compatibility", self.test_backward_compatibility),
            ("Enhanced Features", self.test_enhanced_features),
            ("Data Integration", self.test_data_integration),
            ("Plugin System", self.test_plugin_system),
            ("Error Handling", self.test_error_handling),
            ("Performance & Caching", self.test_performance_and_caching),
            ("End-to-End Workflow", self.test_end_to_end_workflow),
        ]

        # Run all tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        # Generate summary report
        self.print_summary_report()

    def print_summary_report(self):
        """Print comprehensive summary report."""
        total_time = time.time() - self.start_time
        passed_tests = [r for r in self.results if r.passed]
        failed_tests = [r for r in self.results if not r.passed]

        print(f"\n\n{'='*80}")
        print("[SUMMARY] FINAL INTEGRATION TEST SUMMARY")
        print(f"{'='*80}")

        print(f"[RESULTS] Test Results:")
        print(f"   Total Tests: {len(self.results)}")
        print(f"   Passed: {len(passed_tests)} [PASS]")
        print(f"   Failed: {len(failed_tests)} [FAIL]")
        print(f"   Success Rate: {len(passed_tests)/len(self.results)*100:.1f}%")
        print(f"   Total Time: {total_time:.2f} seconds")

        if passed_tests:
            print(f"\n[PASS] Passed Tests:")
            for test in passed_tests:
                print(f"   + {test.name} ({test.duration:.2f}s)")

        if failed_tests:
            print(f"\n[FAIL] Failed Tests:")
            for test in failed_tests:
                print(f"   - {test.name} ({test.duration:.2f}s)")
                if test.error:
                    print(f"     Error: {test.error}")

        # Overall assessment
        print(f"\n[ASSESSMENT] Overall Assessment:")
        if len(failed_tests) == 0:
            print("   [EXCELLENT] All tests passed! System is ready for production.")
        elif len(failed_tests) <= 2:
            print("   [GOOD] Most tests passed. Address minor issues before deployment.")
        elif len(failed_tests) <= 4:
            print("   [FAIR] Some tests failed. Review and fix issues before deployment.")
        else:
            print("   [POOR] Many tests failed. Significant issues need resolution.")

        # Key metrics
        print(f"\n[METRICS] Key Metrics:")
        performance_test = next((r for r in self.results if "Performance" in r.name), None)
        if performance_test and performance_test.passed:
            details = performance_test.details
            print(f"   - First run time: {details.get('first_run_time', 0):.2f}s")
            print(f"   - Cached run time: {details.get('second_run_time', 0):.2f}s")
            print(f"   - Caching active: {details.get('cache_active', False)}")

        data_test = next((r for r in self.results if "Data Integration" in r.name), None)
        if data_test and data_test.passed:
            details = data_test.details
            print(f"   - Suppliers loaded: {details.get('suppliers_loaded', 0)}")
            print(f"   - Customers loaded: {details.get('customers_loaded', 0)}")

        enhanced_test = next((r for r in self.results if "Enhanced Features" in r.name), None)
        if enhanced_test and enhanced_test.passed:
            details = enhanced_test.details
            print(f"   - System mode: {details.get('system_mode', 'unknown')}")
            print(f"   - Active plugins: {details.get('plugin_count', 0)}")

        print(f"\n{'='*80}")
        print("[COMPLETE] Enhanced Compliance Agent Integration Test Complete!")
        print(f"{'='*80}")

        return len(failed_tests) == 0


def main():
    """Run the final integration test suite."""
    test_suite = FinalIntegrationTestSuite()
    all_passed = test_suite.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()