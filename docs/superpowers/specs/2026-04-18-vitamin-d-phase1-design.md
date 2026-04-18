# Agnes Phase 1: Database-First Vitamin D Implementation

**Project:** Agnes MVP – AI Entscheidungsunterstützungssystem  
**Phase:** 1 (Fundament)  
**Demo Substance:** Vitamin D3 (Cholecalciferol)  
**Approach:** Database-First Integration  
**Timeline:** Phase 1 completion by Friday 24:00  
**Date:** 2026-04-18  

## Executive Summary

This specification defines Phase 1 implementation of Agnes using a database-first approach with vitamin D as the demo substance. We will extract real vitamin D SKUs from the existing SQLite database, perform clustering to identify fragmentation patterns, and test the Equivalence-Agent against actual industry data. This provides maximum realism for the demo while validating our assumptions about supplement industry purchasing fragmentation.

## Architecture Overview

```
┌─ PHASE 1 PIPELINE ─────────────────────────────────────────┐
│                                                            │
│ 1. SQLite DB Query    →  2. SKU Parser      →  3. Embeddings  │
│    (vitamin D filter)     (extract substance)   (cluster)     │
│                                                            │
│ 4. Real Clusters      →  5. Equivalence-Agent  →  6. Results   │
│    (grouped vitamin D)    (analyze with mocks)   (JSON)       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Core Components

1. **Database Layer**: SQLAlchemy models for existing 6-table structure
2. **Substance Extractor**: Parse SKU strings to extract vitamin D variants  
3. **Clustering Engine**: Group vitamin D SKUs across companies using embeddings
4. **Equivalence-Agent**: Existing Claude-based agent with JSON contract
5. **External Enrichment**: Cached supplier compliance data for 3 vitamin D suppliers
6. **Results Aggregator**: Collect and format agent outputs for demo

## Database Integration

### Table Structure
Working with existing SQLite schema:
- **Company** (61 rows) - Endmarken (Caltrate, Centrum, etc.)
- **Product** (1025 rows) - 149 finished-goods + 876 raw-materials  
- **BOM** + **BOM_Component** - Relationships between products
- **Supplier** + **Supplier_Product** - M:N supplier mappings

### Vitamin D Discovery Query
```sql
SELECT p.sku, p.name, c.name as company_name, s.name as supplier_name
FROM Product p
JOIN Company c ON p.company_id = c.id  
LEFT JOIN Supplier_Product sp ON p.id = sp.product_id
LEFT JOIN Supplier s ON sp.supplier_id = s.id
WHERE p.type = 'raw-material' 
AND (p.sku ILIKE '%vitamin-d%' OR p.sku ILIKE '%cholecalciferol%' OR p.sku ILIKE '%ergocalciferol%')
ORDER BY c.name, p.sku
```

**Expected Results:** 15-25 vitamin D SKUs across multiple companies demonstrating real fragmentation patterns.

### SQLAlchemy Models
```python
class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    sku = Column(String)
    name = Column(String)
    type = Column(String)  # 'raw-material' or 'finished-good'
    company_id = Column(Integer, ForeignKey('company.id'))

class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Supplier(Base):
    __tablename__ = 'supplier'
    id = Column(Integer, primary_key=True)
    name = Column(String)
```

## SKU Parsing & Substance Extraction

### SKU Pattern Analysis
Pattern: `RM-C{company_id}-{substance}-{variant}-{hash}`

Examples:
- `RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1`
- `RM-C27-cholecalciferol-powder-5000iu-bd4a1f89`
- `RM-C14-vitamin-d3-2000iu-8e9f3c42`

### Parsing Logic
```python
def parse_vitamin_d_sku(sku: str) -> Dict[str, Any]:
    """
    Extract vitamin D substance details from SKU.
    Returns: {
        "substance": "vitamin-d3",
        "chemical_name": "cholecalciferol", 
        "potency": "1000iu",
        "form": "powder|oil|standard"
    }
    """
