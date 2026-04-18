"""
Tests for vitamin D product extraction from the database.

Tests the VitaminDExtractor class which queries the database to extract
vitamin D raw material products and their metadata.
"""

import pytest
from database import get_database_session, Company, Product
from database.vitamin_d_queries import VitaminDExtractor, VitaminDProduct


class TestVitaminDProduct:
    """Tests for the VitaminDProduct dataclass."""

    def test_vitamin_d_product_initialization(self):
        """Test creating a VitaminDProduct instance."""
        product = VitaminDProduct(
            product_id=1,
            sku="RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1",
            company_id=1,
            company_name="Company A",
            product_type="raw_material",
            canonical_material_name="Vitamin D3 (Cholecalciferol) 1000 IU",
            supplier_names="Supplier A, Supplier B"
        )

        assert product.product_id == 1
        assert product.company_id == 1
        assert "Vitamin D3" in product.canonical_material_name

    def test_vitamin_d_product_str(self):
        """Test string representation."""
        product = VitaminDProduct(
            product_id=1,
            sku="RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1",
            company_id=1,
            company_name="Company A",
            product_type="raw_material",
            canonical_material_name="Vitamin D3 (Cholecalciferol) 1000 IU",
            supplier_names="Supplier A"
        )

        str_repr = str(product)
        assert "Vitamin D3" in str_repr
        assert "Company A" in str_repr


class TestVitaminDExtractor:
    """Tests for the VitaminDExtractor class."""

    def test_extractor_initialization(self):
        """Test creating a VitaminDExtractor instance."""
        extractor = VitaminDExtractor()
        assert extractor is not None

    def test_extract_vitamin_d_products(self):
        """Test extracting all vitamin D products from database."""
        extractor = VitaminDExtractor()
        products = extractor.extract_all_vitamin_d()

        assert isinstance(products, list)
        assert len(products) > 0, "Database should contain at least one vitamin D product"
        assert all(isinstance(p, VitaminDProduct) for p in products)
        assert all(p.canonical_material_name for p in products)

    def test_extracted_products_have_required_fields(self):
        """Test that extracted products have all required fields."""
        extractor = VitaminDExtractor()
        products = extractor.extract_all_vitamin_d()

        for product in products:
            assert product.product_id is not None
            assert product.sku is not None
            assert product.company_id is not None
            assert product.company_name is not None
            assert product.canonical_material_name is not None

    def test_count_vitamin_d_products(self):
        """Test getting count of vitamin D products."""
        extractor = VitaminDExtractor()
        count = extractor.count_vitamin_d_products()

        assert isinstance(count, int)
        assert count > 0

    def test_extract_by_company(self):
        """Test extracting vitamin D products by company."""
        extractor = VitaminDExtractor()

        # Get all products first
        all_products = extractor.extract_all_vitamin_d()
        assert len(all_products) > 0

        # Get by specific company
        first_company_id = all_products[0].company_id
        company_products = extractor.extract_by_company(first_company_id)

        assert len(company_products) > 0
        assert all(p.company_id == first_company_id for p in company_products)

    def test_extract_unique_canonical_names(self):
        """Test extracting unique canonical material names."""
        extractor = VitaminDExtractor()
        unique_names = extractor.get_unique_canonical_names()

        assert isinstance(unique_names, list)
        assert len(unique_names) > 0
        assert all(isinstance(name, str) for name in unique_names)

    def test_fragmentation_analysis(self):
        """Test getting fragmentation data (companies per material)."""
        extractor = VitaminDExtractor()
        fragmentation = extractor.get_fragmentation_analysis()

        assert isinstance(fragmentation, dict)
        for material_name, company_data in fragmentation.items():
            assert isinstance(material_name, str)
            assert "companies" in company_data
            assert "count" in company_data
            assert company_data["count"] > 0

    def test_supplier_dispersion(self):
        """Test getting supplier dispersion data."""
        extractor = VitaminDExtractor()
        dispersion = extractor.get_supplier_dispersion()

        assert isinstance(dispersion, dict)
        # Each material should have supplier information
        for material_name, suppliers in dispersion.items():
            assert isinstance(material_name, str)
            assert isinstance(suppliers, list)
