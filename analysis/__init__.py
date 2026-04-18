"""
Analysis package for Agnes MVP - Material Fragmentation Analysis.

This package provides tools to analyze supplement material procurement
fragmentation and identify consolidation opportunities.

Key components:
- MaterialFragmentation: Dataclass for fragmentation metrics
- FragmentationAnalyzer: Main analyzer for fragmentation patterns
"""

from .fragmentation_analyzer import MaterialFragmentation, FragmentationAnalyzer

__all__ = [
    'MaterialFragmentation',
    'FragmentationAnalyzer'
]