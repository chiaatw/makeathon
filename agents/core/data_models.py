"""Core data models for the Enhanced Compliance Agent.

This module defines unified data structures for suppliers, customers, and
compliance analysis results. All models use dataclasses for clean, type-safe
definitions and include metadata for transparency.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class Certificate:
    """Represents a certification held by a supplier.

    Attributes:
        name: Name of the certificate (e.g., "ISO 9001")
        issuer: Organization that issued the certificate (e.g., "TUV SUD")
        valid_until: Expiration date of the certificate
    """
    name: str
    issuer: str
    valid_until: datetime


@dataclass
class PricingInfo:
    """Represents pricing information for a supplier's products.

    Attributes:
        min_price: Minimum unit price
        max_price: Maximum unit price
        currency: Currency code (e.g., "USD", "EUR")
        moq: Minimum order quantity
    """
    min_price: float
    max_price: float
    currency: str
    moq: int


@dataclass
class QualityInfo:
    """Represents quality metrics for a supplier's products.

    Attributes:
        defect_rate: Percentage of defective units (0-1 scale)
        on_time_delivery_rate: Percentage of on-time deliveries (0-1 scale)
        quality_certifications: List of quality-related certifications
    """
    defect_rate: float
    on_time_delivery_rate: float
    quality_certifications: List[str] = field(default_factory=list)


@dataclass
class DeliveryInfo:
    """Represents delivery capabilities and terms.

    Attributes:
        lead_time_days: Standard lead time in days
        shipping_methods: Available shipping methods (e.g., ["Sea", "Air"])
        incoterms: Trade terms (e.g., "FOB", "CIF")
    """
    lead_time_days: int
    shipping_methods: List[str] = field(default_factory=list)
    incoterms: str = ""


@dataclass
class SupplierData:
    """Complete supplier information for compliance analysis.

    This unified structure aggregates all supplier data from multiple sources,
    including metadata about data sources and confidence scores for transparency.

    Attributes:
        name: Supplier company name
        country: Supplier's country of operation
        certificates: List of certifications held
        pricing: Pricing information
        quality_metrics: Quality performance metrics
        delivery_info: Delivery capabilities and terms
        data_sources: List of sources where data was gathered
        confidence_breakdown: Confidence scores for different data aspects
        last_updated: Timestamp of last data update
    """
    name: str
    country: str
    certificates: List[Certificate] = field(default_factory=list)
    pricing: PricingInfo | None = None
    quality_metrics: QualityInfo | None = None
    delivery_info: DeliveryInfo | None = None
    data_sources: List[str] = field(default_factory=list)
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime | None = None


@dataclass
class CustomerRequirements:
    """Customer requirements for supplier compliance.

    Attributes:
        company_name: Name of the customer company
        quality_tier: Desired quality tier (e.g., "premium", "standard")
        certificates_required: List of required certifications
        constraints: Dictionary of specific constraints and limits
    """
    company_name: str
    quality_tier: str
    certificates_required: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginResult:
    """Result from a compliance plugin analysis.

    Each plugin analyzes a specific aspect of supplier compliance and produces
    a score, confidence level, and reasoning.

    Attributes:
        plugin_name: Name of the plugin that generated this result
        score: Compliance score for this aspect (0-1 scale)
        confidence: Confidence level in the score (0-1 scale)
        reasoning: Human-readable explanation of the score
        blocking_issues: List of critical issues that block compliance
    """
    plugin_name: str
    score: float
    confidence: float
    reasoning: str
    blocking_issues: List[str] = field(default_factory=list)


@dataclass
class ComplianceResult:
    """Final compliance analysis result for a supplier.

    Aggregates results from multiple plugins and provides overall compliance
    assessment with transparency into reasoning and data gaps.

    Attributes:
        overall_score: Overall compliance score (0-1 scale)
        overall_confidence: Overall confidence in the assessment (0-1 scale)
        plugin_results: Results from individual plugins
        reasoning_chain: Ordered list of reasoning steps
        data_gaps: List of missing or unavailable data points
        recommendations: Suggested actions or improvements
    """
    overall_score: float
    overall_confidence: float
    plugin_results: List[PluginResult] = field(default_factory=list)
    reasoning_chain: List[str] = field(default_factory=list)
    data_gaps: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
