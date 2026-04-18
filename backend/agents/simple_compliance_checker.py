"""
MVP Compliance Checker: Certificate Status + Supply Chain Synergy

Simple CSV-based compliance checking focusing on:
1. Certificate Status (Required vs. Available)
2. Supply Chain Synergy (Consolidation savings potential)

No APIs, no prompts, no complexity. Just CSV + simple logic.
"""

import csv
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class ComplianceAgentOutput:
    """Output from compliance check."""
    compliance_status: str  # "COMPLIANT", "NON_COMPLIANT", "INSUFFICIENT_DATA"
    confidence: float  # 0.0-1.0
    reasoning: str  # Human-readable summary for multi-agent
    issues: List[Dict] = None  # Details about any issues
    synergy_potential: float = 0.0  # % savings from consolidation


class SimpleComplianceChecker:
    """
    MVP Compliance Checker using CSV data.

    Checks:
    1. Certificate Status (Required vs. Available)
    2. Supply Chain Synergy (Consolidation opportunity)

    Example:
        checker = SimpleComplianceChecker()
        result = checker.check("Vitamin D3", "DSM", "PharmaCorp")
        print(result.reasoning)
        # "OK Certs: cGMP, ISO 9001 complete | Synergy: 20% savings (3->1)"
    """

    def __init__(self):
        """Load CSV data files."""
        self.suppliers_data = self._load_suppliers_csv()
        self.customer_reqs_data = self._load_customer_requirements_csv()

    def _load_suppliers_csv(self) -> List[Dict]:
        """Load suppliers.csv file."""
        try:
            data = []
            with open("data/suppliers.csv", "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            return data
        except FileNotFoundError:
            return None

    def _load_customer_requirements_csv(self) -> List[Dict]:
        """Load customer_requirements.csv file."""
        try:
            data = []
            with open("data/customer_requirements.csv", "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            return data
        except FileNotFoundError:
            return None

    def check(self, material: str, supplier: str, customer: str) -> ComplianceAgentOutput:
        """
        Check compliance: Can supplier deliver what customer needs?

        Args:
            material: e.g. "Vitamin D3"
            supplier: e.g. "DSM"
            customer: e.g. "PharmaCorp"

        Returns:
            ComplianceAgentOutput with status, reasoning, synergy potential
        """

        # 1. Get supplier info
        supplier_info = self._get_supplier_info(supplier)
        if supplier_info is None:
            return ComplianceAgentOutput(
                compliance_status="INSUFFICIENT_DATA",
                confidence=0.0,
                reasoning=f"Supplier '{supplier}' not found in database"
            )

        # 2. Get customer requirements
        customer_reqs = self._get_customer_requirements(customer)
        if customer_reqs is None:
            return ComplianceAgentOutput(
                compliance_status="INSUFFICIENT_DATA",
                confidence=0.0,
                reasoning=f"Customer '{customer}' not found in database"
            )

        # 3. Check certificates
        cert_gaps = self._check_certificates(supplier_info, customer_reqs)

        # 4. Calculate synergy
        synergy = self._calculate_synergy(supplier, customer)

        # 5. Generate verdict
        if cert_gaps:
            status = "NON_COMPLIANT"
            confidence = 0.5
            cert_msg = f"WARN Certs: Missing {', '.join(cert_gaps)}"
        else:
            status = "COMPLIANT"
            confidence = 0.95
            cert_msg = "OK Certs: All required certificates present"

        # 6. Generate reasoning for multi-agent
        reasoning = self._generate_reasoning(
            cert_msg=cert_msg,
            synergy=synergy,
            supplier_country=supplier_info.get("country", "Unknown")
        )

        return ComplianceAgentOutput(
            compliance_status=status,
            confidence=confidence,
            reasoning=reasoning,
            synergy_potential=synergy["savings_percent"],
            issues=cert_gaps
        )

    def _get_supplier_info(self, supplier: str) -> Optional[Dict]:
        """Get supplier info from CSV."""

        if self.suppliers_data is None:
            return self._get_mock_supplier(supplier)

        for row in self.suppliers_data:
            if row.get("supplier", "").lower() == supplier.lower():
                return {
                    "supplier": supplier,
                    "country": row.get("country", "Unknown"),
                    "current_customer_count": int(row.get("current_customer_count", 0)),
                    "certificates": row.get("certificates", "").split(",") if "certificates" in row else []
                }

        return None

    def _get_customer_requirements(self, customer: str) -> Optional[Dict]:
        """Get customer requirements from CSV."""

        if self.customer_reqs_data is None:
            return self._get_mock_customer_requirements(customer)

        for row in self.customer_reqs_data:
            if row.get("company_name", "").lower() == customer.lower():
                return {
                    "company_name": customer,
                    "quality_tier": row.get("quality_tier", "SUPPLEMENT_GRADE"),
                    "certificates_required": row.get("certificates_required", "").split(","),
                    "potency_range": row.get("potency_range", "95.0-105.0"),
                    "dissolution_min": float(row.get("dissolution_min", 75)),
                    "impurities_max": float(row.get("impurities_max", 0.1))
                }

        return None

    def _check_certificates(self, supplier_info: Dict, customer_reqs: Dict) -> List[str]:
        """
        Check if supplier has all required certificates.

        Returns:
            List of missing certificates (empty if all present)
        """

        required = set(
            cert.strip() for cert in customer_reqs["certificates_required"]
            if cert.strip()
        )

        available = set(
            cert.strip() for cert in supplier_info.get("certificates", [])
            if cert.strip()
        )

        missing = required - available
        return list(missing)

    def _calculate_synergy(self, supplier: str, customer: str) -> Dict:
        """
        Calculate supply chain synergy/consolidation savings.

        Simplified logic:
        - For each supplier we eliminate: ~10% savings (logistics, overhead, negotiation)
        - If already single source: 0% savings

        Args:
            supplier: Target consolidation supplier
            customer: Customer being analyzed

        Returns:
            {
                "potential_consolidation": bool,
                "current_suppliers": int,
                "potential_savings": percent
            }
        """

        # For MVP: Assume we don't know current suppliers precisely
        # Use heuristic based on industry tier

        customer_reqs = self._get_customer_requirements(customer)
        if not customer_reqs:
            return {
                "potential_consolidation": False,
                "current_suppliers": 1,
                "savings_percent": 0,
                "note": "Unknown customer tier"
            }

        # Heuristic: What tier determines current supplier count?
        tier = customer_reqs.get("quality_tier", "SUPPLEMENT_GRADE")

        if tier == "PHARMA_GRADE":
            # Pharma usually uses 3-4 suppliers for redundancy
            current_suppliers = 3
        elif tier == "SUPPLEMENT_GRADE":
            # Supplements usually use 2-3 suppliers
            current_suppliers = 2
        else:  # COSMETIC_GRADE
            # Cosmetics often use 1-2 suppliers
            current_suppliers = 1

        # Calculate savings
        if current_suppliers <= 1:
            savings = 0
            note = "Already single source"
        else:
            # Each supplier eliminated saves ~10%
            savings = (current_suppliers - 1) * 10
            note = f"Could consolidate {current_suppliers} suppliers into 1"

        return {
            "potential_consolidation": savings > 0,
            "current_suppliers": current_suppliers,
            "consolidated_to": supplier,
            "savings_percent": savings,
            "note": note
        }

    def _assess_geo_risk(self, supplier: str) -> Dict:
        """
        Assess geopolitical risk of supplier.

        Simple rules:
        - EU/USA/Japan/AU = LOW
        - China/India/Mexico = MEDIUM
        - Sanctioned countries = HIGH
        - Unknown = UNKNOWN
        """

        supplier_info = self._get_supplier_info(supplier)
        if not supplier_info:
            return {"level": "UNKNOWN", "country": "Unknown"}

        country = supplier_info.get("country", "Unknown")

        low_risk = ["USA", "EU", "Canada", "Japan", "Australia", "Switzerland", "Netherlands", "Germany"]
        medium_risk = ["China", "India", "Mexico", "South Korea", "Vietnam"]
        high_risk = ["North Korea", "Iran", "Syria", "Russia"]  # Sanctions

        if country in high_risk:
            level = "HIGH"
        elif country in medium_risk:
            level = "MEDIUM"
        elif country in low_risk:
            level = "LOW"
        else:
            level = "UNKNOWN"

        return {
            "level": level,
            "country": country
        }

    def _generate_reasoning(self, cert_msg: str, synergy: Dict, supplier_country: str) -> str:
        """
        Generate multi-agent friendly reasoning.

        Format: "OK Certs: OK | Synergy: 20% savings | Geo: Low"
        """

        parts = []

        # Certificate status
        parts.append(cert_msg)

        # Synergy
        if synergy["savings_percent"] > 0:
            savings = synergy["savings_percent"]
            current = synergy["current_suppliers"]
            parts.append(f"Synergy: {savings}% savings ({current}->1 supplier)")
        else:
            parts.append("Synergy: None (single source)")

        # Geopolitical risk
        geo = self._assess_geo_risk(synergy.get("consolidated_to", "Unknown"))
        parts.append(f"Geo: {geo['level']} ({geo['country']})")

        return " | ".join(parts)

    # ========== MOCK DATA for testing ==========

    def _get_mock_supplier(self, supplier: str) -> Optional[Dict]:
        """Return mock supplier data when CSV not available."""

        mock_data = {
            "DSM": {
                "supplier": "DSM",
                "country": "Netherlands",
                "current_customer_count": 5,
                "certificates": ["cGMP", "ISO 9001", "ISO 14644"]
            },
            "BASF": {
                "supplier": "BASF",
                "country": "Germany",
                "current_customer_count": 4,
                "certificates": ["GMP", "ISO 9001"]
            },
            "Prinova USA": {
                "supplier": "Prinova USA",
                "country": "USA",
                "current_customer_count": 2,
                "certificates": ["GMP"]
            }
        }

        return mock_data.get(supplier)

    def _get_mock_customer_requirements(self, customer: str) -> Optional[Dict]:
        """Return mock customer requirements when CSV not available."""

        mock_data = {
            "PharmaCorp": {
                "company_name": "PharmaCorp",
                "quality_tier": "PHARMA_GRADE",
                "certificates_required": ["cGMP", "ISO 9001", "ISO 14644"],
                "potency_range": "97.0-103.0",
                "dissolution_min": 90,
                "impurities_max": 0.05
            },
            "FoodSupplementCo": {
                "company_name": "FoodSupplementCo",
                "quality_tier": "SUPPLEMENT_GRADE",
                "certificates_required": ["GMP", "ISO 9001"],
                "potency_range": "95.0-105.0",
                "dissolution_min": 75,
                "impurities_max": 0.1
            },
            "Cosmetics Inc": {
                "company_name": "Cosmetics Inc",
                "quality_tier": "COSMETIC_GRADE",
                "certificates_required": ["GMP"],
                "potency_range": "90.0-110.0",
                "dissolution_min": 0,
                "impurities_max": 0.2
            }
        }

        return mock_data.get(customer)