```

### Normalization Strategy
- **Substance**: vitamin-d3/cholecalciferol/vitamin-d → "vitamin-d3"
- **Potency**: Extract IU values (1000iu, 2000iu, 5000iu)
- **Form**: powder, oil, suspension, micronized
- **Company**: Extract from C{id} pattern

## Clustering Strategy

### Primary Clustering
1. **By Substance**: All vitamin D3 variants grouped together
2. **By Potency Range**: 
   - Standard (1000-2000 IU)
   - High potency (5000+ IU)
3. **By Form**: Powder vs oil vs standard preparations

### Expected Cluster Output
```json
{
  "vitamin-d3-standard": {
    "skus": ["RM-C1-vitamin-d3-1000iu-...", "RM-C14-vitamin-d3-2000iu-..."],
    "companies": ["Nature Made", "Kirkland"],
    "suppliers": ["DSM", "BASF"],
    "potency_range": "1000-2000iu"
  },
  "vitamin-d3-high-potency": {
    "skus": ["RM-C27-vitamin-d3-5000iu-...", "RM-C33-vitamin-d3-10000iu-..."],
    "companies": ["Garden of Life", "NOW Foods"],
    "suppliers": ["DSM", "Fermenta"],
    "potency_range": "5000+ iu"
  }
}
```

This provides 2-4 distinct vitamin D clusters for testing different agent scenarios.

## Equivalence-Agent Integration

### Agent Input Format
Using existing JSON contract from project plan Section 4.1:

```python
@dataclass
class EquivalenceAgentInput:
    cluster_id: str
    skus: List[str]                    # Real vitamin D SKUs from database
    affected_companies: List[str]      # Extracted from company table
    affected_boms: List[int]          # BOMs using these SKUs
    current_suppliers: List[str]       # From supplier relationships  
    end_product_context: List[EndProductContext]  # Finished goods using vitamin D
```

### Real Data Mapping
- **cluster_id**: Generated from substance + potency (e.g., "vitamin-d3-standard-001")
- **skus**: Real SKU strings from Product table
- **affected_companies**: Company.name for each SKU
- **affected_boms**: BOM IDs from BOM_Component relationships
- **current_suppliers**: Supplier.name from Supplier_Product relationships
- **end_product_context**: Finished goods containing these vitamin D SKUs

### Claude API Integration
```python
def call_equivalence_agent(input_data: EquivalenceAgentInput, use_mock: bool = False) -> AgentOutput:
    if not use_mock:
        # Real Claude API call using Anthropic SDK
        # Format prompt with real data
        # Parse JSON response using established schema
    else:
        # Existing mock response system for development
```

## External Enrichment

### Target Suppliers
Based on project plan and industry reality:

```python
VITAMIN_D_SUPPLIERS = {
    "DSM": {
        "website": "dsm.com/human-nutrition/en/products/vitamins/vitamin-d3",
        "target_certs": ["USP", "Non-GMO", "Kosher", "Halal"],
        "specialties": ["pharmaceutical-grade", "food-grade"]
    },
    "BASF": {
        "website": "nutrition.basf.com/global/en/human-nutrition/vitamins/vitamin-d",  
        "target_certs": ["USP", "Non-GMO", "Kosher"],
        "specialties": ["synthetic", "high-purity"]
    },
    "Fermenta": {
        "website": "fermenta.com.ua/en/products/vitamins/vitamin-d3",
        "target_certs": ["GMP", "Non-GMO"],
        "specialties": ["cost-effective", "bulk-powder"]
    }
}
```

### Evidence Caching Strategy
- **Storage**: `external_evidence.json` file (no database schema changes)
- **Structure**: Nested JSON by supplier → certification type → evidence
- **Offline Capability**: All evidence pre-cached for demo reliability
- **Update Mechanism**: Manual refresh during development, not real-time

### Evidence Schema
```json
{
  "DSM": {
    "halal_certified": {
      "status": "verified",
      "evidence_url": "dsm.com/certificates/halal-vitamin-d3-2024.pdf",
      "last_updated": "2024-03-15",
      "verification_method": "direct_scrape"
    }
  }
}
```

## Implementation Pipeline

### End-to-End Flow
```python
def run_vitamin_d_phase1():
    # 1. Database Discovery
    db_session = create_db_connection("db/db.sqlite")
    vitamin_d_skus = query_vitamin_d_products(db_session)
    
    # 2. Parse & Cluster  
    parsed_skus = [parse_vitamin_d_sku(sku) for sku in vitamin_d_skus]
    clusters = cluster_vitamin_d_skus(parsed_skus)
    
    # 3. Enrich with External Data
    supplier_evidence = load_cached_evidence("external_evidence.json")
    
    # 4. Build Agent Inputs
    agent_inputs = []
    for cluster in clusters:
        agent_input = build_agent_input_from_cluster(cluster, supplier_evidence)
        agent_inputs.append(agent_input)
    
    # 5. Run Equivalence-Agent
    results = []
    for agent_input in agent_inputs:
        result = call_equivalence_agent(agent_input, use_mock=False)  
        results.append(result)
    
    return results
