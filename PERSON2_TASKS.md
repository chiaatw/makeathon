# Person 2: Detaillierte Task-Liste

> **Für Person 2 (AI/LLM Engineer)**  
> Diese Liste kann als Checklist während der Makeathon verwendet werden.  
> Markiere Items mit `- [x]` wenn abgeschlossen.

---

## 🚀 Phase 1 Fundament (Fr 20:00 – 24:00)

### ✅ QUICK START (5 min)

- [ ] Clone/pull latest main branch
- [ ] Review `equivalence_agent.py` current state
- [ ] Review `schemas.py` for existing data structures
- [ ] Check `tests/test_parsing/test_equivalence_agent_real.py` for testing patterns

---

## Task 1️⃣: Equivalence-Agent Prompt finalisieren (45 min)

**Current File:** `equivalence_agent.py` (lines ~30-80, the prompt)

### 1.1 Review & Document Current State
- [ ] Open `equivalence_agent.py`
- [ ] Read the prompt template (should be between function definition and call)
- [ ] Note: Currently uses German language → may switch to English for Claude API stability
- [ ] Document: What claims does it extract? What is `missing_evidence` capturing?

### 1.2 Finalize Prompt Template
- [ ] Update if needed: "You are a pharmaceutical equivalence specialist..."
- [ ] Ensure JSON structure matches `AgentOutput` schema:
  - `verdict` (RECOMMENDED | PROPOSED | BLOCKED)
  - `confidence` (0.0-1.0 float)
  - `reasoning` (string explanation)
  - `claims` (List[str] of factual claims)
  - `missing_evidence` (List[str] of gaps)
- [ ] Add handling for edge cases:
  - "What if supplier certifications are missing?"
  - "What if we only have 1 cluster member, not 3?"
  - "What if no external evidence exists?"

### 1.3 Test Equivalence Output
```bash
# Run existing tests
pytest tests/test_parsing/test_equivalence_agent_real.py -v

# Check: Do all tests pass?
# Expected: 7 passing tests
```

- [ ] All 7 equivalence agent tests pass
- [ ] JSON output is valid (no parsing errors)
- [ ] Confidence scores are between 0.0-1.0
- [ ] `reasoning` field is non-empty
- [ ] `claims` array populated correctly

### 1.4 Handle Missing Data Gracefully
- [ ] If no suppliers found: Still return valid JSON with confidence < 0.6
- [ ] If 1 cluster member: Note in reasoning that verdict is provisional
- [ ] Test with incomplete data: `equivalence_agent.py` should handle it

### 1.5 Document the Prompt
- [ ] Add docstring to `call_equivalence_agent()` function explaining:
  - Input format (EquivalenceAgentInput)
  - Output format (AgentOutput)
  - Failure modes (what happens with insufficient data?)

**Acceptance Criteria:**
- [ ] All tests pass
- [ ] Prompt is documented inline
- [ ] Handles edge cases without crashing
- [ ] JSON output is valid 100% of the time

---

## Task 2️⃣: Compliance-Agent Prompt skeleton (60 min)

**File to Create:** `agents/compliance_agent.py` (new file)

### 2.1 Plan Regulatory Framework
- [ ] Document which markets we care about:
  - [ ] USA (FDA approval required)
  - [ ] EU (EMA approval)
  - [ ] Other (Canada, AU, etc. - optional for Phase 1)
- [ ] Map key regulatory requirements:
  - [ ] FDA: Dietary Supplement approval (NDC, warning label)
  - [ ] FDA: Manufacturing (cGMP compliance, site inspection)
  - [ ] USP/EP: Quality standard (dissolution, purity)

### 2.2 Create Schema for Compliance Output
**In `schemas.py`, add:**

```python
class ComplianceCheckCategory(str, Enum):
    APPROVAL_STATUS = "approval_status"
    MANUFACTURING = "manufacturing"
    SAFETY = "safety"
    SUPPLY_CHAIN = "supply_chain"

@dataclass
class ComplianceIssue:
    category: ComplianceCheckCategory
    market: str  # "USA", "EU", etc.
    issue: str  # "FDA approval missing"
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    evidence: str  # What we found or didn't find

@dataclass
class ComplianceAgentOutput:
    material_id: str
    supplier: str
    market: str
    compliance_status: str  # "COMPLIANT", "NON_COMPLIANT", "INSUFFICIENT_DATA"
    issues: List[ComplianceIssue] = field(default_factory=list)
    confidence: float = 0.5  # 0.0-1.0
    reasoning: str = ""
```

- [ ] Schema added to `schemas.py`
- [ ] All fields documented with docstrings

### 2.3 Write Compliance Prompt Template
**In `agents/compliance_agent.py`, create:**

```python
COMPLIANCE_PROMPT_TEMPLATE = """
You are a pharmaceutical compliance specialist. 
Evaluate if this material can be supplied safely in the target market.

Material: {material_id}
Supplier: {supplier_name}
Target Market: {market}  # e.g., "USA"

Known regulatory approvals:
{approvals}  # e.g., "FDA approval: YES/NO/UNKNOWN"

Known manufacturing standards:
{manufacturing}  # e.g., "cGMP certified: YES/NO/UNKNOWN"

Known safety record:
{safety}  # e.g., "No adverse events reported"

Your task:
1. For each regulatory category (approval, manufacturing, safety, supply-chain):
   - Check if compliant
   - Note severity of any issues
   - Provide evidence source or note if insufficient
2. Return JSON with compliance verdict

Return JSON:
{{
  "compliance_status": "COMPLIANT|NON_COMPLIANT|INSUFFICIENT_DATA",
  "issues": [
    {{
      "category": "APPROVAL_STATUS|MANUFACTURING|SAFETY|SUPPLY_CHAIN",
      "market": "USA",
      "issue": "FDA approval missing",
      "severity": "CRITICAL",
      "evidence": "No FDA approval found in records"
    }}
  ],
  "confidence": 0.75,
  "reasoning": "..."
}}
"""

def call_compliance_agent(input_data: ComplianceAgentInput, use_mock=True) -> ComplianceAgentOutput:
    # Similar structure to equivalence_agent
    pass
```

- [ ] Prompt template written
- [ ] Schema fields match template JSON structure

### 2.4 Add Mock Implementation
```python
def mock_compliance_analysis(supplier: str, market: str = "USA") -> ComplianceAgentOutput:
    # Return different verdicts based on supplier
    if supplier in ["DSM", "BASF", "Prinova"]:
        return ComplianceAgentOutput(
            supplier=supplier,
            market=market,
            compliance_status="COMPLIANT",
            issues=[],
            confidence=0.95
        )
    else:
        return ComplianceAgentOutput(
            supplier=supplier,
            market=market,
            compliance_status="INSUFFICIENT_DATA",
            issues=[
                ComplianceIssue(
                    category=ComplianceCheckCategory.APPROVAL_STATUS,
                    market=market,
                    issue="FDA approval unknown",
                    severity="HIGH"
                )
            ],
            confidence=0.4
        )
```

