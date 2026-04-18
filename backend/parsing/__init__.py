"""
Parsing package for extracting substance information from raw material SKUs.

This package provides utilities for parsing vitamin D SKUs and extracting
standardized substance information for clustering and consolidation analysis.
"""

from .sku_parser import VitaminDSKUParser, ParsedSKU

__all__ = ['VitaminDSKUParser', 'ParsedSKU']
