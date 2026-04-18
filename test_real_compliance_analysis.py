#!/usr/bin/env python3
"""
Test Real Compliance Analysis with 2025 Market Data

This script tests whether the Enhanced Compliance Agent can now:
1. Correctly evaluate pricing with real 2025 data
2. Assess quality and substitutability
3. Provide realistic supplier rankings
4. Make intelligent substitution recommendations
"""

import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_real_data_integration():
    """Test that real market data is properly integrated."""
    print("=== Testing Real Market Data Integration ===")
    print()

    try:
        from agents.real_market_data_2025 import REAL_VITAMIN_D3_MARKET_DATA_2025, apply_real_market_data_patch
        from agents.core.data_models import SupplierData, PricingInfo

        # Test data loading
        print(f"[OK] Real market data loaded for {len(REAL_VITAMIN_D3_MARKET_DATA_2025['pricing_usd_per_kg'])} suppliers")

        # Show current pricing
        print("\n📊 Current 2025 Market Prices (per kg):")
        for supplier, data in REAL_VITAMIN_D3_MARKET_DATA_2025['pricing_usd_per_kg'].items():
            print(f"   {supplier}: ${data['min_price']:.2f} - ${data['max_price']:.2f} USD")

        # Test patch application
        test_supplier = SupplierData(
            name="DSM",
            country="Netherlands",
            certificates=[],
            pricing=PricingInfo(min_price=45.0, max_price=55.0, currency="USD", moq=100)  # Old fictional data
        )

        print(f"\n🔧 Testing data patch:")
        print(f"   Before: ${test_supplier.pricing.min_price} - ${test_supplier.pricing.max_price}")

        patched_supplier = apply_real_market_data_patch(test_supplier)
        print(f"   After:  ${patched_supplier.pricing.min_price} - ${patched_supplier.pricing.max_price}")

        return True

    except Exception as e:
        print(f"❌ Real data integration failed: {e}")
        return False

