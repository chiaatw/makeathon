"""
Phase 1 Pipeline - End-to-end vitamin D consolidation orchestration.

Orchestrates all components: database extraction, parsing, clustering,
evidence caching, and Claude API analysis for consolidation opportunities.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from database import VitaminDExtractor
from parsing import VitaminDSKUParser
from clustering import VitaminDClusterer, VitaminDCluster
from enrichment import SupplierEvidenceCache
from equivalence_agent import call_equivalence_agent
from schemas import EquivalenceAgentInput, EndProductContext, AgentOutput


@dataclass
class Phase1Result:
    """Results from Phase 1 pipeline execution."""
    total_vitamin_d_products: int
    unique_materials: int
    clusters_found: int
    consolidation_analyses: List[AgentOutput] = field(default_factory=list)
    execution_summary: str = ""


class Phase1Pipeline:
    """
    Complete Phase 1 pipeline for vitamin D consolidation analysis.

    Workflow:
    1. Extract vitamin D products from database
    2. Parse SKUs to identify materials
    3. Cluster similar materials
    4. Load supplier evidence
    5. Run equivalence analysis on each cluster
    6. Generate consolidation recommendations
    """

    def __init__(self, use_mock_api: bool = True):
        """
        Initialize pipeline components.

        Args:
            use_mock_api: If True, uses mock Claude API for testing
        """
        self.use_mock_api = use_mock_api
        self.extractor = VitaminDExtractor()
        self.parser = VitaminDSKUParser()
        self.clusterer = VitaminDClusterer()
        self.evidence_cache = SupplierEvidenceCache()

    def run(self) -> Phase1Result:
        """
        Execute the complete Phase 1 pipeline.

        Returns:
            Phase1Result with consolidation analysis
        """
        # Step 1: Extract vitamin D products
        products = self.extractor.extract_all_vitamin_d()

        if not products:
            return Phase1Result(
                total_vitamin_d_products=0,
                unique_materials=0,
                clusters_found=0,
                execution_summary="No vitamin D products found in database"
            )

        # Step 2: Get unique materials
        unique_materials = self.extractor.get_unique_canonical_names()

        # Step 3: Cluster products
        clusters = self.clusterer.cluster(products)

        # Step 4: Run equivalence analysis on each cluster
        consolidation_analyses = []
        for cluster in clusters:
            analysis = self._analyze_cluster(cluster)
            consolidation_analyses.append(analysis)

        # Build result
        result = Phase1Result(
            total_vitamin_d_products=len(products),
            unique_materials=len(unique_materials),
            clusters_found=len(clusters),
            consolidation_analyses=consolidation_analyses,
            execution_summary=self._generate_summary(
                len(products),
                len(unique_materials),
                len(clusters),
                consolidation_analyses
            )
        )

        return result

    def _analyze_cluster(self, cluster: VitaminDCluster) -> AgentOutput:
        """
        Run equivalence agent analysis on a cluster.

        Args:
            cluster: VitaminDCluster to analyze

        Returns:
            AgentOutput with consolidation recommendation
        """
        # Extract cluster data
        skus = [p.sku for p in cluster.products]
        companies = list(cluster.get_company_names())
        suppliers = list(cluster.get_suppliers())

        # Get end product context
        end_products = [
            EndProductContext(
                sku=p.sku,
                company=p.company_name,
                name_hint=p.canonical_material_name
            )
            for p in cluster.products[:3]  # Limit to first 3
        ]

        # Create equivalence input
        input_data = EquivalenceAgentInput(
            cluster_id=f"cluster-{cluster.cluster_id}",
            skus=skus,
            affected_companies=companies,
            affected_boms=[],  # Would be populated with actual BOM IDs
            current_suppliers=suppliers if suppliers else ["Unknown"],
            end_product_context=end_products
        )

        # Call equivalence agent
        return call_equivalence_agent(input_data, use_mock=self.use_mock_api)

    def _generate_summary(
        self,
        total_products: int,
        unique_materials: int,
        clusters: int,
        analyses: List[AgentOutput]
    ) -> str:
        """
        Generate execution summary.

        Returns:
            Human-readable summary
        """
        recommended = sum(1 for a in analyses if a.verdict == "RECOMMENDED")
        proposed = sum(1 for a in analyses if a.verdict == "PROPOSED")

        return (
            f"Phase 1 Complete:\n"
            f"  - Processed {total_products} vitamin D products\n"
            f"  - Identified {unique_materials} unique materials\n"
            f"  - Created {clusters} consolidation clusters\n"
            f"  - Analysis: {recommended} Recommended, {proposed} Proposed\n"
            f"  - Consolidation opportunities identified"
        )
