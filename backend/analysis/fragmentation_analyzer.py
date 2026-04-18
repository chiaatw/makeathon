"""
Material Fragmentation Analyzer for Agnes MVP.

This module provides tools to analyze material procurement fragmentation
and identify consolidation opportunities in the supplement industry.

Key components:
- MaterialFragmentation: Dataclass storing fragmentation metrics
- FragmentationAnalyzer: Main analyzer class with database queries
"""

from dataclasses import dataclass, field
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from database import Product, CanonicalMaterialSupplierMap, Company


@dataclass
class MaterialFragmentation:
    """
    Dataclass representing material fragmentation metrics.

    Stores key metrics for analyzing procurement fragmentation:
    - How many companies buy this material
    - How many suppliers provide it
    - The fragmentation ratio (companies / suppliers)
    - Business assessment of consolidation potential
    """
    material_name: str
    company_count: int
    supplier_count: int
    fragmentation_ratio: float
    consolidation_potential: str  # "high", "medium", "low"
    companies: List[str] = field(default_factory=list)
    suppliers: List[str] = field(default_factory=list)


class FragmentationAnalyzer:
    """
    Analyzer for material procurement fragmentation.

    Provides methods to query and analyze fragmentation patterns
    in the supplement industry to identify consolidation opportunities.
    """

    def __init__(self, session: Session):
        """
        Initialize FragmentationAnalyzer with database session.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def get_materials_by_fragmentation(self, limit: int = 10) -> List[MaterialFragmentation]:
        """
        Get materials ranked by fragmentation ratio (highest first).

        Args:
            limit: Maximum number of materials to return

        Returns:
            List of MaterialFragmentation objects sorted by fragmentation ratio
        """
        # Query raw materials with company counts
        material_stats = self.session.query(
            Product.canonical_material_name,
            func.count(func.distinct(Product.CompanyId)).label('company_count')
        ).filter(
            and_(
                Product.Type == 'raw-material',
                Product.canonical_material_name.isnot(None),
                Product.canonical_material_name != ''
            )
        ).group_by(
            Product.canonical_material_name
        ).subquery()

        # Query supplier counts
        supplier_stats = self.session.query(
            CanonicalMaterialSupplierMap.canonical_material_name,
            func.count(func.distinct(CanonicalMaterialSupplierMap.supplier_id)).label('supplier_count')
        ).group_by(
            CanonicalMaterialSupplierMap.canonical_material_name
        ).subquery()

        # Join and calculate fragmentation ratios
        fragmentation_data = self.session.query(
            material_stats.c.canonical_material_name,
            material_stats.c.company_count,
            supplier_stats.c.supplier_count
        ).join(
            supplier_stats,
            material_stats.c.canonical_material_name == supplier_stats.c.canonical_material_name
        ).filter(
            supplier_stats.c.supplier_count > 0  # Avoid division by zero
        ).all()

        # Convert to MaterialFragmentation objects
        materials = []
        for material_name, company_count, supplier_count in fragmentation_data:
            fragmentation_ratio = company_count / supplier_count
            consolidation_potential = self._assess_consolidation_potential(
                company_count, supplier_count, fragmentation_ratio
            )

            materials.append(MaterialFragmentation(
                material_name=material_name,
                company_count=company_count,
                supplier_count=supplier_count,
                fragmentation_ratio=fragmentation_ratio,
                consolidation_potential=consolidation_potential
            ))

        # Sort by fragmentation ratio (highest first) and limit
        materials.sort(key=lambda x: x.fragmentation_ratio, reverse=True)
        return materials[:limit]

    def get_consolidation_candidates(self, min_companies: int = 5, max_suppliers: int = 3) -> List[MaterialFragmentation]:
        """
        Get materials with high consolidation potential.

        Args:
            min_companies: Minimum number of companies for consideration
            max_suppliers: Maximum number of suppliers for consideration

        Returns:
            List of MaterialFragmentation objects meeting criteria
        """
        all_materials = self.get_materials_by_fragmentation(limit=100)

        candidates = [
            material for material in all_materials
            if (material.company_count >= min_companies and
                material.supplier_count <= max_suppliers and
                material.consolidation_potential in ["high", "medium"])
        ]

        return candidates

    def analyze_material(self, material_name: str) -> Optional[MaterialFragmentation]:
        """
        Deep dive analysis of specific material fragmentation.

        Args:
            material_name: Canonical material name to analyze

        Returns:
            MaterialFragmentation object with detailed data or None if not found
        """
        # Get company count and company names
        company_data = self.session.query(
            Company.Name
        ).join(Product).filter(
            and_(
                Product.Type == 'raw-material',
                Product.canonical_material_name == material_name
            )
        ).distinct().all()

        if not company_data:
            return None

        companies = [company.Name for company in company_data]
        company_count = len(companies)

        # Get supplier count and supplier names
        supplier_data = self.session.query(
            CanonicalMaterialSupplierMap.supplier_name
        ).filter(
            CanonicalMaterialSupplierMap.canonical_material_name == material_name
        ).distinct().all()

        suppliers = [supplier.supplier_name for supplier in supplier_data]
        supplier_count = len(suppliers)

        if supplier_count == 0:
            return None

        fragmentation_ratio = company_count / supplier_count
        consolidation_potential = self._assess_consolidation_potential(
            company_count, supplier_count, fragmentation_ratio
        )

        return MaterialFragmentation(
            material_name=material_name,
            company_count=company_count,
            supplier_count=supplier_count,
            fragmentation_ratio=fragmentation_ratio,
            consolidation_potential=consolidation_potential,
            companies=companies,
            suppliers=suppliers
        )

    def _assess_consolidation_potential(self, company_count: int, supplier_count: int, fragmentation_ratio: float) -> str:
        """
        Assess consolidation potential based on fragmentation metrics.

        Args:
            company_count: Number of companies buying this material
            supplier_count: Number of suppliers providing this material
            fragmentation_ratio: Ratio of companies to suppliers

        Returns:
            "high", "medium", or "low" consolidation potential
        """
        # High potential: Many companies buying from very few suppliers
        if fragmentation_ratio >= 5.0 and company_count >= 10:
            return "high"

        # Medium potential: Moderate fragmentation with decent company count
        if fragmentation_ratio >= 3.0 and company_count >= 5:
            return "medium"

        # Low potential: Everything else
        return "low"