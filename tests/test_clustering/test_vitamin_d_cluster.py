"""
Tests for vitamin D clustering engine.

Tests the VitaminDClusterer class which groups similar vitamin D products
based on semantic similarity of their canonical material names.
"""

import pytest
from clustering.vitamin_d_cluster import VitaminDCluster, VitaminDClusterer
from database import VitaminDProduct


class TestVitaminDCluster:
    """Tests for the VitaminDCluster dataclass."""

    def test_vitamin_d_cluster_initialization(self):
        """Test creating a VitaminDCluster instance."""
        products = [
            VitaminDProduct(
                product_id=1,
                sku="RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1",
                company_id=1,
                company_name="Company A",
                product_type="raw_material",
                canonical_material_name="Vitamin D3 (Cholecalciferol) 1000 IU",
                supplier_names="Supplier A"
            )
        ]

        cluster = VitaminDCluster(
            cluster_id=0,
            canonical_name="Vitamin D3 (Cholecalciferol)",
            products=products,
            similarity_score=0.95
        )

        assert cluster.cluster_id == 0
        assert cluster.canonical_name == "Vitamin D3 (Cholecalciferol)"
        assert len(cluster.products) == 1
        assert cluster.similarity_score == 0.95

    def test_vitamin_d_cluster_str(self):
        """Test string representation."""
        products = []
        cluster = VitaminDCluster(
            cluster_id=0,
            canonical_name="Vitamin D3 (Cholecalciferol)",
            products=products,
            similarity_score=0.95
        )

        str_repr = str(cluster)
        assert "Vitamin D3" in str_repr
        assert "0" in str_repr


class TestVitaminDClusterer:
    """Tests for the VitaminDClusterer class."""

    def test_clusterer_initialization(self):
        """Test creating a VitaminDClusterer instance."""
        clusterer = VitaminDClusterer()
        assert clusterer is not None

    def test_cluster_products(self):
        """Test clustering a set of products."""
        from database import VitaminDExtractor

        # Use real data from database
        extractor = VitaminDExtractor()
        products = extractor.extract_all_vitamin_d()

        if len(products) > 0:
            clusterer = VitaminDClusterer()
            clusters = clusterer.cluster(products)

            assert isinstance(clusters, list)
            assert len(clusters) > 0
            assert all(isinstance(c, VitaminDCluster) for c in clusters)

    def test_cluster_with_similarity_threshold(self):
        """Test clustering with custom similarity threshold."""
        from database import VitaminDExtractor

        extractor = VitaminDExtractor()
        products = extractor.extract_all_vitamin_d()

        if len(products) > 0:
            # Higher threshold = stricter grouping
            clusterer_strict = VitaminDClusterer(similarity_threshold=0.95)
            clusters_strict = clusterer_strict.cluster(products)

            # Lower threshold = more lenient grouping
            clusterer_loose = VitaminDClusterer(similarity_threshold=0.5)
            clusters_loose = clusterer_loose.cluster(products)

            # With a lower threshold, we should have <= clusters because more merging occurs
            assert len(clusters_strict) >= len(clusters_loose)

    def test_get_cluster_summary(self):
        """Test getting summary of clusters."""
        from database import VitaminDExtractor

        extractor = VitaminDExtractor()
        products = extractor.extract_all_vitamin_d()

        if len(products) > 0:
            clusterer = VitaminDClusterer()
            clusters = clusterer.cluster(products)
            summary = clusterer.get_cluster_summary(clusters)

            assert isinstance(summary, dict)
            assert "total_clusters" in summary
            assert "total_products" in summary
            assert "average_cluster_size" in summary
            assert summary["total_clusters"] == len(clusters)
            assert summary["total_products"] == len(products)

    def test_cluster_quality_metrics(self):
        """Test calculation of cluster quality metrics."""
        from database import VitaminDExtractor

        extractor = VitaminDExtractor()
        products = extractor.extract_all_vitamin_d()

        if len(products) > 0:
            clusterer = VitaminDClusterer()
            clusters = clusterer.cluster(products)
            metrics = clusterer.get_quality_metrics(clusters)

            assert isinstance(metrics, dict)
            assert "silhouette_score" in metrics or "cohesion_score" in metrics

    def test_clusters_contain_all_products(self):
        """Test that all products are assigned to clusters."""
        from database import VitaminDExtractor

        extractor = VitaminDExtractor()
        products = extractor.extract_all_vitamin_d()

        if len(products) > 0:
            clusterer = VitaminDClusterer()
            clusters = clusterer.cluster(products)

            # Count total products in all clusters
            total_in_clusters = sum(len(cluster.products) for cluster in clusters)

            assert total_in_clusters == len(products), \
                f"Mismatch: {total_in_clusters} in clusters vs {len(products)} total"

    def test_similarity_features(self):
        """Test that clustering uses semantic similarity features."""
        clusterer = VitaminDClusterer()

        # These should be similar and cluster together
        similar_names = [
            "Vitamin D3 (Cholecalciferol) 1000 IU",
            "Vitamin D3 (Cholecalciferol) 1000IU",
            "Cholecalciferol Vitamin D3 1000 IU"
        ]

        # These should be different
        different_names = [
            "Vitamin D2 (Ergocalciferol) 400 IU",
            "Vitamin A (Retinol) 5000 IU"
        ]

        # Check similar names have higher similarity than different names
        similar_similarities = []
        for name in similar_names:
            similarity = clusterer._calculate_similarity(
                "Vitamin D3 (Cholecalciferol) 1000 IU",
                name
            )
            similar_similarities.append(similarity)
            assert similarity > 0.6, f"Expected reasonable similarity for {name}"

        # Check different names have lower similarity
        for name in different_names:
            similarity = clusterer._calculate_similarity(
                "Vitamin D3 (Cholecalciferol) 1000 IU",
                name
            )
            assert similarity < min(similar_similarities), \
                f"Expected {name} to be less similar than the similar names"
