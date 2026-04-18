"""JSON Data Source Adapter for Enhanced Compliance Agent.

This module implements a concrete adapter for loading data from JSON files.
It converts JSON data to standardized data models with proper validation
and error handling, supporting nested structures and rich metadata.
"""

import json
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


class JSONAdapter(DataSourceAdapter):
    """Concrete implementation of DataSourceAdapter for JSON files.

    This adapter can load supplier data and customer requirements from JSON files.
    It supports rich nested structures and handles complex metadata including
    confidence scores, quality metrics, and delivery information.

    Expected JSON formats:

    Suppliers JSON:
    {
      "suppliers": [
        {
          "name": "Supplier Name",
          "country": "Country",
          "certificates": [
            {
              "name": "ISO 9001",
              "issuer": "TUV SUD",
              "valid_until": "2026-12-31T23:59:59"
            }
          ],
          "pricing": {
            "min_price": 100.0,
            "max_price": 150.0,
            "currency": "USD",
            "moq": 500
          },
          "quality_metrics": {...},
          "delivery_info": {...},
          "confidence_breakdown": {...}
        }
      ]
    }

    Customer Requirements JSON:
    {
      "customers": [
        {
          "company_name": "Customer Name",
          "quality_tier": "premium",
          "certificates_required": ["ISO 9001", "cGMP"],
          "constraints": {...}
        }
      ]
    }
    """

    @property
    def source_type(self) -> str:
        """Type identifier for this data source."""
        return "json"

    @property
    def supports_suppliers(self) -> bool:
        """Whether this adapter can load supplier data."""
        return True

    @property
    def supports_customers(self) -> bool:
        """Whether this adapter can load customer requirements."""
        return True

    def _parse_certificate_from_json(self, cert_data: Dict[str, Any]) -> Certificate:
        """Parse a certificate from JSON data.

        Args:
            cert_data: Dictionary with certificate information

        Returns:
            Certificate: Certificate object

        Raises:
            ValueError: If required certificate fields are missing
        """
        name = cert_data.get("name")
        if not name:
            raise ValueError("Certificate 'name' field is required")

        issuer = cert_data.get("issuer", "Unknown")

        # Parse valid_until date
        valid_until_str = cert_data.get("valid_until")
        if valid_until_str:
            try:
                # Try parsing ISO format first
                valid_until = datetime.fromisoformat(valid_until_str.replace("Z", "+00:00"))
            except ValueError:
                try:
                    # Try parsing simple date format
                    valid_until = datetime.strptime(valid_until_str, "%Y-%m-%d")
                except ValueError:
                    # Default to future date if parsing fails
                    valid_until = datetime(2030, 12, 31)
        else:
            valid_until = datetime(2030, 12, 31)

        return Certificate(
            name=name,
            issuer=issuer,
            valid_until=valid_until,
        )

    def _parse_pricing_from_json(self, pricing_data: Dict[str, Any]) -> PricingInfo:
        """Parse pricing information from JSON data.

        Args:
            pricing_data: Dictionary with pricing information

        Returns:
            PricingInfo: PricingInfo object

        Raises:
            ValueError: If required pricing fields are missing or invalid
        """
        min_price = pricing_data.get("min_price")
        if min_price is None:
            raise ValueError("Pricing 'min_price' field is required")

        max_price = pricing_data.get("max_price", min_price)
        currency = pricing_data.get("currency", "USD")
        moq = pricing_data.get("moq", 1)

        try:
            return PricingInfo(
                min_price=float(min_price),
                max_price=float(max_price),
                currency=str(currency),
                moq=int(moq),
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Error parsing pricing data: {e}")

    def _parse_supplier_from_json(
        self,
        supplier_data: Dict[str, Any],
        source_filename: str
    ) -> SupplierData:
        """Parse a supplier from JSON data.

        Args:
            supplier_data: Dictionary with supplier information
            source_filename: Name of the source file for metadata

        Returns:
            SupplierData: SupplierData object

        Raises:
            ValueError: If required supplier fields are missing
        """
        # Required fields
        name = supplier_data.get("name")
        country = supplier_data.get("country")

        if not name:
            raise ValueError("Supplier 'name' field is required")
        if not country:
            raise ValueError("Supplier 'country' field is required")

        # Parse certificates
        certificates = []
        certs_data = supplier_data.get("certificates", [])
        if isinstance(certs_data, list):
            for cert_data in certs_data:
                if isinstance(cert_data, dict):
                    certificates.append(self._parse_certificate_from_json(cert_data))
                elif isinstance(cert_data, str):
                    # Handle simple string format
                    certificates.append(Certificate(
                        name=cert_data,
                        issuer="Unknown",
                        valid_until=datetime(2030, 12, 31),
                    ))

        # Parse pricing
        pricing = None
        pricing_data = supplier_data.get("pricing")
        if pricing_data and isinstance(pricing_data, dict):
            pricing = self._parse_pricing_from_json(pricing_data)

        # Optional fields with defaults
        quality_metrics = supplier_data.get("quality_metrics")
        delivery_info = supplier_data.get("delivery_info")
        confidence_breakdown = supplier_data.get("confidence_breakdown", {})

        return SupplierData(
            name=name,
            country=country,
            certificates=certificates,
            pricing=pricing,
            quality_metrics=quality_metrics,
            delivery_info=delivery_info,
            data_sources=[f"json:{source_filename}"],
            confidence_breakdown=confidence_breakdown,
            last_updated=datetime.now(),
        )

    def _parse_customer_from_json(self, customer_data: Dict[str, Any]) -> CustomerRequirements:
        """Parse customer requirements from JSON data.

        Args:
            customer_data: Dictionary with customer requirements

        Returns:
            CustomerRequirements: CustomerRequirements object

        Raises:
            ValueError: If required customer fields are missing
        """
        # Required fields
        company_name = customer_data.get("company_name")
        quality_tier = customer_data.get("quality_tier")

        if not company_name:
            raise ValueError("Customer 'company_name' field is required")
        if not quality_tier:
            raise ValueError("Customer 'quality_tier' field is required")

        # Optional fields
        certificates_required = customer_data.get("certificates_required", [])
        constraints = customer_data.get("constraints", {})

        return CustomerRequirements(
            company_name=company_name,
            quality_tier=quality_tier,
            certificates_required=certificates_required,
            constraints=constraints,
        )

    def load_suppliers(
        self,
        source_path: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> List[SupplierData]:
        """Load supplier data from JSON file.

        Args:
            source_path: Path to the JSON file
            config: Optional configuration (encoding, etc.)

        Returns:
            List[SupplierData]: List of loaded supplier data

        Raises:
            ValueError: If JSON format is invalid
            FileNotFoundError: If JSON file doesn't exist
        """
        if not self.validate_source(source_path):
            raise FileNotFoundError(f"JSON file not found or unreadable: {source_path}")

        encoding = config.get("encoding", "utf-8") if config else "utf-8"

        try:
            with open(source_path, "r", encoding=encoding) as f:
                data = json.load(f)

            # Handle different JSON structures
            suppliers_data = []
            if isinstance(data, dict):
                if "suppliers" in data:
                    suppliers_data = data["suppliers"]
                elif "data" in data:
                    suppliers_data = data["data"]
                else:
                    # Assume the whole dict is a single supplier
                    suppliers_data = [data]
            elif isinstance(data, list):
                # Assume it's a list of suppliers
                suppliers_data = data
            else:
                raise ValueError("JSON must contain an object or array")

            suppliers = []
            for i, supplier_data in enumerate(suppliers_data):
                try:
                    supplier = self._parse_supplier_from_json(supplier_data, source_path.name)
                    suppliers.append(supplier)
                except Exception as e:
                    raise ValueError(f"Error parsing supplier {i}: {e}")

            return suppliers

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except UnicodeDecodeError as e:
            raise ValueError(f"JSON encoding error: {e}")
        except Exception as e:
            raise ValueError(f"Error reading JSON file: {e}")

    def load_customer_requirements(
        self,
        source_path: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> List[CustomerRequirements]:
        """Load customer requirements from JSON file.

        Args:
            source_path: Path to the JSON file
            config: Optional configuration (encoding, etc.)

        Returns:
            List[CustomerRequirements]: List of loaded customer requirements

        Raises:
            ValueError: If JSON format is invalid
            FileNotFoundError: If JSON file doesn't exist
        """
        if not self.validate_source(source_path):
            raise FileNotFoundError(f"JSON file not found or unreadable: {source_path}")

        encoding = config.get("encoding", "utf-8") if config else "utf-8"

        try:
            with open(source_path, "r", encoding=encoding) as f:
                data = json.load(f)

            # Handle different JSON structures
            customers_data = []
            if isinstance(data, dict):
                if "customers" in data:
                    customers_data = data["customers"]
                elif "customer_requirements" in data:
                    customers_data = data["customer_requirements"]
                elif "data" in data:
                    customers_data = data["data"]
                else:
                    # Assume the whole dict is a single customer requirement
                    customers_data = [data]
            elif isinstance(data, list):
                # Assume it's a list of customer requirements
                customers_data = data
            else:
                raise ValueError("JSON must contain an object or array")

            customer_reqs = []
            for i, customer_data in enumerate(customers_data):
                try:
                    customer_req = self._parse_customer_from_json(customer_data)
                    customer_reqs.append(customer_req)
                except Exception as e:
                    raise ValueError(f"Error parsing customer requirement {i}: {e}")

            return customer_reqs

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except UnicodeDecodeError as e:
            raise ValueError(f"JSON encoding error: {e}")
        except Exception as e:
            raise ValueError(f"Error reading JSON file: {e}")