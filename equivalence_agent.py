"""
Equivalence-Agent implementation for Agnes multi-agent reasoning system.
Based on Section 5.1 of the project plan.
"""

import json
import os
from typing import Dict, Any, Optional
from schemas import EquivalenceAgentInput, AgentOutput, EndProductContext, Claim, Objection, MissingEvidence

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


EQUIVALENCE_AGENT_PROMPT = """
Du bist ein erfahrener Einkäufer in der Supplement-Industrie.
Ziel: Konsolidierungs-Potenzial im gegebenen Cluster identifizieren.

Input: Ein Cluster von SKUs aus verschiedenen Firmen, die potenziell
denselben Rohstoff bezeichnen, inklusive aktueller Lieferanten und
betroffener Endprodukte.

Deine Aufgabe:
1. Bestätige, dass die SKUs tatsächlich denselben Stoff bezeichnen,
   oder flagge Abweichungen (z.B. unterschiedliche Grades).
2. Schlage einen konsolidierten Lieferanten vor.
3. Begründe kurz (2-3 Sätze).

Antworte AUSSCHLIESSLICH im vorgegebenen JSON-Schema.
Setze "missing_evidence" aktiv, wenn dir Info fehlt.
Erfinde niemals Evidenz-URLs. Lieber "missing_evidence" setzen
als einen nicht-existenten Claim zu konstruieren.

WICHTIG:
- Verwende nur "verified": true, wenn du eine konkrete evidence_url hast
- Bei fehlenden Informationen nutze "missing_evidence"
- "confidence" sollte realistisch sein (0.6-0.8 typisch)
- "verdict" für Equivalence-Agent ist meist "PROPOSED"

Input-Daten:
{input_data}

Antwort-Schema:
{{
  "agent": "equivalence",
  "verdict": "PROPOSED|RECOMMENDED|BLOCKED_PENDING_EVIDENCE",
  "confidence": 0.0-1.0,
  "reasoning": "2-3 Sätze Begründung",
  "claims": [
    {{
      "claim": "Konkrete Aussage über die Äquivalenz",
      "evidence_url": null|"https://...",
      "verified": true|false
    }}
  ],
  "objections": [
    {{
      "issue": "Identifiziertes Risiko oder Problem",
      "severity": "low|medium|high"
    }}
  ],
  "missing_evidence": [
    {{
      "what": "Was genau fehlt",
      "why_it_matters": "Warum wichtig für Entscheidung",
      "confidence_lift_if_provided": 0.0-1.0
    }}
  ]
}}
"""


def create_mock_equivalence_response(input_data: EquivalenceAgentInput) -> AgentOutput:
    """
    Mock response generator for development and testing.
    Creates realistic responses for vitamin D consolidation scenarios.
    """

    # Analyze the input to create contextual response
    sku_count = len(input_data.skus)
    supplier_count = len(input_data.current_suppliers)
    company_count = len(input_data.affected_companies)

    # Base confidence depends on cluster size and complexity
    base_confidence = max(0.6, 0.9 - (sku_count * 0.02) - (supplier_count * 0.03))

    # Vitamin D specific mock response
    if any("vitamin" in sku.lower() for sku in input_data.skus):
        return AgentOutput(
            agent="equivalence",
            verdict="PROPOSED",
            confidence=round(base_confidence, 2),
            reasoning=f"Alle {sku_count} SKUs enthalten Vitamin D3 (Cholecalciferol) als Wirkstoff. Unterschiede in Trägersubstanzen und Herstellungsverfahren sind für Konsolidierung unkritisch. Empfehle Konsolidierung auf DSM als Hauptlieferant.",
            claims=[
                Claim(
                    claim="Alle SKUs enthalten denselben Wirkstoff Vitamin D3 (Cholecalciferol)",
                    evidence_url=None,
                    verified=False
                ),
                Claim(
                    claim="DSM ist etablierter Premium-Lieferant mit USP-konformer Qualität",
                    evidence_url=None,
                    verified=False
                )
            ],
            objections=[
                Objection(
                    issue="Potenzstärken variieren zwischen 1000 IU und 5000 IU",
                    severity="low"
                )
            ] if sku_count > 3 else [],
            missing_evidence=[
                MissingEvidence(
                    what="Aktuelle Preisvergleiche zwischen DSM, BASF und anderen Lieferanten",
                    why_it_matters="Konsolidierung nur sinnvoll bei Kostenvorteil",
                    confidence_lift_if_provided=0.15
                ),
                MissingEvidence(
                    what="MOQ-Anforderungen und Lead Times für DSM Vitamin D3",
                    why_it_matters="Lieferengpässe bei Single-Sourcing vermeiden",
                    confidence_lift_if_provided=0.12
                )
            ]
        )

    # Generic fallback response
    return AgentOutput(
        agent="equivalence",
        verdict="PROPOSED",
        confidence=round(base_confidence, 2),
        reasoning=f"Cluster von {sku_count} SKUs scheint denselben Grundstoff zu enthalten. Konsolidierung erscheint machbar, benötige aber mehr technische Spezifikationen.",
        claims=[
            Claim(
                claim=f"SKUs teilen vermutlich denselben Wirkstoff basierend auf Nomenklatur",
                evidence_url=None,
                verified=False
            )
        ],
        objections=[],
        missing_evidence=[
            MissingEvidence(
                what="Technische Spezifikationen und Reinheitsgrade aller SKUs",
                why_it_matters="Funktionale Äquivalenz kann nur mit vollständigen Specs bestätigt werden",
                confidence_lift_if_provided=0.25
            )
        ]
    )


