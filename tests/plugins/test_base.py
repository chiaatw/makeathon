"""Tests for the plugin base interface.

Tests verify that:
- CompliancePlugin is an abstract base class that cannot be instantiated
- Concrete implementations of CompliancePlugin can be created and used
- All required properties and methods work correctly
"""

import pytest
from datetime import datetime
from typing import List, Dict, Any

from makeathon.agents.core.data_models import (
    SupplierData,
    CustomerRequirements,
    PluginResult,
    Certificate,
    PricingInfo,
)
from makeathon.agents.plugins.base import CompliancePlugin


class TestCompliancePluginAbstract:
    """Tests that CompliancePlugin is abstract and cannot be instantiated directly."""

    def test_cannot_instantiate_abstract_class(self):
        """Verify that CompliancePlugin cannot be instantiated directly."""
        with pytest.raises(TypeError):
            CompliancePlugin()


class MockPlugin(CompliancePlugin):
    """Mock implementation of CompliancePlugin for testing."""

    @property
    def name(self) -> str:
        return "MockPlugin"

    @property
    def weight_default(self) -> float:
        return 0.5

    @property
    def required_data_fields(self) -> List[str]:
        return ["certificates", "quality_metrics"]

    def check_compliance(
        self,
        supplier_data: SupplierData,
        customer_requirements: CustomerRequirements,
        user_filters: Dict[str, Any],
    ) -> PluginResult:
        """Simple mock implementation that checks for certificates."""
        supplier_cert_names = [c.name for c in supplier_data.certificates]
        has_required = all(
            cert_name in supplier_cert_names
            for cert_name in customer_requirements.certificates_required
        )
        score = 1.0 if has_required else 0.0
        return PluginResult(
            plugin_name=self.name,
            score=score,
            confidence=0.9,
            reasoning="Mock plugin verified certificates",
            blocking_issues=[] if has_required else ["Missing required certificates"],
        )


class TestCompliancePluginInterface:
    """Tests that verify the CompliancePlugin interface works correctly."""

    def test_concrete_implementation_instantiation(self):
        """Verify that a concrete implementation can be instantiated."""
        plugin = MockPlugin()
        assert plugin is not None

    def test_name_property(self):
        """Verify the name property returns a string."""
        plugin = MockPlugin()
        assert isinstance(plugin.name, str)
        assert plugin.name == "MockPlugin"

    def test_weight_default_property(self):
        """Verify the weight_default property returns a float."""
        plugin = MockPlugin()
        assert isinstance(plugin.weight_default, float)
        assert plugin.weight_default == 0.5

    def test_required_data_fields_property(self):
        """Verify the required_data_fields property returns a list of strings."""
        plugin = MockPlugin()
        fields = plugin.required_data_fields
        assert isinstance(fields, list)
        assert all(isinstance(f, str) for f in fields)
        assert "certificates" in fields
        assert "quality_metrics" in fields

    def test_check_compliance_method_returns_plugin_result(self):
        """Verify that check_compliance returns a PluginResult."""
        plugin = MockPlugin()
        supplier = SupplierData(
            name="Test Supplier",
            country="USA",
            certificates=[
                Certificate(
                    name="ISO 9001",
                    issuer="TUV SUD",
                    valid_until=datetime(2025, 12, 31),
                )
            ],
        )
        customer = CustomerRequirements(
            company_name="Test Customer",
            quality_tier="premium",
            certificates_required=["ISO 9001"],
        )
        user_filters = {}

        result = plugin.check_compliance(supplier, customer, user_filters)

        assert isinstance(result, PluginResult)
        assert result.plugin_name == "MockPlugin"
        assert result.score == 1.0
        assert result.confidence == 0.9

    def test_check_compliance_with_missing_data(self):
        """Verify check_compliance handles missing required data correctly."""
        plugin = MockPlugin()
        supplier = SupplierData(
            name="Test Supplier",
            country="USA",
            certificates=[],  # No certificates
        )
        customer = CustomerRequirements(
            company_name="Test Customer",
            quality_tier="premium",
            certificates_required=["ISO 9001"],
        )
        user_filters = {}

        result = plugin.check_compliance(supplier, customer, user_filters)

        assert isinstance(result, PluginResult)
        assert result.score == 0.0
        assert len(result.blocking_issues) > 0
