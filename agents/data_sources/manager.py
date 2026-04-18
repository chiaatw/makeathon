"""Multi-Source Data Manager for Enhanced Compliance Agent.

This module implements intelligent data aggregation from multiple sources
with conflict resolution, data freshness tracking, and confidence scoring.
It coordinates multiple data source adapters to provide unified data access.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import logging

from makeathon.agents.core.data_models import SupplierData, CustomerRequirements, Certificate
from makeathon.agents.data_sources.base import DataSourceAdapter
from makeathon.agents.data_sources.csv_adapter import CSVAdapter
from makeathon.agents.data_sources.json_adapter import JSONAdapter


class DataConflictResolver:
    """Handles conflicts when the same data exists in multiple sources."""

    @staticmethod
    def resolve_supplier_conflicts(suppliers: List[SupplierData]) -> SupplierData:
        """Resolve conflicts between supplier records from different sources.

        Args:
            suppliers: List of supplier records with the same name

        Returns:
            SupplierData: Merged supplier record with highest confidence data

        Conflict Resolution Strategy:
        1. Most recent data takes precedence for updateable fields
        2. Certificates are merged (union of all certificates)
        3. Pricing uses most recent non-null values
        4. Confidence scores are averaged across sources
        5. Data sources are combined for transparency
        """
        if not suppliers:
            raise ValueError("Cannot resolve conflicts for empty supplier list")

        if len(suppliers) == 1:
            return suppliers[0]

        # Start with the supplier that has the most recent update
        base_supplier = max(suppliers, key=lambda s: s.last_updated or datetime.min)

        # Merge certificates from all sources (avoiding duplicates)
        all_certificates = {}
        for supplier in suppliers:
            for cert in supplier.certificates:
                # Use certificate name as key to avoid duplicates
                # Keep the most recent valid_until date for each certificate
                if cert.name not in all_certificates or cert.valid_until > all_certificates[cert.name].valid_until:
                    all_certificates[cert.name] = cert

        merged_certificates = list(all_certificates.values())

        # Merge pricing - use most recent non-null pricing
        merged_pricing = None
        for supplier in sorted(suppliers, key=lambda s: s.last_updated or datetime.min, reverse=True):
            if supplier.pricing is not None:
                merged_pricing = supplier.pricing
                break

        # Merge quality metrics and delivery info - use most recent non-null
        merged_quality_metrics = None
        merged_delivery_info = None
        for supplier in sorted(suppliers, key=lambda s: s.last_updated or datetime.min, reverse=True):
            if merged_quality_metrics is None and supplier.quality_metrics is not None:
                merged_quality_metrics = supplier.quality_metrics
            if merged_delivery_info is None and supplier.delivery_info is not None:
                merged_delivery_info = supplier.delivery_info

        # Merge data sources
        all_data_sources = []
        for supplier in suppliers:
            all_data_sources.extend(supplier.data_sources)

        # Merge confidence breakdowns - average scores across sources
        merged_confidence = {}
        for supplier in suppliers:
            for key, score in supplier.confidence_breakdown.items():
                if key not in merged_confidence:
                    merged_confidence[key] = []
                merged_confidence[key].append(score)

        # Calculate averaged confidence scores
        averaged_confidence = {
            key: sum(scores) / len(scores)
            for key, scores in merged_confidence.items()
        }

        return SupplierData(
            name=base_supplier.name,
            country=base_supplier.country,
            certificates=merged_certificates,
            pricing=merged_pricing,
            quality_metrics=merged_quality_metrics,
            delivery_info=merged_delivery_info,
            data_sources=list(set(all_data_sources)),  # Remove duplicates
            confidence_breakdown=averaged_confidence,
            last_updated=max(s.last_updated for s in suppliers if s.last_updated),
        )


class MultiSourceDataManager:
    """Manages data loading and aggregation from multiple sources.

    This class coordinates multiple data source adapters to provide unified
    access to supplier and customer data. It handles conflict resolution,
    caching, and data freshness validation.

    Attributes:
        adapters: Dictionary mapping source types to adapter instances
        cache_ttl: Time-to-live for cached data in seconds
        conflict_resolver: Strategy for resolving data conflicts
    """

    def __init__(self, cache_ttl: int = 3600):
        """Initialize the multi-source data manager.

        Args:
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
        """
        self.adapters: Dict[str, DataSourceAdapter] = {
            "csv": CSVAdapter(),
            "json": JSONAdapter(),
        }

        # Import legacy adapters here to avoid circular imports
        try:
            from makeathon.agents.integration.legacy_csv_adapter import (
                LegacySuppliersCSVAdapter,
                LegacyCustomerCSVAdapter,
            )
            self.adapters["legacy_suppliers_csv"] = LegacySuppliersCSVAdapter()
            self.adapters["legacy_customers_csv"] = LegacyCustomerCSVAdapter()
        except ImportError:
            # Legacy adapters not available, continue with standard adapters
            pass
        self.cache_ttl = cache_ttl
        self.conflict_resolver = DataConflictResolver()

        # Internal caches
        self._supplier_cache: Dict[str, Tuple[List[SupplierData], datetime]] = {}
        self._customer_cache: Dict[str, Tuple[List[CustomerRequirements], datetime]] = {}

        # Set up logging
        self.logger = logging.getLogger(__name__)

    def add_adapter(self, source_type: str, adapter: DataSourceAdapter) -> None:
        """Add a new data source adapter.

        Args:
            source_type: Type identifier for the adapter
            adapter: DataSourceAdapter instance
        """
        self.adapters[source_type] = adapter
        self.logger.info(f"Added data adapter for source type: {source_type}")

    def _is_cache_valid(self, cached_time: datetime) -> bool:
        """Check if cached data is still valid.

        Args:
            cached_time: When the data was cached

        Returns:
            bool: True if cache is still valid
        """
        return datetime.now() - cached_time < timedelta(seconds=self.cache_ttl)

    def _detect_source_type(self, source_path: Path) -> Optional[str]:
        """Auto-detect the source type from file extension.

        Args:
            source_path: Path to the data source

        Returns:
            Optional[str]: Detected source type or None if unknown
        """
        extension = source_path.suffix.lower()
        if extension == ".csv":
            return "csv"
        elif extension == ".json":
            return "json"
        else:
            return None

    def load_suppliers_from_source(
        self,
        source_path: Union[str, Path],
        source_type: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> List[SupplierData]:
        """Load supplier data from a single source.

        Args:
            source_path: Path to the data source
            source_type: Source type (auto-detected if None)
            config: Optional configuration for the adapter
            use_cache: Whether to use cached data if available

        Returns:
            List[SupplierData]: List of supplier data

        Raises:
            ValueError: If source type is unsupported or data is invalid
            FileNotFoundError: If source file doesn't exist
        """
        source_path = Path(source_path)
        cache_key = str(source_path)

        # Check cache first
        if use_cache and cache_key in self._supplier_cache:
            cached_data, cached_time = self._supplier_cache[cache_key]
            if self._is_cache_valid(cached_time):
                self.logger.debug(f"Using cached supplier data for {source_path}")
                return cached_data

        # Auto-detect source type if not provided
        if source_type is None:
            source_type = self._detect_source_type(source_path)
            if source_type is None:
                raise ValueError(f"Cannot auto-detect source type for {source_path}")

        # Get appropriate adapter
        if source_type not in self.adapters:
            raise ValueError(f"Unsupported source type: {source_type}")

        adapter = self.adapters[source_type]
        if not adapter.supports_suppliers:
            raise ValueError(f"Adapter for {source_type} does not support supplier data")

        # Load data
        self.logger.info(f"Loading supplier data from {source_type} source: {source_path}")
        suppliers = adapter.load_suppliers(source_path, config)

        # Cache the data
        if use_cache:
            self._supplier_cache[cache_key] = (suppliers, datetime.now())

        return suppliers

    def load_suppliers_from_multiple_sources(
        self,
        sources: List[Dict[str, Any]],
        use_cache: bool = True,
    ) -> List[SupplierData]:
        """Load and merge supplier data from multiple sources.

        Args:
            sources: List of source configurations, each containing:
                    - path: Path to the data source
                    - type: Source type (optional, auto-detected if None)
                    - config: Source-specific configuration (optional)
            use_cache: Whether to use cached data if available

        Returns:
            List[SupplierData]: Merged list of supplier data with conflicts resolved

        Example:
            sources = [
                {"path": "suppliers.csv"},
                {"path": "external_suppliers.json", "type": "json"},
                {"path": "legacy_data.csv", "config": {"delimiter": ";"}}
            ]
        """
        all_suppliers = []

        # Load from each source
        for source in sources:
            try:
                suppliers = self.load_suppliers_from_source(
                    source_path=source["path"],
                    source_type=source.get("type"),
                    config=source.get("config"),
                    use_cache=use_cache,
                )
                all_suppliers.extend(suppliers)
                self.logger.info(f"Loaded {len(suppliers)} suppliers from {source['path']}")
            except Exception as e:
                self.logger.error(f"Failed to load from {source['path']}: {e}")
                # Continue with other sources instead of failing completely

        # Group suppliers by name for conflict resolution
        supplier_groups: Dict[str, List[SupplierData]] = {}
        for supplier in all_suppliers:
            name = supplier.name.strip().lower()  # Normalize for grouping
            if name not in supplier_groups:
                supplier_groups[name] = []
            supplier_groups[name].append(supplier)

        # Resolve conflicts and create final list
        merged_suppliers = []
        for name, group in supplier_groups.items():
            if len(group) > 1:
                self.logger.info(f"Resolving conflicts for supplier '{group[0].name}' from {len(group)} sources")
                merged_supplier = self.conflict_resolver.resolve_supplier_conflicts(group)
            else:
                merged_supplier = group[0]

            merged_suppliers.append(merged_supplier)

        self.logger.info(f"Final result: {len(merged_suppliers)} unique suppliers after conflict resolution")
        return merged_suppliers

    def load_customer_requirements_from_source(
        self,
        source_path: Union[str, Path],
        source_type: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> List[CustomerRequirements]:
        """Load customer requirements from a single source.

        Args:
            source_path: Path to the data source
            source_type: Source type (auto-detected if None)
            config: Optional configuration for the adapter
            use_cache: Whether to use cached data if available

        Returns:
            List[CustomerRequirements]: List of customer requirements

        Raises:
            ValueError: If source type is unsupported or data is invalid
            FileNotFoundError: If source file doesn't exist
        """
        source_path = Path(source_path)
        cache_key = str(source_path)

        # Check cache first
        if use_cache and cache_key in self._customer_cache:
            cached_data, cached_time = self._customer_cache[cache_key]
            if self._is_cache_valid(cached_time):
                self.logger.debug(f"Using cached customer data for {source_path}")
                return cached_data

        # Auto-detect source type if not provided
        if source_type is None:
            source_type = self._detect_source_type(source_path)
            if source_type is None:
                raise ValueError(f"Cannot auto-detect source type for {source_path}")

        # Get appropriate adapter
        if source_type not in self.adapters:
            raise ValueError(f"Unsupported source type: {source_type}")

        adapter = self.adapters[source_type]
        if not adapter.supports_customers:
            raise ValueError(f"Adapter for {source_type} does not support customer requirements")

        # Load data
        self.logger.info(f"Loading customer requirements from {source_type} source: {source_path}")
        customers = adapter.load_customer_requirements(source_path, config)

        # Cache the data
        if use_cache:
            self._customer_cache[cache_key] = (customers, datetime.now())

        return customers

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._supplier_cache.clear()
        self._customer_cache.clear()
        self.logger.info("Cleared data cache")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached data.

        Returns:
            Dict[str, Any]: Cache statistics and status
        """
        now = datetime.now()

        supplier_cache_info = {}
        for key, (data, cached_time) in self._supplier_cache.items():
            supplier_cache_info[key] = {
                "count": len(data),
                "cached_at": cached_time.isoformat(),
                "is_valid": self._is_cache_valid(cached_time),
                "age_seconds": (now - cached_time).total_seconds(),
            }

        customer_cache_info = {}
        for key, (data, cached_time) in self._customer_cache.items():
            customer_cache_info[key] = {
                "count": len(data),
                "cached_at": cached_time.isoformat(),
                "is_valid": self._is_cache_valid(cached_time),
                "age_seconds": (now - cached_time).total_seconds(),
            }

        return {
            "cache_ttl_seconds": self.cache_ttl,
            "suppliers": supplier_cache_info,
            "customers": customer_cache_info,
        }