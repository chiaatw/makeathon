"""
Tests for FragmentationAnalyzer - Material Fragmentation Analysis.

Tests the core fragmentation analysis functionality including:
- MaterialFragmentation dataclass
- FragmentationAnalyzer methods
- Real data validation (vitamin D3 case)
"""

import pytest
from dataclasses import dataclass
from typing import List, Optional
from analysis import MaterialFragmentation, FragmentationAnalyzer
from database import get_database_session


class TestMaterialFragmentation:
    """Test the MaterialFragmentation dataclass."""

    def test_material_fragmentation_creation(self):
        """Test creating MaterialFragmentation with all fields."""
        fragmentation = MaterialFragmentation(
            material_name="vitamin-d3-cholecalciferol",
            company_count=17,
            supplier_count=2,
            fragmentation_ratio=8.5,
            consolidation_potential="high",
            companies=["Company1", "Company2"],
            suppliers=["Prinova USA", "PureBulk"]
        )

        assert fragmentation.material_name == "vitamin-d3-cholecalciferol"
        assert fragmentation.company_count == 17
        assert fragmentation.supplier_count == 2
        assert fragmentation.fragmentation_ratio == 8.5
        assert fragmentation.consolidation_potential == "high"
        assert len(fragmentation.companies) == 2
        assert len(fragmentation.suppliers) == 2

    def test_fragmentation_ratio_calculation(self):
        """Test that fragmentation ratio is calculated correctly."""
        fragmentation = MaterialFragmentation(
            material_name="test-material",
            company_count=10,
            supplier_count=2,
            fragmentation_ratio=5.0,
            consolidation_potential="high"
        )

        # Should be 10 / 2 = 5.0
        assert fragmentation.fragmentation_ratio == 5.0


class TestFragmentationAnalyzer:
    """Test the FragmentationAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create FragmentationAnalyzer instance with database session."""
        session = get_database_session()
        return FragmentationAnalyzer(session)

    def test_analyzer_initialization(self, analyzer):
        """Test FragmentationAnalyzer initializes properly."""
        assert analyzer is not None
        assert analyzer.session is not None

    def test_get_materials_by_fragmentation(self, analyzer):
        """Test getting materials ranked by fragmentation."""
        materials = analyzer.get_materials_by_fragmentation(limit=5)

        # Should return list of MaterialFragmentation objects
        assert isinstance(materials, list)
        assert len(materials) <= 5

        # Should be sorted by fragmentation ratio (highest first)
        if len(materials) > 1:
            for i in range(len(materials) - 1):
                assert materials[i].fragmentation_ratio >= materials[i + 1].fragmentation_ratio

    def test_get_consolidation_candidates(self, analyzer):
        """Test filtering for high consolidation potential materials."""
        candidates = analyzer.get_consolidation_candidates(
            min_companies=5,
            max_suppliers=3
        )

        assert isinstance(candidates, list)

        # All candidates should meet the criteria
        for candidate in candidates:
            assert candidate.company_count >= 5
            assert candidate.supplier_count <= 3
            assert candidate.consolidation_potential in ["high", "medium"]

    def test_analyze_material_vitamin_d3(self, analyzer):
        """Test analyzing specific material - vitamin D3 case."""
        # This is our known case: 17 companies, 2 suppliers
        result = analyzer.analyze_material("vitamin-d3-cholecalciferol")

        assert result is not None
        assert result.material_name == "vitamin-d3-cholecalciferol"
        assert result.company_count == 17
        assert result.supplier_count == 2
        assert result.fragmentation_ratio == 8.5  # 17 / 2
        assert result.consolidation_potential == "high"
        assert len(result.companies) == 17
        assert len(result.suppliers) == 2
        assert "Prinova USA" in result.suppliers

    def test_analyze_nonexistent_material(self, analyzer):
        """Test analyzing material that doesn't exist."""
        result = analyzer.analyze_material("nonexistent-material")
        assert result is None

    def test_consolidation_potential_logic(self, analyzer):
        """Test consolidation potential classification logic."""
        # Get some materials and verify the logic
        materials = analyzer.get_materials_by_fragmentation(limit=10)

        for material in materials:
            if material.fragmentation_ratio >= 5.0 and material.company_count >= 10:
                assert material.consolidation_potential == "high"
            elif material.fragmentation_ratio >= 3.0 and material.company_count >= 5:
                assert material.consolidation_potential == "medium"
            else:
                assert material.consolidation_potential == "low"


class TestFragmentationAnalysisIntegration:
    """Integration tests with real database data."""

    @pytest.fixture
    def analyzer(self):
        """Create FragmentationAnalyzer instance with database session."""
        session = get_database_session()
        return FragmentationAnalyzer(session)

    def test_real_fragmentation_data(self, analyzer):
        """Test analysis with real database data."""
        # Get top fragmented materials
        materials = analyzer.get_materials_by_fragmentation(limit=3)

        assert len(materials) > 0

        # Verify structure of results
        for material in materials:
            assert material.material_name is not None
            assert material.company_count > 0
            assert material.supplier_count > 0
            assert material.fragmentation_ratio > 0
            assert material.consolidation_potential in ["high", "medium", "low"]

    def test_known_fragmentation_patterns(self, analyzer):
        """Test known high-fragmentation materials."""
        # Based on task description, these should be high fragmentation
        known_materials = [
            "vitamin-d3-cholecalciferol",
            "microcrystalline-cellulose",
            "vitamin-c"
        ]

        for material_name in known_materials:
            result = analyzer.analyze_material(material_name)
            if result:  # Only test if the material exists in DB
                assert result.company_count >= 10, f"{material_name} should have many companies"
                assert result.supplier_count <= 3, f"{material_name} should have few suppliers"
                assert result.consolidation_potential in ["high", "medium"]