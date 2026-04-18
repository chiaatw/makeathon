"""
Clustering package for grouping similar vitamin D products.

This package provides utilities for clustering vitamin D products
based on semantic similarity of their canonical material names.
"""

from .vitamin_d_cluster import VitaminDCluster, VitaminDClusterer

__all__ = ['VitaminDCluster', 'VitaminDClusterer']