```

## Phase 1 Deliverables

### Technical Components
1. **Database Connection** - SQLAlchemy models + vitamin D extraction query
2. **SKU Parser** - Extract substance, potency, form from real SKU strings
3. **Clustering Engine** - Group vitamin D SKUs by similarity and business logic
4. **Equivalence-Agent** - Claude API integration with real cluster inputs
5. **Evidence Cache** - 3 vitamin D suppliers with compliance data
6. **Demo Pipeline** - End-to-end script demonstrating real fragmentation → agent reasoning

### Data Outputs
- **15-25 vitamin D SKUs** extracted from existing SQLite database
- **2-4 clusters** showing real fragmentation patterns across companies  
- **Valid agent responses** for each cluster following JSON contract
- **Supplier evidence** for at least DSM and BASF vitamin D products

### Success Criteria
✅ **Real Data Foundation**: Vitamin D SKUs extracted from actual database  
✅ **Clustering Validation**: Multiple companies selling same substance grouped correctly  
✅ **Agent Integration**: Equivalence-Agent produces valid JSON for real clusters  
✅ **External Evidence**: Cached compliance data for key vitamin D suppliers  
✅ **Demo Readiness**: Complete pipeline runs offline without dependencies

## Timeline & Dependencies

### Phase 1 Completion: Friday 24:00
**Person 1 (Product Lead)**: Demo storyline validation, cluster selection
**Person 2 (AI)**: Equivalence-Agent Claude API integration  
**Person 3 (Data)**: Database models, SKU parsing, clustering implementation
**Person 4 (External)**: Supplier evidence gathering and caching
**Person 5 (UI)**: Basic visualization of clusters and agent outputs

### Critical Path Dependencies
1. Database connection → SKU extraction → Clustering
2. Real clusters → Agent input formatting → Claude API testing  
3. Supplier research → Evidence caching → Agent enrichment
4. All components → End-to-end pipeline → Demo validation

### Risk Mitigation
- **Database Issues**: Mock data fallback maintains timeline
- **Claude API Limits**: Existing mock system provides offline capability  
- **Supplier Scraping**: Manual evidence collection if automated fails
- **Clustering Quality**: Business rules backup if embedding clustering insufficient

## Handoff to Phase 2

### Ready for Phase 2 Development
- **Database foundation** supports adding calcium citrate and other substances
- **Agent framework** ready for Compliance-Agent and Devil's Advocate
- **External enrichment** system scales to additional suppliers
- **Real cluster validation** proves concept with industry data

### Phase 2 Inputs
- **Validated vitamin D clusters** as test data for remaining agents
- **Evidence caching framework** ready for compliance-specific enrichment
- **Database query patterns** established for other substance categories
- **Agent input/output contracts** validated with real data

## Conclusion

This database-first approach provides maximum demo credibility by using real supplement industry fragmentation data while maintaining the rapid development timeline. The vitamin D focus gives us a well-understood substance with clear compliance requirements (halal, kosher, potency standards) that will showcase the multi-agent reasoning effectively.

The foundation established in Phase 1 supports the full Agnes vision while proving the concept with actual industry data rather than theoretical examples.