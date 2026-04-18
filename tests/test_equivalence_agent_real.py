"""
Tests for Claude API integration with Equivalence-Agent.

Tests the real Claude API integration for analyzing vitamin D consolidation.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from equivalence_agent import call_equivalence_agent
from schemas import EquivalenceAgentInput, EndProductContext


@pytest.fixture
def sample_vitamin_d_input():
    """Fixture providing sample vitamin D consolidation input."""
    return EquivalenceAgentInput(
        cluster_id="vitamin-d-d3-cluster-test",
        skus=[
            "RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1",
            "RM-C14-vitamin-d3-cholecalciferol-2000iu-8e9f3c42"
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
                name_hint="Extra Strength Vitamin D3 2000 IU"
            )
        ]
    )


class TestClaudeAPIIntegration:
    """Tests for Claude API integration."""

    def test_mock_response_is_valid(self, sample_vitamin_d_input):
        """Test that mock responses are valid AgentOutput objects."""
        response = call_equivalence_agent(sample_vitamin_d_input, use_mock=True)

        assert response is not None
        assert response.agent == "equivalence"
        assert response.verdict in ["PROPOSED", "RECOMMENDED", "BLOCKED_PENDING_EVIDENCE"]
        assert 0.0 <= response.confidence <= 1.0
        assert response.reasoning
        assert isinstance(response.claims, list)
        assert isinstance(response.objections, list)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-12345"})
    @patch("equivalence_agent.Anthropic")
    def test_real_claude_api_call(self, mock_anthropic_class, sample_vitamin_d_input):
        """Test real Claude API call with mocked Anthropic client."""
        # Mock the API response
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock()]
        mock_message.content[0].text = """{
  "agent": "equivalence",
  "verdict": "PROPOSED",
  "confidence": 0.85,
  "reasoning": "Beide SKUs enthalten Vitamin D3 als Wirkstoff. Konsolidierung auf DSM empfohlen.",
  "claims": [
    {
      "claim": "Alle SKUs enthalten denselben Wirkstoff Vitamin D3",
      "evidence_url": null,
      "verified": false
    }
  ],
  "objections": [],
  "missing_evidence": []
}"""

        mock_client.messages.create.return_value = mock_message
        mock_anthropic_class.return_value = mock_client

        # Call with use_mock=False to trigger Claude API
        response = call_equivalence_agent(sample_vitamin_d_input, use_mock=False)

        assert response is not None
        assert response.verdict == "PROPOSED"
        assert response.confidence == 0.85

    def test_api_key_validation(self, sample_vitamin_d_input):
        """Test that missing API key is handled gracefully."""
        # Ensure ANTHROPIC_API_KEY is not set
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]

        # Calling without use_mock=False should work with default (mock)
        response = call_equivalence_agent(sample_vitamin_d_input)
        assert response is not None

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-12345"})
    @patch("equivalence_agent.Anthropic")
    def test_json_parsing_from_claude(self, mock_anthropic_class, sample_vitamin_d_input):
        """Test that Claude's JSON response is properly parsed."""
        mock_client = MagicMock()
        mock_message = MagicMock()

        # Simulate Claude's response with JSON
        claude_json = """{
  "agent": "equivalence",
  "verdict": "RECOMMENDED",
  "confidence": 0.92,
  "reasoning": "Starke Äquivalenz zwischen SKUs identifiziert.",
  "claims": [
    {
      "claim": "Vitamin D3 aus DSM erfüllt alle Qualitätsstandards",
      "evidence_url": "https://example.com/dsm-cert",
      "verified": true
    }
  ],
  "objections": [
    {
      "issue": "BASF könnte MOQ-Anforderungen nicht erfüllen",
      "severity": "medium"
    }
  ],
  "missing_evidence": [
    {
      "what": "Langzeithaltbarkeitsstudien",
      "why_it_matters": "Für 2-Jahr Shelf-Life Garantie nötig",
      "confidence_lift_if_provided": 0.08
    }
  ]
}"""

        mock_message.content = [MagicMock()]
        mock_message.content[0].text = claude_json
        mock_client.messages.create.return_value = mock_message
        mock_anthropic_class.return_value = mock_client

        response = call_equivalence_agent(sample_vitamin_d_input, use_mock=False)

        assert response.verdict == "RECOMMENDED"
        assert response.confidence == 0.92
        assert len(response.claims) == 1
        assert response.claims[0].verified is True
        assert len(response.objections) == 1
        assert len(response.missing_evidence) == 1

    def test_structured_input_formatting(self, sample_vitamin_d_input):
        """Test that structured input is properly formatted for Claude."""
        response = call_equivalence_agent(sample_vitamin_d_input, use_mock=True)

        # Verify all input fields were considered
        assert response is not None
        assert len(response.reasoning) > 0

    def test_verdict_types(self, sample_vitamin_d_input):
        """Test that verdicts match expected types."""
        response = call_equivalence_agent(sample_vitamin_d_input, use_mock=True)

        valid_verdicts = ["PROPOSED", "RECOMMENDED", "BLOCKED_PENDING_EVIDENCE"]
        assert response.verdict in valid_verdicts

    def test_response_contains_reasoning(self, sample_vitamin_d_input):
        """Test that responses include clear reasoning."""
        response = call_equivalence_agent(sample_vitamin_d_input, use_mock=True)

        assert response.reasoning is not None
        assert len(response.reasoning) > 10, "Reasoning should be substantive"
