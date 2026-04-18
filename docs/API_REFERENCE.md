# API Reference

Complete API reference for the Enhanced Compliance Agent.

## Core Classes

### EnhancedComplianceAgent

Main interface for enhanced compliance checking.

#### Constructor

```python
EnhancedComplianceAgent(
    data_sources: Optional[List[Dict[str, Any]]] = None,
    scoring_config: Optional[ScoringConfig] = None,
    use_enhanced_mode: Optional[bool] = None,
    legacy_fallback: bool = True,
)
```

**Parameters:**
- `data_sources`: List of data source configurations
- `scoring_config`: Scoring configuration for enhanced mode
- `use_enhanced_mode`: Force enhanced (True) or legacy (False) mode. Auto-detects if None.
- `legacy_fallback`: Whether to fall back to legacy mode on errors

#### Methods

##### check_compliance()

```python
check_compliance(
    supplier: str,
    customer: str,
    material: Optional[str] = None,
) -> ComplianceAgentOutput
```

Backward compatible compliance check.

**Parameters:**
- `supplier`: Supplier name (e.g., "DSM")
- `customer`: Customer name (e.g., "PharmaCorp") 
- `material`: Material name (optional, for compatibility)

**Returns:** `ComplianceAgentOutput`

**Example:**
```python
result = agent.check_compliance("DSM", "PharmaCorp", "Vitamin D3")
print(f"Status: {result.compliance_status}")
```

##### check_compliance_enhanced()

```python
check_compliance_enhanced(
    supplier: Union[str, SupplierData],
    customer_requirements: Union[str, CustomerRequirements],
    user_filters: Optional[Dict[str, Any]] = None,
    selected_plugins: Optional[List[str]] = None,
) -> ComplianceResult
```

Enhanced compliance check with full feature access.

**Parameters:**
- `supplier`: Supplier name or SupplierData object
- `customer_requirements`: Customer name or CustomerRequirements object
- `user_filters`: Additional user-specified filters or parameters
- `selected_plugins`: List of plugin names to run (all if None)

**Returns:** `ComplianceResult`

**Example:**
```python
result = agent.check_compliance_enhanced(
    "DSM", 
    "PharmaCorp",
    user_filters={"max_price": 50.0},
    selected_plugins=["certificates", "pricing"]
)
```

##### rank_suppliers()

```python
rank_suppliers(
    customer: Union[str, CustomerRequirements],
    supplier_names: Optional[List[str]] = None,
    user_filters: Optional[Dict[str, Any]] = None,
    sort_by: str = "score",
    limit: Optional[int] = None,
) -> List[tuple[str, ComplianceResult]]
```

Rank suppliers for a customer using enhanced mode.

**Parameters:**
- `customer`: Customer name or CustomerRequirements object
- `supplier_names`: List of supplier names to consider (all loaded if None)
- `user_filters`: Additional user-specified filters or parameters
- `sort_by`: Sorting criteria ("score", "confidence", "score_confidence")
- `limit`: Maximum number of results to return (all if None)

**Returns:** List of (supplier_name, ComplianceResult) tuples

**Example:**
```python
rankings = agent.rank_suppliers(
    "PharmaCorp",
    supplier_names=["DSM", "BASF", "Prinova USA"],
    sort_by="score",
    limit=3
)
```

##### configure_scoring()

```python
configure_scoring(
    plugin_weights: Optional[Dict[str, float]] = None,
    aggregation_method: str = "weighted_average",
    confidence_penalty_factor: float = 0.2,
) -> None
```

Configure the scoring system (enhanced mode only).

**Parameters:**
- `plugin_weights`: Dictionary of plugin names to weights
- `aggregation_method`: How to combine plugin scores
- `confidence_penalty_factor`: How much to penalize low confidence

**Example:**
```python
agent.configure_scoring(
    plugin_weights={"certificates": 0.6, "pricing": 0.4},
    aggregation_method="weighted_average",
    confidence_penalty_factor=0.1
)
```

##### add_data_source()

```python
add_data_source(
    source_path: Union[str, Path],
    source_type: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> None
```

Add a new data source to the enhanced mode.

##### get_system_status()

```python
get_system_status() -> Dict[str, Any]
```

Get comprehensive system status for debugging.

**Returns:** Dictionary with system status information

##### clear_caches()

```python
clear_caches() -> None
```

Clear all internal caches.

## Data Models

### ComplianceResult

