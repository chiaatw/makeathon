#!/usr/bin/env python3
"""Demonstration of Enhanced Compliance Agent with existing data.

This script shows how the enhanced compliance system works with the
existing data files and provides examples of both backward-compatible
and enhanced functionality.
"""

import sys
from pathlib import Path

# Set up Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def demo_backward_compatibility():
    """Demonstrate backward compatibility with original interface."""
    print("=== Backward Compatibility Demo ===")
    print()

    # Import the original function that now uses enhanced features automatically
    try:
        # This will work exactly like before, but use enhanced system when available
        from agents.enhanced_compliance_agent import call_compliance_agent

        print("Testing original function signature:")

        # Example 1: Compliant supplier (like original)
        print("\n1. DSM -> PharmaCorp (Should be compliant)")
        result = call_compliance_agent("Vitamin D3", "DSM", "PharmaCorp")
        print(f"   Status: {result.compliance_status}")
        print(f"   Confidence: {result.confidence:.0%}")
        print(f"   Reasoning: {result.reasoning}")

        # Example 2: Test with different customer
        print("\n2. BASF -> FoodSupplementCo (Different requirements)")
        result = call_compliance_agent("Vitamin D3", "BASF", "FoodSupplementCo")
        print(f"   Status: {result.compliance_status}")
        print(f"   Confidence: {result.confidence:.0%}")
        print(f"   Reasoning: {result.reasoning}")

        # Example 3: Unknown supplier (should show intelligent fallback)
        print("\n3. Unknown Supplier -> PharmaCorp (Should handle gracefully)")
        result = call_compliance_agent("Vitamin D3", "UnknownSupplier", "PharmaCorp")
        print(f"   Status: {result.compliance_status}")
        print(f"   Confidence: {result.confidence:.0%}")
        print(f"   Reasoning: {result.reasoning}")

    except ImportError as e:
        print(f"Backward compatibility test failed: {e}")
        print("Enhanced system not fully available - would fall back to legacy mode")


def demo_enhanced_features():
    """Demonstrate enhanced features and capabilities."""
    print("\n\n=== Enhanced Features Demo ===")
    print()

    try:
        from agents.enhanced_compliance_agent import EnhancedComplianceAgent

        # Create enhanced agent with existing data
        print("Creating Enhanced Compliance Agent with existing data sources...")

        data_sources = [
            {"path": "data/suppliers.csv", "type": "legacy_suppliers_csv"},
            {"path": "data/customer_requirements.csv", "type": "legacy_customers_csv"},
            {"path": "data/external_evidence.json", "type": "json"},
        ]

        agent = EnhancedComplianceAgent(
            data_sources=data_sources,
            use_enhanced_mode=True,
            legacy_fallback=True
        )

        # Check system status
        status = agent.get_system_status()
        print(f"✓ System initialized in {status['mode']} mode")
        print(f"✓ Suppliers loaded: {status.get('data_status', {}).get('suppliers_loaded', 0)}")
        print(f"✓ Customers loaded: {status.get('data_status', {}).get('customers_loaded', 0)}")

        # Enhanced compliance check with full details
        print("\n1. Enhanced Compliance Analysis:")
        print("   Analyzing DSM for PharmaCorp with full transparency...")

        enhanced_result = agent.check_compliance_enhanced("DSM", "PharmaCorp")
        print(f"   Overall Score: {enhanced_result.overall_score:.3f}")
        print(f"   Overall Confidence: {enhanced_result.overall_confidence:.2%}")

        print("   Plugin Analysis:")
        for plugin_result in enhanced_result.plugin_results:
            print(f"     - {plugin_result.plugin_name}: {plugin_result.score:.3f} "
                  f"(confidence: {plugin_result.confidence:.2%})")
            if plugin_result.blocking_issues:
                print(f"       Blocking issues: {plugin_result.blocking_issues}")

        print("   Reasoning Chain:")
        for i, reason in enumerate(enhanced_result.reasoning_chain, 1):
            print(f"     {i}. {reason}")

        # Supplier ranking
        print("\n2. Supplier Ranking for PharmaCorp:")
        rankings = agent.rank_suppliers("PharmaCorp", limit=5)

        print("   Ranked suppliers:")
        for i, (supplier_name, result) in enumerate(rankings, 1):
            print(f"     {i}. {supplier_name}: {result.overall_score:.3f} "
                  f"(confidence: {result.overall_confidence:.2%})")

        # Custom scoring configuration
        print("\n3. Custom Scoring Configuration:")
        print("   Reconfiguring to prioritize certificates heavily...")

        agent.configure_scoring(
            plugin_weights={"certificates": 0.8},
            aggregation_method="weighted_average"
        )

        # Re-run analysis with new scoring
        new_result = agent.check_compliance_enhanced("BASF", "PharmaCorp")
        print(f"   New score for BASF: {new_result.overall_score:.3f}")
        print(f"   (Previous scoring would be different)")

    except ImportError as e:
        print(f"Enhanced features demo failed: {e}")
        print("This indicates the enhanced system is not fully available")
    except Exception as e:
        print(f"Enhanced features demo error: {e}")


def demo_data_integration():
    """Demonstrate how the system integrates multiple data sources."""
    print("\n\n=== Data Integration Demo ===")
    print()

    print("Data Source Integration:")
    print("1. suppliers.csv -> Core supplier and certificate data")
    print("2. customer_requirements.csv -> Customer compliance requirements")
    print("3. external_evidence.json -> Enhanced supplier metadata")
    print()
    print("Integration Features:")
    print("✓ Automatic data source detection and format mapping")
    print("✓ Conflict resolution when same supplier appears in multiple sources")
    print("✓ Data freshness tracking and caching")
    print("✓ Graceful handling of missing or malformed data")
    print("✓ Backward compatibility with existing simple compliance checker")


def main():
    """Run the complete demonstration."""
    print("Enhanced Compliance Agent - Integration Demonstration")
    print("=" * 60)

    # Show data integration approach
    demo_data_integration()

    # Show backward compatibility
    demo_backward_compatibility()

    # Show enhanced features
    demo_enhanced_features()

    print("\n" + "=" * 60)
    print("Demonstration Complete!")
    print()
    print("Key Benefits Shown:")
    print("✓ Seamless backward compatibility")
    print("✓ Enhanced multi-source data integration")
    print("✓ Configurable scoring and ranking")
    print("✓ Detailed transparency and reasoning")
    print("✓ Robust error handling and fallbacks")


if __name__ == "__main__":
    main()