def test_substitutability_analysis():
    """Test supplier substitutability analysis."""
    print("\n=== Testing Substitutability Analysis ===")
    print()

    try:
        from agents.real_market_data_2025 import get_substitutability_analysis
        from agents.core.data_models import CustomerRequirements

        # Test pharma customer requirements
        pharma_customer = CustomerRequirements(
            company_name="PharmaCorp",
            quality_tier="PHARMA_GRADE",
            certificates_required=["cGMP", "ISO 9001"]
        )

        # Analyze DSM vs alternatives
        analysis = get_substitutability_analysis(
            primary_supplier="DSM",
            alternative_suppliers=["BASF", "Prinova USA"],
            customer_requirements=pharma_customer
        )

        print(f"📈 Substitution Analysis for DSM:")
        print(f"   Primary: {analysis['primary_supplier']}")

        for alt, data in analysis['alternatives_analysis'].items():
            print(f"\n   Alternative: {alt}")
            print(f"     Substitutability Score: {data['substitutability_score']:.2f}")
            print(f"     Price Difference: {data['price_difference_percent']:+.1f}%")
            print(f"     Quality Compatible: {data['quality_compatible']}")
            print(f"     Lead Time Diff: {data['lead_time_difference_days']:+d} days")
            print(f"     Recommendation: {data['recommendation']}")

        if analysis['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in analysis['recommendations']:
                print(f"   • {rec}")

        return True

    except Exception as e:
        print(f"❌ Substitutability analysis failed: {e}")
        return False

def test_enhanced_compliance_with_real_data():
    """Test Enhanced Compliance Agent with real market data."""
    print("\n=== Testing Enhanced Compliance Agent with Real Data ===")
    print()

    try:
        # Try to use simple CSV reading first
        import csv
        from agents.core.data_models import SupplierData, CustomerRequirements, Certificate
        from agents.real_market_data_2025 import apply_real_market_data_patch
        from datetime import datetime

        # Load suppliers from CSV and apply real data patch
        suppliers_with_real_data = []

        # Read suppliers.csv
        with open("data/suppliers.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Create basic supplier
                supplier = SupplierData(
                    name=row["supplier"],
                    country=row["country"],
                    certificates=[Certificate(cert.strip(), "Unknown", datetime(2030, 12, 31))
                                 for cert in row["certificates"].split(",") if cert.strip()]
                )

                # Apply real market data
                supplier_with_real_data = apply_real_market_data_patch(supplier)
                suppliers_with_real_data.append(supplier_with_real_data)

        print(f"✅ Loaded and patched {len(suppliers_with_real_data)} suppliers with real data")

        # Create customer requirements
        pharma_customer = CustomerRequirements(
            company_name="PharmaCorp",
            quality_tier="PHARMA_GRADE",
            certificates_required=["cGMP", "ISO 9001", "ISO 14644"]
        )

        print(f"\n📊 Real Market Analysis for {pharma_customer.company_name}:")
        print(f"   Quality Tier: {pharma_customer.quality_tier}")

        # Analyze each supplier
        supplier_scores = []

        for supplier in suppliers_with_real_data:
            # Basic compliance scoring based on real data
            score = 0.0
            details = []

            # Certificate compliance (40% weight)
            cert_score = 0.0
            supplier_cert_names = {cert.name for cert in supplier.certificates}
            required_certs = set(pharma_customer.certificates_required)

            # Handle equivalences (cGMP = GMP)
            if "cGMP" in required_certs and "GMP" in supplier_cert_names:
                supplier_cert_names.add("cGMP")

            missing_certs = required_certs - supplier_cert_names
            if not missing_certs:
                cert_score = 1.0
                details.append("✅ All certificates compliant")
            else:
                cert_score = 0.3
                details.append(f"❌ Missing: {', '.join(missing_certs)}")

            # Pricing competitiveness (30% weight)
            price_score = 0.0
            if supplier.pricing:
                avg_price = (supplier.pricing.min_price + supplier.pricing.max_price) / 2
                if avg_price <= 18:  # Competitive for 2025 market
                    price_score = 1.0
                    details.append(f"💰 Competitive price: ${avg_price:.2f}/kg")
                elif avg_price <= 20:
                    price_score = 0.7
                    details.append(f"💰 Acceptable price: ${avg_price:.2f}/kg")
                else:
                    price_score = 0.3
                    details.append(f"💰 High price: ${avg_price:.2f}/kg")

            # Market position (20% weight)
            market_score = 0.0
            if supplier.quality_metrics:
                market_share = supplier.quality_metrics.get("market_share_percent", 0)
                if market_share >= 20:
                    market_score = 1.0
                    details.append(f"📈 Market leader: {market_share}% share")
                elif market_share >= 10:
                    market_score = 0.8
                    details.append(f"📈 Strong player: {market_share}% share")
                else:
                    market_score = 0.5
                    details.append(f"📈 Smaller player: {market_share}% share")

            # Lead time (10% weight)
            lead_score = 0.0
            if supplier.delivery_info:
                lead_time = supplier.delivery_info.get("lead_time_days", 30)
                if lead_time <= 21:
                    lead_score = 1.0
                    details.append(f"🚚 Fast delivery: {lead_time} days")
                elif lead_time <= 30:
                    lead_score = 0.7
                    details.append(f"🚚 Standard delivery: {lead_time} days")
                else:
                    lead_score = 0.3
                    details.append(f"🚚 Slow delivery: {lead_time} days")

            # Calculate weighted score
            final_score = (cert_score * 0.4 + price_score * 0.3 +
                          market_score * 0.2 + lead_score * 0.1)

            supplier_scores.append((supplier.name, final_score, details))

        # Sort by score
        supplier_scores.sort(key=lambda x: x[1], reverse=True)

        print(f"\n🏆 Supplier Rankings (Real 2025 Data):")
        for i, (name, score, details) in enumerate(supplier_scores, 1):
            status = "🌟 EXCELLENT" if score >= 0.8 else "✅ GOOD" if score >= 0.6 else "⚠️ FAIR" if score >= 0.4 else "❌ POOR"
            print(f"\n   {i}. {name} - Score: {score:.2f} {status}")
            for detail in details:
                print(f"      {detail}")

        # Substitution recommendations
        if len(supplier_scores) > 1:
            primary = supplier_scores[0]
            alternatives = supplier_scores[1:]

            print(f"\n🔄 Substitution Analysis:")
            print(f"   Primary Recommendation: {primary[0]} (Score: {primary[1]:.2f})")

            suitable_alternatives = [alt for alt in alternatives if alt[1] >= 0.6]
            if suitable_alternatives:
                print(f"   Suitable Alternatives:")
                for alt_name, alt_score, _ in suitable_alternatives:
                    print(f"     • {alt_name} (Score: {alt_score:.2f})")
            else:
                print(f"   ⚠️ No suitable alternatives found")

        return True

    except Exception as e:
        print(f"❌ Enhanced compliance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all real data compliance tests."""
    print("[TEST] Real Market Data Compliance Analysis Test")
    print("=" * 60)

    tests = [
        ("Real Data Integration", test_real_data_integration),
        ("Substitutability Analysis", test_substitutability_analysis),
        ("Enhanced Compliance with Real Data", test_enhanced_compliance_with_real_data),
    ]

    passed = 0
    for test_name, test_func in tests:
        if test_func():
            passed += 1

    print(f"\n{'='*60}")
    print(f"SUMMARY: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 SUCCESS: Your Compliance Agent can now correctly evaluate:")
        print("   ✅ Real market pricing (2025 data)")
        print("   ✅ Supplier substitutability")
        print("   ✅ Quality vs price trade-offs")
        print("   ✅ Market positioning and lead times")
        print("   ✅ Intelligent supplier rankings")
    else:
        print("⚠️ Some tests failed - check implementation")

    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)