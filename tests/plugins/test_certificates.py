"""Tests for the Certificates Plugin.

Tests verify that:
- CertificatesPlugin checks if supplier has all required certificates
- Certificate equivalents mapping works correctly (cGMP ≈ GMP, etc.)
- Returns compliant (1.0) or non-compliant (0.0) status with reasoning
- Blocking issues are reported for missing certificates
"""

import pytest
from datetime import datetime
from typing import List, Dict, Any

from makeathon.agents.core.data_models import (
    SupplierData,
    CustomerRequirements,
    PluginResult,
    Certificate,
)
from makeathon.agents.plugins.certificates import CertificatesPlugin


class TestCertificatesPluginProperties:
    """Tests that verify the CertificatesPlugin properties."""

    def test_plugin_name(self):
        """Verify the plugin name is 'certificates'."""
        plugin = CertificatesPlugin()
        assert plugin.name == "certificates"

    def test_weight_default(self):
        """Verify the weight_default is 0.4 (high importance)."""
        plugin = CertificatesPlugin()
        assert plugin.weight_default == 0.4

    def test_required_data_fields(self):
        """Verify required_data_fields includes 'certificates'."""
        plugin = CertificatesPlugin()
        fields = plugin.required_data_fields
        assert isinstance(fields, list)
        assert "certificates" in fields


class TestCertificatesPluginCompliant:
    """Tests for compliant supplier cases."""

    def test_supplier_with_all_required_certificates(self):
        """Verify supplier with all required certificates is marked compliant."""
        plugin = CertificatesPlugin()

        supplier = SupplierData(
            name="Compliant Supplier",
            country="Germany",
            certificates=[
                Certificate(
                    name="ISO 9001",
                    issuer="TUV SUD",
                    valid_until=datetime(2026, 12, 31),
                ),
                Certificate(
                    name="cGMP",
                    issuer="FDA",
                    valid_until=datetime(2027, 6, 30),
                ),
            ],
        )

        customer = CustomerRequirements(
            company_name="Test Customer",
            quality_tier="premium",
            certificates_required=["ISO 9001", "cGMP"],
        )

        result = plugin.check_compliance(supplier, customer, {})

        assert result.score == 1.0
        assert result.confidence > 0.8
        assert result.plugin_name == "certificates"
        assert len(result.blocking_issues) == 0

    def test_supplier_with_certificate_equivalents(self):
        """Verify certificate equivalents mapping works (cGMP ≈ GMP)."""
        plugin = CertificatesPlugin()

        # Supplier has GMP, customer requires cGMP (they are equivalent)
        supplier = SupplierData(
            name="Equivalent Supplier",
            country="USA",
            certificates=[
                Certificate(
                    name="ISO 9001",
                    issuer="TUV SUD",
                    valid_until=datetime(2026, 12, 31),
                ),
                Certificate(
                    name="GMP",
                    issuer="FDA",
                    valid_until=datetime(2027, 6, 30),
                ),
            ],
        )

        customer = CustomerRequirements(
            company_name="Test Customer",
            quality_tier="premium",
            certificates_required=["ISO 9001", "cGMP"],
        )

        result = plugin.check_compliance(supplier, customer, {})

        # Should be compliant because GMP is equivalent to cGMP
        assert result.score == 1.0
        assert result.blocking_issues == []

    def test_supplier_with_extra_certificates(self):
        """Verify supplier with extra certificates beyond requirements is still compliant."""
        plugin = CertificatesPlugin()

        supplier = SupplierData(
            name="Extra Certified Supplier",
            country="Germany",
            certificates=[
                Certificate(
                    name="ISO 9001",
                    issuer="TUV SUD",
                    valid_until=datetime(2026, 12, 31),
                ),
                Certificate(
                    name="ISO 14001",
                    issuer="TUV SUD",
                    valid_until=datetime(2026, 12, 31),
                ),
                Certificate(
                    name="cGMP",
                    issuer="FDA",
                    valid_until=datetime(2027, 6, 30),
                ),
            ],
        )

        customer = CustomerRequirements(
            company_name="Test Customer",
            quality_tier="premium",
            certificates_required=["ISO 9001", "cGMP"],
        )

        result = plugin.check_compliance(supplier, customer, {})

        assert result.score == 1.0
        assert result.blocking_issues == []


class TestCertificatesPluginNonCompliant:
    """Tests for non-compliant supplier cases."""

    def test_supplier_with_missing_certificates(self):
        """Verify supplier missing required certificates is non-compliant."""
        plugin = CertificatesPlugin()

        # Supplier only has ISO 9001, missing cGMP
        supplier = SupplierData(
            name="Non-Compliant Supplier",
            country="Germany",
            certificates=[
                Certificate(
                    name="ISO 9001",
                    issuer="TUV SUD",
                    valid_until=datetime(2026, 12, 31),
                ),
            ],
        )

        customer = CustomerRequirements(
            company_name="Test Customer",
            quality_tier="premium",
            certificates_required=["ISO 9001", "cGMP"],
        )

        result = plugin.check_compliance(supplier, customer, {})

        assert result.score == 0.0
        assert len(result.blocking_issues) > 0
        assert "cGMP" in result.reasoning or "missing" in result.reasoning.lower()

    def test_supplier_with_no_certificates(self):
        """Verify supplier with no certificates is non-compliant."""
        plugin = CertificatesPlugin()

        supplier = SupplierData(
            name="Uncertified Supplier",
            country="Germany",
            certificates=[],
        )

        customer = CustomerRequirements(
            company_name="Test Customer",
            quality_tier="premium",
            certificates_required=["ISO 9001", "cGMP"],
        )

        result = plugin.check_compliance(supplier, customer, {})

        assert result.score == 0.0
        assert len(result.blocking_issues) > 0

    def test_supplier_with_some_missing_certificates(self):
        """Verify supplier missing some (but not all) required certificates is non-compliant."""
        plugin = CertificatesPlugin()

        supplier = SupplierData(
            name="Partially Compliant Supplier",
            country="Germany",
            certificates=[
                Certificate(
                    name="ISO 9001",
                    issuer="TUV SUD",
                    valid_until=datetime(2026, 12, 31),
                ),
            ],
        )

        customer = CustomerRequirements(
            company_name="Test Customer",
            quality_tier="premium",
            certificates_required=["ISO 9001", "cGMP", "ISO 14001"],
        )

        result = plugin.check_compliance(supplier, customer, {})

        assert result.score == 0.0
        assert len(result.blocking_issues) > 0


class TestCertificatesPluginNoRequirements:
    """Tests for cases with no certificate requirements."""

    def test_no_required_certificates(self):
        """Verify supplier is compliant when customer has no certificate requirements."""
        plugin = CertificatesPlugin()

        supplier = SupplierData(
            name="Simple Supplier",
            country="Germany",
            certificates=[],
        )

        customer = CustomerRequirements(
            company_name="Test Customer",
            quality_tier="standard",
            certificates_required=[],
        )

        result = plugin.check_compliance(supplier, customer, {})

        assert result.score == 1.0
        assert result.blocking_issues == []
