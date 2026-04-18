"""Main Compliance Engine for Enhanced Compliance Agent.

This module implements the core orchestration engine that coordinates
plugins, data sources, and scoring to perform comprehensive compliance
analysis. It provides the main entry point for compliance checking
with full transparency and configurability.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from makeathon.agents.core.data_models import (
    SupplierData,
    CustomerRequirements,
    PluginResult,
    ComplianceResult,
)
from makeathon.agents.plugins.base import CompliancePlugin
from makeathon.agents.plugins.certificates import CertificatesPlugin
from makeathon.agents.data_sources.manager import MultiSourceDataManager
from makeathon.agents.scoring.engine import ScoringEngine, ScoringConfig


class ComplianceEngineConfig:
    """Configuration for the compliance engine.

    Attributes:
        data_sources: List of data source configurations
        scoring_config: Configuration for the scoring engine
        plugin_configs: Plugin-specific configurations
        cache_enabled: Whether to use data caching
        parallel_processing: Whether to run plugins in parallel
    """

    def __init__(
        self,
        data_sources: Optional[List[Dict[str, Any]]] = None,
        scoring_config: Optional[ScoringConfig] = None,
        plugin_configs: Optional[Dict[str, Dict[str, Any]]] = None,
        cache_enabled: bool = True,
        parallel_processing: bool = False,
    ):
        self.data_sources = data_sources or []
        self.scoring_config = scoring_config
        self.plugin_configs = plugin_configs or {}
        self.cache_enabled = cache_enabled
        self.parallel_processing = parallel_processing


class ComplianceEngine:
    """Main engine for comprehensive compliance analysis.

    This class coordinates all components of the enhanced compliance system:
    - Loads data from multiple sources via data manager
    - Runs compliance plugins for different analysis aspects
    - Aggregates results via scoring engine
    - Provides detailed transparency and reasoning

    Example usage:
        engine = ComplianceEngine()
        result = engine.analyze_supplier_compliance(
            supplier_name="DSM",
            customer_requirements=requirements
        )
        print(f"Compliance Score: {result.overall_score:.2f}")
    """

    def __init__(self, config: Optional[ComplianceEngineConfig] = None):
        """Initialize the compliance engine.

        Args:
            config: Engine configuration. If None, uses defaults.
        """
        self.config = config or ComplianceEngineConfig()
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.data_manager = MultiSourceDataManager(
            cache_ttl=3600 if self.config.cache_enabled else 0
        )
        self.scoring_engine = ScoringEngine(self.config.scoring_config)

        # Initialize plugins
        self.plugins: Dict[str, CompliancePlugin] = {}
        self._initialize_plugins()

        # Internal state
        self._suppliers_loaded: List[SupplierData] = []
        self._customers_loaded: List[CustomerRequirements] = []
        self._last_data_load_time: Optional[datetime] = None

        self.logger.info("Compliance Engine initialized")

    def _initialize_plugins(self) -> None:
        """Initialize all available compliance plugins."""
        # Load built-in plugins
        plugins_to_load = [
            CertificatesPlugin(),
            # Add other plugins here as they're implemented
        ]

        for plugin in plugins_to_load:
            self.register_plugin(plugin)

        self.logger.info(f"Initialized {len(self.plugins)} compliance plugins")

    def register_plugin(self, plugin: CompliancePlugin) -> None:
        """Register a compliance plugin.

        Args:
            plugin: CompliancePlugin instance to register
        """
        self.plugins[plugin.name] = plugin
        self.logger.info(f"Registered plugin: {plugin.name}")

    def unregister_plugin(self, plugin_name: str) -> None:
        """Unregister a compliance plugin.

        Args:
            plugin_name: Name of the plugin to unregister
        """
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            self.logger.info(f"Unregistered plugin: {plugin_name}")

    def load_data_sources(
        self,
        sources: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Load data from configured sources.

        Args:
            sources: List of data source configurations. Uses config default if None.
        """
        sources = sources or self.config.data_sources

        if not sources:
            self.logger.warning("No data sources configured")
            return

        # Load suppliers
        supplier_sources = [s for s in sources if s.get("type") != "customer_only"]
        if supplier_sources:
            self._suppliers_loaded = self.data_manager.load_suppliers_from_multiple_sources(
                supplier_sources,
                use_cache=self.config.cache_enabled
            )
            self.logger.info(f"Loaded {len(self._suppliers_loaded)} suppliers")

        # Load customer requirements
        customer_sources = [s for s in sources if s.get("type") != "supplier_only"]
        all_customers = []
        for source in customer_sources:
            try:
                customers = self.data_manager.load_customer_requirements_from_source(
                    source["path"],
                    source_type=source.get("type"),
                    config=source.get("config"),
                    use_cache=self.config.cache_enabled
                )
                all_customers.extend(customers)
            except Exception as e:
                self.logger.error(f"Failed to load customers from {source['path']}: {e}")

        self._customers_loaded = all_customers
        self.logger.info(f"Loaded {len(self._customers_loaded)} customer requirement sets")

        self._last_data_load_time = datetime.now()

    def get_supplier_by_name(self, supplier_name: str) -> Optional[SupplierData]:
        """Get supplier data by name.

        Args:
            supplier_name: Name of the supplier to find

        Returns:
            Optional[SupplierData]: Supplier data or None if not found
        """
        normalized_name = supplier_name.strip().lower()
        for supplier in self._suppliers_loaded:
            if supplier.name.strip().lower() == normalized_name:
                return supplier
        return None

    def get_customer_requirements_by_name(
        self,
        customer_name: str
    ) -> Optional[CustomerRequirements]:
        """Get customer requirements by company name.

        Args:
            customer_name: Name of the customer company

        Returns:
            Optional[CustomerRequirements]: Customer requirements or None if not found
        """
        normalized_name = customer_name.strip().lower()
        for customer in self._customers_loaded:
            if customer.company_name.strip().lower() == normalized_name:
                return customer
        return None

    def analyze_supplier_compliance(
        self,
        supplier: Union[str, SupplierData],
        customer_requirements: Union[str, CustomerRequirements],
        user_filters: Optional[Dict[str, Any]] = None,
        selected_plugins: Optional[List[str]] = None,
    ) -> ComplianceResult:
        """Analyze compliance for a supplier against customer requirements.

        Args:
            supplier: Supplier name or SupplierData object
            customer_requirements: Customer name or CustomerRequirements object
            user_filters: Additional user-specified filters or parameters
            selected_plugins: List of plugin names to run (all if None)

        Returns:
            ComplianceResult: Comprehensive compliance analysis result

        Raises:
            ValueError: If supplier or customer not found
        """
        # Resolve supplier data
        if isinstance(supplier, str):
            supplier_data = self.get_supplier_by_name(supplier)
            if not supplier_data:
                raise ValueError(f"Supplier not found: {supplier}")
        else:
            supplier_data = supplier

        # Resolve customer requirements
        if isinstance(customer_requirements, str):
            customer_reqs = self.get_customer_requirements_by_name(customer_requirements)
            if not customer_reqs:
                raise ValueError(f"Customer not found: {customer_requirements}")
        else:
            customer_reqs = customer_requirements

        # Default user filters
        user_filters = user_filters or {}

        # Determine which plugins to run
        plugins_to_run = selected_plugins or list(self.plugins.keys())

        # Run compliance plugins
        plugin_results = []
        for plugin_name in plugins_to_run:
            if plugin_name not in self.plugins:
                self.logger.warning(f"Plugin not found: {plugin_name}")
                continue

            plugin = self.plugins[plugin_name]

            try:
                self.logger.debug(f"Running plugin: {plugin_name}")
                result = plugin.check_compliance(
                    supplier_data,
                    customer_reqs,
                    user_filters
                )
                plugin_results.append(result)
                self.logger.debug(
                    f"Plugin {plugin_name} result: {result.score:.2f} "
                    f"(confidence: {result.confidence:.2f})"
                )
            except Exception as e:
                self.logger.error(f"Plugin {plugin_name} failed: {e}")
                # Continue with other plugins rather than failing completely

        if not plugin_results:
            self.logger.warning("No plugins produced results")
            return ComplianceResult(
                overall_score=0.0,
                overall_confidence=0.0,
                reasoning_chain=["No plugins produced results"],
                data_gaps=["No plugin analysis available"],
                recommendations=["Check plugin configuration"],
            )

        # Calculate overall score
        compliance_result = self.scoring_engine.calculate_compliance_score(plugin_results)

        self.logger.info(
            f"Compliance analysis complete for {supplier_data.name}: "
            f"{compliance_result.overall_score:.2f} "
            f"(confidence: {compliance_result.overall_confidence:.2f})"
        )

        return compliance_result

    def batch_analyze_suppliers(
        self,
        supplier_names: List[str],
        customer_requirements: Union[str, CustomerRequirements],
        user_filters: Optional[Dict[str, Any]] = None,
        selected_plugins: Optional[List[str]] = None,
    ) -> Dict[str, ComplianceResult]:
        """Analyze compliance for multiple suppliers.

        Args:
            supplier_names: List of supplier names to analyze
            customer_requirements: Customer name or CustomerRequirements object
            user_filters: Additional user-specified filters or parameters
            selected_plugins: List of plugin names to run (all if None)

        Returns:
            Dict[str, ComplianceResult]: Map of supplier names to compliance results
        """
        results = {}

        for supplier_name in supplier_names:
            try:
                result = self.analyze_supplier_compliance(
                    supplier_name,
                    customer_requirements,
                    user_filters,
                    selected_plugins
                )
                results[supplier_name] = result
            except Exception as e:
                self.logger.error(f"Failed to analyze {supplier_name}: {e}")
                # Include error result rather than skipping
                results[supplier_name] = ComplianceResult(
                    overall_score=0.0,
                    overall_confidence=0.0,
                    reasoning_chain=[f"Analysis failed: {e}"],
                    data_gaps=["Analysis could not be completed"],
                    recommendations=["Check supplier data and configuration"],
                )

        return results

    def rank_suppliers_for_customer(
        self,
        customer_requirements: Union[str, CustomerRequirements],
        supplier_names: Optional[List[str]] = None,
        user_filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "score",
        limit: Optional[int] = None,
    ) -> List[tuple[str, ComplianceResult]]:
        """Rank all available suppliers for a customer.

        Args:
            customer_requirements: Customer name or CustomerRequirements object
            supplier_names: List of supplier names to consider (all loaded if None)
            user_filters: Additional user-specified filters or parameters
            sort_by: Sorting criteria ("score", "confidence", "score_confidence")
            limit: Maximum number of results to return (all if None)

        Returns:
            List[tuple[str, ComplianceResult]]: Ranked list of (supplier_name, result)
        """
        # Use all loaded suppliers if not specified
        if supplier_names is None:
            supplier_names = [s.name for s in self._suppliers_loaded]

        # Analyze all suppliers
        results = self.batch_analyze_suppliers(
            supplier_names,
            customer_requirements,
            user_filters
        )

        # Convert to list of tuples for ranking
        supplier_results = [(name, result) for name, result in results.items()]

        # Rank suppliers
        ranked_results = self.scoring_engine.rank_suppliers(supplier_results, sort_by)

        # Apply limit if specified
        if limit is not None:
            ranked_results = ranked_results[:limit]

        return ranked_results

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status for debugging and monitoring.

        Returns:
            Dict[str, Any]: System status including data, plugins, and configuration
        """
        return {
            "data_status": {
                "suppliers_loaded": len(self._suppliers_loaded),
                "customers_loaded": len(self._customers_loaded),
                "last_load_time": self._last_data_load_time.isoformat() if self._last_data_load_time else None,
                "cache_info": self.data_manager.get_cache_info(),
            },
            "plugin_status": {
                "registered_plugins": list(self.plugins.keys()),
                "plugin_count": len(self.plugins),
            },
            "scoring_config": self.scoring_engine.get_config_summary(),
            "engine_config": {
                "cache_enabled": self.config.cache_enabled,
                "parallel_processing": self.config.parallel_processing,
                "data_sources_configured": len(self.config.data_sources),
            },
        }

    def clear_caches(self) -> None:
        """Clear all internal caches."""
        self.data_manager.clear_cache()
        self.logger.info("Cleared all caches")