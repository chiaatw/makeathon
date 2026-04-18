#!/usr/bin/env python3
"""Quick Integration Validation for Enhanced Compliance Agent.

This script performs essential validation tests to confirm the enhanced
compliance system is working correctly with existing data.
"""

import sys
from pathlib import Path
import time

# Add current directory to path for local imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_data_files():
    """Test 1: Verify data files exist and are readable."""
    print("Test 1: Data File Availability")
    print("-" * 40)

    data_dir = Path("data")
    required_files = [
        "suppliers.csv",
        "customer_requirements.csv",
        "external_evidence.json"
    ]

    all_files_found = True
    for file_name in required_files:
        file_path = data_dir / file_name
        if file_path.exists():
            print(f"  [OK] {file_name}")
        else:
            print(f"  [MISSING] {file_name}")
            all_files_found = False

    return all_files_found

def test_basic_imports():
    """Test 2: Verify core modules can be imported."""
    print("\nTest 2: Core Module Imports")
    print("-" * 40)

    import_results = {}

    # Test core data models
    try:
        from agents.core.data_models import SupplierData, CustomerRequirements, ComplianceResult
        print("  [OK] Core data models")
        import_results["core_models"] = True
    except ImportError as e:
        print(f"  [FAIL] Core data models: {e}")
        import_results["core_models"] = False

    # Test plugin system
    try:
        from agents.plugins.base import CompliancePlugin
        from agents.plugins.certificates import CertificatesPlugin
        print("  [OK] Plugin system")
        import_results["plugins"] = True
    except ImportError as e:
        print(f"  [FAIL] Plugin system: {e}")
        import_results["plugins"] = False

    # Test data sources
    try:
        from agents.data_sources.csv_adapter import CSVAdapter
        from agents.data_sources.json_adapter import JSONAdapter
        print("  [OK] Data source adapters")
        import_results["data_sources"] = True
    except ImportError as e:
        print(f"  [FAIL] Data source adapters: {e}")
        import_results["data_sources"] = False

    # Test scoring engine
    try:
        from agents.scoring.engine import ScoringEngine
        print("  [OK] Scoring engine")
        import_results["scoring"] = True
    except ImportError as e:
        print(f"  [FAIL] Scoring engine: {e}")
        import_results["scoring"] = False

    # Test compliance engine
    try:
        from agents.engine.compliance_engine import ComplianceEngine
        print("  [OK] Compliance engine")
        import_results["engine"] = True
    except ImportError as e:
        print(f"  [FAIL] Compliance engine: {e}")
        import_results["engine"] = False

    return all(import_results.values())

def test_legacy_compatibility():
    """Test 3: Verify legacy compatibility works."""
    print("\nTest 3: Legacy Compatibility")
    print("-" * 40)

    try:
        # Test original SimpleComplianceChecker still works
        from agents.simple_compliance_checker import SimpleComplianceChecker

        checker = SimpleComplianceChecker()
        result = checker.check("Vitamin D3", "DSM", "PharmaCorp")

        # Verify result structure
        has_required_attrs = all(
            hasattr(result, attr) for attr in
            ["compliance_status", "confidence", "reasoning", "synergy_potential"]
        )

        if has_required_attrs:
            print(f"  [OK] SimpleComplianceChecker works")
            print(f"       Status: {result.compliance_status}")
            print(f"       Confidence: {result.confidence:.1%}")
            return True
        else:
            print(f"  [FAIL] Missing attributes in result")
            return False

    except Exception as e:
        print(f"  [FAIL] Legacy compatibility error: {e}")
        return False

