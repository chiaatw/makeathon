"""
Devil's Advocate Agent for compliance-positive reasoning.

This agent intentionally argues the strongest case for why a raw material
could be compliant with a company's specifications, while still exposing
caveats and missing evidence transparently.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from schemas import AgentOutput, Claim, MissingEvidence, Objection


@dataclass
class DevilsAdvocateAgentInput:
    """Input for compliance-positive analysis.

    Attributes:
        material: Raw material name (for narrative context)
        supplier: Supplier name to evaluate
        company: Customer/company whose specs apply
        material_attributes: Optional measured attributes of this material batch
            Example: {
                "potency": 99.2,
                "dissolution": 91.0,
                "impurities": 0.03,
                "certificates": ["cGMP", "ISO 9001"]
            }
    """

    material: str
    supplier: str
    company: str
    material_attributes: Dict[str, Any] = field(default_factory=dict)


class DevilsAdvocateComplianceAgent:
    """Compliance-positive reasoning agent based on project CSV/JSON sources."""

    def __init__(
        self,
        data_dir: str = "data",
        external_evidence_path: str = "data/external_evidence.json",
    ):
        self.data_dir = Path(data_dir)
        self.external_evidence_path = Path(external_evidence_path)

        self.suppliers_data = self._load_suppliers_csv(self.data_dir / "suppliers.csv")
        self.customer_reqs_data = self._load_customer_requirements_csv(
            self.data_dir / "customer_requirements.csv"
        )
        self.external_evidence = self._load_external_evidence(self.external_evidence_path)

    def analyze(self, input_data: DevilsAdvocateAgentInput) -> AgentOutput:
        """Produce a structured compliance-positive argument set."""

        supplier_info = self._get_supplier_info(input_data.supplier)
        customer_specs = self._get_customer_specs(input_data.company)

        if supplier_info is None:
            return AgentOutput(
                agent="devils_advocate",
                verdict="BLOCKED_PENDING_EVIDENCE",
                confidence=0.0,
                reasoning=f"Supplier '{input_data.supplier}' not found; no case can be built yet.",
                claims=[],
                objections=[
                    Objection(
                        issue="Supplier master data missing",
                        severity="high",
                    )
                ],
                missing_evidence=[
                    MissingEvidence(
                        what=f"Supplier profile for {input_data.supplier}",
                        why_it_matters="Required to map certificates and quality posture to company specs",
                        confidence_lift_if_provided=0.6,
                    )
                ],
            )

        if customer_specs is None:
            return AgentOutput(
                agent="devils_advocate",
                verdict="BLOCKED_PENDING_EVIDENCE",
                confidence=0.0,
                reasoning=f"Company '{input_data.company}' specs are unavailable, so compliance cannot be argued credibly.",
                claims=[],
                objections=[
                    Objection(
                        issue="Customer specification profile missing",
                        severity="high",
                    )
                ],
                missing_evidence=[
                    MissingEvidence(
                        what=f"Specification profile for {input_data.company}",
                        why_it_matters="Defines required certificates and quality thresholds",
                        confidence_lift_if_provided=0.65,
                    )
                ],
            )

        claims: List[Claim] = []
        objections: List[Objection] = []
        missing_evidence: List[MissingEvidence] = []

        positive_signals = 0

        # 1) Certificate-based pro-compliance arguments
        cert_claims, cert_objections, cert_missing, cert_score = self._build_certificate_case(
            supplier_info=supplier_info,
            customer_specs=customer_specs,
            material_attributes=input_data.material_attributes,
        )
        claims.extend(cert_claims)
        objections.extend(cert_objections)
        missing_evidence.extend(cert_missing)
        positive_signals += cert_score

        # 2) Spec-metric arguments (potency, dissolution, impurities)
        metric_claims, metric_missing, metric_score = self._build_metric_case(
            material=input_data.material,
            customer_specs=customer_specs,
            material_attributes=input_data.material_attributes,
        )
        claims.extend(metric_claims)
        missing_evidence.extend(metric_missing)
        positive_signals += metric_score

        # 3) Supplier maturity argument
        supplier_size = supplier_info.get("current_customer_count", 0)
        if supplier_size >= 4:
            claims.append(
                Claim(
                    claim=(
                        f"{input_data.supplier} already serves {supplier_size} customers, "
                        "which supports process maturity and repeatable compliance operations."
                    ),
                    evidence_url=None,
                    verified=False,
                )
            )
            positive_signals += 1

        # 4) External narrative evidence (if available)
        evidence_claim, evidence_missing, evidence_score = self._build_external_evidence_case(
            supplier=input_data.supplier,
            material=input_data.material,
        )
        if evidence_claim:
            claims.append(evidence_claim)
        if evidence_missing:
            missing_evidence.append(evidence_missing)
        positive_signals += evidence_score

        confidence = self._compute_confidence(
            positive_signals=positive_signals,
            objections=objections,
            missing_evidence=missing_evidence,
        )
        verdict = self._compute_verdict(objections, confidence)

        if claims:
            summary = (
                f"A compliance-positive case can be made for {input_data.material} from "
                f"{input_data.supplier} against {input_data.company} specs, based on "
                f"{len(claims)} supporting arguments."
            )
        else:
            summary = (
                "No strong compliance-positive arguments could be constructed from available data."
            )

        return AgentOutput(
            agent="devils_advocate",
            verdict=verdict,
            confidence=confidence,
            reasoning=summary,
            claims=claims,
            objections=objections,
            missing_evidence=missing_evidence,
        )

    def _build_certificate_case(
        self,
        supplier_info: Dict[str, Any],
        customer_specs: Dict[str, Any],
        material_attributes: Dict[str, Any],
    ) -> Tuple[List[Claim], List[Objection], List[MissingEvidence], int]:
        claims: List[Claim] = []
        objections: List[Objection] = []
        missing: List[MissingEvidence] = []
        score = 0

        required = self._normalize_certs(customer_specs.get("certificates_required", []))
        supplier_certs = self._normalize_certs(supplier_info.get("certificates", []))

        # If batch-level cert list is provided, combine it with supplier-level data.
        batch_certs_raw = material_attributes.get("certificates", [])
        batch_certs = self._normalize_certs(batch_certs_raw)
        available = supplier_certs | batch_certs

        exact_matches = sorted(required & available)
        if exact_matches:
            claims.append(
                Claim(
                    claim=(
                        "Required certifications directly matched: "
                        + ", ".join(exact_matches)
                        + "."
                    ),
                    evidence_url=None,
                    verified=False,
                )
            )
            score += 2

        missing_required = sorted(required - available)

        # Devil's advocate bridge: treat GMP/cGMP as near-equivalent with caveat.
        bridged = []
        unresolved = []
        for req in missing_required:
            if req == "CGMP" and "GMP" in available:
                bridged.append("CGMP via GMP baseline and QMS documentation")
            elif req == "GMP" and "CGMP" in available:
                bridged.append("GMP via cGMP superset practices")
            else:
                unresolved.append(req)

        if bridged:
            claims.append(
                Claim(
                    claim=(
                        "A compliance argument exists for near-equivalent certificate coverage: "
                        + "; ".join(bridged)
                        + "."
                    ),
                    evidence_url=None,
                    verified=False,
                )
            )
            objections.append(
                Objection(
                    issue=(
                        "Certificate equivalence assumptions require auditor acceptance "
                        "and formal mapping evidence."
                    ),
                    severity="low",
                )
            )
            missing.append(
                MissingEvidence(
                    what="Formal cGMP/GMP equivalence mapping or customer waiver",
                    why_it_matters="Converts an argument from plausible to auditable compliance",
                    confidence_lift_if_provided=0.15,
                )
            )
            score += 1

        if unresolved:
            objections.append(
                Objection(
                    issue="Missing required certificates: " + ", ".join(unresolved),
                    severity="medium",
                )
            )
            missing.append(
                MissingEvidence(
                    what="Valid certificate copies for: " + ", ".join(unresolved),
                    why_it_matters="Directly determines mandatory compliance eligibility",
                    confidence_lift_if_provided=0.2,
                )
            )

        return claims, objections, missing, score

    def _build_metric_case(
        self,
        material: str,
        customer_specs: Dict[str, Any],
        material_attributes: Dict[str, Any],
    ) -> Tuple[List[Claim], List[MissingEvidence], int]:
        claims: List[Claim] = []
        missing: List[MissingEvidence] = []
        score = 0

        potency = material_attributes.get("potency")
        dissolution = material_attributes.get("dissolution")
        impurities = material_attributes.get("impurities")

        potency_range = customer_specs.get("potency_range")
        dissolution_min = customer_specs.get("dissolution_min")
        impurities_max = customer_specs.get("impurities_max")

        # Potency
        if potency is not None and potency_range:
            low, high = self._parse_range(potency_range)
            if low is not None and high is not None and low <= float(potency) <= high:
                claims.append(
                    Claim(
                        claim=(
                            f"{material} potency ({potency}) sits within required range "
                            f"{low}-{high}."
                        ),
                        evidence_url=None,
                        verified=False,
                    )
                )
                score += 1
        else:
            missing.append(
                MissingEvidence(
                    what="Recent potency COA values",
                    why_it_matters="Needed to defend potency-range compliance",
                    confidence_lift_if_provided=0.12,
                )
            )

        # Dissolution
        if dissolution is not None and dissolution_min is not None:
            if float(dissolution) >= float(dissolution_min):
                claims.append(
                    Claim(
                        claim=(
                            f"Dissolution result ({dissolution}) meets minimum requirement "
                            f"({dissolution_min})."
                        ),
                        evidence_url=None,
                        verified=False,
                    )
                )
                score += 1
        elif dissolution_min and float(dissolution_min) > 0:
            missing.append(
                MissingEvidence(
                    what="Dissolution test result for current batch",
                    why_it_matters="Needed for dissolution threshold compliance",
                    confidence_lift_if_provided=0.1,
                )
            )

        # Impurities
        if impurities is not None and impurities_max is not None:
            if float(impurities) <= float(impurities_max):
                claims.append(
                    Claim(
                        claim=(
                            f"Impurity level ({impurities}) is at or below max limit "
                            f"({impurities_max})."
                        ),
                        evidence_url=None,
                        verified=False,
                    )
                )
                score += 1
        else:
            missing.append(
                MissingEvidence(
                    what="Impurity profile from latest QC release",
                    why_it_matters="Required to support contamination risk compliance",
                    confidence_lift_if_provided=0.12,
                )
            )

        return claims, missing, score

    def _build_external_evidence_case(
        self,
        supplier: str,
        material: str,
    ) -> Tuple[Optional[Claim], Optional[MissingEvidence], int]:
        if not self.external_evidence:
            return (
                None,
                MissingEvidence(
                    what="External market/compliance evidence source",
                    why_it_matters="Adds independent support to compliance-positive reasoning",
                    confidence_lift_if_provided=0.08,
                ),
                0,
            )

        supplier_records = self.external_evidence.get("suppliers", [])
        for record in supplier_records:
            if str(record.get("supplier_name", "")).lower() == supplier.lower():
                substance = str(record.get("substance", "")).lower()
                notes = str(record.get("compliance_notes", "")).strip()
                if material.lower() in substance or substance in material.lower():
                    if notes:
                        return (
                            Claim(
                                claim=(
                                    f"External evidence narrative supports compliance posture: {notes}"
                                ),
                                evidence_url=None,
                                verified=False,
                            ),
                            None,
                            1,
                        )

        return (
            None,
            MissingEvidence(
                what=f"External compliance note linking {supplier} and {material}",
                why_it_matters="Improves confidence with independent narrative evidence",
                confidence_lift_if_provided=0.06,
            ),
            0,
        )

    @staticmethod
    def _compute_confidence(
        positive_signals: int,
        objections: List[Objection],
        missing_evidence: List[MissingEvidence],
    ) -> float:
        high_count = sum(1 for o in objections if o.severity == "high")
        medium_count = sum(1 for o in objections if o.severity == "medium")

        confidence = 0.52 + (0.08 * positive_signals)
        confidence -= 0.22 * high_count
        confidence -= 0.1 * medium_count
        confidence -= min(0.18, 0.03 * len(missing_evidence))

        return round(max(0.0, min(0.95, confidence)), 2)

    @staticmethod
    def _compute_verdict(objections: List[Objection], confidence: float) -> str:
        if any(o.severity == "high" for o in objections):
            return "BLOCKED_PENDING_EVIDENCE"
        if any(o.severity == "medium" for o in objections):
            return "REVIEW_REQUIRED"
        if confidence >= 0.7:
            return "RECOMMENDED"
        return "RECOMMENDED_WITH_CAVEAT"

    @staticmethod
    def _parse_range(range_text: Any) -> Tuple[Optional[float], Optional[float]]:
        if not range_text:
            return None, None
        if isinstance(range_text, (int, float)):
            val = float(range_text)
            return val, val

        text = str(range_text).strip()
        if "-" not in text:
            try:
                val = float(text)
                return val, val
            except ValueError:
                return None, None

        left, right = text.split("-", 1)
        try:
            return float(left.strip()), float(right.strip())
        except ValueError:
            return None, None

    @staticmethod
    def _normalize_certs(certs: List[str]) -> Set[str]:
        normalized: Set[str] = set()
        for cert in certs:
            key = str(cert).strip().upper().replace(" ", "")
            if key:
                normalized.add(key)
        return normalized

    @staticmethod
    def _load_suppliers_csv(path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []

        data: List[Dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                certs = [c.strip() for c in row.get("certificates", "").split(",") if c.strip()]
                data.append(
                    {
                        "supplier": row.get("supplier", ""),
                        "country": row.get("country", "Unknown"),
                        "current_customer_count": int(row.get("current_customer_count", 0) or 0),
                        "certificates": certs,
                    }
                )
        return data

    @staticmethod
    def _load_customer_requirements_csv(path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []

        data: List[Dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                certs = [c.strip() for c in row.get("certificates_required", "").split(",") if c.strip()]
                data.append(
                    {
                        "company_name": row.get("company_name", ""),
                        "quality_tier": row.get("quality_tier", "SUPPLEMENT_GRADE"),
                        "certificates_required": certs,
                        "potency_range": row.get("potency_range"),
                        "dissolution_min": float(row.get("dissolution_min", 0) or 0),
                        "impurities_max": float(row.get("impurities_max", 0) or 0),
                    }
                )
        return data

    @staticmethod
    def _load_external_evidence(path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}

        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _get_supplier_info(self, supplier: str) -> Optional[Dict[str, Any]]:
        for row in self.suppliers_data:
            if str(row.get("supplier", "")).lower() == supplier.lower():
                return row
        return None

    def _get_customer_specs(self, company: str) -> Optional[Dict[str, Any]]:
        for row in self.customer_reqs_data:
            if str(row.get("company_name", "")).lower() == company.lower():
                return row
        return None


def call_devils_advocate_agent(
    input_data: DevilsAdvocateAgentInput,
    data_dir: str = "data",
    external_evidence_path: str = "data/external_evidence.json",
) -> AgentOutput:
    """Public entrypoint for the Devil's Advocate compliance agent."""

    agent = DevilsAdvocateComplianceAgent(
        data_dir=data_dir,
        external_evidence_path=external_evidence_path,
    )
    return agent.analyze(input_data)


if __name__ == "__main__":
    # Example usage
    demo_input = DevilsAdvocateAgentInput(
        material="Vitamin D3",
        supplier="BASF",
        company="FoodSupplementCo",
        material_attributes={
            "potency": 99.1,
            "dissolution": 82.0,
            "impurities": 0.08,
            "certificates": ["GMP", "ISO 9001"],
        },
    )

    result = call_devils_advocate_agent(demo_input)
    print(json.dumps(result.dict(), indent=2, ensure_ascii=False))
