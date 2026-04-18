"""
Clustering engine for vitamin D products.

This module provides clustering functionality to group similar vitamin D products
based on semantic similarity of their canonical material names using string similarity
metrics and clustering algorithms.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from difflib import SequenceMatcher
import math


@dataclass
class VitaminDCluster:
    """
    Represents a cluster of similar vitamin D products.

    Attributes:
        cluster_id: Unique identifier for this cluster
        canonical_name: Representative canonical name for the cluster
        products: List of VitaminDProduct objects in this cluster
        similarity_score: Average similarity score within the cluster
    """
    cluster_id: int
    canonical_name: str
    products: List = field(default_factory=list)
    similarity_score: float = 0.0

    def __post_init__(self):
        """Ensure products is a list."""
        if not isinstance(self.products, list):
            self.products = list(self.products)

    def __str__(self) -> str:
        """Return human-readable representation."""
        return (
            f"VitaminDCluster(id={self.cluster_id}, name={self.canonical_name}, "
            f"size={len(self.products)}, similarity={self.similarity_score:.3f})"
        )

    def __repr__(self) -> str:
        """Return developer-friendly representation."""
        return (
            f"VitaminDCluster(id={self.cluster_id}, "
            f"products={len(self.products)}, "
            f"similarity={self.similarity_score:.3f})"
        )

    def get_company_names(self) -> set:
        """Get unique company names in this cluster."""
        return set(p.company_name for p in self.products)

    def get_suppliers(self) -> set:
        """Get unique suppliers for products in this cluster."""
        suppliers = set()
        for product in self.products:
            if product.supplier_names:
                suppliers.update(s.strip() for s in product.supplier_names.split(','))
        return suppliers

    @property
    def company_count(self) -> int:
        """Get number of unique companies in cluster."""
        return len(self.get_company_names())

    @property
    def product_count(self) -> int:
        """Get number of products in cluster."""
        return len(self.products)


class VitaminDClusterer:
    """
    Clusters vitamin D products based on semantic similarity.

    Uses string similarity metrics to group products with similar canonical
    material names, identifying consolidation opportunities.
    """

    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize the clusterer.

        Args:
            similarity_threshold: Minimum similarity score for grouping (0.0-1.0)
        """
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")

        self.similarity_threshold = similarity_threshold

    def cluster(self, products: List) -> List[VitaminDCluster]:
        """
        Cluster a list of vitamin D products.

        Args:
            products: List of VitaminDProduct objects to cluster

        Returns:
            List of VitaminDCluster objects
        """
        if not products:
            return []

        # Get unique canonical names to use as cluster centers
        unique_names = list(set(p.canonical_material_name for p in products))

        # Group products by name first (exact matches)
        clusters_dict: Dict[str, List] = {}
        ungrouped_products = []

        for product in products:
            name = product.canonical_material_name
            if name not in clusters_dict:
                clusters_dict[name] = []
            clusters_dict[name].append(product)

        # Now perform similarity-based clustering to merge similar clusters
        cluster_centers = list(clusters_dict.keys())
        merged_clusters: Dict[str, List] = {}

        for center in cluster_centers:
            # Find the best matching existing cluster
            best_match = None
            best_similarity = self.similarity_threshold

            for existing_center in merged_clusters.keys():
                similarity = self._calculate_similarity(center, existing_center)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = existing_center

            if best_match:
                # Merge with existing cluster
                merged_clusters[best_match].extend(clusters_dict[center])
            else:
                # Create new cluster
                merged_clusters[center] = clusters_dict[center]

        # Convert to VitaminDCluster objects
        result_clusters = []
        for cluster_id, (center_name, products_list) in enumerate(merged_clusters.items()):
            # Calculate average similarity within cluster
            avg_similarity = self._calculate_cluster_similarity(center_name, products_list)

            cluster = VitaminDCluster(
                cluster_id=cluster_id,
                canonical_name=center_name,
                products=products_list,
                similarity_score=avg_similarity
            )
            result_clusters.append(cluster)

        # Sort by cluster ID
        result_clusters.sort(key=lambda c: c.cluster_id)

        return result_clusters

    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate semantic similarity between two names.

        Args:
            name1: First name
            name2: Second name

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Use SequenceMatcher for string similarity
        matcher = SequenceMatcher(None, name1.lower(), name2.lower())
        ratio = matcher.ratio()

        # Also consider if key components are present
        # Extract key words (D2, D3, cholecalciferol, ergocalciferol, dosage)
        words1 = set(name1.lower().split())
        words2 = set(name2.lower().split())

        if words1 and words2:
            # Jaccard similarity of words
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            jaccard = intersection / union if union > 0 else 0.0

            # Weight: 70% sequence match, 30% word overlap
            combined_similarity = (0.7 * ratio) + (0.3 * jaccard)
        else:
            combined_similarity = ratio

        return combined_similarity

    def _calculate_cluster_similarity(self, center_name: str, products: List) -> float:
        """
        Calculate average similarity within a cluster.

        Args:
            center_name: The cluster center name
            products: List of products in cluster

        Returns:
            Average similarity score
        """
        if not products:
            return 0.0

        similarities = [
            self._calculate_similarity(center_name, p.canonical_material_name)
            for p in products
        ]

        return sum(similarities) / len(similarities) if similarities else 0.0

    def get_cluster_summary(self, clusters: List[VitaminDCluster]) -> Dict:
        """
        Get summary statistics for clusters.

        Args:
            clusters: List of VitaminDCluster objects

        Returns:
            Dictionary with summary metrics
        """
        if not clusters:
            return {
                "total_clusters": 0,
                "total_products": 0,
                "average_cluster_size": 0.0,
                "largest_cluster_size": 0,
                "smallest_cluster_size": 0
            }

        sizes = [len(c.products) for c in clusters]

        return {
            "total_clusters": len(clusters),
            "total_products": sum(sizes),
            "average_cluster_size": sum(sizes) / len(clusters),
            "largest_cluster_size": max(sizes),
            "smallest_cluster_size": min(sizes),
            "clusters_by_size": dict(sorted(
                {i: len(c.products) for i, c in enumerate(clusters)}.items(),
                key=lambda x: x[1],
                reverse=True
            ))
        }

    def get_quality_metrics(self, clusters: List[VitaminDCluster]) -> Dict:
        """
        Calculate clustering quality metrics.

        Args:
            clusters: List of VitaminDCluster objects

        Returns:
            Dictionary with quality metrics
        """
        if not clusters:
            return {"silhouette_score": 0.0, "cohesion_score": 0.0}

        # Average similarity score (cohesion)
        avg_cohesion = (
            sum(c.similarity_score for c in clusters) / len(clusters)
            if clusters else 0.0
        )

        # Separation metric: how different are the cluster centers?
        cluster_names = [c.canonical_name for c in clusters]
        separations = []

        for i, name1 in enumerate(cluster_names):
            for name2 in cluster_names[i + 1:]:
                separation = 1.0 - self._calculate_similarity(name1, name2)
                separations.append(separation)

        avg_separation = sum(separations) / len(separations) if separations else 0.0

        # Silhouette score (combination of cohesion and separation)
        silhouette = avg_cohesion - avg_separation if len(clusters) > 1 else 0.0

        return {
            "cohesion_score": avg_cohesion,
            "separation_score": avg_separation,
            "silhouette_score": max(-1.0, min(1.0, silhouette)),
            "num_clusters": len(clusters),
            "num_products": sum(len(c.products) for c in clusters)
        }
