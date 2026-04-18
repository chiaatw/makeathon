#!/usr/bin/env python3
"""Simple test to verify existing data files can be read."""

import csv
import json
from pathlib import Path

def test_data_files():
    """Test reading existing data files directly."""
    print("=== Simple Data File Test ===")

    data_dir = Path("data")

    # Test suppliers.csv
    suppliers_file = data_dir / "suppliers.csv"
    if suppliers_file.exists():
        print("\n1. Reading suppliers.csv:")
        try:
            with open(suppliers_file, 'r') as f:
                reader = csv.DictReader(f)
                suppliers = list(reader)
                print(f"   [OK] Found {len(suppliers)} suppliers")

                if suppliers:
                    sample = suppliers[0]
                    print(f"   [OK] Sample: {sample}")

        except Exception as e:
            print(f"   [ERROR] Error reading suppliers.csv: {e}")
    else:
        print(f"   [ERROR] File not found: {suppliers_file}")

    # Test customer_requirements.csv
    customers_file = data_dir / "customer_requirements.csv"
    if customers_file.exists():
        print("\n2. Reading customer_requirements.csv:")
        try:
            with open(customers_file, 'r') as f:
                reader = csv.DictReader(f)
                customers = list(reader)
                print(f"   [OK] Found {len(customers)} customer requirements")

                if customers:
                    sample = customers[0]
                    print(f"   [OK] Sample: {sample}")

        except Exception as e:
            print(f"   [ERROR] Error reading customer_requirements.csv: {e}")
    else:
        print(f"   [ERROR] File not found: {customers_file}")

    # Test external_evidence.json
    evidence_file = data_dir / "external_evidence.json"
    if evidence_file.exists():
        print("\n3. Reading external_evidence.json:")
        try:
            with open(evidence_file, 'r') as f:
                data = json.load(f)
                print(f"   [OK] Loaded JSON data")

                if isinstance(data, dict) and "suppliers" in data:
                    suppliers = data["suppliers"]
                    print(f"   [OK] Found {len(suppliers)} suppliers in external evidence")

                    if suppliers:
                        sample = suppliers[0]
                        print(f"   [OK] Sample supplier: {sample.get('supplier_name', 'Unknown')}")

        except Exception as e:
            print(f"   [ERROR] Error reading external_evidence.json: {e}")
    else:
        print(f"   [ERROR] File not found: {evidence_file}")

if __name__ == "__main__":
    test_data_files()