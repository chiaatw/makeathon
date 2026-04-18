"""
JSON schemas and data models for Agnes multi-agent reasoning system.
Based on Section 4 of the project plan.
Simplified version without external dependencies for MVP.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class EndProductContext:
    """Context about end products affected by the consolidation."""
    sku: str
    company: str
    name_hint: str


@dataclass
class EquivalenceAgentInput:
    """Input schema for the Equivalence-Agent."""
    cluster_id: str
    skus: List[str]
    affected_companies: List[str]
    affected_boms: List[int]
    current_suppliers: List[str]
    end_product_context: List[EndProductContext]


@dataclass
class Claim:
    """A claim made by an agent with supporting evidence."""
    claim: str
    evidence_url: Optional[str] = None
    verified: bool = False


@dataclass
class Objection:
    """An objection raised by an agent."""
    issue: str
    severity: str  # "low", "medium", "high"


@dataclass
class MissingEvidence:
    """Evidence that is missing but needed for better confidence."""
    what: str
    why_it_matters: str
    confidence_lift_if_provided: float


@dataclass
class AgentOutput:
    """Unified output schema for all agents."""
    agent: str
    verdict: str
    confidence: float
    reasoning: str
    claims: List[Claim] = None
    objections: List[Objection] = None
    missing_evidence: List[MissingEvidence] = None

    def __post_init__(self):
        if self.claims is None:
            self.claims = []
        if self.objections is None:
            self.objections = []
        if self.missing_evidence is None:
            self.missing_evidence = []

    def dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


# Arbiter decision rules from Section 4.3
ARBITER_RULES = {
    "RECOMMENDED": {
        "conditions": ["no_objections", "confidence_gte_0.7"],
        "description": "Keine Objections, Confidence ≥ 0.7"
    },
    "RECOMMENDED_WITH_CAVEAT": {
        "conditions": ["objections_only_low", "confidence_gte_0.6"],
        "description": "Objections nur low, Confidence ≥ 0.6"
    },
    "REVIEW_REQUIRED": {
        "conditions": ["has_medium_objection"],
        "description": "Mind. eine Objection medium"
    },
    "BLOCKED_PENDING_EVIDENCE": {
        "conditions": ["has_high_objection"],
        "description": "Mind. eine Objection high"
    }
}