def call_equivalence_agent(input_data: EquivalenceAgentInput, use_mock: bool = True) -> AgentOutput:
    """
    Main function to call the Equivalence-Agent.

    Args:
        input_data: Structured input following the JSON contract
        use_mock: If True, uses mock responses. If False, calls real Claude API.

    Returns:
        AgentOutput with the agent's analysis and recommendation

    Raises:
        ImportError: If Claude API is not available and use_mock=False
        ValueError: If API key is missing for real API call
    """

    if use_mock:
        return create_mock_equivalence_response(input_data)

    # Use real Claude API
    return call_claude_api(input_data)


def call_claude_api(input_data: EquivalenceAgentInput) -> AgentOutput:
    """
    Call the real Claude API for equivalence analysis.

    Args:
        input_data: Structured input for the agent

    Returns:
        AgentOutput with Claude's analysis

    Raises:
        ImportError: If Anthropic SDK is not installed
        ValueError: If API key is missing
    """

    if Anthropic is None:
        raise ImportError(
            "Anthropic SDK is not installed. "
            "Install it with: pip install anthropic"
        )

    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Please set your API key before calling the real Claude API."
        )

    # Initialize Anthropic client
    client = Anthropic(api_key=api_key)

    # Format the input data for Claude
    input_json = format_input_for_claude(input_data)

    # Create the prompt with input data
    prompt = EQUIVALENCE_AGENT_PROMPT.format(input_data=input_json)

    # Call Claude API
    message = client.messages.create(
        model="claude-opus-4-6",  # Using Opus for better reasoning
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Extract the response text
    response_text = message.content[0].text

    # Parse the JSON response
    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError:
        # If JSON parsing fails, create a structured error response
        return AgentOutput(
            agent="equivalence",
            verdict="BLOCKED_PENDING_EVIDENCE",
            confidence=0.0,
            reasoning="Fehler bei der Verarbeitung der API-Antwort",
            claims=[],
            objections=[
                Objection(
                    issue="Claude API response could not be parsed as JSON",
                    severity="high"
                )
            ],
            missing_evidence=[]
        )

    # Convert JSON response to AgentOutput
    return AgentOutput(
        agent=response_json.get("agent", "equivalence"),
        verdict=response_json.get("verdict", "PROPOSED"),
        confidence=float(response_json.get("confidence", 0.5)),
        reasoning=response_json.get("reasoning", ""),
        claims=[
            Claim(
                claim=c.get("claim", ""),
                evidence_url=c.get("evidence_url"),
                verified=c.get("verified", False)
            )
            for c in response_json.get("claims", [])
        ],
        objections=[
            Objection(
                issue=o.get("issue", ""),
                severity=o.get("severity", "low")
            )
            for o in response_json.get("objections", [])
        ],
        missing_evidence=[
            MissingEvidence(
                what=m.get("what", ""),
                why_it_matters=m.get("why_it_matters", ""),
                confidence_lift_if_provided=float(m.get("confidence_lift_if_provided", 0.0))
            )
            for m in response_json.get("missing_evidence", [])
        ]
    )


def format_input_for_claude(input_data: EquivalenceAgentInput) -> str:
    """
    Format structured input as JSON for Claude.

    Args:
        input_data: Structured equivalence analysis input

    Returns:
        JSON string formatted for Claude
    """

    return json.dumps({
        "cluster_id": input_data.cluster_id,
        "skus": input_data.skus,
        "affected_companies": input_data.affected_companies,
        "affected_boms": input_data.affected_boms,
        "current_suppliers": input_data.current_suppliers,
        "end_product_context": [
            {
                "sku": epc.sku,
                "company": epc.company,
                "name_hint": epc.name_hint
            }
            for epc in input_data.end_product_context
        ]
    }, indent=2, ensure_ascii=False)


def test_equivalence_agent():
    """Test function with realistic vitamin D scenario."""

    test_input = EquivalenceAgentInput(
        cluster_id="vitamin-d-d3-cluster-001",
        skus=[
            "RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1",
            "RM-C14-vitamin-d3-cholecalciferol-2000iu-8e9f3c42",
            "RM-C27-vitamin-d3-powder-5000iu-bd4a1f89",
            "RM-C33-cholecalciferol-vitamin-d3-72c8e3d5"
        ],
        affected_companies=["Nature Made", "Kirkland", "Garden of Life", "NOW Foods"],
        affected_boms=[15, 42, 67, 89],
        current_suppliers=["DSM", "BASF", "Fermenta", "Zhejiang Medicine"],
        end_product_context=[
            EndProductContext(
                sku="FG-naturemade-12041",
                company="Nature Made",
                name_hint="Vitamin D3 1000 IU Softgels"
            ),
            EndProductContext(
                sku="FG-kirkland-89210",
                company="Kirkland",
                name_hint="Extra Strength Vitamin D3 2000 IU"
            ),
            EndProductContext(
                sku="FG-gardenlife-45678",
                company="Garden of Life",
                name_hint="Vitamin Code Raw D3 5000 IU"
            )
        ]
    )

    # Test the mock agent
    response = call_equivalence_agent(test_input, use_mock=True)

    print("=== EQUIVALENCE AGENT TEST ===")
    print(f"Verdict: {response.verdict}")
    print(f"Confidence: {response.confidence}")
    print(f"Reasoning: {response.reasoning}")
    print(f"Claims: {len(response.claims)}")
    print(f"Objections: {len(response.objections)}")
    print(f"Missing Evidence: {len(response.missing_evidence)}")

    # Print full JSON for verification
    print("\n=== FULL JSON OUTPUT ===")
    print(json.dumps(response.dict(), indent=2, ensure_ascii=False))

    return response


if __name__ == "__main__":
    test_equivalence_agent()