"""
Tests for external supplier evidence caching.

Tests the SupplierEvidenceCache class which manages cached supplier
compliance, capability, and pricing data.
"""

import pytest
import json
from pathlib import Path
from enrichment.supplier_cache import SupplierEvidence, SupplierEvidenceCache


class TestSupplierEvidence:
    """Tests for the SupplierEvidence dataclass."""

    def test_supplier_evidence_initialization(self):
        """Test creating a SupplierEvidence instance."""
        evidence = SupplierEvidence(
            supplier_name="DSM",
            substance="Vitamin D3",
            quality_certifications=["USP", "ISO 9001"],
            compliance_notes="Meets all FDA requirements",
            pricing_range_per_kg="$45-55",
            moq_units=100,
            lead_time_days=30
        )

        assert evidence.supplier_name == "DSM"
        assert "USP" in evidence.quality_certifications
        assert evidence.moq_units == 100

    def test_supplier_evidence_str(self):
        """Test string representation."""
        evidence = SupplierEvidence(
            supplier_name="DSM",
            substance="Vitamin D3",
            quality_certifications=["USP"],
            compliance_notes="FDA compliant",
            pricing_range_per_kg="$45-55",
            moq_units=100,
            lead_time_days=30
        )

        str_repr = str(evidence)
        assert "DSM" in str_repr


class TestSupplierEvidenceCache:
    """Tests for the SupplierEvidenceCache class."""

    def test_cache_initialization(self):
        """Test creating a SupplierEvidenceCache instance."""
        cache = SupplierEvidenceCache()
        assert cache is not None

    def test_cache_load_from_file(self):
        """Test loading evidence from cache file."""
        cache = SupplierEvidenceCache()
        evidence_list = cache.load_evidence()

        assert isinstance(evidence_list, list)
        assert len(evidence_list) > 0

    def test_get_evidence_for_supplier(self):
        """Test retrieving evidence for a specific supplier."""
        cache = SupplierEvidenceCache()

        # Get all evidence first to find a valid supplier
        all_evidence = cache.load_evidence()
        if all_evidence:
            supplier_name = all_evidence[0].supplier_name
            evidence = cache.get_evidence_for_supplier(supplier_name)

            assert evidence is not None
            assert evidence.supplier_name == supplier_name

    def test_get_evidence_for_substance(self):
        """Test retrieving evidence for a specific substance."""
        cache = SupplierEvidenceCache()
        evidence_list = cache.get_evidence_for_substance("Vitamin D3")

        assert isinstance(evidence_list, list)
        assert all(e.substance == "Vitamin D3" for e in evidence_list)

    def test_cache_suppliers_for_substance(self):
        """Test getting all suppliers for a substance."""
        cache = SupplierEvidenceCache()
        suppliers = cache.get_suppliers_for_substance("Vitamin D3")

        assert isinstance(suppliers, list)
        assert len(suppliers) > 0

    def test_evidence_quality_filtering(self):
        """Test filtering evidence by certification."""
        cache = SupplierEvidenceCache()
        evidence = cache.get_evidence_by_certification("USP")

        assert isinstance(evidence, list)
        for e in evidence:
            assert "USP" in e.quality_certifications

    def test_evidence_compliance_notes(self):
        """Test that compliance notes are captured."""
        cache = SupplierEvidenceCache()
        evidence_list = cache.load_evidence()

        for evidence in evidence_list:
            assert evidence.compliance_notes is not None
            assert len(evidence.compliance_notes) > 0

    def test_pricing_comparison(self):
        """Test getting pricing information for suppliers."""
        cache = SupplierEvidenceCache()
        evidence_list = cache.load_evidence()

        # All evidence should have pricing
        for evidence in evidence_list:
            assert evidence.pricing_range_per_kg is not None

    def test_cache_reload(self):
        """Test reloading cache from file."""
        cache = SupplierEvidenceCache()

        initial_count = len(cache.load_evidence())
        reloaded_count = len(cache.load_evidence())

        assert initial_count == reloaded_count

    def test_get_evidence_dict(self):
        """Test getting evidence as dictionary format."""
        cache = SupplierEvidenceCache()
        evidence = cache.get_evidence_dict()

        assert isinstance(evidence, dict)
        # Should have supplier names as keys
        assert len(evidence) > 0
