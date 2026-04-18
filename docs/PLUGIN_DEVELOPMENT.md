# Plugin Development Guide

This guide explains how to create custom compliance plugins for the Enhanced Compliance Agent.

## Plugin Architecture Overview

Plugins are modular components that analyze specific aspects of supplier compliance. Each plugin:

- Implements the `CompliancePlugin` abstract interface
- Receives supplier data and customer requirements  
- Returns a scored result with reasoning and confidence
- Can declare data dependencies and default weights

## Creating a Plugin

### 1. Basic Plugin Structure

```python
from typing import List, Dict, Any
from agents.plugins.base import CompliancePlugin
from agents.core.data_models import (
    SupplierData,
    CustomerRequirements, 
    PluginResult
)

class MyCustomPlugin(CompliancePlugin):
    @property
    def name(self) -> str:
        """Unique plugin name."""
        return "my_custom"
    
    @property
    def weight_default(self) -> float:
        """Default weight in aggregated scoring (0.0-1.0)."""
        return 0.2
    
    @property
    def required_data_fields(self) -> List[str]:
        """List of required SupplierData fields."""
        return ["certificates", "country"]
    
    def check_compliance(
        self,
        supplier_data: SupplierData,
        customer_requirements: CustomerRequirements,
        user_filters: Dict[str, Any],
    ) -> PluginResult:
        """Main compliance checking logic."""
        
        # Your compliance logic here
        score = self._calculate_score(supplier_data, customer_requirements)
        confidence = self._calculate_confidence(supplier_data)
        reasoning = self._generate_reasoning(score, supplier_data)
        blocking_issues = self._check_blocking_issues(supplier_data)
        
        return PluginResult(
            plugin_name=self.name,
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            blocking_issues=blocking_issues,
        )
```

### 2. Implementation Examples

#### Example 1: Geographic Compliance Plugin

```python
class GeographicCompliancePlugin(CompliancePlugin):
    """Check if supplier is from an allowed geographic region."""
    
    # Allowed countries by customer tier
    ALLOWED_COUNTRIES = {
        "PHARMA_GRADE": {"Netherlands", "Germany", "USA", "Switzerland"},
        "SUPPLEMENT_GRADE": {"Netherlands", "Germany", "USA", "Switzerland", "China", "India"},
        "COSMETIC_GRADE": set(),  # All countries allowed
    }
    
    @property
    def name(self) -> str:
        return "geographic"
    
    @property
    def weight_default(self) -> float:
        return 0.15
    
    @property 
    def required_data_fields(self) -> List[str]:
        return ["country"]
    
    def check_compliance(self, supplier_data, customer_requirements, user_filters):
        customer_tier = customer_requirements.quality_tier
        supplier_country = supplier_data.country
        
        # Check if country restrictions apply
        allowed_countries = self.ALLOWED_COUNTRIES.get(customer_tier, set())
        
        if not allowed_countries:  # No restrictions
            score = 1.0
            reasoning = f"No geographic restrictions for {customer_tier}"
            blocking_issues = []
        elif supplier_country in allowed_countries:
            score = 1.0  
            reasoning = f"Supplier from {supplier_country} is approved for {customer_tier}"
            blocking_issues = []
        else:
            score = 0.0
            reasoning = f"Supplier from {supplier_country} not approved for {customer_tier}"
            blocking_issues = [f"Country {supplier_country} not allowed for {customer_tier}"]
        
        return PluginResult(
            plugin_name=self.name,
            score=score,
            confidence=0.95,  # High confidence in geographic data
            reasoning=reasoning,
            blocking_issues=blocking_issues,
        )
```

#### Example 2: Pricing Competitiveness Plugin

