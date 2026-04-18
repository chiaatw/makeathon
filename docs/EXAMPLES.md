# Enhanced Compliance Agent - Examples

This document provides comprehensive examples of using the Enhanced Compliance Agent.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Enhanced Features](#enhanced-features)
3. [Configuration Examples](#configuration-examples)
4. [Integration Examples](#integration-examples)
5. [Plugin Development Examples](#plugin-development-examples)
6. [Data Source Examples](#data-source-examples)
7. [Error Handling Examples](#error-handling-examples)
8. [Performance Examples](#performance-examples)

## Basic Usage

### Example 1: Simple Compliance Check

```python
from agents.enhanced_compliance_agent import call_compliance_agent

# Most basic usage - exactly like original SimpleComplianceChecker
result = call_compliance_agent("Vitamin D3", "DSM", "PharmaCorp")

print(f"Compliance Status: {result.compliance_status}")
print(f"Confidence: {result.confidence:.1%}")
print(f"Reasoning: {result.reasoning}")
print(f"Synergy Potential: {result.synergy_potential:.1f}% savings")

# Output:
# Compliance Status: COMPLIANT
# Confidence: 95.0%
# Reasoning: certificates: ✓ | Overall: 85%
# Synergy Potential: 21.3% savings
```

### Example 2: Multiple Supplier Comparison

```python
from agents.enhanced_compliance_agent import call_compliance_agent

suppliers = ["DSM", "BASF", "Prinova USA"]
customer = "PharmaCorp"
material = "Vitamin D3"

print(f"Compliance comparison for {customer}:")
print("-" * 50)

for supplier in suppliers:
    result = call_compliance_agent(material, supplier, customer)
    
    print(f"{supplier:15} | {result.compliance_status:15} | "
          f"Conf: {result.confidence:.1%} | "
          f"Synergy: {result.synergy_potential:.1f}%")

# Output:
# DSM             | COMPLIANT       | Conf: 95.0% | Synergy: 21.3%
# BASF            | COMPLIANT       | Conf: 90.0% | Synergy: 18.0%
# Prinova USA     | NON_COMPLIANT   | Conf: 85.0% | Synergy: 0.0%
```

## Enhanced Features

### Example 3: Enhanced Compliance Analysis

```python
from agents.enhanced_compliance_agent import EnhancedComplianceAgent

# Create agent with automatic data source detection
agent = EnhancedComplianceAgent()

# Enhanced analysis with detailed results
result = agent.check_compliance_enhanced("DSM", "PharmaCorp")

print(f"Overall Compliance Score: {result.overall_score:.3f}")
print(f"Overall Confidence: {result.overall_confidence:.1%}")
print()

print("Plugin Analysis:")
for plugin_result in result.plugin_results:
    print(f"  {plugin_result.plugin_name:12} | "
          f"Score: {plugin_result.score:.3f} | "
          f"Conf: {plugin_result.confidence:.1%}")
    
    if plugin_result.blocking_issues:
        for issue in plugin_result.blocking_issues:
            print(f"    ⚠️  {issue}")

print("\nReasoning Chain:")
for i, reason in enumerate(result.reasoning_chain, 1):
    print(f"  {i}. {reason}")

if result.recommendations:
    print("\nRecommendations:")
    for rec in result.recommendations:
        print(f"  • {rec}")
```

### Example 4: Supplier Ranking

```python
from agents.enhanced_compliance_agent import EnhancedComplianceAgent

agent = EnhancedComplianceAgent()

# Rank all available suppliers for PharmaCorp
rankings = agent.rank_suppliers("PharmaCorp", limit=5)

print("Supplier Rankings for PharmaCorp:")
print("=" * 60)
print(f"{'Rank':<4} {'Supplier':<15} {'Score':<8} {'Confidence':<12} {'Status'}")
print("-" * 60)

for i, (supplier_name, result) in enumerate(rankings, 1):
    status = "✅ COMPLIANT" if result.overall_score >= 0.8 else "❌ NON_COMPLIANT"
    print(f"{i:<4} {supplier_name:<15} {result.overall_score:<8.3f} "
          f"{result.overall_confidence:<12.1%} {status}")
```

### Example 5: Batch Analysis

```python
from agents.enhanced_compliance_agent import EnhancedComplianceAgent

agent = EnhancedComplianceAgent()

# Analyze multiple suppliers at once
suppliers = ["DSM", "BASF", "Prinova USA", "Unknown Supplier"]
results = agent.batch_analyze_suppliers(suppliers, "PharmaCorp")

print("Batch Analysis Results:")
print("-" * 40)

for supplier, result in results.items():
    print(f"\n{supplier}:")
    print(f"  Score: {result.overall_score:.3f}")
    print(f"  Confidence: {result.overall_confidence:.1%}")
    print(f"  Plugins: {len(result.plugin_results)}")
    
    if result.data_gaps:
        print(f"  Data gaps: {', '.join(result.data_gaps)}")
```

## Configuration Examples

### Example 6: Custom Scoring Configuration

```python
from agents.enhanced_compliance_agent import EnhancedComplianceAgent

# Create agent and configure custom scoring
agent = EnhancedComplianceAgent()

# Scenario 1: Prioritize certificates heavily for pharmaceutical customer
agent.configure_scoring(
    plugin_weights={
        "certificates": 0.8,  # Very important for pharma
        "pricing": 0.2        # Less important
    },
    aggregation_method="weighted_average",
    confidence_penalty_factor=0.1  # Light penalty for low confidence
)

result1 = agent.check_compliance_enhanced("DSM", "PharmaCorp")
print(f"Certificate-focused score: {result1.overall_score:.3f}")

# Scenario 2: Balance certificates and pricing for supplement customer  
agent.configure_scoring(
    plugin_weights={
        "certificates": 0.5,
        "pricing": 0.5
    },
    aggregation_method="weighted_average"
)

result2 = agent.check_compliance_enhanced("DSM", "FoodSupplementCo")
print(f"Balanced score: {result2.overall_score:.3f}")

# Scenario 3: Strict mode - any issues are blocking
agent.configure_scoring(
    plugin_weights={"certificates": 1.0},
    aggregation_method="min",  # Most restrictive
    confidence_penalty_factor=0.3
)

result3 = agent.check_compliance_enhanced("Prinova USA", "PharmaCorp")
print(f"Strict mode score: {result3.overall_score:.3f}")
```

### Example 7: Data Source Configuration

```python
from agents.enhanced_compliance_agent import EnhancedComplianceAgent

# Configure with specific data sources
data_sources = [
    {
        "path": "data/suppliers.csv",
        "type": "csv",
        "config": {
            "encoding": "utf-8",
            "delimiter": ","
        }
    },
    {
        "path": "data/external_evidence.json", 
        "type": "json"
    },
    {
        "path": "data/additional_suppliers.csv",
        "type": "csv",
        "config": {
            "delimiter": ";"  # Different delimiter
        }
    }
]

agent = EnhancedComplianceAgent(
    data_sources=data_sources,
    use_enhanced_mode=True,
    legacy_fallback=False  # Don't fall back to legacy mode
)

# Check system status
status = agent.get_system_status()
print(f"Data sources loaded: {status['data_status']['suppliers_loaded']} suppliers")
```

## Integration Examples

### Example 8: Simple Integration Setup

```python
from agents.integration.data_integration import setup_integration

# Simplest setup - automatically detects data in 'data/' directory
agent = setup_integration()

# Test the integration
result = agent.check_compliance("DSM", "PharmaCorp")
print(f"Integration test result: {result.compliance_status}")

# Check what data was loaded
status = agent.get_system_status()
print(f"Mode: {status['mode']}")
print(f"Suppliers: {status.get('data_status', {}).get('suppliers_loaded', 0)}")
```

### Example 9: Custom Integration with Validation

```python
from agents.integration.data_integration import LegacyDataAdapter
from pathlib import Path

# Create adapter for specific data directory
adapter = LegacyDataAdapter(Path("data"))

# Validate data files first
print("Validating data files...")
validation_report = adapter.validate_data_files()

print("Files found:")
for file_name, exists in validation_report["files_found"].items():
    status = "✅" if exists else "❌"
    print(f"  {status} {file_name}")

if validation_report["issues"]:
    print("\nIssues:")
    for issue in validation_report["issues"]:
        print(f"  ⚠️  {issue}")

# Run integration test
print("\nRunning integration test...")
test_report = adapter.test_integration()

if test_report["integration_test"] == "completed":
    print("✅ Integration test passed")
else:
    print("❌ Integration test failed")
    for error in test_report["errors"]:
        print(f"  Error: {error}")
```

### Example 10: Adding New Data Sources Dynamically

```python
from agents.enhanced_compliance_agent import EnhancedComplianceAgent

# Start with basic setup
agent = EnhancedComplianceAgent()

# Add additional data source during runtime
agent.add_data_source(
    source_path="data/new_suppliers.json",
    source_type="json"
)

# Add CSV with custom configuration
agent.add_data_source(
    source_path="data/european_suppliers.csv",
    config={
        "encoding": "iso-8859-1",
        "delimiter": ";"
    }
)

# Verify new data is loaded
status = agent.get_system_status()
cache_info = status.get('data_status', {}).get('cache_info', {})
print(f"Cached data sources: {list(cache_info.get('suppliers', {}).keys())}")
```

## Plugin Development Examples

### Example 11: Simple Custom Plugin

```python
from agents.plugins.base import CompliancePlugin
from agents.core.data_models import PluginResult

class SimpleQualityPlugin(CompliancePlugin):
    """Example plugin that scores based on country reputation."""
    
    # Define quality scores by country
    COUNTRY_QUALITY_SCORES = {
        "Netherlands": 0.95,
        "Germany": 0.90,
        "Switzerland": 0.95,
        "USA": 0.85,
        "China": 0.70,
        "India": 0.65,
    }
    
    @property
    def name(self) -> str:
        return "country_quality"
    
    @property
    def weight_default(self) -> float:
        return 0.15
    
    @property
    def required_data_fields(self) -> List[str]:
        return ["country"]
    
    def check_compliance(self, supplier_data, customer_requirements, user_filters):
        country = supplier_data.country
        quality_score = self.COUNTRY_QUALITY_SCORES.get(country, 0.5)
        
        if quality_score >= 0.8:
            reasoning = f"High quality manufacturing in {country}"
        elif quality_score >= 0.6:
            reasoning = f"Acceptable quality standards in {country}"
        else:
            reasoning = f"Quality concerns for manufacturing in {country}"
        
        return PluginResult(
            plugin_name=self.name,
            score=quality_score,
            confidence=0.8,
            reasoning=reasoning,
            blocking_issues=[],
        )

# Register and test the plugin
agent = EnhancedComplianceAgent()
agent.enhanced_engine.register_plugin(SimpleQualityPlugin())

result = agent.check_compliance_enhanced("DSM", "PharmaCorp")
print(f"With custom plugin: {result.overall_score:.3f}")
```

### Example 12: Advanced Plugin with User Filters

```python
from typing import List, Dict, Any
from agents.plugins.base import CompliancePlugin
from agents.core.data_models import PluginResult

class AdvancedPricingPlugin(CompliancePlugin):
    """Advanced pricing plugin that uses user filters and market data."""
    
    @property
    def name(self) -> str:
        return "advanced_pricing"
    
    @property
    def weight_default(self) -> float:
        return 0.3
    
    @property
    def required_data_fields(self) -> List[str]:
        return ["pricing"]
    
    def check_compliance(self, supplier_data, customer_requirements, user_filters):
        if not supplier_data.pricing:
            return PluginResult(
                plugin_name=self.name,
                score=0.0,
                confidence=0.0,
                reasoning="No pricing data available",
                blocking_issues=[],
            )
        
        pricing = supplier_data.pricing
        avg_price = (pricing.min_price + pricing.max_price) / 2
        
        # Use user filters if provided
        max_budget = user_filters.get("max_budget")
        preferred_currency = user_filters.get("preferred_currency", "USD")
        volume_discount_threshold = user_filters.get("volume_threshold", 1000)
        
        blocking_issues = []
        
        # Check budget constraint
        if max_budget and avg_price > max_budget:
            blocking_issues.append(f"Price ${avg_price:.2f} exceeds budget ${max_budget:.2f}")
            score = 0.0
        else:
            # Score based on competitiveness
            if avg_price <= 40:
                score = 1.0
            elif avg_price <= 60:
                score = 0.8
            else:
                score = 0.5
        
        # Currency preference bonus
        if pricing.currency == preferred_currency:
            score = min(1.0, score + 0.1)
        
        # Volume discount consideration
        if pricing.moq <= volume_discount_threshold:
            score = min(1.0, score + 0.05)
        
        reasoning_parts = [
            f"Avg price: ${avg_price:.2f} {pricing.currency}",
            f"MOQ: {pricing.moq} units"
        ]
        
        if max_budget:
            reasoning_parts.append(f"Budget: ${max_budget:.2f}")
        
        return PluginResult(
            plugin_name=self.name,
            score=score,
            confidence=0.9,
            reasoning=" | ".join(reasoning_parts),
            blocking_issues=blocking_issues,
        )

# Use the plugin with user filters
agent = EnhancedComplianceAgent()
agent.enhanced_engine.register_plugin(AdvancedPricingPlugin())

# Test with user constraints
result = agent.check_compliance_enhanced(
    "DSM",
    "PharmaCorp", 
    user_filters={
        "max_budget": 50.0,
        "preferred_currency": "USD",
        "volume_threshold": 500
    }
)

for plugin_result in result.plugin_results:
    if plugin_result.plugin_name == "advanced_pricing":
        print(f"Advanced pricing score: {plugin_result.score:.3f}")
        print(f"Reasoning: {plugin_result.reasoning}")
```

## Data Source Examples

### Example 13: Custom CSV Format

```python
from pathlib import Path
from typing import List, Dict, Any, Optional
from agents.data_sources.base import DataSourceAdapter
from agents.core.data_models import SupplierData, Certificate
import csv
from datetime import datetime

class CustomCSVAdapter(DataSourceAdapter):
    """Adapter for a custom CSV format."""
    
    @property
    def source_type(self) -> str:
        return "custom_csv"
    
    @property
    def supports_suppliers(self) -> bool:
        return True
    
    @property
    def supports_customers(self) -> bool:
        return False
    
    def load_suppliers(self, source_path: Path, config: Optional[Dict[str, Any]] = None) -> List[SupplierData]:
        suppliers = []
        
        with open(source_path, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Custom field mapping
                name = row['company_name']
                country = row['location']
                
                # Parse custom certificate format
                certs = []
                if row.get('certifications'):
                    for cert_code in row['certifications'].split('|'):
                        cert_name = self._decode_cert(cert_code.strip())
                        if cert_name:
                            certs.append(Certificate(
                                name=cert_name,
                                issuer="Unknown",
                                valid_until=datetime(2030, 12, 31)
                            ))
                
                supplier = SupplierData(
                    name=name,
                    country=country,
                    certificates=certs,
                    data_sources=[f"custom_csv:{source_path.name}"],
                    last_updated=datetime.now()
                )
                
                suppliers.append(supplier)
        
        return suppliers
    
    def _decode_cert(self, cert_code: str) -> str:
        """Decode custom certificate codes."""
        cert_map = {
            "ISO9": "ISO 9001",
            "CGMP": "cGMP",
            "FDA": "FDA Registered",
            "HACCP": "HACCP"
        }
        return cert_map.get(cert_code, cert_code)
    
    def load_customer_requirements(self, source_path: Path, config: Optional[Dict[str, Any]] = None):
        raise NotImplementedError("Custom CSV adapter only supports suppliers")

# Register and use the custom adapter
from agents.data_sources.manager import MultiSourceDataManager

manager = MultiSourceDataManager()
manager.add_adapter("custom_csv", CustomCSVAdapter())

# Load data with custom adapter
suppliers = manager.load_suppliers_from_source(
    "data/custom_format.csv",
    source_type="custom_csv"
)

print(f"Loaded {len(suppliers)} suppliers from custom format")
```

## Error Handling Examples

### Example 14: Graceful Error Handling

```python
from agents.enhanced_compliance_agent import EnhancedComplianceAgent

def safe_compliance_check(supplier, customer):
    """Demonstrate robust error handling."""
    
    try:
        # Try enhanced mode first
        agent = EnhancedComplianceAgent(use_enhanced_mode=True, legacy_fallback=True)
        result = agent.check_compliance(supplier, customer)
        return result, "enhanced"
        
    except FileNotFoundError as e:
        print(f"Data file not found: {e}")
        
        # Try with legacy mode only
        try:
            agent = EnhancedComplianceAgent(use_enhanced_mode=False)
            result = agent.check_compliance(supplier, customer)
            return result, "legacy"
        except Exception as e:
            print(f"Legacy mode also failed: {e}")
            return None, "failed"
    
    except ValueError as e:
        print(f"Invalid supplier or customer: {e}")
        return None, "invalid_input"
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, "error"

# Test with various inputs
test_cases = [
    ("DSM", "PharmaCorp"),           # Should work
    ("Unknown", "PharmaCorp"),       # May work with lower confidence
    ("DSM", "UnknownCustomer"),      # Should fail gracefully
]

for supplier, customer in test_cases:
    print(f"\nTesting {supplier} -> {customer}:")
    result, mode = safe_compliance_check(supplier, customer)
    
    if result:
        print(f"✅ Success ({mode}): {result.compliance_status}")
    else:
        print(f"❌ Failed ({mode})")
```

### Example 15: Plugin Error Isolation

```python
from agents.plugins.base import CompliancePlugin
from agents.core.data_models import PluginResult

class BuggyPlugin(CompliancePlugin):
    """Example plugin that demonstrates error handling."""
    
    @property
    def name(self) -> str:
        return "buggy_example"
    
    @property
    def weight_default(self) -> float:
        return 0.1
    
    @property
    def required_data_fields(self):
        return ["certificates"]
    
    def check_compliance(self, supplier_data, customer_requirements, user_filters):
        try:
            # Simulate a calculation that might fail
            if supplier_data.name == "ERROR_TEST":
                raise ValueError("Simulated plugin error")
            
            # Normal processing
            score = 0.8
            return PluginResult(
                plugin_name=self.name,
                score=score,
                confidence=0.7,
                reasoning="Normal plugin execution",
            )
            
        except Exception as e:
            # Plugin should handle its own errors gracefully
            return PluginResult(
                plugin_name=self.name,
                score=0.0,
                confidence=0.0,
                reasoning=f"Plugin error: {str(e)}",
                blocking_issues=[f"Plugin calculation failed: {str(e)}"],
            )

# Test error isolation
agent = EnhancedComplianceAgent()
agent.enhanced_engine.register_plugin(BuggyPlugin())

# This should work despite the buggy plugin
result1 = agent.check_compliance_enhanced("DSM", "PharmaCorp")
print(f"Normal case with buggy plugin: {result1.overall_score:.3f}")

# This should handle the plugin error gracefully
result2 = agent.check_compliance_enhanced("ERROR_TEST", "PharmaCorp")
print(f"Error case with buggy plugin: {result2.overall_score:.3f}")

# Check if the error was captured
for plugin_result in result2.plugin_results:
    if plugin_result.plugin_name == "buggy_example":
        print(f"Plugin error captured: {plugin_result.reasoning}")
```

## Performance Examples

### Example 16: Caching and Performance

```python
from agents.enhanced_compliance_agent import EnhancedComplianceAgent
import time

# Create agent with caching enabled
agent = EnhancedComplianceAgent()

# First run - loads data and caches it
start_time = time.time()
result1 = agent.check_compliance_enhanced("DSM", "PharmaCorp")
first_run_time = time.time() - start_time

print(f"First run: {first_run_time:.3f} seconds")
print(f"Score: {result1.overall_score:.3f}")

# Second run - should use cached data
start_time = time.time()
result2 = agent.check_compliance_enhanced("BASF", "PharmaCorp") 
second_run_time = time.time() - start_time

print(f"Second run: {second_run_time:.3f} seconds")
print(f"Score: {result2.overall_score:.3f}")

# Check cache status
cache_info = agent.get_system_status()['data_status']['cache_info']
print(f"\nCache status:")
for source, info in cache_info['suppliers'].items():
    print(f"  {source}: {info['count']} records, age: {info['age_seconds']:.1f}s")

# Clear cache and test performance difference
agent.clear_caches()

start_time = time.time()
result3 = agent.check_compliance_enhanced("DSM", "PharmaCorp")
third_run_time = time.time() - start_time

print(f"\nAfter cache clear: {third_run_time:.3f} seconds")
print(f"Performance improvement: {(first_run_time - second_run_time) / first_run_time * 100:.1f}%")
```

### Example 17: Batch Processing Optimization

```python
from agents.enhanced_compliance_agent import EnhancedComplianceAgent
import time

agent = EnhancedComplianceAgent()

# Define test data
suppliers = ["DSM", "BASF", "Prinova USA", "Unknown1", "Unknown2"]
customers = ["PharmaCorp", "FoodSupplementCo", "Cosmetics Inc"]

# Method 1: Individual checks (less efficient)
print("Method 1: Individual compliance checks")
start_time = time.time()

individual_results = {}
for customer in customers:
    for supplier in suppliers:
        try:
            result = agent.check_compliance_enhanced(supplier, customer)
            individual_results[(supplier, customer)] = result.overall_score
        except Exception as e:
            individual_results[(supplier, customer)] = 0.0

individual_time = time.time() - start_time
print(f"Individual checks: {individual_time:.3f} seconds")

# Method 2: Batch processing (more efficient)
print("\nMethod 2: Batch processing")
start_time = time.time()

batch_results = {}
for customer in customers:
    results = agent.batch_analyze_suppliers(suppliers, customer)
    for supplier, result in results.items():
        batch_results[(supplier, customer)] = result.overall_score

batch_time = time.time() - start_time
print(f"Batch processing: {batch_time:.3f} seconds")

# Method 3: Ranking (most efficient for comparison)
print("\nMethod 3: Ranking approach")
start_time = time.time()

ranking_results = {}
for customer in customers:
    rankings = agent.rank_suppliers(customer, supplier_names=suppliers)
    for i, (supplier, result) in enumerate(rankings):
        ranking_results[(supplier, customer)] = result.overall_score

ranking_time = time.time() - start_time
print(f"Ranking approach: {ranking_time:.3f} seconds")

# Compare results and performance
print(f"\nPerformance comparison:")
print(f"  Individual: {individual_time:.3f}s (baseline)")
print(f"  Batch: {batch_time:.3f}s ({batch_time/individual_time:.1f}x)")
print(f"  Ranking: {ranking_time:.3f}s ({ranking_time/individual_time:.1f}x)")
```

### Example 18: Memory Usage Optimization

```python
from agents.enhanced_compliance_agent import EnhancedComplianceAgent
import sys

def get_memory_usage():
    """Simple memory usage estimation."""
    import gc
    gc.collect()
    return sum(sys.getsizeof(obj) for obj in gc.get_objects()) / 1024 / 1024  # MB

# Test memory usage with different configurations
print("Memory Usage Analysis:")

# Baseline
baseline_memory = get_memory_usage()
print(f"Baseline memory: {baseline_memory:.1f} MB")

# Create agent with caching
agent = EnhancedComplianceAgent()
after_agent_memory = get_memory_usage()
print(f"After agent creation: {after_agent_memory:.1f} MB (+{after_agent_memory-baseline_memory:.1f} MB)")

# Load data
agent.check_compliance_enhanced("DSM", "PharmaCorp")
after_data_memory = get_memory_usage()
print(f"After data loading: {after_data_memory:.1f} MB (+{after_data_memory-after_agent_memory:.1f} MB)")

# Process multiple suppliers
for supplier in ["BASF", "Prinova USA"]:
    agent.check_compliance_enhanced(supplier, "PharmaCorp")

after_processing_memory = get_memory_usage()
print(f"After processing: {after_processing_memory:.1f} MB (+{after_processing_memory-after_data_memory:.1f} MB)")

# Clear caches
agent.clear_caches()
after_clear_memory = get_memory_usage()
print(f"After cache clear: {after_clear_memory:.1f} MB ({after_clear_memory-after_processing_memory:+.1f} MB)")

print(f"\nMemory efficiency:")
print(f"  Data overhead: {after_data_memory - after_agent_memory:.1f} MB")
print(f"  Processing overhead: {after_processing_memory - after_data_memory:.1f} MB")
print(f"  Cache savings: {after_processing_memory - after_clear_memory:.1f} MB")
```

These examples demonstrate the full range of capabilities of the Enhanced Compliance Agent, from basic usage to advanced configuration and optimization techniques. Use them as a starting point for your own implementations and customizations.