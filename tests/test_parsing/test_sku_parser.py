"""
Tests for vitamin D SKU parsing module.

Tests the VitaminDSKUParser class which parses SKUs following the pattern:
RM-C{company_id}-{substance}-{variant}-{hash}
Example: RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1
"""

import pytest
from parsing.sku_parser import VitaminDSKUParser, ParsedSKU


class TestParsedSKU:
    """Tests for the ParsedSKU dataclass."""

    def test_parsed_sku_initialization(self):
        """Test creating a ParsedSKU instance."""
        sku = ParsedSKU(
            original_sku="RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1",
            company_id=1,
            substance="vitamin-d3",
            variant="cholecalciferol-1000iu",
            hash_value="15a7d2b1",
            is_vitamin_d=True,
            canonical_name="Vitamin D3 (Cholecalciferol) 1000 IU"
        )

        assert sku.original_sku == "RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1"
        assert sku.company_id == 1
        assert sku.substance == "vitamin-d3"
        assert sku.is_vitamin_d is True
        assert sku.canonical_name == "Vitamin D3 (Cholecalciferol) 1000 IU"

    def test_parsed_sku_str_representation(self):
        """Test string representation of ParsedSKU."""
        sku = ParsedSKU(
            original_sku="RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1",
            company_id=1,
            substance="vitamin-d3",
            variant="cholecalciferol-1000iu",
            hash_value="15a7d2b1",
            is_vitamin_d=True,
            canonical_name="Vitamin D3 (Cholecalciferol) 1000 IU"
        )

        str_repr = str(sku)
        assert "Vitamin D3" in str_repr


class TestVitaminDSKUParser:
    """Tests for the VitaminDSKUParser class."""

    def test_parser_initialization(self):
        """Test creating a VitaminDSKUParser instance."""
        parser = VitaminDSKUParser()
        assert parser is not None

    def test_parse_simple_vitamin_d3_sku(self):
        """Test parsing a simple vitamin D3 SKU."""
        parser = VitaminDSKUParser()
        sku = "RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1"

        result = parser.parse(sku)

        assert result is not None
        assert result.original_sku == sku
        assert result.company_id == 1
        assert result.substance == "vitamin-d3"
        assert result.is_vitamin_d is True
        assert "1000" in result.variant or "1000" in result.canonical_name

    def test_parse_vitamin_d2_sku(self):
        """Test parsing a vitamin D2 (ergocalciferol) SKU."""
        parser = VitaminDSKUParser()
        sku = "RM-C2-vitamin-d2-ergocalciferol-400iu-a3f5b2c1"

        result = parser.parse(sku)

        assert result is not None
        assert result.is_vitamin_d is True
        assert "d2" in result.substance.lower() or "ergocalciferol" in result.canonical_name.lower()

    def test_parse_non_vitamin_d_sku(self):
        """Test parsing a non-vitamin D SKU."""
        parser = VitaminDSKUParser()
        sku = "RM-C3-vitamin-a-retinol-5000iu-c1d2e3f4"

        result = parser.parse(sku)

        assert result is not None
        assert result.is_vitamin_d is False

    def test_parse_invalid_sku_format(self):
        """Test parsing an SKU with invalid format."""
        parser = VitaminDSKUParser()
        sku = "INVALID-SKU-FORMAT"

        with pytest.raises(ValueError):
            parser.parse(sku)

    def test_parse_multiple_skus(self):
        """Test parsing a batch of SKUs."""
        parser = VitaminDSKUParser()
        skus = [
            "RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1",
            "RM-C2-vitamin-d2-ergocalciferol-400iu-a3f5b2c1",
            "RM-C3-vitamin-a-retinol-5000iu-c1d2e3f4",
        ]

        results = [parser.parse(sku) for sku in skus]

        assert len(results) == 3
        assert results[0].is_vitamin_d is True
        assert results[1].is_vitamin_d is True
        assert results[2].is_vitamin_d is False

    def test_parse_extracts_dosage(self):
        """Test that parser correctly extracts dosage from SKU."""
        parser = VitaminDSKUParser()
        sku = "RM-C1-vitamin-d3-cholecalciferol-5000iu-15a7d2b1"

        result = parser.parse(sku)

        assert result is not None
        # Dosage should be extracted from variant
        assert "5000" in result.variant or "5000" in result.canonical_name

    def test_canonical_name_normalization(self):
        """Test that canonical names are normalized consistently."""
        parser = VitaminDSKUParser()

        sku1 = "RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1"
        sku2 = "RM-C5-vitamin-d3-cholecalciferol-1000iu-9f2e3d4c"

        result1 = parser.parse(sku1)
        result2 = parser.parse(sku2)

        # Same substance and dosage should have same canonical name
        assert result1.canonical_name == result2.canonical_name
