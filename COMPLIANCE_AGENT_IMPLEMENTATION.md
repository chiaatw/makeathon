# Task 2: Compliance-Agent Implementierung (MVP)

> **Für Person 2: How to implement the Compliance-Agent with CSV + Simple Logic**

**Duration:** 45 minutes (vs. 60 min in original plan)  
**Complexity:** Simple (CSV + ~100 lines Python)  
**No APIs, no Prompts, no Complexity**

---

## 📋 Overview

Das Compliance-Agent soll prüfen: **Kann dieser Supplier das liefern, was dieser Customer braucht?**

**MVP fokussiert auf 2 Faktoren:**
1. **Certificate Status** — Hat der Supplier alle erforderlichen Zertifikate?
2. **Supply Chain Synergy** — Wie viel können wir durch Konsolidation sparen?

**Reasoning Output (für Multi-Agent):**
```
"✓ Certs: cGMP, ISO 9001 complete | 💰 Synergy: 20% savings (3→1 supplier) | 🌍 Geo: Low (NL)"
```

---

## ✅ Implementierungs-Schritte (45 min)

### Schritt 1: Create `data/suppliers.csv` (5 min)

```csv
supplier,country,current_customer_count
DSM,Netherlands,5
BASF,Germany,4
Prinova USA,USA,2
```

**Datei:** `data/suppliers.csv`

---

### Schritt 2: Create `data/customer_requirements.csv` (5 min)

```csv
company_name,quality_tier,certificates_required,potency_range,dissolution_min,impurities_max
PharmaCorp,PHARMA_GRADE,"cGMP,ISO 9001,ISO 14644",97.0-103.0,90,0.05
FoodSupplementCo,SUPPLEMENT_GRADE,"GMP,ISO 9001",95.0-105.0,75,0.1
Cosmetics Inc,COSMETIC_GRADE,GMP,90.0-110.0,0,0.2
```

**Datei:** `data/customer_requirements.csv`

---

### Schritt 3: Create `agents/simple_compliance_checker.py` (20 min)

**Main class: `SimpleComplianceChecker`**

```python
class SimpleComplianceChecker:
    """CSV-based compliance checking."""
    
    def check(self, material: str, supplier: str, customer: str) -> ComplianceAgentOutput:
        # 1. Get supplier info from CSV
        # 2. Get customer requirements from CSV
        # 3. Check certificates (Required vs. Available)
        # 4. Calculate synergy (consolidation savings)
        # 5. Generate reasoning for multi-agent
        # 6. Return ComplianceAgentOutput
```

**Key Methods:**
- `check()` — Main entry point
- `_get_supplier_info()` — Load supplier from CSV
- `_get_customer_requirements()` — Load customer from CSV
- `_check_certificates()` — Compare required vs. available certs
- `_calculate_synergy()` — Calculate consolidation savings (10% per supplier eliminated)
- `_assess_geo_risk()` — Simple country-based risk assessment
- `_generate_reasoning()` — Multi-agent friendly output

**File has been created:** `agents/simple_compliance_checker.py`

---

### Schritt 4: Update `schemas.py` (5 min)

**Add ComplianceAgentOutput:**

```python
@dataclass
class ComplianceAgentOutput:
    """Output from compliance check."""
    compliance_status: str  # "COMPLIANT", "NON_COMPLIANT", "INSUFFICIENT_DATA"
    confidence: float  # 0.0-1.0
    reasoning: str  # Human-readable summary for multi-agent
    synergy_potential: float = 0.0  # % savings from consolidation
    issues: List[Dict] = None  # Details about any issues
```

---

### Schritt 5: Create Integration Wrapper `agents/compliance_agent.py` (5 min)

```python
def call_compliance_agent(material: str, supplier: str, customer: str) -> ComplianceAgentOutput:
    """Simple wrapper for integration."""
    checker = SimpleComplianceChecker()
    return checker.check(material, supplier, customer)
```

**File has been created:** `agents/compliance_agent.py`

---

### Schritt 6: Write Unit Tests (10 min)

**Create:** `tests/test_agents/test_simple_compliance_checker.py`

**Test cases (min. 4, ideally 10):**

