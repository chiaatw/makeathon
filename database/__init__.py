"""
Database package for Agnes MVP - Vitamin D Database Integration.

This package provides SQLAlchemy models and connection utilities for the
6-table supplement database structure:

- Company: Supplement companies (61 rows)
- Product: Products including finished goods and raw materials (1025 rows)
- BOM + BOM_Component: Bill of materials relationships
- Supplier + Supplier_Product: M:N supplier mappings

Database Schema Context:
SKU pattern: RM-C{company_id}-{substance}-{variant}-{hash}
Example: RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1
"""

from .models import Company, Product, BOM, BOMComponent, Supplier, SupplierProduct, CanonicalMaterialSupplierMap
from .connection import get_database_session, get_database_url, get_engine
from .vitamin_d_queries import VitaminDExtractor, VitaminDProduct

__all__ = [
    'Company', 'Product', 'BOM', 'BOMComponent', 'Supplier', 'SupplierProduct', 'CanonicalMaterialSupplierMap',
    'get_database_session', 'get_database_url', 'get_engine',
    'VitaminDExtractor', 'VitaminDProduct'
]