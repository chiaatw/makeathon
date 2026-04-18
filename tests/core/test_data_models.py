"""Tests for core data models."""

import pytest
from datetime import datetime, timedelta
from makeathon.agents.core.data_models import (
    Certificate,
    PricingInfo,
    SupplierData,
    CustomerRequirements,
    PluginResult,
    ComplianceResult,
)


class TestCertificate:
    """Test Certificate model."""

    def test_certificate_creation(self):
        """Test creating a Certificate instance."""
        cert = Certificate(
            name="ISO 9001",
            issuer="TUV SUD",
            valid_until=datetime(2026, 12, 31),
        )
        assert cert.name == "ISO 9001"
        assert cert.issuer == "TUV SUD"
        assert cert.valid_until == datetime(2026, 12, 31)


class TestPricingInfo:
    """Test PricingInfo model."""

    def test_pricing_info_creation(self):
        """Test creating a PricingInfo instance."""
        pricing = PricingInfo(
            min_price=10.0,
            max_price=15.0,
            currency="USD",
            moq=100,
        )
        assert pricing.min_price == 10.0
        assert pricing.max_price == 15.0
        assert pricing.currency == "USD"
        assert pricing.moq == 100


class TestSupplierData:
    """Test SupplierData model."""

    def test_supplier_data_creation_with_all_fields(self):
        """Test creating a SupplierData instance with all fields."""
        cert = Certificate(
            name="ISO 9001",
            issuer="TUV SUD",
            valid_until=datetime(2026, 12, 31),
        )
        pricing = PricingInfo(
            min_price=10.0,
            max_price=15.0,
            currency="USD",
            moq=100,
        )
        quality_metrics = {
            "defect_rate": 0.5,
            "on_time_delivery_rate": 0.95,
            "quality_certifications": ["ISO 9001"],
        }
        delivery_info = {
            "lead_time_days": 14,
            "shipping_methods": ["Sea"],
            "incoterms": "FOB",
        }

        supplier = SupplierData(
            name="Acme Manufacturing",
            country="China",
            certificates=[cert],
            pricing=pricing,
            quality_metrics=quality_metrics,
            delivery_info=delivery_info,
            data_sources=["supplier_portal", "third_party_audit"],
            confidence_breakdown={
                "certificates": 0.95,
                "pricing": 0.85,
                "quality": 0.90,
            },
            last_updated=datetime(2026, 4, 18),
        )

        assert supplier.name == "Acme Manufacturing"
        assert supplier.country == "China"
        assert len(supplier.certificates) == 1
        assert supplier.certificates[0].name == "ISO 9001"
        assert supplier.pricing.min_price == 10.0
        assert supplier.quality_metrics["defect_rate"] == 0.5
        assert supplier.delivery_info["lead_time_days"] == 14
        assert supplier.data_sources == ["supplier_portal", "third_party_audit"]
        assert supplier.confidence_breakdown["certificates"] == 0.95
        assert supplier.last_updated == datetime(2026, 4, 18)


class TestCustomerRequirements:
    """Test CustomerRequirements model."""

    def test_customer_requirements_creation(self):
        """Test creating a CustomerRequirements instance."""
        requirements = CustomerRequirements(
            company_name="TechCorp Inc",
            quality_tier="premium",
            certificates_required=["ISO 9001", "ISO 14001"],
            constraints={
                "max_defect_rate": 0.01,
                "min_on_time_delivery": 0.98,
                "max_lead_time_days": 21,
            },
        )

        assert requirements.company_name == "TechCorp Inc"
        assert requirements.quality_tier == "premium"
        assert requirements.certificates_required == ["ISO 9001", "ISO 14001"]
        assert requirements.constraints["max_defect_rate"] == 0.01
        assert requirements.constraints["min_on_time_delivery"] == 0.98
        assert requirements.constraints["max_lead_time_days"] == 21


class TestPluginResult:
    """Test PluginResult model."""

    def test_plugin_result_creation(self):
        """Test creating a PluginResult instance."""
        plugin_result = PluginResult(
            plugin_name="certificate_checker",
            score=0.92,
            confidence=0.88,
            reasoning="Supplier has required ISO 9001 and ISO 14001 certifications",
            blocking_issues=[],
        )

        assert plugin_result.plugin_name == "certificate_checker"
        assert plugin_result.score == 0.92
        assert plugin_result.confidence == 0.88
        assert plugin_result.reasoning == "Supplier has required ISO 9001 and ISO 14001 certifications"
        assert plugin_result.blocking_issues == []

    def test_plugin_result_with_blocking_issues(self):
        """Test creating a PluginResult instance with blocking issues."""
        plugin_result = PluginResult(
            plugin_name="quality_checker",
            score=0.45,
            confidence=0.75,
            reasoning="Quality metrics below thresholds",
            blocking_issues=["defect_rate_exceeds_threshold", "delivery_unreliable"],
        )

        assert plugin_result.plugin_name == "quality_checker"
        assert len(plugin_result.blocking_issues) == 2
        assert "defect_rate_exceeds_threshold" in plugin_result.blocking_issues


class TestComplianceResult:
    """Test ComplianceResult model."""

    def test_compliance_result_creation(self):
        """Test creating a ComplianceResult instance."""
        plugin_results = [
            PluginResult(
                plugin_name="certificate_checker",
                score=0.92,
                confidence=0.88,
                reasoning="Certifications valid",
                blocking_issues=[],
            ),
            PluginResult(
                plugin_name="quality_checker",
                score=0.87,
                confidence=0.92,
                reasoning="Quality metrics acceptable",
                blocking_issues=[],
            ),
        ]

        compliance_result = ComplianceResult(
            overall_score=0.89,
            overall_confidence=0.90,
            plugin_results=plugin_results,
            reasoning_chain=[
                "Verified certificates are valid",
                "Quality metrics within acceptable range",
                "Delivery performance meets requirements",
            ],
            data_gaps=["recent_audit_report", "sustainability_certifications"],
            recommendations=[
                "Request updated audit report",
                "Consider sustainability certifications",
            ],
        )

        assert compliance_result.overall_score == 0.89
        assert compliance_result.overall_confidence == 0.90
        assert len(compliance_result.plugin_results) == 2
        assert len(compliance_result.reasoning_chain) == 3
        assert len(compliance_result.data_gaps) == 2
        assert len(compliance_result.recommendations) == 2