- [ ] Mock function implemented and returns valid JSON

### 2.5 Write Basic Tests
**Create `tests/test_agents/test_compliance_prompt.py`:**

```python
def test_compliance_mock_known_supplier():
    output = mock_compliance_analysis("DSM", "USA")
    assert output.compliance_status == "COMPLIANT"
    assert output.confidence >= 0.9

def test_compliance_mock_unknown_supplier():
    output = mock_compliance_analysis("UnknownCorp", "USA")
    assert output.compliance_status == "INSUFFICIENT_DATA"
    assert output.confidence < 0.5

def test_compliance_json_serialization():
    output = mock_compliance_analysis("DSM")
    json_str = json.dumps(asdict(output))
    assert "COMPLIANT" in json_str
```

- [ ] Tests written (min. 3 test cases)
- [ ] `pytest tests/test_agents/test_compliance_prompt.py -v` passes

**Acceptance Criteria:**
- [ ] `agents/compliance_agent.py` exists with prompt template
- [ ] `ComplianceAgentOutput` schema in `schemas.py`
- [ ] Mock function works and returns valid JSON
- [ ] Tests pass
- [ ] Prompt handles "USA" market (can extend to others in Phase 2)

---

## Task 3️⃣: Devil's Advocate Prompt skeleton (45 min)

**File to Create:** `agents/devils_advocate_agent.py` (new file)

### 3.1 Design Devil's Advocate Output Schema
**In `schemas.py`, add:**

```python
@dataclass
class DevilsAdvocateRisk:
    category: str  # "quality", "regulatory", "commercial", "supply_chain"
    risk: str  # e.g., "Quality loss due to supplier change"
    severity: int  # 1-10, where 10 is catastrophic
    likelihood: int  # 1-10, where 10 is certain
    mitigation: str  # How to mitigate this risk

@dataclass
class DevilsAdvocateOutput:
    verdict: str  # The original consolidation verdict
    risks: List[DevilsAdvocateRisk] = field(default_factory=list)
    critical_risks: List[str] = field(default_factory=list)  # Top 3 risks
    confidence_reduction: float = 0.0  # How much to reduce original confidence
    recommendation: str  # "Proceed with caution", "Reject consolidation", etc.
```

- [ ] Schema added to `schemas.py`

### 3.2 Write Devil's Advocate Prompt
**In `agents/devils_advocate_agent.py`:**

```python
DEVILS_ADVOCATE_PROMPT = """
You are a Devil's Advocate - your job is to find problems with proposed consolidations.

Original Recommendation: {original_verdict}
Consolidation Plan: Consolidate from {num_suppliers} suppliers to 1

Current Plan Details:
- Materials: {materials}
- Companies affected: {companies}
- Target suppliers: {target_supplier}

Your task: Identify potential risks that could make this consolidation fail.
Consider:
1. Quality Loss: Could switching suppliers cause bioavailability issues?
2. Regulatory: What if FDA audits the new supplier and finds issues?
3. Commercial: What if customers reject the new supplier?
4. Supply Chain: What if the new supplier has geopolitical risk?

Return JSON:
{{
  "risks": [
    {{
      "category": "quality|regulatory|commercial|supply_chain",
      "risk": "Bioavailability drops 5%",
      "severity": 7,
      "likelihood": 4,
      "mitigation": "Run dissolution testing before full transition"
    }}
  ],
  "critical_risks": ["Top 1", "Top 2", "Top 3"],
  "confidence_reduction": 0.15,
  "recommendation": "Proceed with extensive testing"
}}
"""
```

- [ ] Prompt template written

### 3.3 Add Mock Implementation
```python
def mock_devils_advocate(verdict: str, num_suppliers: int = 2) -> DevilsAdvocateOutput:
    # If RECOMMENDED, always find some risks
    if verdict == "RECOMMENDED":
        return DevilsAdvocateOutput(
            verdict=verdict,
            risks=[
                DevilsAdvocateRisk(
                    category="quality",
                    risk="Different bioavailability profile",
                    severity=6,
                    likelihood=5,
                    mitigation="Run dissolution test"
                ),
                DevilsAdvocateRisk(
                    category="regulatory",
                    risk="FDA audit could reveal non-compliance",
                    severity=9,
                    likelihood=3,
                    mitigation="Conduct full site audit first"
                )
            ],
            critical_risks=["Quality mismatch", "Regulatory risk"],
            confidence_reduction=0.1,
            recommendation="Approve with conditions"
        )
    else:
        return DevilsAdvocateOutput(verdict=verdict, risks=[])
```

- [ ] Mock function works

### 3.4 Write Tests
**Create `tests/test_agents/test_devils_advocate.py`:**

```python
def test_devils_advocate_finds_risks():
    output = mock_devils_advocate("RECOMMENDED")
    assert len(output.risks) > 0
    assert output.confidence_reduction > 0

def test_devils_advocate_no_risks_if_blocked():
    output = mock_devils_advocate("BLOCKED")
    assert len(output.risks) == 0
```

- [ ] Tests pass

**Acceptance Criteria:**
- [ ] `agents/devils_advocate_agent.py` exists with prompt
- [ ] `DevilsAdvocateOutput` schema in `schemas.py`
- [ ] Mock function works
- [ ] Tests pass
- [ ] Risk categories cover: quality, regulatory, commercial, supply_chain

---

## Task 4️⃣: JSON Contract v1.0 dokumentieren (30 min)

**File to Create:** `docs/JSON_CONTRACT_V1.md`

### 4.1 Inventory All Schemas
- [ ] List all schemas in `schemas.py`:
  - ParsedSKU
  - VitaminDProduct
  - EquivalenceAgentInput
  - EndProductContext
  - AgentOutput
  - ComplianceAgentOutput (new)
  - DevilsAdvocateOutput (new)
  - AggregatedGaps (later)
  - RankedGaps (later)

### 4.2 Document Each Schema
For each schema, write:

```markdown
### EquivalenceAgentInput

**Purpose:** Input data for equivalence analysis agent

**Fields:**
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| cluster_id | str | Yes | Unique cluster ID | "cluster-1" |
| skus | List[str] | Yes | Product SKUs in cluster | ["RM-C1-...", "RM-C2-..."] |
| affected_companies | List[str] | Yes | Company names | ["Company A", "Company B"] |

**JSON Example:**
\`\`\`json
{
  "cluster_id": "cluster-1",
  "skus": ["RM-C1-vitamin-d3-..."],
  "affected_companies": ["DSM"],
  "affected_boms": [],
  "current_suppliers": ["Supplier A", "Supplier B"],
  "end_product_context": [...]
}
\`\`\`

**Constraints:**
- cluster_id must start with "cluster-"
- skus list must not be empty
- affected_companies must match company_name from database
```

- [ ] All schemas documented with tables + examples

### 4.3 Document Constraints & Validations
- [ ] For each field with constraints:
  - [ ] Data type requirements
  - [ ] Valid value ranges (e.g., 0.0-1.0 for confidence)
  - [ ] Required vs. optional
  - [ ] Format rules (e.g., UUID, enum values)

**Example:**
```markdown
### Confidence Field

**Constraint:** Float between 0.0 and 1.0
- 0.0 = No confidence (guess only)
- 0.5 = Medium confidence (some data missing)
- 1.0 = Complete confidence (all data present)

**Validation:**
- Must fail if outside range
- Must round to 2 decimal places in JSON
```

- [ ] All constraints documented

### 4.4 Document Versioning Strategy
```markdown
## Versioning

### Current: v1.0
- Initial schemas for Phase 1
- Supports: Equivalence, Compliance, Devil's Advocate

### When to bump version?

**Major (v2.0):**
- Remove or rename required field
- Change type of existing field
- Break backward compatibility

**Minor (v1.1):**
- Add new optional field
- Add new schema
- Extend enum values
- Add new required field with default

**Patch (v1.0.1):**
- Fix documentation
- Clarify constraint
- Add example

### Breaking Changes Policy
- Announce 1 week in advance
- Provide migration script
- Support both old + new versions for 1 week
```

- [ ] Versioning strategy documented

**Acceptance Criteria:**
- [ ] `docs/JSON_CONTRACT_V1.md` exists
- [ ] All schemas documented with:
  - Purpose
  - Field table
  - JSON example
  - Constraints
- [ ] Versioning & compatibility policy documented

---

## Task 5️⃣: Gap-Aggregator implementieren (90 min)

**Files to Create:**
- `agents/gap_aggregator.py`
- `tests/test_agents/test_gap_aggregator.py`

### 5.1 Design Gap-Aggregator Schema
**In `schemas.py`, add:**

```python
@dataclass
class Gap:
    id: str  # "gap_regulatory_001"
    source: str  # "equivalence", "compliance", "devils_advocate"
    type: str  # "regulatory", "technical", "commercial", "supply_chain"
    description: str  # "FDA approval missing"
    severity: int  # 1-10
    evidence: str  # Citation or explanation

@dataclass
class AggregatedGaps:
    cluster_id: str
    total_gaps: int
    by_type: dict  # e.g., {"regulatory": 3, "technical": 2}
    gaps: List[Gap] = field(default_factory=list)
    timestamp: str = ""  # ISO timestamp
```

- [ ] Schema added to `schemas.py`

### 5.2 Implement Aggregator Class
**In `agents/gap_aggregator.py`:**

```python
from dataclasses import asdict
from schemas import AggregatedGaps, Gap

class GapAggregator:
    """Collects gaps from all agent sources into unified structure."""
    
    def aggregate(self,
        cluster_id: str,
        equivalence_output: AgentOutput,
        compliance_output: ComplianceAgentOutput,
        devils_advocate_output: DevilsAdvocateOutput
    ) -> AggregatedGaps:
        """
        Aggregate missing evidence/risks from all agents.
        
        Args:
            cluster_id: The cluster being analyzed
            equivalence_output: Missing evidence from equivalence analysis
            compliance_output: Compliance issues
            devils_advocate_output: Identified risks
            
        Returns:
            AggregatedGaps with unified gap list
        """
        gaps = []
        gap_counter = 0
        
        # Extract from Equivalence missing_evidence
        for evidence_gap in equivalence_output.missing_evidence:
            gaps.append(Gap(
                id=f"gap_equivalence_{gap_counter:03d}",
                source="equivalence",
                type="technical",  # Could be more nuanced
                description=evidence_gap,
                severity=5,  # Default, could be inferred
                evidence=""
            ))
            gap_counter += 1
        
        # Extract from Compliance issues
        for issue in compliance_output.issues:
            # Map compliance category to gap type
            gap_type = {
                "APPROVAL_STATUS": "regulatory",
                "MANUFACTURING": "technical",
                "SAFETY": "regulatory",
                "SUPPLY_CHAIN": "supply_chain"
            }.get(issue.category, "technical")
            
            gaps.append(Gap(
                id=f"gap_compliance_{gap_counter:03d}",
                source="compliance",
                type=gap_type,
                description=f"{issue.issue} (Market: {issue.market})",
                severity=self._map_severity(issue.severity),
                evidence=issue.evidence
            ))
            gap_counter += 1
        
        # Extract from Devil's Advocate risks
        for risk in devils_advocate_output.risks:
            gaps.append(Gap(
                id=f"gap_devils_advocate_{gap_counter:03d}",
                source="devils_advocate",
                type=risk.category,
                description=risk.risk,
                severity=risk.severity,
                evidence=risk.mitigation
            ))
            gap_counter += 1
        
        # Count by type
        by_type = {}
        for gap in gaps:
            by_type[gap.type] = by_type.get(gap.type, 0) + 1
        
        return AggregatedGaps(
            cluster_id=cluster_id,
            total_gaps=len(gaps),
            by_type=by_type,
            gaps=gaps,
            timestamp=datetime.now().isoformat()
        )
    
    def _map_severity(self, severity_str: str) -> int:
        """Map string severity to 1-10 scale."""
        mapping = {
            "CRITICAL": 9,
            "HIGH": 7,
            "MEDIUM": 5,
            "LOW": 3
        }
        return mapping.get(severity_str, 5)
```

