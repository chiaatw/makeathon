"""Plugin system for the Enhanced Compliance Agent.

This package provides the plugin architecture for extending compliance checking
capabilities. Plugins implement specific compliance checks and return PluginResult
objects that are aggregated into a final ComplianceResult.
"""

from makeathon.agents.plugins.base import CompliancePlugin

__all__ = ["CompliancePlugin"]
