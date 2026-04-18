"""Legacy CSV Adapter for existing data file formats.

This module provides CSV adapters specifically designed to work with the
existing data file formats used in the makeathon project. It handles the
specific column mappings and data transformations needed.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from makeathon.agents.core.data_models import (
    SupplierData,
    CustomerRequirements,
    Certificate,
)
from makeathon.agents.data_sources.base import DataSourceAdapter


class LegacySuppliersCSVAdapter(DataSourceAdapter):
    """CSV adapter for existing suppliers.csv format.

    Expected format:
    supplier,country,current_customer_count,certificates

    Example:
    DSM,Netherlands,5,"cGMP,ISO 9001,ISO 14644"
    """

    @property
    def source_type(self) -> str:
        return "legacy_suppliers_csv"

    @property
    def supports_suppliers(self) -> bool:
        return True

    @property
    def supports_customers(self) -> bool:
        return False

    def _parse_certificates_semicolon(self, cert_string: str) -> List[Certificate]:
        """Parse comma-separated certificate string from legacy CSV.

        Args:
            cert_string: String like "cGMP,ISO 9001,ISO 14644"

        Returns:
            List[Certificate]: List of Certificate objects
        """
        if not cert_string or cert_string.strip() == "":
            return []

        certificates = []
        # Remove quotes if present and split by comma
        cert_string = cert_string.strip('"')
        for cert_name in cert_string.split(","):
            cert_name = cert_name.strip()
            if cert_name:
                certificates.append(
                    Certificate(
                        name=cert_name,
                        issuer="Unknown",
                        valid_until=datetime(2030, 12, 31),
                    )
                )

        return certificates

    def load_suppliers(
        self,
        source_path: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> List[SupplierData]:
        """Load supplier data from legacy CSV format."""
        if not self.validate_source(source_path):
            raise FileNotFoundError(f"CSV file not found: {source_path}")

        encoding = config.get("encoding", "utf-8") if config else "utf-8"
        delimiter = config.get("delimiter", ",") if config else ","

        suppliers = []

        try:
            with open(source_path, "r", encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)

                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Map legacy column names
                        name = row.get("supplier", "").strip()
                        country = row.get("country", "").strip()

                        if not name:
                            continue  # Skip empty rows

                        # Parse certificates
                        certificates = self._parse_certificates_semicolon(
                            row.get("certificates", "")
                        )

                        # Create supplier data
                        supplier = SupplierData(
                            name=name,
                            country=country,
                            certificates=certificates,
                            data_sources=[f"legacy_csv:{source_path.name}"],
                            confidence_breakdown={"data_source": 0.8},  # Legacy data confidence
                            last_updated=datetime.now(),
                        )

                        suppliers.append(supplier)

                    except Exception as e:
                        raise ValueError(f"Error parsing row {row_num}: {e}")

        except Exception as e:
            raise ValueError(f"Error reading legacy suppliers CSV: {e}")

        return suppliers

    def load_customer_requirements(
        self,
        source_path: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> List[CustomerRequirements]:
        """Not supported by suppliers CSV adapter."""
        raise NotImplementedError("Suppliers CSV adapter does not support customer requirements")


class LegacyCustomerCSVAdapter(DataSourceAdapter):
    """CSV adapter for existing customer_requirements.csv format.

    Expected format:
    company_name,quality_tier,certificates_required,potency_range,dissolution_min,impurities_max

    Example:
    PharmaCorp,PHARMA_GRADE,"cGMP,ISO 9001,ISO 14644",97.0-103.0,90,0.05
    """

    @property
    def source_type(self) -> str:
        return "legacy_customers_csv"

    @property
    def supports_suppliers(self) -> bool:
        return False

    @property
    def supports_customers(self) -> bool:
        return True

    def _parse_certificates_list(self, cert_string: str) -> List[str]:
        """Parse comma-separated certificate string from legacy CSV."""
        if not cert_string or cert_string.strip() == "":
            return []

        # Remove quotes if present and split by comma
        cert_string = cert_string.strip('"')
        return [cert.strip() for cert in cert_string.split(",") if cert.strip()]

    def _parse_constraints(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Parse additional constraint fields into constraints dict."""
        constraints = {}

        # Parse potency range
        potency_range = row.get("potency_range", "")
        if potency_range:
            try:
                if "-" in potency_range:
                    min_val, max_val = potency_range.split("-")
                    constraints["potency_min"] = float(min_val)
                    constraints["potency_max"] = float(max_val)
            except ValueError:
                pass

        # Parse dissolution minimum
        dissolution_min = row.get("dissolution_min", "")
        if dissolution_min:
            try:
                constraints["dissolution_min"] = float(dissolution_min)
            except ValueError:
                pass

        # Parse impurities maximum
        impurities_max = row.get("impurities_max", "")
        if impurities_max:
            try:
                constraints["impurities_max"] = float(impurities_max)
            except ValueError:
                pass

        return constraints

    def load_suppliers(
        self,
        source_path: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> List[SupplierData]:
        """Not supported by customer requirements CSV adapter."""
        raise NotImplementedError("Customer CSV adapter does not support supplier data")

    def load_customer_requirements(
        self,
        source_path: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> List[CustomerRequirements]:
        """Load customer requirements from legacy CSV format."""
        if not self.validate_source(source_path):
            raise FileNotFoundError(f"CSV file not found: {source_path}")

        encoding = config.get("encoding", "utf-8") if config else "utf-8"
        delimiter = config.get("delimiter", ",") if config else ","

        customer_reqs = []

        try:
            with open(source_path, "r", encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)

                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Map legacy column names
                        company_name = row.get("company_name", "").strip()
                        quality_tier = row.get("quality_tier", "").strip()

                        if not company_name:
                            continue  # Skip empty rows

                        # Parse certificates required
                        certificates_required = self._parse_certificates_list(
                            row.get("certificates_required", "")
                        )

                        # Parse additional constraints
                        constraints = self._parse_constraints(row)

                        customer_req = CustomerRequirements(
                            company_name=company_name,
                            quality_tier=quality_tier,
                            certificates_required=certificates_required,
                            constraints=constraints,
                        )

                        customer_reqs.append(customer_req)

                    except Exception as e:
                        raise ValueError(f"Error parsing row {row_num}: {e}")

        except Exception as e:
            raise ValueError(f"Error reading legacy customer requirements CSV: {e}")

        return customer_reqs