Enhanced compliance analysis result.

#### Attributes

- **`overall_score: float`** - Overall compliance score (0.0-1.0)
- **`overall_confidence: float`** - Confidence in assessment (0.0-1.0)  
- **`plugin_results: List[PluginResult]`** - Results from individual plugins
- **`reasoning_chain: List[str]`** - Ordered list of reasoning steps
- **`data_gaps: List[str]`** - List of missing or unavailable data points
- **`recommendations: List[str]`** - Suggested actions or improvements

### PluginResult

Result from a compliance plugin analysis.

#### Attributes

- **`plugin_name: str`** - Name of the plugin that generated this result
- **`score: float`** - Compliance score for this aspect (0.0-1.0)
- **`confidence: float`** - Confidence level in the score (0.0-1.0)
- **`reasoning: str`** - Human-readable explanation of the score
- **`blocking_issues: List[str]`** - List of critical issues that block compliance

### SupplierData

Complete supplier information for compliance analysis.

#### Attributes

- **`name: str`** - Supplier company name
- **`country: str`** - Supplier's country of operation
- **`certificates: List[Certificate]`** - List of certifications held
- **`pricing: Optional[PricingInfo]`** - Pricing information
- **`quality_metrics: Optional[Dict[str, Any]]`** - Quality performance metrics
- **`delivery_info: Optional[Dict[str, Any]]`** - Delivery capabilities and terms
- **`data_sources: List[str]`** - List of sources where data was gathered
- **`confidence_breakdown: Dict[str, float]`** - Confidence scores for different data aspects
- **`last_updated: Optional[datetime]`** - Timestamp of last data update

### CustomerRequirements

Customer requirements for supplier compliance.

#### Attributes

- **`company_name: str`** - Name of the customer company
- **`quality_tier: str`** - Desired quality tier (e.g., "premium", "standard")
- **`certificates_required: List[str]`** - List of required certifications
- **`constraints: Dict[str, Any]`** - Dictionary of specific constraints and limits

### Certificate

Represents a certification held by a supplier.

#### Attributes

- **`name: str`** - Name of the certificate (e.g., "ISO 9001")
- **`issuer: str`** - Organization that issued the certificate
- **`valid_until: datetime`** - Expiration date of the certificate

### PricingInfo

Represents pricing information for a supplier's products.

#### Attributes

- **`min_price: float`** - Minimum unit price
- **`max_price: float`** - Maximum unit price
- **`currency: str`** - Currency code (e.g., "USD", "EUR")
- **`moq: int`** - Minimum order quantity

### ComplianceAgentOutput

Legacy format compliance result (for backward compatibility).

#### Attributes

- **`compliance_status: str`** - "COMPLIANT", "NON_COMPLIANT", or "INSUFFICIENT_DATA"
- **`confidence: float`** - Confidence level (0.0-1.0)
- **`reasoning: str`** - Human-readable summary
- **`issues: List[Dict]`** - Details about any issues
- **`synergy_potential: float`** - % savings from consolidation

## Scoring Configuration

### ScoringConfig

Configuration for the scoring engine.

#### Attributes

- **`weights: List[ScoringWeight]`** - List of plugin weights and configurations
- **`aggregation_method: str`** - How to combine plugin scores
- **`confidence_penalty_factor: float`** - How much to penalize low confidence
- **`blocking_issue_penalty: float`** - Score assigned when blocking issues are present
- **`normalize_final_score: bool`** - Whether to normalize final score to 0.0-1.0 range

#### Methods

##### get_weight_for_plugin()

```python
get_weight_for_plugin(plugin_name: str) -> Optional[ScoringWeight]
```

Get the weight configuration for a specific plugin.

##### is_plugin_enabled()

```python
is_plugin_enabled(plugin_name: str) -> bool
```

Check if a plugin is enabled for scoring.

### ScoringWeight

Configuration for a plugin's weight in the overall score.

#### Attributes

- **`plugin_name: str`** - Name of the plugin this weight applies to
- **`weight: float`** - Numeric weight (typically 0.0-1.0, but can be higher)
- **`enabled: bool`** - Whether this plugin contributes to the score
- **`min_confidence: float`** - Minimum confidence required to include this result

## Plugins

### CompliancePlugin

Abstract base class for all compliance plugins.

#### Abstract Properties

##### name

```python
@property
@abstractmethod
def name(self) -> str
```

The unique name of this plugin.

##### weight_default