```python
def test_compliant_supplier_pharma():
    """DSM → PharmaCorp should be COMPLIANT."""
    result = checker.check("Vitamin D3", "DSM", "PharmaCorp")
    assert result.compliance_status == "COMPLIANT"

def test_non_compliant_missing_certs():
    """Prinova USA → PharmaCorp should be NON_COMPLIANT (missing cGMP)."""
    result = checker.check("Vitamin D3", "Prinova USA", "PharmaCorp")
    assert result.compliance_status == "NON_COMPLIANT"

def test_synergy_calculation():
    """Pharma tier = 3 suppliers = 20% savings."""
    result = checker.check("Vitamin D3", "DSM", "PharmaCorp")
    assert result.synergy_potential == 20.0

def test_reasoning_format():
    """Reasoning should include cert status, synergy, geo risk."""
    result = checker.check("Vitamin D3", "DSM", "PharmaCorp")
    assert "|" in result.reasoning  # Multiple parts
    assert "Certs" in result.reasoning
    assert "Synergy" in result.reasoning
```

**File has been created:** `tests/test_agents/test_simple_compliance_checker.py`

---

## 🧪 Run Tests

```bash
pytest tests/test_agents/test_simple_compliance_checker.py -v

# Expected output: 10+ tests passing
```

---

## 📊 Example Outputs

### Example 1: Compliant ✅

```python
result = call_compliance_agent("Vitamin D3", "DSM", "PharmaCorp")

# Output:
{
    "compliance_status": "COMPLIANT",
    "confidence": 0.95,
    "reasoning": "✓ Certs: cGMP, ISO 9001, ISO 14644 complete | 💰 Synergy: 20% savings (3→1) | 🌍 Geo: Low (NL)",
    "synergy_potential": 20.0
}
```

### Example 2: Non-Compliant ❌

```python
result = call_compliance_agent("Vitamin D3", "Prinova USA", "PharmaCorp")

# Output:
{
    "compliance_status": "NON_COMPLIANT",
    "confidence": 0.5,
    "reasoning": "⚠️ Certs: Missing cGMP, ISO 9001, ISO 14644 | 💰 Synergy: 20% savings | 🌍 Geo: Low (USA)",
    "issues": ["cGMP", "ISO 9001", "ISO 14644"],
    "synergy_potential": 20.0
}
```

### Example 3: Unknown Supplier ❓

```python
result = call_compliance_agent("Vitamin D3", "UnknownCorp", "PharmaCorp")

# Output:
{
    "compliance_status": "INSUFFICIENT_DATA",
    "confidence": 0.0,
    "reasoning": "Supplier 'UnknownCorp' not found in database",
    "issues": None
}
```

---

## 🔌 Integration mit Multi-Agent

Der Compliance-Agent gibt **aussagekräftiges Reasoning**, das andere Agents verwenden können:

```
Equivalence-Agent sagt:
→ "Consolidate from 3 → 1 supplier (DSM) is technically feasible"

Compliance-Agent sagt:
→ "✓ Certs: OK | 💰 Synergy: 20% savings | 🌍 Geo: Low"

Devil's Advocate sagt:
→ "But what if DSM raises prices post-consolidation?"

Arbiter kombiniert:
→ "Synergy benefit (20% savings) outweighs quality-drift risk. APPROVED"
```

---

## 🎯 Success Criteria (Phase 1 EOD)

- [ ] `data/suppliers.csv` erstellt und befüllt
- [ ] `data/customer_requirements.csv` erstellt und befüllt
- [ ] `agents/simple_compliance_checker.py` implementiert
- [ ] `agents/compliance_agent.py` wrapper erstellt
- [ ] `ComplianceAgentOutput` in `schemas.py` definiert
- [ ] Unit-Tests geschrieben (min. 10 test cases)
- [ ] All tests passing: `pytest tests/test_agents/test_simple_compliance_checker.py -v`
- [ ] Reasoning output is aussagekräftig für Multi-Agent

---

## 💡 Why This MVP Works

| Aspekt | Alte Idee | MVP |
|--------|-----------|-----|
| Datenquellen | FDA API, USP DB, PDFs | CSVs |
| Complexity | Complex prompts + Claude API | Simple CSV logic |
| Zeit | 60+ min | 45 min |
| Wartung | APIs können kaputt gehen | Einfache CSVs zum Updaten |
| Testing | API mocking schwierig | Einfache Unit-Tests |
| **Wirkung** | Über-engineered | **Perfect für MVP** |

---

## 📝 Next Steps (Phase 2)

Wenn MVP funktioniert, kann man upgraden zu:
- Database statt CSV
- Supplier-Portal zum Ausfüllen
- PDF-Parser für Zertifikate
- Echte USP-Daten statt Heuristics

Aber für JETZT: **CSV + 100 Zeilen Code = ausreichend!**
