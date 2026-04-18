"""
External supplier evidence caching system.

This module manages cached evidence about suppliers including certifications,
compliance information, pricing, and lead times. Used for offline analysis
and consolidation decision support.
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class SupplierEvidence:
    """
    Represents cached evidence about a supplier's capabilities and compliance.

    Attributes:
        supplier_name: Name of the supplier
        substance: Substance/material this evidence applies to
        quality_certifications: List of certifications (USP, ISO, etc.)
        compliance_notes: Descriptive notes about compliance and quality
        pricing_range_per_kg: Price range as string (e.g., "$45-55")
        moq_units: Minimum order quantity in kg
        lead_time_days: Typical lead time in days
    """
    supplier_name: str
    substance: str
    quality_certifications: List[str] = field(default_factory=list)
    compliance_notes: str = ""
    pricing_range_per_kg: str = ""
    moq_units: int = 0
    lead_time_days: int = 0

    def __str__(self) -> str:
        """Return human-readable representation."""
        certs = ", ".join(self.quality_certifications)
        return (
            f"SupplierEvidence({self.supplier_name} | {self.substance} | "
            f"{certs} | MOQ: {self.moq_units}kg)"
        )

    def __repr__(self) -> str:
        """Return developer-friendly representation."""
        return (
            f"SupplierEvidence(supplier={self.supplier_name}, "
            f"substance={self.substance})"
        )

    def has_certification(self, cert: str) -> bool:
        """Check if supplier has a specific certification."""
        return cert in self.quality_certifications

    def get_price_range(self) -> tuple[float, float]:
        """Extract min and max price from pricing string."""
        try:
            # Parse strings like "$45-55" or "45-55"
            price_str = self.pricing_range_per_kg.replace("$", "")
            parts = price_str.split("-")
            if len(parts) == 2:
                return (float(parts[0]), float(parts[1]))
        except (ValueError, AttributeError):
            pass
        return (0.0, 0.0)


class SupplierEvidenceCache:
    """
    Manages cached evidence about supplement suppliers.

    Loads evidence from external JSON file and provides query interfaces
    for filtering and accessing supplier information.
    """

    def __init__(self, cache_file: Optional[str] = None):
        """
        Initialize the cache.

        Args:
            cache_file: Path to external evidence JSON file.
                       Defaults to data/external_evidence.json
        """
        if cache_file is None:
            # Default to data/external_evidence.json relative to this file
            project_root = Path(__file__).parent.parent
            cache_file = str(project_root / "data" / "external_evidence.json")

        self.cache_file = cache_file
        self._cache: Dict[str, SupplierEvidence] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load evidence from JSON file into memory."""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._cache = {}
            for supplier_data in data.get('suppliers', []):
                # Create unique key based on supplier and substance
                key = f"{supplier_data['supplier_name']}_{supplier_data['substance']}"
                evidence = SupplierEvidence(
                    supplier_name=supplier_data['supplier_name'],
                    substance=supplier_data['substance'],
                    quality_certifications=supplier_data.get('quality_certifications', []),
                    compliance_notes=supplier_data.get('compliance_notes', ''),
                    pricing_range_per_kg=supplier_data.get('pricing_range_per_kg', ''),
                    moq_units=supplier_data.get('moq_units', 0),
                    lead_time_days=supplier_data.get('lead_time_days', 0)
                )
                self._cache[key] = evidence

        except FileNotFoundError:
            raise FileNotFoundError(f"Evidence cache file not found: {self.cache_file}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in cache file: {self.cache_file}")

    def load_evidence(self) -> List[SupplierEvidence]:
        """
        Get all cached evidence.

        Returns:
            List of all SupplierEvidence objects
        """
        return list(self._cache.values())

    def get_evidence_for_supplier(self, supplier_name: str) -> Optional[SupplierEvidence]:
        """
        Get evidence for a specific supplier and vitamin D3.

        Args:
            supplier_name: Name of the supplier

        Returns:
            SupplierEvidence object or None if not found
        """
        # Look for "Vitamin D3" substance entry
        key = f"{supplier_name}_Vitamin D3"
        return self._cache.get(key)

    def get_evidence_for_substance(self, substance: str) -> List[SupplierEvidence]:
        """
        Get all evidence entries for a specific substance.

        Args:
            substance: Substance name (e.g., "Vitamin D3")

        Returns:
            List of SupplierEvidence for that substance
        """
        return [
            evidence for evidence in self._cache.values()
            if evidence.substance == substance
        ]

    def get_suppliers_for_substance(self, substance: str) -> List[str]:
        """
        Get list of suppliers for a specific substance.

        Args:
            substance: Substance name

        Returns:
            Sorted list of unique supplier names
        """
        suppliers = set()
        for evidence in self.get_evidence_for_substance(substance):
            suppliers.add(evidence.supplier_name)
        return sorted(list(suppliers))

    def get_evidence_by_certification(self, certification: str) -> List[SupplierEvidence]:
        """
        Get all evidence entries with a specific certification.

        Args:
            certification: Certification code (e.g., "USP", "GMP")

        Returns:
            List of SupplierEvidence with the certification
        """
        return [
            evidence for evidence in self._cache.values()
            if certification in evidence.quality_certifications
        ]

    def get_evidence_dict(self) -> Dict[str, SupplierEvidence]:
        """
        Get evidence as a dictionary keyed by supplier name.

        Returns:
            Dictionary mapping supplier names to SupplierEvidence
        """
        result = {}
        for evidence in self._cache.values():
            if evidence.supplier_name not in result:
                result[evidence.supplier_name] = evidence
        return result

    def get_most_cost_effective(self, substance: str) -> Optional[SupplierEvidence]:
        """
        Get the most cost-effective supplier for a substance.

        Args:
            substance: Substance name

        Returns:
            SupplierEvidence with lowest minimum price
        """
        evidence_list = self.get_evidence_for_substance(substance)
        if not evidence_list:
            return None

        # Find supplier with lowest max price (conservative estimate)
        return min(evidence_list, key=lambda e: e.get_price_range()[1])

    def get_premium_suppliers(self, substance: str) -> List[SupplierEvidence]:
        """
        Get premium suppliers with USP certification.

        Args:
            substance: Substance name

        Returns:
            List of premium suppliers with USP certification
        """
        evidence_list = self.get_evidence_for_substance(substance)
        return [e for e in evidence_list if e.has_certification("USP")]
