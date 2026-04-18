"""Abstract base class for compliance plugins.

This module defines the CompliancePlugin abstract base class that all compliance
plugins must implement. It establishes the interface contract for plugin behavior.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from makeathon.agents.core.data_models import (
    SupplierData,
    CustomerRequirements,
    PluginResult,
)


class CompliancePlugin(ABC):
    """Abstract base class for all compliance plugins.

    Each plugin implements a specific aspect of supplier compliance checking.
    Plugins are instantiated by the compliance agent and their check_compliance
    methods are called to analyze supplier data against customer requirements.

    Attributes:
        name: The unique name of the plugin
        weight_default: Default weight for this plugin in aggregation
        required_data_fields: List of supplier data fields required by this plugin
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The unique name of this plugin.

        Returns:
            str: Plugin name (e.g., "CertificatePlugin", "PricingPlugin")
        """
        pass

    @property
    @abstractmethod
    def weight_default(self) -> float:
        """Default weight for this plugin in compliance score aggregation.

        Returns:
            float: Weight value, typically between 0.0 and 1.0
        """
        pass

    @property
    @abstractmethod
    def required_data_fields(self) -> List[str]:
        """List of supplier data fields required by this plugin.

        This list helps the compliance agent identify data gaps and optimize
        data collection. If required fields are missing, the plugin should
        handle gracefully or report appropriate confidence penalties.

        Returns:
            List[str]: List of required field names from SupplierData
        """
        pass

    @abstractmethod
    def check_compliance(
        self,
        supplier_data: SupplierData,
        customer_requirements: CustomerRequirements,
        user_filters: Dict[str, Any],
    ) -> PluginResult:
        """Analyze supplier compliance for a specific aspect.

        This method is the main entry point for plugin execution. It analyzes
        the supplied data and returns a PluginResult with score, confidence,
        reasoning, and any blocking issues.

        Args:
            supplier_data: Complete supplier information for analysis
            customer_requirements: Customer's compliance requirements
            user_filters: Additional user-specified filters or parameters

        Returns:
            PluginResult: Result of the compliance analysis including score,
                         confidence, reasoning, and blocking issues
        """
        pass