```python
class PricingPlugin(CompliancePlugin):
    """Evaluate pricing competitiveness and value."""
    
    @property
    def name(self) -> str:
        return "pricing"
    
    @property
    def weight_default(self) -> float:
        return 0.25
    
    @property
    def required_data_fields(self) -> List[str]:
        return ["pricing"]
    
    def check_compliance(self, supplier_data, customer_requirements, user_filters):
        if not supplier_data.pricing:
            return PluginResult(
                plugin_name=self.name,
                score=0.5,  # Neutral score for missing data
                confidence=0.0,
                reasoning="No pricing information available",
                blocking_issues=[],
            )
        
        pricing = supplier_data.pricing
        
        # Price competitiveness scoring (simplified example)
        avg_price = (pricing.min_price + pricing.max_price) / 2
        
        # Define competitive ranges by tier
        competitive_ranges = {
            "PHARMA_GRADE": (40, 60),
            "SUPPLEMENT_GRADE": (30, 50), 
            "COSMETIC_GRADE": (20, 40),
        }
        
        tier = customer_requirements.quality_tier
        min_competitive, max_competitive = competitive_ranges.get(tier, (0, 100))
        
        if avg_price <= max_competitive:
            if avg_price >= min_competitive:
                score = 1.0 - (avg_price - min_competitive) / (max_competitive - min_competitive) * 0.3
                reasoning = f"Competitive pricing: ${avg_price:.2f} (range: ${min_competitive}-{max_competitive})"
            else:
                score = 1.0
                reasoning = f"Excellent pricing: ${avg_price:.2f} below competitive range"
        else:
            score = max(0.0, 1.0 - (avg_price - max_competitive) / max_competitive)
            reasoning = f"Above competitive range: ${avg_price:.2f} (max: ${max_competitive})"
        
        return PluginResult(
            plugin_name=self.name,
            score=score,
            confidence=0.8,
            reasoning=reasoning,
            blocking_issues=[],
        )
```

### 3. Advanced Plugin Features

#### Using User Filters

```python
def check_compliance(self, supplier_data, customer_requirements, user_filters):
    # Access user-provided filters
    max_price_override = user_filters.get("max_price")
    preferred_countries = user_filters.get("preferred_countries", [])
    
    # Use filters in your logic
    if max_price_override and supplier_data.pricing:
        if supplier_data.pricing.max_price > max_price_override:
            return PluginResult(
                plugin_name=self.name,
                score=0.0,
                confidence=1.0,
                reasoning=f"Price ${supplier_data.pricing.max_price} exceeds user limit ${max_price_override}",
                blocking_issues=[f"Price exceeds user limit of ${max_price_override}"],
            )
```

#### Confidence Scoring

```python
def _calculate_confidence(self, supplier_data: SupplierData) -> float:
    """Calculate confidence based on data quality."""
    confidence_factors = []
    
    # Data source confidence
    source_confidence = supplier_data.confidence_breakdown.get("data_source", 0.5)
    confidence_factors.append(source_confidence)
    
    # Data completeness
    required_fields = ["certificates", "country", "pricing"]
    complete_fields = sum(1 for field in required_fields 
                         if getattr(supplier_data, field) is not None)
    completeness = complete_fields / len(required_fields)
    confidence_factors.append(completeness)
    
    # Data freshness
    if supplier_data.last_updated:
        age_days = (datetime.now() - supplier_data.last_updated).days
        freshness = max(0.0, 1.0 - age_days / 365)  # Decay over a year
        confidence_factors.append(freshness)
    
    return sum(confidence_factors) / len(confidence_factors)
```

## Plugin Registration

### Manual Registration

```python
from agents.engine.compliance_engine import ComplianceEngine

engine = ComplianceEngine()
engine.register_plugin(MyCustomPlugin())
```

### Automatic Registration via Enhanced Agent

```python
from agents.enhanced_compliance_agent import EnhancedComplianceAgent

agent = EnhancedComplianceAgent()
agent.enhanced_engine.register_plugin(MyCustomPlugin())
```

## Testing Plugins

### Unit Testing

