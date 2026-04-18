"""Certificates Plugin for Enhanced Compliance Agent.

This module implements a concrete plugin for checking supplier certificate
compliance. It verifies that suppliers have all required certifications
from customer requirements and supports certificate equivalents mapping.
"""

from typing import List, Dict, Any, Set

from makeathon.agents.core.data_models import (
    SupplierData,
    CustomerRequirements,
    PluginResult,
)
from makeathon.agents.plugins.base import CompliancePlugin


class CertificatesPlugin(CompliancePlugin):
    """Concrete implementation of CompliancePlugin for certificate checking.

    This plugin checks whether a supplier holds all required certifications
    specified by the customer. It supports certificate equivalence mapping
    to recognize that different certificate names may fulfill the same
    compliance requirement (e.g., cGMP and GMP are equivalent).

    Attributes:
        name: The plugin name "certificates"
        weight_default: 0.4 (high importance for compliance)
        required_data_fields: ["certificates"]
    """

    # Certificate equivalents mapping
    # Maps certificate names to their equivalent forms
    _CERTIFICATE_EQUIVALENTS = {
        "cGMP": {"cGMP", "GMP"},
        "GMP": {"cGMP", "GMP"},
        "ISO 9001": {"ISO 9001"},
        "ISO 14001": {"ISO 14001"},
        "ISO 45001": {"ISO 45001"},
        "IATF 16949": {"IATF 16949"},
        "ISO 13485": {"ISO 13485"},
    }

    @property
    def name(self) -> str:
        """The unique name of this plugin.

        Returns:
            str: "certificates"
        """
        return "certificates"

    @property
    def weight_default(self) -> float:
        """Default weight for this plugin in compliance score aggregation.

        Certificates are important for compliance, so this has a high weight.

        Returns:
            float: 0.4 (high importance)
        """
        return 0.4

    @property
    def required_data_fields(self) -> List[str]:
        """List of supplier data fields required by this plugin.

        Returns:
            List[str]: ["certificates"]
        """
        return ["certificates"]

    def _normalize_certificate(self, cert_name: str) -> Set[str]:
        """Normalize a certificate name to its equivalence set.

        Args:
            cert_name: The certificate name to normalize

        Returns:
            Set[str]: Set of equivalent certificate names (includes the original)
        """
        # Check if this certificate has known equivalents
        if cert_name in self._CERTIFICATE_EQUIVALENTS:
            return self._CERTIFICATE_EQUIVALENTS[cert_name]

        # If not in the equivalents map, return a set with just itself
        return {cert_name}

    def _get_supplier_certificates_normalized(
        self, supplier_data: SupplierData
    ) -> Set[str]:
        """Get supplier certificates, normalized to handle equivalents.

        Args:
            supplier_data: The supplier data containing certificates

        Returns:
            Set[str]: Set of all normalized certificate names
        """
        normalized_certs = set()

        for cert in supplier_data.certificates:
            # Get all equivalent forms of this certificate
            equivalents = self._normalize_certificate(cert.name)
            normalized_certs.update(equivalents)

        return normalized_certs

    def _check_certificate_satisfied(
        self, required_cert: str, supplier_certs: Set[str]
    ) -> bool:
        """Check if a required certificate is satisfied by supplier certificates.

        Handles certificate equivalents (e.g., GMP satisfies cGMP requirement).

        Args:
            required_cert: The required certificate name
            supplier_certs: Set of normalized supplier certificate names

        Returns:
            bool: True if the requirement is satisfied, False otherwise
        """
        # Get all equivalent forms of the required certificate
        required_equivalents = self._normalize_certificate(required_cert)

        # Check if any equivalent is in the supplier's certificates
        return bool(required_equivalents & supplier_certs)

    def check_compliance(
        self,
        supplier_data: SupplierData,
        customer_requirements: CustomerRequirements,
        user_filters: Dict[str, Any],
    ) -> PluginResult:
        """Check if supplier has all required certificates.

        Args:
            supplier_data: Complete supplier information
            customer_requirements: Customer's compliance requirements
            user_filters: Additional user-specified filters

        Returns:
            PluginResult: Result with score (1.0 compliant, 0.0 non-compliant),
                         confidence, reasoning, and blocking issues
        """
        # Get normalized set of supplier certificates
        supplier_certs = self._get_supplier_certificates_normalized(supplier_data)

        # Check which required certificates are missing
        missing_certificates = []
        for required_cert in customer_requirements.certificates_required:
            if not self._check_certificate_satisfied(required_cert, supplier_certs):
                missing_certificates.append(required_cert)

        # Determine compliance status
        is_compliant = len(missing_certificates) == 0

        if is_compliant:
            # Supplier has all required certificates
            score = 1.0
            confidence = 0.95
            blocking_issues = []

            if customer_requirements.certificates_required:
                reasoning = (
                    f"Supplier has all {len(customer_requirements.certificates_required)} "
                    f"required certificate(s): "
                    f"{', '.join(customer_requirements.certificates_required)}"
                )
            else:
                reasoning = "No certificate requirements specified by customer"
        else:
            # Supplier is missing required certificates
            score = 0.0
            confidence = 0.95
            blocking_issues = [
                f"Missing required certificate(s): {', '.join(missing_certificates)}"
            ]
            reasoning = (
                f"Supplier is missing {len(missing_certificates)} required certificate(s): "
                f"{', '.join(missing_certificates)}. "
                f"Supplier has: {', '.join(sorted(supplier_certs)) if supplier_certs else 'none'}"
            )

        return PluginResult(
            plugin_name=self.name,
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            blocking_issues=blocking_issues,
        )
