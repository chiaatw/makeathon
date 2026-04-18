"""CSV Data Source Adapter for Enhanced Compliance Agent.

This module implements a concrete adapter for loading data from CSV files.
It converts CSV data to standardized data models with proper validation
and error handling.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from makeathon.agents.core.data_models import (
    SupplierData,
    CustomerRequirements,
    Certificate,
    PricingInfo,
)
from makeathon.agents.data_sources.base import DataSourceAdapter


class CSVAdapter(DataSourceAdapter):
    """Concrete implementation of DataSourceAdapter for CSV files.

    This adapter can load supplier data and customer requirements from CSV files.
    It expects specific column formats and handles data type conversion and
    validation automatically.

    Expected CSV formats:

    Suppliers CSV:
    - name: Supplier name (required)
    - country: Country of operation (required)
    - certificates: Semicolon-separated list of certificates (optional)
    - pricing_min: Minimum price (optional)
    - pricing_max: Maximum price (optional)
    - currency: Currency code (optional)
    - moq: Minimum order quantity (optional)

    Customer Requirements CSV:
    - company_name: Customer company name (required)
    - quality_tier: Quality tier (required)
    - certificates_required: Semicolon-separated list (optional)
    """

    @property
    def source_type(self) -> str:
        """Type identifier for this data source."""
        return "csv"

    @property
    def supports_suppliers(self) -> bool:
        """Whether this adapter can load supplier data."""
        return True

    @property
    def supports_customers(self) -> bool:
        """Whether this adapter can load customer requirements."""
        return True

    def _parse_certificates(self, cert_string: str) -> List[Certificate]:
        """Parse semicolon-separated certificate string.

        Args:
            cert_string: String like "ISO 9001;cGMP;ISO 14001"

        Returns:
            List[Certificate]: List of Certificate objects
        """
        if not cert_string or cert_string.strip() == "":
            return []

        certificates = []
        for cert_name in cert_string.split(";"):
            cert_name = cert_name.strip()
            if cert_name:
                # For CSV data, we don't have issuer or expiration info
                # Use placeholder values that can be enriched later
                certificates.append(
                    Certificate(
                        name=cert_name,
                        issuer="Unknown",
                        valid_until=datetime(2030, 12, 31),  # Default future date
                    )
                )

        return certificates

    def _parse_pricing(
        self,
        min_price_str: str,
        max_price_str: str,
        currency_str: str,
        moq_str: str,
    ) -> Optional[PricingInfo]:
        """Parse pricing information from CSV fields.

        Args:
            min_price_str: Minimum price as string
            max_price_str: Maximum price as string
            currency_str: Currency code
            moq_str: Minimum order quantity as string

        Returns:
            Optional[PricingInfo]: PricingInfo object or None if data insufficient
        """
        try:
            # We need at least min price to create pricing info
            if not min_price_str or min_price_str.strip() == "":
                return None

            min_price = float(min_price_str)
            max_price = float(max_price_str) if max_price_str else min_price
            currency = currency_str.strip() if currency_str else "USD"
            moq = int(float(moq_str)) if moq_str else 1

            return PricingInfo(
                min_price=min_price,
                max_price=max_price,
                currency=currency,
                moq=moq,
            )
        except (ValueError, TypeError):
            # If parsing fails, return None rather than crashing
            return None

    def load_suppliers(
        self,
        source_path: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> List[SupplierData]:
        """Load supplier data from CSV file.

        Args:
            source_path: Path to the CSV file
            config: Optional configuration (encoding, delimiter, etc.)

        Returns:
            List[SupplierData]: List of loaded supplier data

        Raises:
            ValueError: If CSV format is invalid
            FileNotFoundError: If CSV file doesn't exist
        """
        if not self.validate_source(source_path):
            raise FileNotFoundError(f"CSV file not found or unreadable: {source_path}")

        # Set defaults from config
        encoding = config.get("encoding", "utf-8") if config else "utf-8"
        delimiter = config.get("delimiter", ",") if config else ","

        suppliers = []

        try:
            with open(source_path, "r", encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        # Required fields
                        name = row.get("name", "").strip()
                        country = row.get("country", "").strip()

                        if not name:
                            raise ValueError(f"Row {row_num}: 'name' field is required")
                        if not country:
                            raise ValueError(f"Row {row_num}: 'country' field is required")

                        # Optional fields
                        certificates = self._parse_certificates(row.get("certificates", ""))
                        pricing = self._parse_pricing(
                            row.get("pricing_min", ""),
                            row.get("pricing_max", ""),
                            row.get("currency", ""),
                            row.get("moq", ""),
                        )

                        supplier = SupplierData(
                            name=name,
                            country=country,
                            certificates=certificates,
                            pricing=pricing,
                            data_sources=[f"csv:{source_path.name}"],
                            last_updated=datetime.now(),
                        )

                        suppliers.append(supplier)

                    except Exception as e:
                        raise ValueError(f"Error parsing row {row_num}: {e}")

        except UnicodeDecodeError as e:
            raise ValueError(f"CSV encoding error: {e}")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")

        return suppliers

    def load_customer_requirements(
        self,
        source_path: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> List[CustomerRequirements]:
        """Load customer requirements from CSV file.

        Args:
            source_path: Path to the CSV file
            config: Optional configuration (encoding, delimiter, etc.)

        Returns:
            List[CustomerRequirements]: List of loaded customer requirements

        Raises:
            ValueError: If CSV format is invalid
            FileNotFoundError: If CSV file doesn't exist
        """
        if not self.validate_source(source_path):
            raise FileNotFoundError(f"CSV file not found or unreadable: {source_path}")

        # Set defaults from config
        encoding = config.get("encoding", "utf-8") if config else "utf-8"
        delimiter = config.get("delimiter", ",") if config else ","

        customer_reqs = []

        try:
            with open(source_path, "r", encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)

                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Required fields
                        company_name = row.get("company_name", "").strip()
                        quality_tier = row.get("quality_tier", "").strip()

                        if not company_name:
                            raise ValueError(f"Row {row_num}: 'company_name' field is required")
                        if not quality_tier:
                            raise ValueError(f"Row {row_num}: 'quality_tier' field is required")

                        # Optional fields
                        certificates_required = []
                        certs_str = row.get("certificates_required", "")
                        if certs_str and certs_str.strip():
                            certificates_required = [
                                cert.strip() for cert in certs_str.split(";")
                                if cert.strip()
                            ]

                        customer_req = CustomerRequirements(
                            company_name=company_name,
                            quality_tier=quality_tier,
                            certificates_required=certificates_required,
                        )

                        customer_reqs.append(customer_req)

                    except Exception as e:
                        raise ValueError(f"Error parsing row {row_num}: {e}")

        except UnicodeDecodeError as e:
            raise ValueError(f"CSV encoding error: {e}")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")

        return customer_reqs