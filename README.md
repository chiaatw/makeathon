# Makeathon - Enhanced Compliance Agent

Makeathon spherecast challenge - Enhanced compliance checking system for supplier evaluation.

## Enhanced Compliance Agent

A sophisticated, plugin-based compliance checking system for supplier evaluation with multi-source data aggregation and user-configurable prioritization.

### Features

- **Plugin Architecture**: Extensible compliance checking modules (certificates, pricing, quality, etc.)
- **Multi-Source Data**: Intelligent aggregation from CSV, JSON, and other data sources
- **Configurable Scoring**: User-defined weights and prioritization for compliance factors
- **Backward Compatibility**: Seamless integration with existing SimpleComplianceChecker interface
- **Transparency**: Detailed reasoning chains and confidence scoring

### Quick Start

#### Basic Usage (Backward Compatible)

```python
from agents.enhanced_compliance_agent import call_compliance_agent

# Works exactly like the original SimpleComplianceChecker
result = call_compliance_agent("Vitamin D3", "DSM", "PharmaCorp")

print(f"Status: {result.compliance_status}")
print(f"Confidence: {result.confidence:.1%}")
print(f"Reasoning: {result.reasoning}")
```

#### Enhanced Usage

```python
from agents.enhanced_compliance_agent import EnhancedComplianceAgent

# Create agent with multiple data sources
agent = EnhancedComplianceAgent(data_sources=[
    {"path": "data/suppliers.csv"},
    {"path": "data/external_evidence.json"},
])

# Enhanced compliance check with detailed results
result = agent.check_compliance_enhanced("DSM", "PharmaCorp")

print(f"Overall Score: {result.overall_score:.3f}")
print(f"Plugin Results: {len(result.plugin_results)}")

# Rank all suppliers for a customer
rankings = agent.rank_suppliers("PharmaCorp", limit=5)
for rank, (supplier, result) in enumerate(rankings, 1):
    print(f"{rank}. {supplier}: {result.overall_score:.3f}")
```

### Architecture

#### Core Components

1. **Data Models** (`agents/core/data_models.py`)
   - Unified data structures for suppliers, customers, and results
   - Type-safe dataclasses with metadata tracking

2. **Plugin System** (`agents/plugins/`)
   - `base.py`: Abstract plugin interface
   - `certificates.py`: Certificate compliance checking
   - Extensible for additional compliance factors

3. **Data Sources** (`agents/data_sources/`)
   - `manager.py`: Multi-source data aggregation with conflict resolution
   - `csv_adapter.py`: CSV file adapter
   - `json_adapter.py`: JSON file adapter

4. **Scoring Engine** (`agents/scoring/engine.py`)
   - Configurable weights and aggregation methods
   - Confidence penalty system
   - Multiple ranking strategies

5. **Compliance Engine** (`agents/engine/compliance_engine.py`)
   - Core orchestration of plugins, data, and scoring
   - Batch analysis and ranking capabilities

6. **Enhanced Agent** (`agents/enhanced_compliance_agent.py`)
   - Main public interface with backward compatibility
   - Automatic mode detection and fallback

### Testing

```bash
# Simple data validation
python simple_test.py

# Full integration demonstration  
python demo_enhanced_compliance.py

# Integration validation
python -c "from agents.integration.data_integration import run_integration_validation; run_integration_validation()"
```

### Migration from SimpleComplianceChecker

The Enhanced Compliance Agent is designed for seamless migration:

#### Before (SimpleComplianceChecker)
```python
from simple_compliance_checker import SimpleComplianceChecker

checker = SimpleComplianceChecker()
result = checker.check("Vitamin D3", "DSM", "PharmaCorp")
```

#### After (Enhanced Agent)
```python
from agents.enhanced_compliance_agent import call_compliance_agent

# Exact same interface - enhanced automatically when data sources available
result = call_compliance_agent("Vitamin D3", "DSM", "PharmaCorp")
```

No code changes required! The enhanced system automatically detects available data sources and falls back to legacy mode if enhanced features unavailable.

### File Structure

```
makeathon/
├── agents/
│   ├── core/
│   │   ├── __init__.py
│   │   └── data_models.py
│   ├── plugins/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── certificates.py
│   ├── data_sources/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── csv_adapter.py
│   │   ├── json_adapter.py
│   │   └── manager.py
│   ├── scoring/
│   │   ├── __init__.py
│   │   └── engine.py
│   ├── engine/
│   │   ├── __init__.py
│   │   └── compliance_engine.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── data_integration.py
│   │   └── legacy_csv_adapter.py
│   ├── enhanced_compliance_agent.py
│   └── simple_compliance_checker.py (original)
├── data/
│   ├── suppliers.csv
│   ├── customer_requirements.csv
│   └── external_evidence.json
├── tests/
│   ├── core/
│   ├── plugins/
│   └── test_agents/
├── simple_test.py
├── demo_enhanced_compliance.py
└── README.md
```

## Original Project Components

The makeathon project also includes other analysis components for vitamin D clustering, supplier caching, and data pipeline processing. See individual module documentation for details.