def test_plugin_functionality():
    """Test 4: Verify plugin system works."""
    print("\nTest 4: Plugin System")
    print("-" * 40)

    try:
        from agents.plugins.certificates import CertificatesPlugin
        from agents.core.data_models import SupplierData, CustomerRequirements, Certificate
        from datetime import datetime

        # Create test data
        supplier = SupplierData(
            name="Test Supplier",
            country="Netherlands",
            certificates=[
                Certificate("ISO 9001", "TUV SUD", datetime(2025, 12, 31)),
                Certificate("cGMP", "FDA", datetime(2026, 6, 30))
            ]
        )

        customer = CustomerRequirements(
            company_name="Test Customer",
            quality_tier="PHARMA_GRADE",
            certificates_required=["ISO 9001", "cGMP"]
        )

        # Test plugin
        plugin = CertificatesPlugin()
        result = plugin.check_compliance(supplier, customer, {})

        # Verify result
        if hasattr(result, "score") and hasattr(result, "confidence"):
            print(f"  [OK] Certificate plugin works")
            print(f"       Score: {result.score:.2f}")
            print(f"       Confidence: {result.confidence:.1%}")
            return True
        else:
            print(f"  [FAIL] Invalid plugin result")
            return False

    except Exception as e:
        print(f"  [FAIL] Plugin system error: {e}")
        return False

def test_data_loading():
    """Test 5: Verify data can be loaded from files."""
    print("\nTest 5: Data Loading")
    print("-" * 40)

    try:
        from agents.integration.legacy_csv_adapter import LegacySuppliersCSVAdapter, LegacyCustomerCSVAdapter
        from pathlib import Path

        # Test suppliers loading
        suppliers_adapter = LegacySuppliersCSVAdapter()
        suppliers = suppliers_adapter.load_suppliers(Path("data/suppliers.csv"))

        print(f"  [OK] Loaded {len(suppliers)} suppliers")
        if suppliers:
            sample = suppliers[0]
            print(f"       Sample: {sample.name} from {sample.country}")
            print(f"       Certificates: {len(sample.certificates)}")

        # Test customers loading
        customers_adapter = LegacyCustomerCSVAdapter()
        customers = customers_adapter.load_customer_requirements(Path("data/customer_requirements.csv"))

        print(f"  [OK] Loaded {len(customers)} customer requirements")
        if customers:
            sample = customers[0]
            print(f"       Sample: {sample.company_name} ({sample.quality_tier})")

        return len(suppliers) > 0 and len(customers) > 0

    except Exception as e:
        print(f"  [FAIL] Data loading error: {e}")
        return False

def test_enhanced_agent():
    """Test 6: Verify enhanced agent can be created and used."""
    print("\nTest 6: Enhanced Agent")
    print("-" * 40)

    try:
        # Try to create enhanced agent without the complex imports
        # by using the integration setup
        from agents.integration.data_integration import setup_integration

        agent = setup_integration("data")

        # Test basic compliance check
        result = agent.check_compliance("DSM", "PharmaCorp")
        print(f"  [OK] Enhanced agent created and tested")
        print(f"       Status: {result.compliance_status}")
        print(f"       Confidence: {result.confidence:.1%}")

        # Get system status
        status = agent.get_system_status()
        print(f"       Mode: {status['mode']}")

        return True

    except Exception as e:
        print(f"  [FAIL] Enhanced agent error: {e}")
        return False

def run_quick_validation():
    """Run all validation tests."""
    print("Enhanced Compliance Agent - Quick Integration Validation")
    print("=" * 60)

    start_time = time.time()

    # Run tests
    tests = [
        ("Data Files", test_data_files),
        ("Core Imports", test_basic_imports),
        ("Legacy Compatibility", test_legacy_compatibility),
        ("Plugin System", test_plugin_functionality),
        ("Data Loading", test_data_loading),
        ("Enhanced Agent", test_enhanced_agent),
    ]

    passed_tests = 0
    total_tests = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"\n{test_name} failed with exception: {e}")

    # Summary
    total_time = time.time() - start_time
    success_rate = (passed_tests / total_tests) * 100

    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print(f"Total Time: {total_time:.2f} seconds")

    if success_rate >= 80:
        print("Status: [EXCELLENT] System is ready for use!")
    elif success_rate >= 60:
        print("Status: [GOOD] Most features working, minor issues remain")
    else:
        print("Status: [NEEDS WORK] Significant issues need resolution")

    print(f"{'='*60}")

    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_quick_validation()
    sys.exit(0 if success else 1)