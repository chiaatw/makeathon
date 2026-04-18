"""
Vitamin D product extraction and analysis from the database.

This module provides utilities to query and extract vitamin D products
from the supplement database, with fragmentation and supplier analysis.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from parsing.sku_parser import VitaminDSKUParser
from .connection import get_database_session
from .models import Product, Company, SupplierProduct, Supplier


@dataclass
class VitaminDProduct:
    """
    Represents an extracted vitamin D product from the database.

    Attributes:
        product_id: Database Product ID
        sku: Raw material SKU
        company_id: Company ID that this product belongs to
        company_name: Name of the company
        product_type: Type of product (raw_material, finished_good, etc.)
        canonical_material_name: Normalized material name
        supplier_names: Comma-separated supplier names
    """
    product_id: int
    sku: str
    company_id: int
    company_name: str
    product_type: str
    canonical_material_name: str
    supplier_names: Optional[str] = None

    def __str__(self) -> str:
        """Return human-readable representation."""
        return (
            f"VitaminDProduct({self.canonical_material_name} | "
            f"Company: {self.company_name} | SKU: {self.sku})"
        )

    def __repr__(self) -> str:
        """Return developer-friendly representation."""
        return (
            f"VitaminDProduct(id={self.product_id}, "
            f"name={self.canonical_material_name})"
        )


class VitaminDExtractor:
    """
    Extracts vitamin D products and metadata from the supplement database.

    Provides methods to:
    - Extract all vitamin D products
    - Filter by company or supplier
    - Analyze fragmentation (how many companies have the same material)
    - Track supplier dispersion (how distributed a material is)
    """

    def __init__(self):
        """Initialize the extractor with a SKU parser."""
        self.parser = VitaminDSKUParser()

    def extract_all_vitamin_d(self) -> List[VitaminDProduct]:
        """
        Extract all vitamin D products from the database.

        Returns:
            List of VitaminDProduct objects
        """
        session = get_database_session()
        try:
            # Query all raw materials (type starts with 'RM')
            products = session.query(Product).all()

            vitamin_d_products = []

            for product in products:
                try:
                    # Try to parse the SKU
                    parsed = self.parser.parse(product.SKU)

                    # Only include vitamin D products
                    if not parsed.is_vitamin_d:
                        continue

                    # Get company name
                    company = session.query(Company).filter_by(Id=product.CompanyId).first()
                    company_name = company.Name if company else f"Company {product.CompanyId}"

                    # Get suppliers for this product
                    supplier_products = (
                        session.query(SupplierProduct)
                        .filter_by(ProductId=product.Id)
                        .all()
                    )
                    supplier_names = []
                    for sp in supplier_products:
                        supplier = session.query(Supplier).filter_by(Id=sp.SupplierId).first()
                        if supplier:
                            supplier_names.append(supplier.Name)

                    # Use parsed canonical name if available, otherwise use SKU
                    canonical_name = (
                        parsed.canonical_name if parsed.canonical_name else product.SKU
                    )

                    vitamin_d_product = VitaminDProduct(
                        product_id=product.Id,
                        sku=product.SKU,
                        company_id=product.CompanyId,
                        company_name=company_name,
                        product_type=product.Type,
                        canonical_material_name=canonical_name,
                        supplier_names=", ".join(supplier_names) if supplier_names else None
                    )

                    vitamin_d_products.append(vitamin_d_product)

                except (ValueError, AttributeError):
                    # Skip products that can't be parsed
                    continue

            return vitamin_d_products

        finally:
            session.close()

    def count_vitamin_d_products(self) -> int:
        """
        Get count of vitamin D products in database.

        Returns:
            Number of vitamin D products
        """
        return len(self.extract_all_vitamin_d())

    def extract_by_company(self, company_id: int) -> List[VitaminDProduct]:
        """
        Extract vitamin D products for a specific company.

        Args:
            company_id: Company ID to filter by

        Returns:
            List of VitaminDProduct objects for the company
        """
        all_products = self.extract_all_vitamin_d()
        return [p for p in all_products if p.company_id == company_id]

    def get_unique_canonical_names(self) -> List[str]:
        """
        Get list of unique canonical material names.

        Returns:
            Sorted list of unique material names
        """
        products = self.extract_all_vitamin_d()
        unique_names = sorted(set(p.canonical_material_name for p in products))
        return unique_names

    def get_fragmentation_analysis(self) -> Dict[str, Dict]:
        """
        Analyze material fragmentation - how many companies have each material.

        Returns:
            Dict mapping canonical name to {'companies': [names], 'count': int}
        """
        products = self.extract_all_vitamin_d()
        fragmentation = {}

        for product in products:
            name = product.canonical_material_name
            if name not in fragmentation:
                fragmentation[name] = {
                    'companies': set(),
                    'count': 0
                }

            fragmentation[name]['companies'].add(product.company_name)

        # Convert sets to sorted lists and update counts
        for name in fragmentation:
            fragmentation[name]['companies'] = sorted(list(fragmentation[name]['companies']))
            fragmentation[name]['count'] = len(fragmentation[name]['companies'])

        return fragmentation

    def get_supplier_dispersion(self) -> Dict[str, List[str]]:
        """
        Analyze supplier dispersion - which suppliers provide each material.

        Returns:
            Dict mapping canonical name to list of unique supplier names
        """
        products = self.extract_all_vitamin_d()
        dispersion = {}

        for product in products:
            name = product.canonical_material_name
            if name not in dispersion:
                dispersion[name] = set()

            # Add suppliers for this product
            if product.supplier_names:
                suppliers = [s.strip() for s in product.supplier_names.split(',')]
                dispersion[name].update(suppliers)

        # Convert sets to sorted lists
        return {name: sorted(list(suppliers)) for name, suppliers in dispersion.items()}
