#!/usr/bin/env python3
"""Integration test script for Enhanced Compliance Agent with existing data.

This script tests the integration between the enhanced compliance system
and the existing data files (suppliers.csv, customer_requirements.csv,
external_evidence.json).
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from agents.data_sources.manager import MultiSourceDataManager
    from agents.integration.legacy_csv_adapter import LegacySuppliersCSVAdapter, LegacyCustomerCSVAdapter
    from agents.integration.data_integration import setup_integration, run_integration_validation
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the correct directory and all files are present.")
    sys.exit(1)


def test_legacy_adapters():
    """Test the legacy CSV adapters directly."""
    print("=== Testing Legacy CSV Adapters ===")

    data_dir = Path("data")

    # Test suppliers adapter
    print("\n1. Testing Suppliers CSV Adapter:")
    suppliers_adapter = LegacySuppliersCSVAdapter()

    try:
        suppliers = suppliers_adapter.load_suppliers(data_dir / "suppliers.csv")
        print(f"   ✓ Loaded {len(suppliers)} suppliers")

        if suppliers:
            sample = suppliers[0]
            print(f"   ✓ Sample supplier: {sample.name} from {sample.country}")
            print(f"   ✓ Certificates: {[c.name for c in sample.certificates]}")
    except Exception as e:
        print(f"   ✗ Error loading suppliers: {e}")

    # Test customers adapter
    print("\n2. Testing Customer Requirements CSV Adapter:")
    customers_adapter = LegacyCustomerCSVAdapter()

    try:
        customers = customers_adapter.load_customer_requirements(data_dir / "customer_requirements.csv")
        print(f"   ✓ Loaded {len(customers)} customer requirement sets")

        if customers:
            sample = customers[0]
            print(f"   ✓ Sample customer: {sample.company_name} ({sample.quality_tier})")
            print(f"   ✓ Required certificates: {sample.certificates_required}")
            print(f"   ✓ Constraints: {sample.constraints}")
    except Exception as e:
        print(f"   ✗ Error loading customers: {e}")


def test_enhanced_system():
    """Test the complete enhanced compliance system."""
    print("\n=== Testing Enhanced Compliance System ===")

    try:
        # Set up integration with existing data
        agent = setup_integration("data")
        print("   ✓ Enhanced compliance agent created successfully")

        # Get system status
        status = agent.get_system_status()
        print(f"   ✓ System mode: {status['mode']}")
        print(f"   ✓ Suppliers loaded: {status.get('data_status', {}).get('suppliers_loaded', 0)}")
        print(f"   ✓ Customers loaded: {status.get('data_status', {}).get('customers_loaded', 0)}")

        # Test basic compliance check (backward compatible)
        print("\n3. Testing Backward Compatible Interface:")
        try:
            result = agent.check_compliance("DSM", "PharmaCorp")
            print(f"   ✓ Compliance check: {result.compliance_status}")
            print(f"   ✓ Confidence: {result.confidence:.1%}")
            print(f"   ✓ Reasoning: {result.reasoning[:100]}...")
        except Exception as e:
            print(f"   ✗ Error in compliance check: {e}")

        # Test enhanced interface
        print("\n4. Testing Enhanced Interface:")
        try:
            enhanced_result = agent.check_compliance_enhanced("DSM", "PharmaCorp")
            print(f"   ✓ Enhanced compliance score: {enhanced_result.overall_score:.2f}")
            print(f"   ✓ Enhanced confidence: {enhanced_result.overall_confidence:.1%}")
            print(f"   ✓ Plugin results: {len(enhanced_result.plugin_results)}")

            for plugin_result in enhanced_result.plugin_results:
                print(f"     - {plugin_result.plugin_name}: {plugin_result.score:.2f} "
                      f"(conf: {plugin_result.confidence:.2f})")
        except Exception as e:
            print(f"   ✗ Error in enhanced compliance check: {e}")

        # Test supplier ranking
        print("\n5. Testing Supplier Ranking:")
        try:
            rankings = agent.rank_suppliers("PharmaCorp", limit=3)
            print(f"   ✓ Ranked {len(rankings)} suppliers for PharmaCorp:")

            for i, (supplier_name, result) in enumerate(rankings, 1):
                print(f"     {i}. {supplier_name}: {result.overall_score:.2f}")
        except Exception as e:
            print(f"   ✗ Error in supplier ranking: {e}")

    except Exception as e:
        print(f"   ✗ Error setting up enhanced system: {e}")


def main():
    """Run the complete integration test."""
    print("Enhanced Compliance Agent - Integration Test")
    print("=" * 50)

    # Test individual components
    test_legacy_adapters()

    # Test complete system
    test_enhanced_system()

    # Run comprehensive validation
    print("\n" + "=" * 50)
    run_integration_validation("data")


if __name__ == "__main__":
    main()