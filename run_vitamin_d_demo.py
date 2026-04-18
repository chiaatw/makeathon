#!/usr/bin/env python3
"""
Quick demo runner for vitamin D Equivalence-Agent testing.
Perfect for Phase 1 development and testing.
"""

import json
from equivalence_agent import call_equivalence_agent, test_equivalence_agent
from schemas import EquivalenceAgentInput, EndProductContext


def demo_small_cluster():
    """Demo with small vitamin D cluster (2 companies)."""
    print("=== SMALL CLUSTER DEMO ===")

    input_data = EquivalenceAgentInput(
        cluster_id="vitamin-d3-small-001",
        skus=[
            "RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1",
            "RM-C14-vitamin-d3-cholecalciferol-1000iu-8e9f3c42"
        ],
        affected_companies=["Nature Made", "Kirkland"],
        affected_boms=[15, 42],
        current_suppliers=["DSM", "BASF"],
        end_product_context=[
            EndProductContext(
                sku="FG-naturemade-12041",
                company="Nature Made",
                name_hint="Vitamin D3 1000 IU Softgels"
            ),
            EndProductContext(
                sku="FG-kirkland-89210",
                company="Kirkland",
                name_hint="Kirkland Vitamin D3 1000 IU"
            )
        ]
    )

    response = call_equivalence_agent(input_data, use_mock=True)
    print(f"Verdict: {response.verdict}")
    print(f"Confidence: {response.confidence}")
    print(f"Missing Evidence Items: {len(response.missing_evidence)}")
    print()


def demo_large_cluster():
    """Demo with large vitamin D cluster (complex scenario)."""
    print("=== LARGE COMPLEX CLUSTER DEMO ===")

    input_data = EquivalenceAgentInput(
        cluster_id="vitamin-d3-complex-001",
        skus=[
            "RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1",
            "RM-C14-vitamin-d3-cholecalciferol-2000iu-8e9f3c42",
            "RM-C27-vitamin-d3-powder-5000iu-bd4a1f89",
            "RM-C33-cholecalciferol-vitamin-d3-72c8e3d5",
            "RM-C41-vitamin-d3-oil-suspension-9f2a6b84",
            "RM-C52-vit-d3-micronized-powder-4d8e7a91"
        ],
        affected_companies=["Nature Made", "Kirkland", "Garden of Life", "NOW Foods", "Swanson", "Solgar"],
        affected_boms=[15, 42, 67, 89, 112, 134],
        current_suppliers=["DSM", "BASF", "Fermenta", "Zhejiang Medicine", "Dishman"],
        end_product_context=[
            EndProductContext(sku="FG-naturemade-12041", company="Nature Made", name_hint="Vitamin D3 1000 IU Softgels"),
            EndProductContext(sku="FG-kirkland-89210", company="Kirkland", name_hint="Extra Strength Vitamin D3 2000 IU"),
            EndProductContext(sku="FG-gardenlife-45678", company="Garden of Life", name_hint="Vitamin Code Raw D3 5000 IU"),
            EndProductContext(sku="FG-now-87432", company="NOW Foods", name_hint="Vitamin D-3 High Potency 5000 IU"),
            EndProductContext(sku="FG-swanson-23456", company="Swanson", name_hint="Vitamin D3 2000 IU Capsules"),
            EndProductContext(sku="FG-solgar-67890", company="Solgar", name_hint="Vitamin D3 1000 IU Tablets")
        ]
    )

    response = call_equivalence_agent(input_data, use_mock=True)
    print(f"Verdict: {response.verdict}")
    print(f"Confidence: {response.confidence}")
    print(f"Claims: {len(response.claims)}")
    print(f"Objections: {len(response.objections)}")
    print(f"Missing Evidence Items: {len(response.missing_evidence)}")
    print(f"Reasoning: {response.reasoning}")
    print()


def demo_calcium_citrate():
    """Demo with calcium citrate (alternative substance)."""
    print("=== CALCIUM CITRATE DEMO ===")

    input_data = EquivalenceAgentInput(
        cluster_id="calcium-citrate-001",
        skus=[
            "RM-C1-calcium-citrate-05c28cc3",
            "RM-C14-calcium-citrate-8e9f3c42",
            "RM-C27-calcium-citrate-bd4a1f89"
        ],
        affected_companies=["Caltrate", "Centrum", "Body Fortress"],
        affected_boms=[12, 47, 83],
        current_suppliers=["ADM", "Cargill", "BulkSupplements"],
        end_product_context=[
            EndProductContext(sku="FG-caltrate-10421", company="Caltrate", name_hint="Caltrate 600+D3 Calcium Supplement"),
            EndProductContext(sku="FG-centrum-20532", company="Centrum", name_hint="Centrum Silver Multivitamin"),
            EndProductContext(sku="FG-bodyfortress-30643", company="Body Fortress", name_hint="Super Advanced Calcium")
        ]
    )

    response = call_equivalence_agent(input_data, use_mock=True)
    print(f"Verdict: {response.verdict}")
    print(f"Confidence: {response.confidence}")
    print(f"Reasoning: {response.reasoning}")
    print()


if __name__ == "__main__":
    print("Agnes Equivalence-Agent Demo")
    print("=" * 50)
    print()

    # Run the original comprehensive test
    test_equivalence_agent()
    print("\n" + "=" * 50 + "\n")

    # Run additional demos
    demo_small_cluster()
    demo_large_cluster()
    demo_calcium_citrate()

    print("All demos completed successfully!")
    print("\nNext steps:")
    print("- Person 4: Start external enrichment for vitamin D suppliers")
    print("- Person 2: Begin Compliance-Agent prompt development")
    print("- Person 3: Start clustering real vitamin D SKUs from database")