- [ ] GapAggregator class implemented
- [ ] aggregate() method complete
- [ ] Handles all 3 input types (Equivalence, Compliance, Devil's Advocate)

### 5.3 Write Comprehensive Tests
**In `tests/test_agents/test_gap_aggregator.py`:**

```python
@pytest.fixture
def aggregator():
    return GapAggregator()

@pytest.fixture
def mock_equivalence():
    return AgentOutput(
        verdict="RECOMMENDED",
        confidence=0.85,
        reasoning="...",
        claims=["..."],
        missing_evidence=["Supplier bioavailability data", "Long-term stability data"]
    )

@pytest.fixture
def mock_compliance():
    return ComplianceAgentOutput(
        material_id="VD3",
        supplier="DSM",
        market="USA",
        compliance_status="COMPLIANT",
        issues=[
            ComplianceIssue(
                category=ComplianceCheckCategory.APPROVAL_STATUS,
                market="EU",
                issue="EMA approval pending",
                severity="HIGH"
            )
        ]
    )

def test_aggregate_basic(aggregator, mock_equivalence, mock_compliance):
    """Test basic aggregation from 2 sources."""
    devils = mock_devils_advocate("RECOMMENDED")
    
    result = aggregator.aggregate(
        cluster_id="cluster-1",
        equivalence_output=mock_equivalence,
        compliance_output=mock_compliance,
        devils_advocate_output=devils
    )
    
    assert result.cluster_id == "cluster-1"
    assert result.total_gaps > 0
    assert len(result.gaps) > 0
    assert "technical" in result.by_type or "regulatory" in result.by_type

def test_aggregate_gap_ids_unique(aggregator, mock_equivalence, mock_compliance):
    """Ensure gap IDs don't overlap."""
    devils = mock_devils_advocate("RECOMMENDED")
    result = aggregator.aggregate(
        cluster_id="cluster-1",
        equivalence_output=mock_equivalence,
        compliance_output=mock_compliance,
        devils_advocate_output=devils
    )
    
    ids = [gap.id for gap in result.gaps]
    assert len(ids) == len(set(ids))  # No duplicates

def test_aggregate_severity_mapping(aggregator):
    """Test severity string → int mapping."""
    assert aggregator._map_severity("CRITICAL") == 9
    assert aggregator._map_severity("HIGH") == 7
    assert aggregator._map_severity("MEDIUM") == 5
    assert aggregator._map_severity("LOW") == 3

def test_aggregate_empty_sources(aggregator):
    """Test with sources that have no gaps."""
    equiv = AgentOutput(verdict="RECOMMENDED", missing_evidence=[])
    compliance = ComplianceAgentOutput(
        material_id="VD3",
        supplier="DSM",
        market="USA",
        compliance_status="COMPLIANT",
        issues=[]
    )
    devils = mock_devils_advocate("BLOCKED")  # No risks if blocked
    
    result = aggregator.aggregate("cluster-1", equiv, compliance, devils)
    assert result.total_gaps == 0
```

- [ ] Test file created with min. 4 test cases
- [ ] All tests pass: `pytest tests/test_agents/test_gap_aggregator.py -v`

### 5.4 Integration Test
- [ ] GapAggregator works with real equivalence + compliance + devils outputs
- [ ] No crashes on edge cases (empty lists, None values, etc.)

**Acceptance Criteria:**
- [ ] `agents/gap_aggregator.py` complete
- [ ] `AggregatedGaps` + `Gap` schemas in `schemas.py`
- [ ] Tests pass (min. 4 test cases)
- [ ] Handles all 3 input types
- [ ] Gap IDs are unique
- [ ] Severity mapping works

---

## Task 6️⃣: Gap-Ranker implementieren (60 min)

**Files to Create:**
- `agents/gap_ranker.py`
- `tests/test_agents/test_gap_ranker.py`

### 6.1 Design Ranking Schema
**In `schemas.py`, add:**

```python
@dataclass
class RankedGap:
    gap_id: str
    description: str
    type: str  # regulatory, technical, commercial, supply_chain
    impact_score: float  # 1.0-10.0, business impact
    effort_score: float  # 1.0-10.0, effort to resolve
    risk_score: float  # 1.0-10.0, risk if unresolved
    priority_score: float  # Calculated: (impact + risk - effort) / 3
    rank: int  # 1st, 2nd, etc.

@dataclass
class RankedGaps:
    cluster_id: str
    gaps: List[RankedGap] = field(default_factory=list)
    top_5: List[RankedGap] = field(default_factory=list)
    total_priority_score: float = 0.0
```

- [ ] Schema added to `schemas.py`

### 6.2 Implement Ranker Class
**In `agents/gap_ranker.py`:**

```python
class GapRanker:
    """Ranks gaps by priority (impact, effort, risk)."""
    
    # Configurable weights
    WEIGHT_IMPACT = 0.4
    WEIGHT_RISK = 0.4
    WEIGHT_EFFORT = -0.2  # Negative: less effort = higher priority
    
    def rank(self, aggregated_gaps: AggregatedGaps) -> RankedGaps:
        """
        Rank gaps by priority score.
        
        Priority Score = (Impact × 0.4) + (Risk × 0.4) - (Effort × 0.2)
        
        Args:
            aggregated_gaps: Output from GapAggregator
            
        Returns:
            RankedGaps with sorted + ranked list
        """
        ranked = []
        
        for gap in aggregated_gaps.gaps:
            # Assess scores (could be enhanced with heuristics)
            impact = self._assess_impact(gap)
            effort = self._assess_effort(gap)
            risk = self._assess_risk(gap)
            
            priority = (
                impact * self.WEIGHT_IMPACT +
                risk * self.WEIGHT_RISK +
                effort * self.WEIGHT_EFFORT
            )
            
            ranked.append(RankedGap(
                gap_id=gap.id,
                description=gap.description,
                type=gap.type,
                impact_score=impact,
                effort_score=effort,
                risk_score=risk,
                priority_score=priority,
                rank=0  # Will set after sorting
            ))
        
        # Sort by priority (descending)
        ranked.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Set ranks
        for i, gap in enumerate(ranked, 1):
            gap.rank = i
        
        # Get top 5
        top_5 = ranked[:5]
        
        return RankedGaps(
            cluster_id=aggregated_gaps.cluster_id,
            gaps=ranked,
            top_5=top_5,
            total_priority_score=sum(g.priority_score for g in ranked)
        )
    
    def _assess_impact(self, gap: Gap) -> float:
        """Assess business impact of this gap (1-10)."""
        # Regulatory gaps = high impact
        if gap.type == "regulatory":
            return min(9, gap.severity + 2)  # regulatory is critical
        # Technical = medium-high
        elif gap.type == "technical":
            return min(8, gap.severity + 1)
        # Supply chain = medium
        elif gap.type == "supply_chain":
            return gap.severity
        # Commercial = lower
        else:  # commercial
            return max(1, gap.severity - 2)
    
    def _assess_effort(self, gap: Gap) -> float:
        """Assess effort to resolve (1-10)."""
        # Regulatory: usually high effort
        if gap.type == "regulatory":
            return 8.0
        # Technical: medium-high
        elif gap.type == "technical":
            return 6.0
        # Supply chain: medium
        elif gap.type == "supply_chain":
            return 5.0
        # Commercial: low effort (just communication)
        else:
            return 3.0
    
    def _assess_risk(self, gap: Gap) -> float:
        """Assess risk if gap is not resolved (1-10)."""
        # Use original severity as proxy
        return float(gap.severity)
```

- [ ] GapRanker class implemented
- [ ] rank() method complete
- [ ] Scoring heuristics implemented

### 6.3 Write Tests
**In `tests/test_agents/test_gap_ranker.py`:**

```python
@pytest.fixture
def ranker():
    return GapRanker()

def test_rank_sorts_by_priority(ranker):
    """Test that gaps are sorted by priority."""
    gaps = AggregatedGaps(
        cluster_id="cluster-1",
        total_gaps=3,
        gaps=[
            Gap("g1", "equivalence", "technical", "Minor issue", 2, ""),
            Gap("g2", "compliance", "regulatory", "FDA issue", 9, ""),
            Gap("g3", "devils_advocate", "commercial", "Brand risk", 3, "")
        ]
    )
    
    result = ranker.rank(gaps)
    
    # FDA issue should be first (highest priority)
    assert result.gaps[0].gap_id == "g2"
    assert result.gaps[0].rank == 1
    assert all(g.rank > 0 for g in result.gaps)

def test_rank_top_5(ranker):
    """Test top_5 extraction."""
    gaps = AggregatedGaps(
        cluster_id="cluster-1",
        total_gaps=10,
        gaps=[Gap(f"g{i}", "source", "type", f"Gap {i}", i, "") for i in range(10)]
    )
    
    result = ranker.rank(gaps)
    assert len(result.top_5) <= 5

def test_rank_priority_score_calculation(ranker):
    """Test priority score formula."""
    # Gap with high impact, low effort = high priority
    gap = Gap("g1", "compliance", "regulatory", "FDA issue", 9, "")
    gaps = AggregatedGaps(cluster_id="c1", total_gaps=1, gaps=[gap])
    
    result = ranker.rank(gaps)
    
    # Should have high priority score
    assert result.gaps[0].priority_score > 0
```

- [ ] Tests written and passing

**Acceptance Criteria:**
- [ ] `agents/gap_ranker.py` complete
- [ ] `RankedGap` + `RankedGaps` in `schemas.py`
- [ ] Scoring formula implements: (impact + risk - effort) / 3
- [ ] Tests pass
- [ ] Top 5 extracted correctly

---

## Task 7️⃣: Arbiter-Regeln definieren & testen (45 min)

**Files to Create:**
- `agents/arbiter.py`
- `agents/arbiter_rules.json`
- `tests/test_agents/test_arbiter.py`

### 7.1 Design Arbiter Output Schema
**In `schemas.py`, add:**

```python
@dataclass
class ArbiterVerdictOutput:
    cluster_id: str
    verdict: str  # "APPROVED", "BLOCKED", "DEFERRED"
    reasoning: str  # Why this verdict
    triggered_rules: List[str] = field(default_factory=list)  # Which rules fired
    approval_conditions: List[str] = field(default_factory=list)  # If APPROVED, what needs to be done
```

- [ ] Schema added

### 7.2 Create Arbiter Rules JSON
**In `agents/arbiter_rules.json`:**

```json
{
  "rules": [
    {
      "name": "all_clear",
      "condition": "total_gaps == 0",
      "verdict": "APPROVED",
      "reasoning": "No gaps identified, consolidation is safe"
    },
    {
      "name": "critical_regulatory_gap",
      "condition": "exists gap where type=='regulatory' AND priority > 8",
      "verdict": "BLOCKED",
      "reasoning": "Critical regulatory gap must be resolved before consolidation"
    },
    {
      "name": "budget_constraint",
      "condition": "total_effort > 40 AND timeline_months < 6",
      "verdict": "DEFERRED",
      "reasoning": "Insufficient time/budget to resolve all gaps"
    },
    {
      "name": "acceptable_risk",
      "condition": "top_5_avg_priority < 5",
      "verdict": "APPROVED",
      "reasoning": "Top gaps are manageable"
    }
  ]
}
```

- [ ] Rules file created with min. 3-4 rules

### 7.3 Implement Arbiter Engine
**In `agents/arbiter.py`:**

```python
import json

class ArbiterEngine:
    """Applies rules to generate final consolidation verdict."""
    
    def __init__(self, rules_file: str = "agents/arbiter_rules.json"):
        with open(rules_file) as f:
            self.rules = json.load(f)["rules"]
    
    def arbitrate(self,
        ranked_gaps: RankedGaps,
        timeline_months: int = 12,
        budget_score: float = 10.0
    ) -> ArbiterVerdictOutput:
        """
        Apply arbiter rules to determine final verdict.
        
        Args:
            ranked_gaps: Output from GapRanker
            timeline_months: How many months to resolve gaps
            budget_score: Budget available (1-10)
            
        Returns:
            ArbiterVerdictOutput with final verdict
        """
        context = {
            "total_gaps": len(ranked_gaps.gaps),
            "has_regulatory_gap": any(g.type == "regulatory" for g in ranked_gaps.gaps),
            "has_critical_gap": any(g.priority_score > 8 for g in ranked_gaps.gaps),
            "top_1_priority": ranked_gaps.top_5[0].priority_score if ranked_gaps.top_5 else 0,
            "timeline_months": timeline_months,
            "total_effort": sum(g.effort_score for g in ranked_gaps.top_5),
        }
        
        # Apply rules in order
        triggered_rules = []
        verdict = None
        reasoning = ""
        
        for rule in self.rules:
            if self._evaluate_rule(rule, context):
                triggered_rules.append(rule["name"])
                if verdict is None:  # First matching rule wins
                    verdict = rule["verdict"]
                    reasoning = rule["reasoning"]
        
        # Default if no rules match
        if verdict is None:
            verdict = "DEFERRED"
            reasoning = "Unable to determine clear verdict, deferring"
        
        # Generate approval conditions
        conditions = []
        if verdict == "APPROVED" and len(ranked_gaps.top_5) > 0:
            conditions = [f"Resolve: {g.description}" for g in ranked_gaps.top_5[:3]]
        
        return ArbiterVerdictOutput(
            cluster_id=ranked_gaps.cluster_id,
            verdict=verdict,
            reasoning=reasoning,
            triggered_rules=triggered_rules,
            approval_conditions=conditions
        )
    
    def _evaluate_rule(self, rule: dict, context: dict) -> bool:
        """Simple rule evaluation (could be enhanced with expression parser)."""
        condition = rule["condition"]
        
        # Simple pattern matching
        if condition == "total_gaps == 0":
            return context["total_gaps"] == 0
        elif condition == "exists gap where type=='regulatory' AND priority > 8":
            return context["has_critical_gap"] and context["has_regulatory_gap"]
        elif condition == "total_effort > 40 AND timeline_months < 6":
            return context["total_effort"] > 40 and context["timeline_months"] < 6
        elif condition == "top_5_avg_priority < 5":
            return context["top_1_priority"] < 5
        
        return False
```

- [ ] ArbiterEngine class implemented
- [ ] rule evaluation logic working

### 7.4 Write Tests
**In `tests/test_agents/test_arbiter.py`:**

```python
@pytest.fixture
def arbiter():
    # Use test rules file
    return ArbiterEngine()

def test_arbiter_all_clear():
    """Test APPROVED verdict when no gaps."""
    gaps = RankedGaps(cluster_id="c1", gaps=[], top_5=[])
    verdict = arbiter.arbitrate(gaps)
    assert verdict.verdict == "APPROVED"

def test_arbiter_blocks_critical_regulatory():
    """Test BLOCKED when critical regulatory gap."""
    gap = RankedGap(
        gap_id="g1",
        description="FDA approval missing",
        type="regulatory",
        impact_score=9,
        effort_score=8,
        risk_score=9,
        priority_score=9.0,
        rank=1
    )
    gaps = RankedGaps(cluster_id="c1", gaps=[gap], top_5=[gap])
    
    verdict = arbiter.arbitrate(gaps, timeline_months=12)
    # Should be blocked due to critical regulatory gap
    # (adjust based on actual rule)

def test_arbiter_defers_budget_constraint():
    """Test DEFERRED when insufficient time."""
    gaps = RankedGaps(cluster_id="c1", gaps=[], top_5=[])
    verdict = arbiter.arbitrate(gaps, timeline_months=1, budget_score=1.0)
    # Should be deferred due to tight timeline
```

- [ ] Tests pass

**Acceptance Criteria:**
- [ ] `agents/arbiter.py` complete
- [ ] `arbiter_rules.json` with min. 3-4 rules
- [ ] `ArbiterVerdictOutput` in `schemas.py`
- [ ] Tests pass
- [ ] Verdicts: APPROVED, BLOCKED, DEFERRED all working

---

## Task 8️⃣: Insufficient_Evidence Handling (60 min)

**Files to Create:**
- `agents/evidence_checker.py`
- `tests/test_agents/test_evidence_checker.py`

### 8.1 Design Evidence Schema
**In `schemas.py`, add:**

```python
from enum import Enum

class EvidenceLevel(str, Enum):
    COMPLETE = "complete"  # 0.95-1.0
    SUBSTANTIAL = "substantial"  # 0.80-0.95
    PARTIAL = "partial"  # 0.50-0.80
    INSUFFICIENT = "insufficient"  # 0.0-0.50

@dataclass
class EvidenceQuality:
    level: EvidenceLevel
    confidence: float  # 0.0-1.0
    gaps: List[str]  # What's missing
    fallback_strategy: str  # "defer", "proceed_cautious", "block"
    notes: str  # Why this level
```

- [ ] Schema added

### 8.2 Implement Evidence Checker
**In `agents/evidence_checker.py`:**

```python
class EvidenceChecker:
    """Evaluates quality of evidence for a consolidation decision."""
    
    def check_equivalence_evidence(self, output: AgentOutput) -> EvidenceQuality:
        """Check evidence quality for equivalence analysis."""
        
        missing = output.missing_evidence
        num_claims = len(output.claims)
        
        # Heuristic: more claims + fewer gaps = better evidence
        evidence_score = (num_claims / max(1, num_claims + len(missing)))
        
        # Map to levels
        if evidence_score >= 0.95:
            level = EvidenceLevel.COMPLETE
            strategy = "proceed_normal"
        elif evidence_score >= 0.80:
            level = EvidenceLevel.SUBSTANTIAL
            strategy = "proceed_normal"
        elif evidence_score >= 0.50:
            level = EvidenceLevel.PARTIAL
            strategy = "proceed_cautious"
        else:
            level = EvidenceLevel.INSUFFICIENT
            strategy = "defer"
        
        return EvidenceQuality(
            level=level,
            confidence=evidence_score,
            gaps=missing,
            fallback_strategy=strategy,
            notes=f"{len(output.claims)} claims, {len(missing)} gaps"
        )
    
    def check_compliance_evidence(self, output: ComplianceAgentOutput) -> EvidenceQuality:
        """Check evidence quality for compliance analysis."""
        
        # If unknown/insufficient data, low confidence
        if output.compliance_status == "INSUFFICIENT_DATA":
            return EvidenceQuality(
                level=EvidenceLevel.INSUFFICIENT,
                confidence=0.3,
                gaps=["Compliance status unknown", "No regulatory data found"],
                fallback_strategy="defer",
                notes="Insufficient compliance data"
            )
        
        # If compliant, good confidence
        elif output.compliance_status == "COMPLIANT":
            return EvidenceQuality(
                level=EvidenceLevel.SUBSTANTIAL,
                confidence=output.confidence,
                gaps=[],
                fallback_strategy="proceed_normal",
                notes="Supplier compliance verified"
            )
        
        # Non-compliant
        else:
            return EvidenceQuality(
                level=EvidenceLevel.PARTIAL,
                confidence=output.confidence,
                gaps=[i.issue for i in output.issues],
                fallback_strategy="block",
                notes=f"{len(output.issues)} compliance issues"
            )
    
    def aggregate_evidence(self, evidence_qualities: List[EvidenceQuality]) -> EvidenceQuality:
        """Combine evidence from multiple sources."""
        
        avg_confidence = sum(e.confidence for e in evidence_qualities) / len(evidence_qualities)
        all_gaps = []
        for e in evidence_qualities:
            all_gaps.extend(e.gaps)
        
        # Determine overall level
        if avg_confidence >= 0.95:
            level = EvidenceLevel.COMPLETE
            strategy = "proceed_normal"
        elif avg_confidence >= 0.80:
            level = EvidenceLevel.SUBSTANTIAL
            strategy = "proceed_normal"
        elif avg_confidence >= 0.50:
            level = EvidenceLevel.PARTIAL
            strategy = "proceed_cautious"
        else:
            level = EvidenceLevel.INSUFFICIENT
            strategy = "defer"
        
        return EvidenceQuality(
            level=level,
            confidence=avg_confidence,
            gaps=list(set(all_gaps)),  # Unique
            fallback_strategy=strategy,
            notes=f"Overall: {level} (avg confidence: {avg_confidence:.1%})"
        )
```

- [ ] EvidenceChecker class complete

### 8.3 Write Tests
**In `tests/test_agents/test_evidence_checker.py`:**

```python
@pytest.fixture
def checker():
    return EvidenceChecker()

def test_check_equivalence_complete():
    """Test complete evidence recognition."""
    output = AgentOutput(
        verdict="RECOMMENDED",
        confidence=0.95,
        claims=["Claim 1", "Claim 2", "Claim 3"],
        missing_evidence=[]
    )
    
    result = checker.check_equivalence_evidence(output)
    assert result.level == EvidenceLevel.COMPLETE
    assert result.fallback_strategy == "proceed_normal"

def test_check_equivalence_insufficient():
    """Test insufficient evidence detection."""
    output = AgentOutput(
        verdict="PROPOSED",
        confidence=0.4,
        claims=[],
        missing_evidence=["Supplier data", "Safety data", "Cost data"]
    )
    
    result = checker.check_equivalence_evidence(output)
    assert result.level == EvidenceLevel.INSUFFICIENT
    assert result.fallback_strategy == "defer"

def test_check_compliance_unknown():
    """Test compliance status unknown."""
    output = ComplianceAgentOutput(
        material_id="VD3",
        supplier="Unknown",
        market="USA",
        compliance_status="INSUFFICIENT_DATA",
        issues=[]
    )
    
    result = checker.check_compliance_evidence(output)
    assert result.level == EvidenceLevel.INSUFFICIENT

def test_aggregate_multiple_sources(checker):
    """Test combining evidence from multiple sources."""
    ev1 = EvidenceQuality(
        level=EvidenceLevel.SUBSTANTIAL,
        confidence=0.85,
        gaps=["Gap A"],
        fallback_strategy="proceed_normal"
    )
    ev2 = EvidenceQuality(
        level=EvidenceLevel.PARTIAL,
        confidence=0.60,
        gaps=["Gap B", "Gap C"],
        fallback_strategy="proceed_cautious"
    )
    
    result = checker.aggregate_evidence([ev1, ev2])
    assert 0.70 < result.confidence < 0.85
    assert result.level in [EvidenceLevel.PARTIAL, EvidenceLevel.SUBSTANTIAL]
```

- [ ] Tests pass

**Acceptance Criteria:**
- [ ] `agents/evidence_checker.py` complete
- [ ] `EvidenceQuality` + `EvidenceLevel` in `schemas.py`
- [ ] Tests pass
- [ ] Fallback strategies: "defer", "proceed_cautious", "proceed_normal", "block"

---

## Task 9️⃣: Parsing robustness Tests (45 min)

**File to Create:** `tests/test_parsing/test_robustness.py`

### 9.1 Test Edge Cases
```python
import json
import pytest
from equivalence_agent import call_equivalence_agent, mock_equivalence_analysis

class TestJSONParsing:
    """Test robustness of JSON parsing from Claude."""
    
    def test_missing_required_field(self):
        """Test handling of missing verdict field."""
        bad_json = {
            "confidence": 0.8,
            "reasoning": "...",
            # Missing 'verdict'
        }
        # Should handle gracefully (set default or raise clear error)
    
    def test_extra_unknown_fields(self):
        """Test forward compatibility with unknown fields."""
        json_with_extras = {
            "verdict": "RECOMMENDED",
            "confidence": 0.8,
            "reasoning": "...",
            "claims": [],
            "missing_evidence": [],
            "future_field_v2": "value"  # Unknown field
        }
        # Should parse successfully, ignoring unknown field
    
    def test_wrong_data_type(self):
        """Test type validation."""
        bad_type = {
            "verdict": "RECOMMENDED",
            "confidence": "0.8",  # Should be float, not string
            "reasoning": "...",
            "claims": [],
            "missing_evidence": []
        }
        # Should coerce or error clearly
    
    def test_malformed_json(self):
        """Test handling of invalid JSON."""
        malformed = '{"verdict": "RECOMMENDED", "confidence": 0.8,}'  # trailing comma
        # Should handle parse error gracefully
    
    def test_unicode_handling(self):
        """Test non-ASCII characters."""
        unicode_json = {
            "verdict": "RECOMMENDED",
            "confidence": 0.8,
            "reasoning": "Supplier ist 德国制造",  # German + Chinese
            "claims": ["Certifié", "✓"],  # Accents + emoji
            "missing_evidence": []
        }
        # Should handle without UnicodeError
    
    def test_large_claims_list(self):
        """Test with very large number of claims."""
        large_output = {
            "verdict": "RECOMMENDED",
            "confidence": 0.8,
            "reasoning": "...",
            "claims": [f"Claim {i}" for i in range(1000)],
            "missing_evidence": []
        }
        # Should handle without performance degradation
    
    def test_null_optional_fields(self):
        """Test null in optional fields."""
        with_nulls = {
            "verdict": "RECOMMENDED",
            "confidence": 0.8,
            "reasoning": None,  # Optional but null
            "claims": None,
            "missing_evidence": None
        }
        # Should have defaults for null optional fields
    
    def test_nested_structure_validity(self):
        """Test deeply nested or invalid structures."""
        invalid_nested = {
            "verdict": "RECOMMENDED",
            "confidence": 0.8,
            "claims": [{"nested": "object"}],  # Should be strings
        }
        # Should validate or coerce

def test_claude_api_unexpected_response():
    """Test behavior when Claude returns unexpected format."""
    # Mock Claude returning HTML error instead of JSON
    with patch("anthropic.Anthropic") as mock_client:
        mock_client.return_value.messages.create.return_value.content = "<html>Error</html>"
        
        # Should handle gracefully, not crash
        # result = call_equivalence_agent(...)
        # assert result.confidence < 0.5 or fallback triggered
```

- [ ] Test file created with min. 8 edge case scenarios

### 9.2 Create Error Handling Documentation
**In `docs/ERROR_HANDLING.md`:**

```markdown
# Error Handling & Fallback Strategies

## JSON Parsing Failures

**Scenario:** Claude returns invalid JSON or missing fields
**Handling:**
- Parse error → Log warning, return mock output
- Missing required field → Set sensible default + confidence < 0.5
- Wrong data type → Attempt coercion, log if fails
- Unicode issues → Use utf-8 encoding throughout

**Example:**
\`\`\`python
try:
    output = AgentOutput(**parsed_json)
except ValidationError:
    # Fallback to conservative estimate
    output = AgentOutput(
        verdict="PROPOSED",
        confidence=0.3,
        reasoning="Unable to parse full response",
        claims=[],
        missing_evidence=["Complete analysis unavailable"]
    )
\`\`\`

## Insufficient Evidence Thresholds

| Evidence Level | Confidence | Action |
|---|---|---|
| COMPLETE | 0.95-1.0 | Proceed normally |
| SUBSTANTIAL | 0.80-0.95 | Proceed normally |
| PARTIAL | 0.50-0.80 | Proceed with caution (flag top gaps) |
| INSUFFICIENT | 0.0-0.50 | DEFER (flag for manual review) |

## Fallback Strategies per Agent

### Equivalence Agent Fallback
- If Claude API unreachable: Use mock_equivalence_analysis()
- If JSON invalid: Return confidence=0.3, verdict="PROPOSED"
- If supplier data missing: Still process other data, note gaps

### Compliance Agent Fallback
- If no regulatory data found: Assume INSUFFICIENT_DATA
- If approval status unknown: Mark as "UNKNOWN" not "NON_COMPLIANT"

### Devil's Advocate Fallback
- If cannot identify risks: Return empty risks list (not error)
- If original verdict uncertain: Return broader risk categories

## Monitoring & Logging

All error paths should log:
- Which step failed
- Fallback action taken
- Confidence reduction
```

- [ ] Documentation created

**Acceptance Criteria:**
- [ ] `test_robustness.py` with min. 8 edge cases
- [ ] All edge case tests pass
- [ ] `docs/ERROR_HANDLING.md` documents fallbacks
- [ ] No crashes on malformed JSON, Unicode, or missing fields

---

## Task 🔟: Integrations-Test (end-to-end) (45 min)

**File to Create:** `tests/test_integration/test_full_analysis_flow.py`

### 10.1 Create Integration Test Fixtures
```python
@pytest.fixture
def sample_cluster():
    """Realistic Vitamin D cluster."""
    return VitaminDCluster(
        cluster_id="cluster-1",
        products=[
            VitaminDProduct(
                sku="RM-C1-vitamin-d3-cholecalciferol-1000iu-abc12345",
                company_name="Company A",
                canonical_material_name="Vitamin D3"
            ),
            VitaminDProduct(
                sku="RM-C2-vitamin-d3-cholecalciferol-1000iu-def67890",
                company_name="Company B",
                canonical_material_name="Vitamin D3"
            )
        ]
    )

@pytest.fixture
def mock_all_agents():
    """Mock all 3 agent outputs."""
    equiv = mock_equivalence_analysis()
    compliance = mock_compliance_analysis("DSM", "USA")
    devils = mock_devils_advocate("RECOMMENDED")
    return equiv, compliance, devils
```

- [ ] Fixtures created

### 10.2 Write Happy Path Test
```python
def test_full_flow_happy_path(sample_cluster, mock_all_agents):
    """Test: Good cluster → No gaps → APPROVED."""
    equiv, compliance, devils = mock_all_agents
    
    # Aggregate gaps
    aggregator = GapAggregator()
    gaps = aggregator.aggregate("cluster-1", equiv, compliance, devils)
    
    # Rank gaps
    ranker = GapRanker()
    ranked = ranker.rank(gaps)
    
    # Arbitrate
    arbiter = ArbiterEngine()
    verdict = arbiter.arbitrate(ranked)
    
    assert verdict.verdict == "APPROVED"
    assert "no gaps" in verdict.reasoning.lower() or verdict.triggered_rules
```

- [ ] Happy path test written and passing

### 10.3 Write Failure Scenario Tests
```python
def test_full_flow_regulatory_blocker():
    """Test: Regulatory gap → BLOCKED."""
    # Modify compliance output to have critical issue
    # Expect: BLOCKED verdict

def test_full_flow_evidence_insufficient():
    """Test: Missing data → DEFERRED."""
    # Use compliance output with INSUFFICIENT_DATA
    # Expect: Fallback to DEFERRED

def test_full_flow_multiple_gaps_acceptable():
    """Test: Several gaps but manageable → APPROVED_WITH_CONDITIONS."""
    # Create gaps with moderate priorities
    # Expect: APPROVED with top 5 conditions listed
```

- [ ] Min. 4 scenario tests (happy path + 3 failure modes)

### 10.4 Performance Test
```python
def test_performance_under_load():
    """Test: Process 1 cluster in < 5 seconds."""
    import time
    
    start = time.time()
    # Run full pipeline on sample cluster
    elapsed = time.time() - start
    
    assert elapsed < 5.0, f"Pipeline took {elapsed}s, max 5s"
```

- [ ] Performance test added

**Acceptance Criteria:**
- [ ] `tests/test_integration/test_full_analysis_flow.py` complete
- [ ] Min. 4 scenario tests, all passing
- [ ] Performance < 5s per cluster
- [ ] End-to-end: Equivalence → Compliance → Devil's Advocate → Gap-Agg → Gap-Rank → Arbiter → Verdict

---

## ✅ Phase 1 Completion Checklist

By end of Fr 24:00, **all of these** should be checked:

### Prompts (Tasks 1-3)
- [ ] Equivalence Prompt v1.0 finalized + tested
- [ ] Compliance Prompt skeleton written
- [ ] Devil's Advocate Prompt skeleton written
- [ ] All 3 prompts follow consistent JSON format
- [ ] All 3 prompts have error handling

### Infrastructure (Tasks 4-8)
- [ ] JSON Contract v1.0 documented
- [ ] Gap-Aggregator implemented + tests passing
- [ ] Gap-Ranker implemented + tests passing
- [ ] Arbiter rules + engine working
- [ ] Insufficient_Evidence handling in all agents
- [ ] Robustness tests written (min. 8 edge cases)

### Integration (Task 10)
- [ ] Full pipeline tested (happy path + 3 failure modes)
- [ ] Performance < 5s per cluster
- [ ] No crashes on malformed input

### Documentation
- [ ] `docs/JSON_CONTRACT_V1.md` complete
- [ ] `docs/ERROR_HANDLING.md` complete
- [ ] All new code has docstrings
- [ ] README updated with agent descriptions

### Code Quality
- [ ] All new tests passing (target: 30+ new tests)
- [ ] No breaking changes to existing schemas
- [ ] No API calls in unit tests (all mocked)
- [ ] Consistent with project style (black, pytest)

---

## 📞 Success Handoff Criteria

**To Person 1 & 5:**
- [ ] All prompts documented + tested
- [ ] JSON Contract v1.0 finalized
- [ ] Integration ready for Phase 2 enrichment

**To Phase 2 Team:**
- [ ] Gap-Aggregator + Ranker ready for material prioritization
- [ ] Arbiter rules template (can be extended with business logic)
- [ ] Compliance + Devil's Advocate prompts ready for refinement

---

**Ready to start? Run this to get set up:**
```bash
cd makeathon
python -m pytest tests/ -v
```

**Questions?** Check `docs/` folder or existing test examples.
