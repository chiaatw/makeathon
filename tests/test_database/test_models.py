"""
Test suite for database models and connection functionality.

This module tests the SQLAlchemy models for the 6-table structure:
- Company, Product, BOM, BOM_Component, Supplier, Supplier_Product

Tests are designed to work with the real db/db.sqlite database file.
"""

import pytest
import os
from pathlib import Path
from database.connection import get_database_session, get_database_url
from database.models import Company, Product, BOM, BOMComponent, Supplier, SupplierProduct


class TestDatabaseConnection:
    """Test database connection functionality."""

    def test_database_file_exists(self):
        """Test that the SQLite database file exists."""
        db_path = Path("db/db.sqlite")
        assert db_path.exists(), f"Database file not found at {db_path}"
        assert db_path.is_file(), f"Database path is not a file: {db_path}"

    def test_get_database_url(self):
        """Test database URL generation."""
        url = get_database_url()
        assert url is not None
        assert isinstance(url, str)
        assert "sqlite" in url
        assert "db.sqlite" in url  # Check for filename, not exact path

    def test_database_session_creation(self):
        """Test that we can create a database session."""
        from sqlalchemy import text
        session = get_database_session()
        assert session is not None
        # Test basic query to verify connection works
        result = session.execute(text("SELECT 1")).fetchone()
        assert result[0] == 1
        session.close()


class TestDatabaseModels:
    """Test SQLAlchemy models against real database data."""

    @pytest.fixture
    def session(self):
        """Provide a database session for tests."""
        session = get_database_session()
        yield session
        session.close()

    def test_company_model(self, session):
        """Test Company model can query real data."""
        companies = session.query(Company).limit(5).all()
        assert len(companies) > 0

        # Test first company structure
        company = companies[0]
        assert hasattr(company, 'Id')
        assert hasattr(company, 'Name')
        assert company.Id is not None
        assert company.Name is not None
        assert isinstance(company.Name, str)

    def test_product_model(self, session):
        """Test Product model can query real data."""
        products = session.query(Product).limit(5).all()
        assert len(products) > 0

        # Test first product structure
        product = products[0]
        assert hasattr(product, 'Id')
        assert hasattr(product, 'SKU')
        assert hasattr(product, 'CompanyId')
        assert hasattr(product, 'Type')
        assert product.Id is not None
        assert product.SKU is not None
        assert product.CompanyId is not None
        assert product.Type is not None

    def test_product_company_relationship(self, session):
        """Test that Product -> Company relationship works."""
        product = session.query(Product).first()
        company = product.company
        assert company is not None
        assert isinstance(company, Company)
        assert company.Id == product.CompanyId

    def test_company_products_relationship(self, session):
        """Test that Company -> Products relationship works."""
        company = session.query(Company).first()
        products = company.products
        assert products is not None
        assert len(products) >= 0  # Could be empty for some companies
        if len(products) > 0:
            assert isinstance(products[0], Product)
            assert products[0].CompanyId == company.Id

    def test_bom_model(self, session):
        """Test BOM model can query real data."""
        boms = session.query(BOM).limit(5).all()
        assert len(boms) > 0

        bom = boms[0]
        assert hasattr(bom, 'Id')
        assert hasattr(bom, 'ProducedProductId')
        assert bom.Id is not None
        assert bom.ProducedProductId is not None

    def test_bom_component_model(self, session):
        """Test BOMComponent model can query real data."""
        components = session.query(BOMComponent).limit(5).all()
        assert len(components) > 0

        component = components[0]
        assert hasattr(component, 'BOMId')
        assert hasattr(component, 'ConsumedProductId')
        assert component.BOMId is not None
        assert component.ConsumedProductId is not None

    def test_supplier_model(self, session):
        """Test Supplier model can query real data."""
        suppliers = session.query(Supplier).limit(5).all()
        assert len(suppliers) > 0

        supplier = suppliers[0]
        assert hasattr(supplier, 'Id')
        assert hasattr(supplier, 'Name')
        assert supplier.Id is not None
        assert supplier.Name is not None
        assert isinstance(supplier.Name, str)

    def test_supplier_product_model(self, session):
        """Test SupplierProduct model can query real data."""
        supplier_products = session.query(SupplierProduct).limit(5).all()
        assert len(supplier_products) > 0

        sp = supplier_products[0]
        assert hasattr(sp, 'SupplierId')
        assert hasattr(sp, 'ProductId')
        assert sp.SupplierId is not None
        assert sp.ProductId is not None


class TestDatabaseRelationships:
    """Test complex relationships between models."""

    @pytest.fixture
    def session(self):
        """Provide a database session for tests."""
        session = get_database_session()
        yield session
        session.close()

    def test_bom_relationships(self, session):
        """Test BOM -> Product relationships."""
        bom = session.query(BOM).first()
        produced_product = bom.produced_product
        assert produced_product is not None
        assert isinstance(produced_product, Product)
        assert produced_product.Id == bom.ProducedProductId

        # Test components relationship
        components = bom.components
        assert components is not None
        assert len(components) >= 0
        if len(components) > 0:
            assert isinstance(components[0], BOMComponent)
            assert components[0].BOMId == bom.Id

    def test_supplier_product_relationships(self, session):
        """Test SupplierProduct -> Supplier and Product relationships."""
        sp = session.query(SupplierProduct).first()

        supplier = sp.supplier
        product = sp.product

        assert supplier is not None
        assert isinstance(supplier, Supplier)
        assert supplier.Id == sp.SupplierId

        assert product is not None
        assert isinstance(product, Product)
        assert product.Id == sp.ProductId

    def test_vitamin_d_products_exist(self, session):
        """Test that vitamin D products exist in the database."""
        # Look for products with vitamin D in SKU
        vitamin_d_products = session.query(Product).filter(
            Product.SKU.like('%vitamin-d%')
        ).limit(10).all()

        assert len(vitamin_d_products) > 0, "No vitamin D products found in database"

        # Verify SKU pattern matches expected format
        for product in vitamin_d_products:
            sku = product.SKU
            assert 'vitamin-d' in sku.lower()
            # Should follow pattern: RM-C{company_id}-{substance}-{variant}-{hash}
            if sku.startswith('RM-'):
                parts = sku.split('-')
                assert len(parts) >= 4, f"Unexpected SKU format: {sku}"
                assert parts[1].startswith('C'), f"Expected company ID format C{{id}}: {sku}"