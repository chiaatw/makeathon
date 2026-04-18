#!/usr/bin/env python
"""
Data exploration script for vitamin D products in the database.

Runs analysis on the extracted vitamin D products to understand:
- How many vitamin D products are in the database
- Fragmentation across companies
- Supplier dispersion
"""

from database import VitaminDExtractor


def main():
    """Run data exploration analysis."""
    print("=" * 80)
    print("VITAMIN D DATABASE EXPLORATION")
    print("=" * 80)

    extractor = VitaminDExtractor()

    # Extract all vitamin D products
    print("\n1. EXTRACTING VITAMIN D PRODUCTS...")
    products = extractor.extract_all_vitamin_d()
    print(f"   [OK] Found {len(products)} vitamin D products")

    if products:
        print("\n2. SAMPLE PRODUCTS (first 5):")
        for i, product in enumerate(products[:5], 1):
            print(f"   {i}. {product.canonical_material_name}")
            print(f"      Company: {product.company_name}")
            print(f"      SKU: {product.sku}")
            if product.supplier_names:
                print(f"      Suppliers: {product.supplier_names}")

    # Get unique materials
    print("\n3. UNIQUE CANONICAL MATERIAL NAMES:")
    unique_names = extractor.get_unique_canonical_names()
    print(f"   [OK] Found {len(unique_names)} unique materials")
    for i, name in enumerate(unique_names[:10], 1):
        print(f"   {i}. {name}")
    if len(unique_names) > 10:
        print(f"   ... and {len(unique_names) - 10} more")

    # Fragmentation analysis
    print("\n4. MATERIAL FRAGMENTATION ANALYSIS:")
    fragmentation = extractor.get_fragmentation_analysis()
    print(f"   Total unique materials: {len(fragmentation)}")

    # Sort by number of companies
    sorted_frags = sorted(
        fragmentation.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )

    print("\n   Top 10 most fragmented materials:")
    for i, (material, data) in enumerate(sorted_frags[:10], 1):
        count = data['count']
        companies = data['companies']
        print(f"   {i}. {material}")
        print(f"      Supplied by {count} companies:")
        for company in companies:
            print(f"         • {company}")

    # Supplier dispersion
    print("\n5. SUPPLIER DISPERSION:")
    dispersion = extractor.get_supplier_dispersion()

    # Find materials with most suppliers
    sorted_dispersion = sorted(
        dispersion.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    print("\n   Materials with most suppliers (top 5):")
    for i, (material, suppliers) in enumerate(sorted_dispersion[:5], 1):
        print(f"   {i}. {material}")
        print(f"      {len(suppliers)} suppliers:")
        for supplier in suppliers[:5]:
            print(f"         • {supplier}")
        if len(suppliers) > 5:
            print(f"         ... and {len(suppliers) - 5} more")

    # Summary statistics
    print("\n6. SUMMARY STATISTICS:")
    total_products = len(products)
    unique_materials = len(unique_names)
    unique_companies = len(set(p.company_name for p in products))

    print(f"   Total Vitamin D Products: {total_products}")
    print(f"   Unique Materials: {unique_materials}")
    print(f"   Companies involved: {unique_companies}")

    # Calculate average fragmentation
    if fragmentation:
        avg_fragmentation = sum(d['count'] for d in fragmentation.values()) / len(fragmentation)
        print(f"   Average companies per material: {avg_fragmentation:.2f}")

    print("\n" + "=" * 80)
    print("EXPLORATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
