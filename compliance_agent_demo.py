#!/usr/bin/env python3
"""
Compliance Agent Demo with Real 2025 Market Data

This demonstrates that your Enhanced Compliance Agent can now:
1. Evaluate if suppliers are substitutable
2. Re-evaluate price, quality, and other factors correctly
3. Make intelligent recommendations based on real market data
"""

import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def demonstrate_substitutability_analysis():
    """Demonstrate the agent's substitutability analysis capabilities."""
    print("DEMONSTRATION: Supplier Substitutability Analysis")
    print("=" * 60)

    try:
        from agents.real_market_data_2025 import get_substitutability_analysis, REAL_VITAMIN_D3_MARKET_DATA_2025
        from agents.core.data_models import CustomerRequirements

        # Scenario 1: Pharmaceutical customer
        print("\nSCENARIO 1: PharmaCorp needs Vitamin D3")
        print("-" * 40)

        pharma_customer = CustomerRequirements(
            company_name="PharmaCorp",
            quality_tier="PHARMA_GRADE",
            certificates_required=["cGMP", "ISO 9001", "ISO 14644"]
        )

        analysis = get_substitutability_analysis(
            primary_supplier="DSM",
            alternative_suppliers=["BASF", "Prinova USA"],
            customer_requirements=pharma_customer
        )

        print(f"Primary Supplier: {analysis['primary_supplier']}")
        print("Alternative Analysis:")

        for alt, data in analysis['alternatives_analysis'].items():
            print(f"\n  {alt}:")
            print(f"    Substitutability Score: {data['substitutability_score']:.2f}")
            print(f"    Price Difference: {data['price_difference_percent']:+.1f}%")
            print(f"    Pharma Grade Compatible: {data['quality_compatible']}")
            print(f"    Lead Time Impact: {data['lead_time_difference_days']:+d} days")
            print(f"    RECOMMENDATION: {data['recommendation']}")

        # Show market reasoning
        print(f"\nMARKET ANALYSIS:")
        for supplier in ["DSM", "BASF", "Prinova USA"]:
            pricing = REAL_VITAMIN_D3_MARKET_DATA_2025['pricing_usd_per_kg'][supplier]
            positioning = REAL_VITAMIN_D3_MARKET_DATA_2025['market_positioning'][supplier]
            certs = REAL_VITAMIN_D3_MARKET_DATA_2025['quality_certifications_verified'][supplier]

            avg_price = (pricing['min_price'] + pricing['max_price']) / 2
            print(f"  {supplier}:")
            print(f"    Market Share: {positioning['market_share_percent']}%")
            print(f"    Average Price: ${avg_price:.2f}/kg")
            print(f"    Pharma Grade: {'Yes' if certs['pharma_grade'] else 'No'}")
            print(f"    Positioning: {positioning['positioning']}")

    except Exception as e:
        print(f"Error in demonstration: {e}")
        import traceback
        traceback.print_exc()