```python
import unittest
from datetime import datetime
from agents.core.data_models import SupplierData, CustomerRequirements, Certificate

class TestMyCustomPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = MyCustomPlugin()
        
        self.supplier_data = SupplierData(
            name="Test Supplier",
            country="Netherlands",
            certificates=[
                Certificate("ISO 9001", "TUV SUD", datetime(2025, 12, 31))
            ]
        )
        
        self.customer_requirements = CustomerRequirements(
            company_name="Test Customer",
            quality_tier="PHARMA_GRADE",
            certificates_required=["ISO 9001"]
        )
    
    def test_compliant_supplier(self):
        result = self.plugin.check_compliance(
            self.supplier_data,
            self.customer_requirements,
            {}
        )
        
        self.assertEqual(result.plugin_name, "my_custom")
        self.assertGreater(result.score, 0.7)
        self.assertGreater(result.confidence, 0.0)
        self.assertIsInstance(result.reasoning, str)
        self.assertIsInstance(result.blocking_issues, list)
```

### Integration Testing

```python
def test_plugin_integration():
    """Test plugin works within the full system."""
    from agents.enhanced_compliance_agent import EnhancedComplianceAgent
    
    agent = EnhancedComplianceAgent()
    agent.enhanced_engine.register_plugin(MyCustomPlugin())
    
    result = agent.check_compliance_enhanced("DSM", "PharmaCorp")
    
    # Check that our plugin contributed to the result
    plugin_names = [pr.plugin_name for pr in result.plugin_results]
    assert "my_custom" in plugin_names
```

## Best Practices

### 1. Error Handling

```python
def check_compliance(self, supplier_data, customer_requirements, user_filters):
    try:
        # Your compliance logic
        score = self._calculate_score(supplier_data)
        
        return PluginResult(
            plugin_name=self.name,
            score=score,
            confidence=0.8,
            reasoning="Calculation completed successfully",
        )
        
    except Exception as e:
        # Graceful error handling
        return PluginResult(
            plugin_name=self.name,
            score=0.0,
            confidence=0.0,
            reasoning=f"Plugin error: {str(e)}",
            blocking_issues=[f"Plugin calculation failed: {str(e)}"],
        )
```

### 2. Data Validation

```python
def check_compliance(self, supplier_data, customer_requirements, user_filters):
    # Validate required data is present
    missing_fields = []
    for field in self.required_data_fields:
        if not getattr(supplier_data, field):
            missing_fields.append(field)
    
    if missing_fields:
        return PluginResult(
            plugin_name=self.name,
            score=0.0,
            confidence=0.0,
            reasoning=f"Missing required data: {', '.join(missing_fields)}",
            blocking_issues=[],
        )
```

### 3. Configurable Behavior

```python
class ConfigurablePlugin(CompliancePlugin):
    def __init__(self, strict_mode: bool = False, weight_override: float = None):
        self.strict_mode = strict_mode
        self._weight_override = weight_override
    
    @property
    def weight_default(self) -> float:
        return self._weight_override or 0.3
    
    def check_compliance(self, supplier_data, customer_requirements, user_filters):
        if self.strict_mode:
            # Apply stricter scoring
            pass
        else:
            # Apply normal scoring
            pass
```

## Plugin Ideas

Here are some plugin ideas you might implement:

1. **Quality Metrics Plugin**: Score based on quality performance data
2. **Delivery Reliability Plugin**: Evaluate on-time delivery performance  
3. **Financial Stability Plugin**: Check supplier financial health
4. **Sustainability Plugin**: Score environmental and social responsibility
5. **Innovation Plugin**: Rate R&D capabilities and new product development
6. **Risk Assessment Plugin**: Evaluate supply chain and political risks
7. **Audit Results Plugin**: Score based on recent audit findings
8. **Capacity Plugin**: Check if supplier can meet volume requirements

## Contributing

When contributing a new plugin:

1. Follow the interface exactly
2. Include comprehensive tests
3. Document the scoring logic clearly
4. Consider edge cases and error handling
5. Add to the plugin registry in the appropriate location