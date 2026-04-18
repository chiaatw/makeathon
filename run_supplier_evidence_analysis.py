#!/usr/bin/env python
"""
Supplier evidence exploration script.

Demonstrates the cached supplier evidence and key metrics.
"""

from enrichment import SupplierEvidenceCache


def main():
    """Explore supplier evidence cache."""
    print("=" * 80)
    print("SUPPLIER EVIDENCE CACHE EXPLORATION")
    print("=" * 80)

    cache = SupplierEvidenceCache()

    # Load all evidence
    print("\n1. LOADING SUPPLIER EVIDENCE...")
    all_evidence = cache.load_evidence()
    print(f"   [OK] Loaded {len(all_evidence)} evidence entries")

    # Get suppliers for vitamin D3
    print("\n2. SUPPLIERS FOR VITAMIN D3...")
    suppliers = cache.get_suppliers_for_substance("Vitamin D3")
    print(f"   Total suppliers: {len(suppliers)}")
    for supplier in suppliers:
        print(f"   - {supplier}")

    # Show details for each supplier
    print("\n3. SUPPLIER DETAILS FOR VITAMIN D3:")
    for supplier_name in suppliers:
        evidence = cache.get_evidence_for_supplier(supplier_name)
        if evidence:
            print(f"\n   [{supplier_name}]")
            print(f"   Certifications: {', '.join(evidence.quality_certifications)}")
            print(f"   Pricing: {evidence.pricing_range_per_kg}/kg")
            print(f"   MOQ: {evidence.moq_units} kg")
            print(f"   Lead time: {evidence.lead_time_days} days")
            print(f"   Notes: {evidence.compliance_notes}")

    # Certification analysis
    print("\n4. CERTIFICATION ANALYSIS:")
    for cert in ["USP", "ISO 9001", "GMP"]:
        certified = cache.get_evidence_by_certification(cert)
        suppliers_with_cert = set(e.supplier_name for e in certified)
        print(f"   {cert}: {len(suppliers_with_cert)} suppliers")

    # Cost analysis
    print("\n5. COST ANALYSIS FOR VITAMIN D3:")
    evidence_list = cache.get_evidence_for_substance("Vitamin D3")
    price_ranges = {}
    for evidence in evidence_list:
        min_price, max_price = evidence.get_price_range()
        price_ranges[evidence.supplier_name] = (min_price, max_price)

    print("   Sorted by maximum price (descending):")
    for supplier, (min_p, max_p) in sorted(price_ranges.items(), key=lambda x: x[1][1], reverse=True):
        print(f"   ${min_p:.0f}-${max_p:.0f}: {supplier}")

    # Best options
    print("\n6. SUPPLIER RECOMMENDATIONS:")
    premium = cache.get_premium_suppliers("Vitamin D3")
    cost_effective = cache.get_most_cost_effective("Vitamin D3")

    print(f"\n   Premium suppliers (USP certified): {len(premium)}")
    for evidence in premium:
        print(f"   - {evidence.supplier_name}")

    if cost_effective:
        min_price, max_price = cost_effective.get_price_range()
        print(f"\n   Most cost-effective: {cost_effective.supplier_name}")
        print(f"   Price: ${min_price:.0f}-${max_price:.0f}/kg")

    print("\n" + "=" * 80)
    print("EXPLORATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
