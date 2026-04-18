"""
Integration: How to use SimpleComplianceChecker in Phase1Pipeline.

This shows how the compliance check fits into the multi-agent flow.
"""

from simple_compliance_checker import SimpleComplianceChecker, ComplianceAgentOutput


def call_compliance_agent(
    material: str,
    supplier: str,
    customer: str = "FoodSupplementCo"
) -> ComplianceAgentOutput:
    """
    Call compliance checker (MVP version).

    This is much simpler than the prompt-based approach!

    Args:
        material: e.g. "Vitamin D3"
        supplier: e.g. "DSM"
        customer: e.g. "PharmaCorp" (defaults to FoodSupplementCo)

    Returns:
        ComplianceAgentOutput with status and reasoning
    """

    checker = SimpleComplianceChecker()
    return checker.check(material, supplier, customer)


# ========== EXAMPLE USAGE ==========

if __name__ == "__main__":
    # Example 1: Compliant supplier
    print("=" * 80)
    print("EXAMPLE 1: DSM -> PharmaCorp (Compliant)")
    print("=" * 80)

    result = call_compliance_agent("Vitamin D3", "DSM", "PharmaCorp")
    print(f"Status: {result.compliance_status}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Synergy: {result.synergy_potential}% savings")
    print(f"Reasoning: {result.reasoning}")
    print()

    # Example 2: Non-compliant (missing certs)
    print("=" * 80)
    print("EXAMPLE 2: Prinova USA -> PharmaCorp (Non-Compliant)")
    print("=" * 80)

    result = call_compliance_agent("Vitamin D3", "Prinova USA", "PharmaCorp")
    print(f"Status: {result.compliance_status}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Issues: {result.issues}")
    print(f"Reasoning: {result.reasoning}")
    print()

    # Example 3: Supplement tier (lower requirements)
    print("=" * 80)
    print("EXAMPLE 3: BASF -> FoodSupplementCo (Supplement Tier)")
    print("=" * 80)

    result = call_compliance_agent("Vitamin D3", "BASF", "FoodSupplementCo")
    print(f"Status: {result.compliance_status}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Synergy: {result.synergy_potential}% savings")
    print(f"Reasoning: {result.reasoning}")
    print()

    # Example 4: Unknown supplier
    print("=" * 80)
    print("EXAMPLE 4: UnknownCorp -> PharmaCorp (Insufficient Data)")
    print("=" * 80)

    result = call_compliance_agent("Vitamin D3", "UnknownCorp", "PharmaCorp")
    print(f"Status: {result.compliance_status}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Reasoning: {result.reasoning}")
