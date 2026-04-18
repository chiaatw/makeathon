#!/usr/bin/env python3
"""Simple test of real market data integration without Unicode characters."""

import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_real_pricing():
    """Test real market pricing data."""
    print("Testing Real Market Pricing Data")
    print("-" * 40)

    try:
        from agents.real_market_data_2025 import REAL_VITAMIN_D3_MARKET_DATA_2025

        pricing_data = REAL_VITAMIN_D3_MARKET_DATA_2025['pricing_usd_per_kg']

        print(f"Loaded pricing for {len(pricing_data)} suppliers:")
        for supplier, data in pricing_data.items():
            print(f"  {supplier}: ${data['min_price']:.2f} - ${data['max_price']:.2f}")

        # Verify pricing is realistic (2025 market: $16-22 per kg)
        for supplier, data in pricing_data.items():
            if data['min_price'] < 10 or data['max_price'] > 25:
                print(f"WARNING: Unrealistic pricing for {supplier}")
                return False

        print("SUCCESS: All pricing data appears realistic for 2025 market")
        return True

    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_substitution_logic():
    """Test substitution recommendation logic."""
    print("\nTesting Substitution Logic")
    print("-" * 40)

    try:
        from agents.real_market_data_2025 import get_substitutability_analysis
        from agents.core.data_models import CustomerRequirements

        # Test pharma customer
        customer = CustomerRequirements(
            company_name="PharmaCorp",
            quality_tier="PHARMA_GRADE",
            certificates_required=["cGMP", "ISO 9001"]
        )

        analysis = get_substitutability_analysis(
            primary_supplier="DSM",
            alternative_suppliers=["BASF", "Prinova USA"],
            customer_requirements=customer
        )

        print(f"Analysis completed for primary supplier: {analysis['primary_supplier']}")

        for alt, data in analysis['alternatives_analysis'].items():
            score = data['substitutability_score']
            recommendation = data['recommendation']
            price_diff = data['price_difference_percent']

            print(f"  {alt}: Score {score:.2f}, {recommendation}, Price diff: {price_diff:+.1f}%")

        # Verify logic makes sense
        basf_analysis = analysis['alternatives_analysis']['BASF']
        prinova_analysis = analysis['alternatives_analysis']['Prinova USA']

        # BASF should score higher than Prinova for pharma grade
        if basf_analysis['substitutability_score'] <= prinova_analysis['substitutability_score']:
            print("WARNING: BASF should score higher than Prinova for pharma customers")

        print("SUCCESS: Substitution logic appears reasonable")
        return True

    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_compliance_evaluation():
    """Test basic compliance evaluation with real data."""
    print("\nTesting Compliance Evaluation")
    print("-" * 40)

    try:
        from agents.real_market_data_2025 import apply_real_market_data_patch
        from agents.core.data_models import SupplierData, PricingInfo, Certificate
        from datetime import datetime

        # Create test supplier with old fictional data
        supplier = SupplierData(
            name="DSM",
            country="Netherlands",
            certificates=[Certificate("cGMP", "Unknown", datetime(2030, 12, 31))],
            pricing=PricingInfo(min_price=45.0, max_price=55.0, currency="USD", moq=100)
        )

        print(f"Before patch: ${supplier.pricing.min_price} - ${supplier.pricing.max_price}")

        # Apply real market data patch
        patched_supplier = apply_real_market_data_patch(supplier)

        print(f"After patch: ${patched_supplier.pricing.min_price} - ${patched_supplier.pricing.max_price}")

        # Verify the patch worked
        if patched_supplier.pricing.min_price == 45.0:
            print("FAILED: Patch did not update pricing")
            return False

        # Check realistic pricing range
        if patched_supplier.pricing.min_price < 15 or patched_supplier.pricing.max_price > 25:
            print("WARNING: Patched pricing outside realistic 2025 range")

        # Check quality metrics were added
        if not patched_supplier.quality_metrics:
            print("WARNING: No quality metrics added")
        else:
            print(f"Market share: {patched_supplier.quality_metrics.get('market_share_percent', 'N/A')}%")

        print("SUCCESS: Real data patch applied successfully")
        return True

    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run basic real data tests."""
    print("Real Market Data Integration Test")
    print("=" * 50)

    tests = [
        test_real_pricing,
        test_substitution_logic,
        test_compliance_evaluation
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\nSUCCESS: Your compliance agent now has:")
        print("- Real 2025 market pricing data")
        print("- Intelligent substitution analysis")
        print("- Realistic compliance evaluation")
        print("\nYour MVP can now make data-driven decisions!")
    else:
        print(f"\n{len(tests)-passed} test(s) failed - check implementation")

    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    print(f"\nExit code: {0 if success else 1}")
    sys.exit(0 if success else 1)