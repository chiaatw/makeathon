"""Abstract base class for data source adapters.

This module defines the DataSourceAdapter abstract base class that all data
source adapters must implement. It establishes the interface contract for
loading and standardizing data from various sources.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

from makeathon.agents.core.data_models import SupplierData, CustomerRequirements


class DataSourceAdapter(ABC):
    """Abstract base class for all data source adapters.

    Each adapter implements loading data from a specific source format (CSV, JSON, etc.)
    and converts it to standardized data models. Adapters handle data validation,
    error reporting, and metadata tracking for transparency.

    Attributes:
        source_type: Type identifier for this data source (e.g., "csv", "json")
        supports_suppliers: Whether this adapter can load supplier data
        supports_customers: Whether this adapter can load customer requirements
    """

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Type identifier for this data source.

        Returns:
            str: Source type identifier (e.g., "csv", "json", "api")
        """
        pass

    @property
    @abstractmethod
    def supports_suppliers(self) -> bool:
        """Whether this adapter can load supplier data.

        Returns:
            bool: True if adapter supports loading SupplierData objects
        """
        pass

    @property
    @abstractmethod
    def supports_customers(self) -> bool:
        """Whether this adapter can load customer requirements.

        Returns:
            bool: True if adapter supports loading CustomerRequirements objects
        """
        pass

    @abstractmethod
    def load_suppliers(
        self,
        source_path: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> List[SupplierData]:
        """Load supplier data from the source.

        Args:
            source_path: Path to the data source file or location
            config: Optional configuration parameters for loading

        Returns:
            List[SupplierData]: List of loaded and standardized supplier data

        Raises:
            ValueError: If source_path is invalid or data is malformed
            FileNotFoundError: If source file doesn't exist
            NotImplementedError: If adapter doesn't support suppliers
        """
        pass

    @abstractmethod
    def load_customer_requirements(
        self,
        source_path: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> List[CustomerRequirements]:
        """Load customer requirements from the source.

        Args:
            source_path: Path to the data source file or location
            config: Optional configuration parameters for loading

        Returns:
            List[CustomerRequirements]: List of loaded customer requirements

        Raises:
            ValueError: If source_path is invalid or data is malformed
            FileNotFoundError: If source file doesn't exist
            NotImplementedError: If adapter doesn't support customer requirements
        """
        pass

    def validate_source(self, source_path: Path) -> bool:
        """Validate that the source path exists and is readable.

        Args:
            source_path: Path to validate

        Returns:
            bool: True if source is valid and readable
        """
        return source_path.exists() and source_path.is_file()

    def get_data_metadata(
        self,
        source_path: Path
    ) -> Dict[str, Any]:
        """Get metadata about the data source.

        Args:
            source_path: Path to the data source

        Returns:
            Dict[str, Any]: Metadata including file size, modification time, etc.
        """
        if not source_path.exists():
            return {"exists": False}

        stat = source_path.stat()
        return {
            "exists": True,
            "size_bytes": stat.st_size,
            "modified_time": stat.st_mtime,
            "source_type": self.source_type,
            "supports_suppliers": self.supports_suppliers,
            "supports_customers": self.supports_customers,
        }