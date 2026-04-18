#!/usr/bin/env python
"""
Phase 1 Pipeline Demo - Complete vitamin D consolidation analysis.

Demonstrates the end-to-end workflow from database extraction through
consolidation recommendations.
"""

from pipeline import Phase1Pipeline
import json


def main():
    """Run Phase 1 pipeline demo."""
    print("=" * 80)
    print("PHASE 1 VITAMIN D CONSOLIDATION PIPELINE")
    print("=" * 80)

    # Initialize pipeline with mock API (can set use_mock_api=False for real Claude)
    print("\n[1] Initializing pipeline...")
    pipeline = Phase1Pipeline(use_mock_api=True)
    print("    [OK] Pipeline initialized")

    # Run pipeline
    print("\n[2] Running consolidation analysis...")
    result = pipeline.run()
    print(f"    [OK] Pipeline complete")

    # Display results
    print("\n" + "=" * 80)
    print("PIPELINE RESULTS")
    print("=" * 80)

    print(f"\n{result.execution_summary}")

    # Show consolidation recommendations
    if result.consolidation_analyses:
        print("\n" + "=" * 80)
        print("CONSOLIDATION RECOMMENDATIONS")
        print("=" * 80)

        for i, analysis in enumerate(result.consolidation_analyses[:3], 1):
            print(f"\n[Recommendation {i}]")
            print(f"  Verdict: {analysis.verdict}")
            print(f"  Confidence: {analysis.confidence:.1%}")
            print(f"  Reasoning: {analysis.reasoning[:100]}...")

            if analysis.claims:
                print(f"  Key Claims: {len(analysis.claims)}")
            if analysis.missing_evidence:
                print(f"  Missing Evidence: {len(analysis.missing_evidence)}")

        if len(result.consolidation_analyses) > 3:
            print(f"\n... and {len(result.consolidation_analyses) - 3} more recommendations")

    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
