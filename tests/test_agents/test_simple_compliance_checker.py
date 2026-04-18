"""
Tests for SimpleComplianceChecker.

Tests focus on:
1. Certificate status checking
2. Supply chain synergy calculation
3. Reasoning generation for multi-agent
"""

import pytest
from agents.simple_compliance_checker import SimpleComplianceChecker


@pytest.fixture
def checker():
    """Create checker instance with mock data."""
    return SimpleComplianceChecker()


class TestComplianceChecker:
    """Test SimpleComplianceChecker functionality."""

    def test_compliant_supplier_pharma(self, checker):
        """Test: DSM → PharmaCorp (should be COMPLIANT)."""
        result = checker.check("Vitamin D3", "DSM", "PharmaCorp")

        assert result.compliance_status == "COMPLIANT"
        assert result.confidence >= 0.9
        assert "Certs" in result.reasoning
        assert "Synergy" in result.reasoning

    def test_non_compliant_missing_certs(self, checker):
        """Test: Prinova USA → PharmaCorp (missing cGMP, etc)."""
        result = checker.check("Vitamin D3", "Prinova USA", "PharmaCorp")

        assert result.compliance_status == "NON_COMPLIANT"
        assert result.confidence <= 0.6
        assert "cGMP" in result.reasoning or "Missing" in result.reasoning

    def test_compliant_supplement_supplier(self, checker):
        """Test: BASF → FoodSupplementCo (should be COMPLIANT)."""
        result = checker.check("Vitamin D3", "BASF", "FoodSupplementCo")

        assert result.compliance_status == "COMPLIANT"
        assert "Certs" in result.reasoning

    def test_synergy_calculation_pharma(self, checker):
        """Test: Pharma tier implies 3 suppliers, so 20% savings."""
        result = checker.check("Vitamin D3", "DSM", "PharmaCorp")

        # Pharma tier = 3 suppliers → 20% savings
        assert result.synergy_potential == 20.0
        assert "20%" in result.reasoning

    def test_synergy_calculation_supplement(self, checker):
        """Test: Supplement tier implies 2 suppliers, so 10% savings."""
        result = checker.check("Vitamin D3", "DSM", "FoodSupplementCo")

        # Supplement tier = 2 suppliers → 10% savings
        assert result.synergy_potential == 10.0
        assert "10%" in result.reasoning

    def test_synergy_zero_for_cosmetics(self, checker):
        """Test: Cosmetics tier single source, so 0% savings."""
        result = checker.check("Vitamin D3", "DSM", "Cosmetics Inc")

        # Cosmetics tier = 1 supplier → 0% savings
        assert result.synergy_potential == 0.0
        assert "None (single source)" in result.reasoning

    def test_unknown_supplier(self, checker):
        """Test: Unknown supplier returns INSUFFICIENT_DATA."""
        result = checker.check("Vitamin D3", "UnknownCorp", "PharmaCorp")

        assert result.compliance_status == "INSUFFICIENT_DATA"
        assert "not found" in result.reasoning

    def test_unknown_customer(self, checker):
        """Test: Unknown customer returns INSUFFICIENT_DATA."""
        result = checker.check("Vitamin D3", "DSM", "UnknownCompany")

        assert result.compliance_status == "INSUFFICIENT_DATA"
        assert "not found" in result.reasoning

    def test_reasoning_format(self, checker):
        """Test: Reasoning includes all expected parts."""
        result = checker.check("Vitamin D3", "DSM", "PharmaCorp")

        reasoning = result.reasoning
        # Should include cert status, synergy, geo risk
        assert "|" in reasoning  # Multiple parts separated by |
        assert "Certs" in reasoning or "✓" in reasoning
        assert "Synergy" in reasoning or "💰" in reasoning
        assert "Geo" in reasoning or "🌍" in reasoning

    def test_geopolitical_risk_low(self, checker):
        """Test: Netherlands = LOW risk."""
        result = checker.check("Vitamin D3", "DSM", "PharmaCorp")
        assert "Low" in result.reasoning or "LOW" in result.reasoning

    def test_geopolitical_risk_medium(self, checker):
        """Test: Germany = LOW risk (EU)."""
        result = checker.check("Vitamin D3", "BASF", "PharmaCorp")
        assert "Low" in result.reasoning or "LOW" in result.reasoning

    def test_certificate_gap_message(self, checker):
        """Test: Missing certs are reported."""
        result = checker.check("Vitamin D3", "Prinova USA", "PharmaCorp")
        # Prinova USA has only GMP, PharmaCorp needs cGMP, ISO 9001, ISO 14644
        assert "Missing" in result.reasoning or "⚠️" in result.reasoning


class TestCertificateChecking:
    """Test certificate checking logic."""

    def test_all_certs_present(self, checker):
        """Test: All required certs present = no gaps."""
        supplier = {
            "supplier": "DSM",
            "certificates": ["cGMP", "ISO 9001", "ISO 14644"]
        }
        customer = {
            "certificates_required": ["cGMP", "ISO 9001", "ISO 14644"]
        }

        gaps = checker._check_certificates(supplier, customer)
        assert gaps == []

    def test_partial_certs_present(self, checker):
        """Test: Missing some certs."""
        supplier = {
            "supplier": "BASF",
            "certificates": ["GMP", "ISO 9001"]
        }
        customer = {
            "certificates_required": ["cGMP", "ISO 9001", "ISO 14644"]
        }

        gaps = checker._check_certificates(supplier, customer)
        assert "cGMP" in gaps
        assert "ISO 14644" in gaps

    def test_no_certs_required(self, checker):
        """Test: No certs required = no gaps."""
        supplier = {"certificates": []}
        customer = {"certificates_required": [""]}

        gaps = checker._check_certificates(supplier, customer)
        assert gaps == []


class TestSynergyCalculation:
    """Test synergy/consolidation savings calculation."""

    def test_pharma_tier_consolidation(self, checker):
        """Test: Pharma tier = 3 suppliers = 20% savings."""
        synergy = checker._calculate_synergy("DSM", "PharmaCorp")

        assert synergy["current_suppliers"] == 3
        assert synergy["savings_percent"] == 20.0

    def test_supplement_tier_consolidation(self, checker):
        """Test: Supplement tier = 2 suppliers = 10% savings."""
        synergy = checker._calculate_synergy("DSM", "FoodSupplementCo")

        assert synergy["current_suppliers"] == 2
        assert synergy["savings_percent"] == 10.0

    def test_cosmetics_tier_no_savings(self, checker):
        """Test: Cosmetics tier = 1 supplier = 0% savings."""
        synergy = checker._calculate_synergy("DSM", "Cosmetics Inc")

        assert synergy["current_suppliers"] == 1
        assert synergy["savings_percent"] == 0

    def test_synergy_consolidation_target(self, checker):
        """Test: Synergy tracks target supplier."""
        synergy = checker._calculate_synergy("DSM", "PharmaCorp")

        assert synergy["consolidated_to"] == "DSM"