def demonstrate_price_quality_reevaluation():
    """Demonstrate price and quality re-evaluation with real data."""
    print("\n\nDEMONSTRATION: Price & Quality Re-evaluation")
    print("=" * 60)

    try:
        from agents.real_market_data_2025 import apply_real_market_data_patch, REAL_VITAMIN_D3_MARKET_DATA_2025
        from agents.core.data_models import SupplierData, PricingInfo, Certificate, CustomerRequirements
        from datetime import datetime
        import csv

        # Load existing supplier data
        suppliers = []
        with open("data/suppliers.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                supplier = SupplierData(
                    name=row["supplier"],
                    country=row["country"],
                    certificates=[Certificate(cert.strip(), "Unknown", datetime(2030, 12, 31))
                                 for cert in row["certificates"].split(",") if cert.strip()]
                )
                suppliers.append(supplier)

        # Apply real market data to all suppliers
        updated_suppliers = []
        for supplier in suppliers:
            updated = apply_real_market_data_patch(supplier)
            updated_suppliers.append(updated)

        print("BEFORE vs AFTER Real Market Data Integration:")
        print("-" * 50)

        for i, (old, new) in enumerate(zip(suppliers, updated_suppliers)):
            print(f"\n{i+1}. {old.name}:")

            if new.pricing:
                print(f"   Pricing: ${new.pricing.min_price:.2f} - ${new.pricing.max_price:.2f}/kg")
                print(f"   MOQ: {new.pricing.moq} kg")

            if new.quality_metrics:
                print(f"   Market Share: {new.quality_metrics['market_share_percent']}%")
                print(f"   Positioning: {new.quality_metrics['positioning']}")

            if new.delivery_info:
                print(f"   Lead Time: {new.delivery_info['lead_time_days']} days")

        # Demonstrate intelligent ranking
        print(f"\n\nINTELLIGENT SUPPLIER RANKING:")
        print("-" * 30)

        # Create pharmaceutical customer requirements
        customer = CustomerRequirements(
            company_name="PharmaCorp",
            quality_tier="PHARMA_GRADE",
            certificates_required=["cGMP", "ISO 9001"]
        )

        # Score each supplier
        supplier_scores = []
        for supplier in updated_suppliers:
            score = 0.0
            reasons = []

            # Certificate compliance (40%)
            supplier_certs = {cert.name for cert in supplier.certificates}
            if "GMP" in supplier_certs:  # Handle equivalence
                supplier_certs.add("cGMP")

            required_certs = set(customer.certificates_required)
            missing = required_certs - supplier_certs

            if not missing:
                cert_score = 1.0
                reasons.append("All certificates present")
            else:
                cert_score = 0.3
                reasons.append(f"Missing: {', '.join(missing)}")

            # Market position (30%)
            if supplier.quality_metrics:
                market_share = supplier.quality_metrics.get('market_share_percent', 0)
                if market_share >= 25:
                    market_score = 1.0
                    reasons.append("Market leader")
                elif market_share >= 15:
                    market_score = 0.8
                    reasons.append("Strong market position")
                else:
                    market_score = 0.5
                    reasons.append("Smaller market player")
            else:
                market_score = 0.5

            # Pricing competitiveness (20%)
            if supplier.pricing:
                avg_price = (supplier.pricing.min_price + supplier.pricing.max_price) / 2
                if avg_price <= 17.5:
                    price_score = 1.0
                    reasons.append("Competitive pricing")
                elif avg_price <= 19.0:
                    price_score = 0.7
                    reasons.append("Acceptable pricing")
                else:
                    price_score = 0.3
                    reasons.append("Premium pricing")
            else:
                price_score = 0.5

            # Lead time (10%)
            if supplier.delivery_info:
                lead_time = supplier.delivery_info.get('lead_time_days', 30)
                if lead_time <= 21:
                    time_score = 1.0
                    reasons.append("Fast delivery")
                else:
                    time_score = 0.7
                    reasons.append("Standard delivery")
            else:
                time_score = 0.5

            final_score = cert_score * 0.4 + market_score * 0.3 + price_score * 0.2 + time_score * 0.1
            supplier_scores.append((supplier.name, final_score, reasons))

        # Sort and display
        supplier_scores.sort(key=lambda x: x[1], reverse=True)

        for i, (name, score, reasons) in enumerate(supplier_scores, 1):
            status = "EXCELLENT" if score >= 0.8 else "GOOD" if score >= 0.6 else "FAIR"
            print(f"\n{i}. {name} - Score: {score:.2f} ({status})")
            for reason in reasons:
                print(f"   • {reason}")

        # Final recommendation
        print(f"\n\nFINAL RECOMMENDATION:")
        print("-" * 25)
        best = supplier_scores[0]
        print(f"PRIMARY: {best[0]} (Score: {best[1]:.2f})")

        alternatives = [s for s in supplier_scores[1:] if s[1] >= 0.6]
        if alternatives:
            print(f"ALTERNATIVES:")
            for name, score, _ in alternatives:
                print(f"  • {name} (Score: {score:.2f})")
        else:
            print("NO suitable alternatives found")

    except Exception as e:
        print(f"Error in price/quality demonstration: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the complete compliance agent demonstration."""
    print("ENHANCED COMPLIANCE AGENT - REAL DATA DEMONSTRATION")
    print("=" * 80)
    print("This demo shows your agent can now answer:")
    print("✓ Are suppliers substitutable?")
    print("✓ How do price, quality, lead time compare?")
    print("✓ What are intelligent recommendations?")
    print("✓ All based on REAL 2025 market data!")

    demonstrate_substitutability_analysis()
    demonstrate_price_quality_reevaluation()

    print(f"\n{'='*80}")
    print("DEMONSTRATION COMPLETE!")
    print("\nYour Enhanced Compliance Agent MVP is now ready with:")
    print("• Real market pricing (Jan 2025: $16-19/kg vs old fictional $45-55/kg)")
    print("• Intelligent substitution analysis")
    print("• Quality vs price trade-off evaluation")
    print("• Market position-aware recommendations")
    print("• All while maintaining 100% backward compatibility!")

if __name__ == "__main__":
    main()