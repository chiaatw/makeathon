"""Enhanced Compliance Agent - Main Public Interface.

This module provides the main public interface for the enhanced compliance
checking system. It maintains backward compatibility with the simple
compliance checker while offering advanced features through the enhanced
system architecture.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging

from makeathon.agents.core.data_models import (
    SupplierData,
    CustomerRequirements,
    ComplianceResult,
)
from makeathon.agents.engine.compliance_engine import ComplianceEngine, ComplianceEngineConfig
from makeathon.agents.scoring.engine import ScoringConfig, ScoringWeight
from makeathon.agents.simple_compliance_checker import (
    SimpleComplianceChecker,
    ComplianceAgentOutput,
)


class EnhancedComplianceAgent:
    """Enhanced Compliance Agent with multi-source data and plugin architecture.

    This class provides a simplified interface to the enhanced compliance system
    while maintaining backward compatibility with the original SimpleComplianceChecker.
    It can operate in two modes:
    1. Enhanced mode: Uses full plugin architecture with multi-source data
    2. Legacy mode: Falls back to SimpleComplianceChecker for compatibility

    Example usage:
        # Basic usage (automatic mode detection)
        agent = EnhancedComplianceAgent()
        result = agent.check_compliance("DSM", "PharmaCorp", "Vitamin D3")

        # Enhanced usage with configuration
        agent = EnhancedComplianceAgent(
            data_sources=[
                {"path": "data/suppliers.csv"},
                {"path": "data/external_evidence.json"},
            ]
        )
        result = agent.check_compliance_enhanced("DSM", "PharmaCorp")
    """

    def __init__(
        self,
        data_sources: Optional[List[Dict[str, Any]]] = None,
        scoring_config: Optional[ScoringConfig] = None,
        use_enhanced_mode: Optional[bool] = None,
        legacy_fallback: bool = True,
    ):
        """Initialize the Enhanced Compliance Agent.

        Args:
            data_sources: List of data source configurations for enhanced mode
            scoring_config: Scoring configuration for enhanced mode
            use_enhanced_mode: Force enhanced mode (True) or legacy mode (False).
                              If None, auto-detects based on data sources.
            legacy_fallback: Whether to fall back to legacy mode on errors
        """
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.legacy_fallback = legacy_fallback
        self.data_sources = data_sources or []

        # Auto-detect mode if not specified
        if use_enhanced_mode is None:
            use_enhanced_mode = len(self.data_sources) > 0

        self.use_enhanced_mode = use_enhanced_mode

        # Initialize components based on mode
        self.enhanced_engine: Optional[ComplianceEngine] = None
        self.legacy_checker: Optional[SimpleComplianceChecker] = None

        if self.use_enhanced_mode:
            self._initialize_enhanced_mode(scoring_config)
        else:
            self._initialize_legacy_mode()

        self.logger.info(
            f"Enhanced Compliance Agent initialized "
            f"(mode: {'enhanced' if self.use_enhanced_mode else 'legacy'})"
        )

    def _initialize_enhanced_mode(self, scoring_config: Optional[ScoringConfig]) -> None:
        """Initialize enhanced mode components."""
        try:
            # Create engine configuration
            engine_config = ComplianceEngineConfig(
                data_sources=self.data_sources,
                scoring_config=scoring_config,
                cache_enabled=True,
                parallel_processing=False,
            )

            # Initialize enhanced engine
            self.enhanced_engine = ComplianceEngine(engine_config)

            # Load data sources if configured
            if self.data_sources:
                self.enhanced_engine.load_data_sources()

            self.logger.info("Enhanced mode initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize enhanced mode: {e}")
            if self.legacy_fallback:
                self.logger.info("Falling back to legacy mode")
                self.use_enhanced_mode = False
                self._initialize_legacy_mode()
            else:
                raise

    def _initialize_legacy_mode(self) -> None:
        """Initialize legacy mode components."""
        self.legacy_checker = SimpleComplianceChecker()
        self.logger.info("Legacy mode initialized")

    def check_compliance(
        self,
        supplier: str,
        customer: str,
        material: Optional[str] = None,
    ) -> ComplianceAgentOutput:
        """Check compliance using the appropriate mode (backward compatible).

        This method maintains backward compatibility with the SimpleComplianceChecker
        interface while automatically using enhanced features when available.

        Args:
            supplier: Supplier name (e.g., "DSM")
            customer: Customer name (e.g., "PharmaCorp")
            material: Material name (optional, for compatibility)

        Returns:
            ComplianceAgentOutput: Compliance result in legacy format
        """
        if self.use_enhanced_mode and self.enhanced_engine:
            try:
                return self._check_compliance_enhanced_legacy_format(
                    supplier, customer, material
                )
            except Exception as e:
                self.logger.error(f"Enhanced mode failed: {e}")
                if self.legacy_fallback and self.legacy_checker:
                    self.logger.info("Falling back to legacy mode for this request")
                    return self.legacy_checker.check(material or "Unknown", supplier, customer)
                else:
                    raise
        else:
            if not self.legacy_checker:
                raise RuntimeError("No compliance checker available")
            return self.legacy_checker.check(material or "Unknown", supplier, customer)

    def _check_compliance_enhanced_legacy_format(
        self,
        supplier: str,
        customer: str,
        material: Optional[str] = None,
    ) -> ComplianceAgentOutput:
        """Run enhanced compliance check and convert to legacy format.

        Args:
            supplier: Supplier name
            customer: Customer name
            material: Material name (for context in reasoning)

        Returns:
            ComplianceAgentOutput: Enhanced result in legacy format
        """
        try:
            # Run enhanced compliance analysis
            result = self.enhanced_engine.analyze_supplier_compliance(
                supplier=supplier,
                customer_requirements=customer,
            )

            # Convert to legacy format
            return self._convert_to_legacy_format(result, supplier, customer, material)

        except ValueError as e:
            # Handle missing supplier/customer by creating insufficient data result
            return ComplianceAgentOutput(
                compliance_status="INSUFFICIENT_DATA",
                confidence=0.0,
                reasoning=str(e),
                issues=[{"type": "missing_data", "description": str(e)}],
                synergy_potential=0.0,
            )

    def _convert_to_legacy_format(
        self,
        result: ComplianceResult,
        supplier: str,
        customer: str,
        material: Optional[str],
    ) -> ComplianceAgentOutput:
        """Convert enhanced ComplianceResult to legacy ComplianceAgentOutput.

        Args:
            result: Enhanced compliance result
            supplier: Supplier name
            customer: Customer name
            material: Material name

        Returns:
            ComplianceAgentOutput: Result in legacy format
        """
        # Determine compliance status
        if result.overall_score >= 0.8:
            status = "COMPLIANT"
        elif result.overall_score >= 0.3:
            status = "NON_COMPLIANT"
        else:
            status = "INSUFFICIENT_DATA"

        # Extract issues from plugin results
        issues = []
        for plugin_result in result.plugin_results:
            for blocking_issue in plugin_result.blocking_issues:
                issues.append({
                    "type": plugin_result.plugin_name,
                    "description": blocking_issue,
                })

        # Create reasoning that resembles legacy format
        reasoning_parts = []
        if material:
            reasoning_parts.append(f"Material: {material}")

        # Add plugin summaries
        for plugin_result in result.plugin_results:
            score_desc = "✓" if plugin_result.score >= 0.8 else "✗" if plugin_result.score < 0.3 else "~"
            reasoning_parts.append(f"{plugin_result.plugin_name}: {score_desc}")

        # Add overall score
        reasoning_parts.append(f"Overall: {result.overall_score:.0%}")

        reasoning = " | ".join(reasoning_parts)

        # Calculate synergy potential (simplified heuristic)
        synergy_potential = min(25.0, result.overall_score * 25.0) if status == "COMPLIANT" else 0.0

        return ComplianceAgentOutput(
            compliance_status=status,
            confidence=result.overall_confidence,
            reasoning=reasoning,
            issues=issues,
            synergy_potential=synergy_potential,
        )

    def check_compliance_enhanced(
        self,
        supplier: Union[str, SupplierData],
        customer_requirements: Union[str, CustomerRequirements],
        user_filters: Optional[Dict[str, Any]] = None,
        selected_plugins: Optional[List[str]] = None,
    ) -> ComplianceResult:
        """Check compliance using enhanced mode with full feature access.

        This method provides direct access to enhanced features without
        legacy format conversion.

        Args:
            supplier: Supplier name or SupplierData object
            customer_requirements: Customer name or CustomerRequirements object
            user_filters: Additional user-specified filters or parameters
            selected_plugins: List of plugin names to run (all if None)

        Returns:
            ComplianceResult: Full enhanced compliance result

        Raises:
            RuntimeError: If enhanced mode is not available
            ValueError: If supplier or customer not found
        """
        if not self.use_enhanced_mode or not self.enhanced_engine:
            raise RuntimeError("Enhanced mode is not available")

        return self.enhanced_engine.analyze_supplier_compliance(
            supplier=supplier,
            customer_requirements=customer_requirements,
            user_filters=user_filters,
            selected_plugins=selected_plugins,
        )

    def rank_suppliers(
        self,
        customer: Union[str, CustomerRequirements],
        supplier_names: Optional[List[str]] = None,
        user_filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "score",
        limit: Optional[int] = None,
    ) -> List[tuple[str, ComplianceResult]]:
        """Rank suppliers for a customer using enhanced mode.

        Args:
            customer: Customer name or CustomerRequirements object
            supplier_names: List of supplier names to consider (all loaded if None)
            user_filters: Additional user-specified filters or parameters
            sort_by: Sorting criteria ("score", "confidence", "score_confidence")
            limit: Maximum number of results to return (all if None)

        Returns:
            List[tuple[str, ComplianceResult]]: Ranked list of suppliers

        Raises:
            RuntimeError: If enhanced mode is not available
        """
        if not self.use_enhanced_mode or not self.enhanced_engine:
            raise RuntimeError("Enhanced mode is not available")

        return self.enhanced_engine.rank_suppliers_for_customer(
            customer_requirements=customer,
            supplier_names=supplier_names,
            user_filters=user_filters,
            sort_by=sort_by,
            limit=limit,
        )

    def configure_scoring(
        self,
        plugin_weights: Optional[Dict[str, float]] = None,
        aggregation_method: str = "weighted_average",
        confidence_penalty_factor: float = 0.2,
    ) -> None:
        """Configure the scoring system (enhanced mode only).

        Args:
            plugin_weights: Dictionary of plugin names to weights
            aggregation_method: How to combine plugin scores
            confidence_penalty_factor: How much to penalize low confidence

        Raises:
            RuntimeError: If enhanced mode is not available
        """
        if not self.use_enhanced_mode or not self.enhanced_engine:
            raise RuntimeError("Enhanced mode is not available")

        # Create new scoring configuration
        weights = []
        if plugin_weights:
            for plugin_name, weight in plugin_weights.items():
                weights.append(ScoringWeight(plugin_name, weight))

        scoring_config = ScoringConfig(
            weights=weights,
            aggregation_method=aggregation_method,
            confidence_penalty_factor=confidence_penalty_factor,
        )

        self.enhanced_engine.scoring_engine.update_config(scoring_config)
        self.logger.info("Updated scoring configuration")

    def add_data_source(
        self,
        source_path: Union[str, Path],
        source_type: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a new data source to the enhanced mode.

        Args:
            source_path: Path to the data source
            source_type: Source type (auto-detected if None)
            config: Source-specific configuration

        Raises:
            RuntimeError: If enhanced mode is not available
        """
        if not self.use_enhanced_mode or not self.enhanced_engine:
            raise RuntimeError("Enhanced mode is not available")

        source_config = {
            "path": str(source_path),
            "type": source_type,
            "config": config,
        }

        self.data_sources.append(source_config)
        self.enhanced_engine.load_data_sources([source_config])
        self.logger.info(f"Added data source: {source_path}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status for debugging.

        Returns:
            Dict[str, Any]: System status information
        """
        base_status = {
            "mode": "enhanced" if self.use_enhanced_mode else "legacy",
            "legacy_fallback": self.legacy_fallback,
            "data_sources_configured": len(self.data_sources),
        }

        if self.use_enhanced_mode and self.enhanced_engine:
            base_status.update(self.enhanced_engine.get_system_status())
        elif self.legacy_checker:
            base_status["legacy_checker_available"] = True

        return base_status

    def clear_caches(self) -> None:
        """Clear all internal caches."""
        if self.enhanced_engine:
            self.enhanced_engine.clear_caches()


# Convenience function for backward compatibility
def call_compliance_agent(
    material: str,
    supplier: str,
    customer: str = "FoodSupplementCo",
) -> ComplianceAgentOutput:
    """Convenience function that maintains exact backward compatibility.

    This function matches the signature of the original call_compliance_agent
    from the simple compliance checker while automatically using enhanced
    features when data sources are available.

    Args:
        material: Material name (e.g., "Vitamin D3")
        supplier: Supplier name (e.g., "DSM")
        customer: Customer name (default: "FoodSupplementCo")

    Returns:
        ComplianceAgentOutput: Compliance result in legacy format
    """
    # Try to detect if enhanced data sources are available
    data_sources = []

    # Check for common data files
    common_files = [
        "data/suppliers.csv",
        "data/customer_requirements.csv",
        "data/external_evidence.json",
    ]

    for file_path in common_files:
        if Path(file_path).exists():
            data_sources.append({"path": file_path})

    # Create agent with appropriate mode
    agent = EnhancedComplianceAgent(
        data_sources=data_sources,
        legacy_fallback=True,
    )

    # Use legacy function signature order (material, supplier, customer)
    return agent.check_compliance(supplier, customer, material)