```python
@property
@abstractmethod  
def weight_default(self) -> float
```

Default weight for this plugin in compliance score aggregation.

##### required_data_fields

```python
@property
@abstractmethod
def required_data_fields(self) -> List[str]
```

List of supplier data fields required by this plugin.

#### Abstract Methods

##### check_compliance()

```python
@abstractmethod
def check_compliance(
    self,
    supplier_data: SupplierData,
    customer_requirements: CustomerRequirements,
    user_filters: Dict[str, Any],
) -> PluginResult
```

Analyze supplier compliance for a specific aspect.

## Data Source Adapters

### DataSourceAdapter

Abstract base class for all data source adapters.

#### Abstract Properties

##### source_type

```python
@property
@abstractmethod
def source_type(self) -> str
```

Type identifier for this data source.

##### supports_suppliers

```python
@property
@abstractmethod
def supports_suppliers(self) -> bool
```

Whether this adapter can load supplier data.

##### supports_customers

```python
@property
@abstractmethod
def supports_customers(self) -> bool
```

Whether this adapter can load customer requirements.

#### Abstract Methods

##### load_suppliers()

```python
@abstractmethod
def load_suppliers(
    self,
    source_path: Path,
    config: Optional[Dict[str, Any]] = None
) -> List[SupplierData]
```

Load supplier data from the source.

##### load_customer_requirements()

```python
@abstractmethod
def load_customer_requirements(
    self,
    source_path: Path,
    config: Optional[Dict[str, Any]] = None
) -> List[CustomerRequirements]
```

Load customer requirements from the source.

## Engine Classes

### ComplianceEngine

Main engine for comprehensive compliance analysis.

#### Methods

##### register_plugin()

```python
register_plugin(plugin: CompliancePlugin) -> None
```

Register a compliance plugin.

##### analyze_supplier_compliance()

```python
analyze_supplier_compliance(
    self,
    supplier: Union[str, SupplierData],
    customer_requirements: Union[str, CustomerRequirements],
    user_filters: Optional[Dict[str, Any]] = None,
    selected_plugins: Optional[List[str]] = None,
) -> ComplianceResult
```

Analyze compliance for a supplier against customer requirements.

### ScoringEngine  

Engine for scoring and prioritizing compliance results.

#### Methods

##### calculate_compliance_score()

```python
calculate_compliance_score(
    self,
    plugin_results: List[PluginResult]
) -> ComplianceResult
```

Calculate overall compliance score from plugin results.

##### rank_suppliers()

```python
rank_suppliers(
    self,
    compliance_results: List[tuple[str, ComplianceResult]],
    sort_by: str = "score"
) -> List[tuple[str, ComplianceResult]]
```

Rank suppliers by compliance score or other criteria.

## Utility Functions

### call_compliance_agent()

```python
call_compliance_agent(
    material: str,
    supplier: str,
    customer: str = "FoodSupplementCo",
) -> ComplianceAgentOutput
```

Convenience function that maintains exact backward compatibility with the original SimpleComplianceChecker.

### setup_integration()

```python
setup_integration(
    data_dir: Optional[str] = None,
    custom_scoring: Optional[Dict[str, float]] = None
) -> EnhancedComplianceAgent
```

Convenience function to set up enhanced compliance agent with existing data.

### run_integration_validation()

```python
run_integration_validation(data_dir: Optional[str] = None) -> None
```

Run complete integration validation and print report.

## Error Handling

The Enhanced Compliance Agent is designed to handle errors gracefully:

### Common Exceptions

- **`ValueError`**: Raised when supplier or customer not found, or invalid configuration
- **`FileNotFoundError`**: Raised when data source files are missing
- **`RuntimeError`**: Raised when enhanced mode is not available for enhanced-only methods

### Error Recovery

The system includes multiple fallback mechanisms:

1. **Legacy Fallback**: Falls back to SimpleComplianceChecker when enhanced mode unavailable
2. **Plugin Isolation**: Plugin errors don't crash the entire system
3. **Graceful Degradation**: Missing data sources result in lower confidence rather than failures
4. **Cache Recovery**: Cache failures result in fresh data loading rather than errors

### Debugging

Use `get_system_status()` to debug configuration and data loading issues:

```python
status = agent.get_system_status()
print(f"Mode: {status['mode']}")
print(f"Data loaded: {status['data_status']}")
print(f"Plugin status: {status['plugin_status']}")
```