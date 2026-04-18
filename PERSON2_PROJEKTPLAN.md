# Person 2: AI/LLM Engineer - Projektplan

**Rolle:** AI/LLM Engineer  
**Verantwortung:** Agent-Prompts, JSON-Kontrakte, Gap-Aggregation & Ranking, Arbiter-Logik, Unsicherheits-Handling  
**Phase:** Phase 1 Fundament (Fr 20:00 – 24:00 = 4h)  
**Eventuell Phase 2:** Compliance-Agent Prompt Refinement

---

## 📋 Übersicht der Aufgaben

| Task | Status | Priorität | Aufwand | Dependencies |
|------|--------|-----------|---------|--------------|
| 1. Equivalence-Agent Prompt finalisieren | ⚠️ Partial | P0 | 45m | DB data (Person 1) |
| 2. Compliance-Agent CSV-basiert | ⚠️ Partial | P0 | 45m | DB data (Person 1) |
| 3. Devil's Advocate Prompt entwerfen | ❌ Not started | P1 | 45m | Equivalence Prompt |
| 4. JSON Contract v1.0 dokumentieren | ❌ Not started | P0 | 30m | Existing schemas.py |
| 5. Gap-Aggregator implementieren | ❌ Not started | P1 | 90m | JSON Contract |
| 6. Gap-Ranker implementieren | ❌ Not started | P1 | 60m | Gap-Aggregator |
| 7. Arbiter-Regeln definieren & testen | ❌ Not started | P2 | 45m | Gap-Ranker |
| 8. Insufficient_Evidence Handling | ❌ Not started | P0 | 60m | All prompts |
| 9. Parsing robustness Tests | ❌ Not started | P1 | 45m | All prompts |
| 10. Integrations-Test (end-to-end) | ❌ Not started | P1 | 45m | All components |

**Geschätzte Gesamtdauer:** ~6h (Phase 1: 4h + Phase 2 prep: 2h)

---

## 🎯 Phase 1 Fundament (Fr 20:00 – 24:00)

### Task 1: Equivalence-Agent Prompt finalisieren (45 min)
**Status:** ⚠️ Partially Complete (exists in `equivalence_agent.py`)  
**Ziel:** Production-ready Equivalence-Prompt für Vitamin D Cluster-Analyse  

**Checklist:**
- [ ] Aktuellen Prompt in `equivalence_agent.py` reviewen
- [ ] German → English übersetzten (für Claude API Stabilität)
- [ ] Confidence-Scoring Logik schärfen
- [ ] Claim-Struktur validieren
- [ ] Missing-Evidence Format standardisieren
- [ ] JSON-Output Schema testen mit `pytest tests/test_parsing/test_equivalence_agent_real.py`
- [ ] Fehlercases documentieren (z.B. unvollständige Daten)

**Input:** Cluster data von Person 3+4 (SKU, Supplier, Company)  
**Output:** `EquivalenceAgentInput` + `AgentOutput` JSON  
**Files:**
- `equivalence_agent.py` (Prompt + mock)
- `schemas.py` (Datenstrukturen)

---

### Task 2: Compliance-Agent: Certificate Status + Supply Chain Synergy (45 min)
**Status:** ⚠️ Simplified  
**Ziel:** MVP-basierte CSV-Compliance mit aussagekräftigem Reasoning  

**MVP-Ansatz (keine Prompts, keine APIs):**
- [ ] Create `data/suppliers.csv` with country + customer_count
- [ ] Create `data/customer_requirements.csv` with quality specs
- [ ] Write `SimpleComplianceChecker` class (~80 lines)
- [ ] Implement 2 core reasoning factors:
  - ✅ **Certificate Status:** Required vs. Available certs
  - ✅ **Supply Chain Synergy:** Consolidation savings potential (10% per supplier eliminated)
- [ ] ComplianceAgentOutput Schema in `schemas.py`
- [ ] Unit-Tests schreiben (min. 4 test cases)

**Reasoning Output (Beispiel):**
```
"✓ Certs: cGMP, ISO 9001 complete | 💰 Synergy: 20% savings (3→1 supplier) | 🌍 Geo: Low (NL)"
```

**Input:** Material + Supplier + Customer  
**Output:** `ComplianceAgentOutput` JSON mit Cert Status + Synergy Score  
**Files:**
- `agents/simple_compliance_checker.py` (neu - ~80 lines)
- `data/suppliers.csv` (neu)
- `data/customer_requirements.csv` (neu)
- `schemas.py` (ComplianceAgentOutput)

---

### Task 3: Devil's Advocate Prompt (45 min)
**Status:** ❌ Not Started  
**Ziel:** Kontra-Argumente zu Consolidation-Empfehlungen generieren  

**Checklist:**
- [ ] Prompt entwerfen: "Gegeben ein RECOMMENDED Szenario, was könnte schiefgehen?"
- [ ] Risk-Categories:
  - Quality loss (Bioavailability, dissolution rate)
  - Regulatory rejection (Supply chain audits fail)
  - Customer resistance (Brand loyalty, specification lock-in)
  - Cost overrun (Integration testing, new supplier audit)
- [ ] Strukturiertes Output-Format definieren
- [ ] Schema in `schemas.py` hinzufügen
- [ ] Mock-Tests schreiben

**Input:** `AgentOutput` (Equivalence Verdict + Reasoning)  
**Output:** `DevilsAdvocateOutput` JSON mit Risks + Severity  
**Files:**
- `agents/devils_advocate_agent.py` (neu)
- `schemas.py` (DevilsAdvocateOutput)

---

## 🔧 Phase 1 Core Implementation

### Task 4: JSON Contract v1.0 dokumentieren (30 min)
**Status:** ⚠️ Partial (schemas.py existiert)  
**Ziel:** Klare, versionierte Daten-Verträge für alle Agents  

**Checklist:**
- [ ] `schemas.py` reviewen → alle Klassen auflisten
- [ ] JSON-Contract Dokument schreiben: `docs/JSON_CONTRACT_V1.md`
- [ ] Für jedes Schema:
  - Feldname + Typ + Beschreibung
  - Constraints (z.B. 0.0-1.0 für confidence)
  - Beispiel-JSON
- [ ] Versioning-Logik definieren (major.minor.patch)
- [ ] Breaking Changes Policy dokumentieren

**Schema-Übersicht:**
```
EquivalenceAgentInput → AgentOutput
ComplianceAgentInput → ComplianceAgentOutput  
DevilsAdvocateInput → DevilsAdvocateOutput
GapAggregationInput → AggregatedGaps
GapRankingInput → RankedGaps
ArbiterInput → ArbiterVerdictOutput
```

**Output:** `docs/JSON_CONTRACT_V1.md`  
**Files:** `schemas.py` (update docstrings)

---

### Task 5: Gap-Aggregator implementieren (90 min)
**Status:** ❌ Not Started  
**Ziel:** Sammle alle fehlenden Informationen von Equivalence, Compliance, Devil's Advocate  

**Architecture:**
```python
class GapAggregator:
    def aggregate(self, 
        equivalence: AgentOutput,
        compliance: ComplianceAgentOutput, 
        devils_advocate: DevilsAdvocateOutput
    ) -> AggregatedGaps:
        # Extrahiere missing_evidence from all sources
        # Kategorisiere nach Type (regulatory, technical, commercial)
        # Füge Confidence-Scores hinzu
        # Return strukturiertes AggregatedGaps Objekt
```

**Checklist:**
- [ ] `AggregatedGaps` Schema in `schemas.py` definieren
- [ ] Aggregator-Klasse in `agents/gap_aggregator.py` schreiben
- [ ] Gap-Kategorisierung:
  - `regulatory_gaps` (Compliance + missing approvals)
  - `technical_gaps` (Quality, bioavailability)
  - `commercial_gaps` (Customer feedback, pricing)
  - `supply_chain_gaps` (Audits, certifications)
- [ ] Unit-Tests schreiben (min. 5 scenarios)
- [ ] Integration mit Phase1Pipeline testen

**Input:** Outputs von Task 1, 2, 3  
**Output:** `AggregatedGaps` mit priorisierter Gap-Liste  
**Files:**
- `agents/gap_aggregator.py` (neu)
- `tests/test_agents/test_gap_aggregator.py` (neu)

---

### Task 6: Gap-Ranker implementieren (60 min)
**Status:** ❌ Not Started  
**Ziel:** Priorisiere Gaps nach Impact & Feasibility  

**Architecture:**
```python
class GapRanker:
    def rank(self, aggregated_gaps: AggregatedGaps) -> RankedGaps:
        # Score jedes Gap nach Kriterien:
        # - Business Impact (1-10)
        # - Effort to resolve (1-10)
        # - Risk if unresolved (1-10)
        # - Sortiere nach Priorität
        # Return RankedGaps mit Priority-Liste
```

**Scoring-Logik:**
```
Priority Score = (Impact × 0.4) + (Risk × 0.4) - (Effort × 0.2)
```

**Checklist:**
- [ ] `RankedGaps` + `RankedGap` Schemas in `schemas.py`
- [ ] Ranker-Klasse in `agents/gap_ranker.py`
- [ ] Scoring-Gewichte definieren (adjustable via config)
- [ ] Tests mit verschiedenen Gap-Mixen (100% regulatory, 100% commercial, mixed)
- [ ] Output: Top 5 Gaps + Rationale

**Input:** `AggregatedGaps`  
**Output:** `RankedGaps` (sorted list + top-5)  
**Files:**
- `agents/gap_ranker.py` (neu)
- `tests/test_agents/test_gap_ranker.py` (neu)

---

### Task 7: Arbiter-Regeln definieren & testen (45 min)
**Status:** ❌ Not Started  
**Ziel:** Finale Entscheidung: RECOMMENDED → APPROVED vs. BLOCKED?  

**Arbiter-Logik:**
```
IF ranked_gaps.count == 0:
    APPROVED (alle Gaps gelöst)
ELIF ranked_gaps[0].priority >= 8 AND ranked_gaps[0].category IN [regulatory, safety]:
    BLOCKED (kritische Gaps ungelöst)
ELIF top_3_gaps.avg_effort > 40 AND timeline < 6_months:
    DEFERRED (zu teuer jetzt)
ELSE:
    APPROVED_WITH_CONDITIONS (Top 5 Gaps zu lösen)
```

**Checklist:**
- [ ] `ArbiterVerdictOutput` Schema definieren (APPROVED | BLOCKED | DEFERRED)
- [ ] `ArbiterEngine` Klasse in `agents/arbiter.py`
- [ ] Conditions als konfigurierbare Rules (JSON)
- [ ] Tests: mind. 8 Szenarien (all-clear, critical-gap, budget-issue, etc.)
- [ ] Audit-Trail: Zeige welche Rule welche Entscheidung führte

**Input:** `RankedGaps` + Timeline/Budget Context  
**Output:** `ArbiterVerdictOutput`  
**Files:**
- `agents/arbiter.py` (neu)
- `agents/arbiter_rules.json` (konfigurierbar)
- `tests/test_agents/test_arbiter.py` (neu)

---

### Task 8: Insufficient_Evidence Handling (60 min)
**Status:** ❌ Not Started  
**Ziel:** Strukturiertes Fallback bei unvollständigen Daten  

**Unsicherheits-Framework:**
```python
class EvidenceLevel(Enum):
    COMPLETE = 0.95-1.0         # All data present
    SUBSTANTIAL = 0.80-0.95     # 80%+ data, minor gaps
    PARTIAL = 0.50-0.80         # Significant gaps, can estimate
    INSUFFICIENT = 0.0-0.50     # Cannot make confident recommendation

@dataclass
class EvidenceQuality:
    level: EvidenceLevel
    confidence: float
    gaps: List[str]
    fallback_strategy: str  # "defer", "proceed_cautious", "block"
```

**Checklist:**
- [ ] `EvidenceQuality` + `EvidenceLevel` in `schemas.py`
- [ ] Evidence-Quality-Checker in `agents/evidence_checker.py`
- [ ] Für jede Agent-Output: Confidence-Level berechnen
- [ ] Fallback-Strategien:
  - `insufficient_evidence` → DEFERRED (Arbiter blockiert)
  - `partial` → APPROVED_WITH_CONDITIONS (Top gaps required)
  - `substantial` → normal flow
- [ ] Tests: Szenarien mit fehlenden Suppliern, Regulations, etc.
- [ ] Dokumentation: Wann fällt man in welchen Fallback?

**Output:** `EvidenceQuality` für jede Entscheidung  
**Files:**
- `agents/evidence_checker.py` (neu)
- `tests/test_agents/test_evidence_checker.py` (neu)

---

### Task 9: Parsing robustness Tests (45 min)
**Status:** ❌ Not Started  
**Ziel:** JSON-Parsing bei bösen Inputs nicht crashen  

**Edge Cases zu testen:**
- [ ] Missing required fields (z.B. kein `verdict`)
- [ ] Extra unknown fields (forward-compatibility)
- [ ] Falsche Datentypen (int statt string in `confidence`)
- [ ] Malformed JSON (trailing comma, duplicate keys)
- [ ] Unicode edge cases (Chinese supplier names, emojis)
- [ ] Large numbers (very long claim lists, 100+ gaps)
- [ ] Null values in optional vs. required fields
- [ ] Claude API returns non-JSON (fallback needed?)

**Checklist:**
- [ ] `tests/test_parsing/test_robustness.py` schreiben
- [ ] Für jeden Edge Case: try-except + sensible default
- [ ] Unit-Tests mindestens 10 Szenarien
- [ ] Integration: Teste mit Mock Claude (return bad JSON)
- [ ] Dokumentiere Fallback-Verhalten in `docs/ERROR_HANDLING.md`

**Output:** Robust JSON parser + error handling  
**Files:**
- `agents/json_parser.py` (oder in `equivalence_agent.py`)
- `tests/test_parsing/test_robustness.py` (neu)

---

### Task 10: Integrations-Test (end-to-end) (45 min)
**Status:** ❌ Not Started  
**Ziel:** Alle Agents zusammen testen mit realem Cluster-Data  

**Test-Szenarios:**
1. **Happy Path:** Equivalence ✅ → Compliance ✅ → No major gaps → APPROVED
2. **Regulatory Blocker:** Equivalence OK → Compliance ❌ Approval missing → BLOCKED
3. **Technical + Commercial:** Multiple gap types → top 5 → APPROVED_WITH_CONDITIONS
4. **Insufficient Evidence:** Missing supplier data → confidence < 0.5 → DEFERRED

**Checklist:**
- [ ] `tests/test_integration/test_full_analysis_flow.py` schreiben
- [ ] Test fixture mit 3-4 Vitamin D Cluster-Szenarien
- [ ] Mock Equivalence + Compliance + Devil's Advocate outputs
- [ ] Run durch full pipeline:
  - Equivalence → Compliance → Devil's Advocate
  - Gap-Aggregation → Gap-Ranking → Arbiter
  - Final Verdict + Rationale
- [ ] Assert auf erwartete Output-Struktur + Verdicts
- [ ] Performance test (< 5s für 1 Cluster)

**Output:** Green integration tests + Performance baseline  
**Files:**
- `tests/test_integration/test_full_analysis_flow.py` (neu)

---

## 📁 File-Struktur nach Completion

```
agents/
  ├── __init__.py
  ├── equivalence_agent.py           [UPDATED]
  ├── simple_compliance_checker.py   [NEW - Task 2]
  ├── devils_advocate_agent.py       [NEW - Task 3]
  ├── gap_aggregator.py              [NEW - Task 5]
  ├── gap_ranker.py                  [NEW - Task 6]
  ├── arbiter.py                     [NEW - Task 7]
  ├── arbiter_rules.json             [NEW - Task 7]
  ├── evidence_checker.py            [NEW - Task 8]
  └── json_parser.py                 [NEW - Task 9]

data/
  ├── suppliers.csv                  [NEW - Task 2]
  ├── customer_requirements.csv      [NEW - Task 2]
  └── external_evidence.json         [EXISTING]

schemas.py                            [UPDATED - Tasks 1,2,3,4,5,6,7,8]

docs/
  ├── JSON_CONTRACT_V1.md        [NEW - Task 4]
  └── ERROR_HANDLING.md          [NEW - Task 9]

tests/test_agents/
  ├── test_equivalence_agent_real.py     [EXISTING]
  ├── test_simple_compliance_checker.py  [NEW - Task 2]
  ├── test_devils_advocate.py            [NEW - Task 3]
  ├── test_gap_aggregator.py             [NEW - Task 5]
  ├── test_gap_ranker.py                 [NEW - Task 6]
  ├── test_arbiter.py                    [NEW - Task 7]
  └── test_evidence_checker.py           [NEW - Task 8]

tests/test_parsing/
  └── test_robustness.py         [NEW - Task 9]

tests/test_integration/
  └── test_full_analysis_flow.py [NEW - Task 10]
```

---

## ⏱️ Timeline Vorschlag (Phase 1)

| Zeit | Task | Dauer | Person 2 |
|------|------|-------|----------|
| 20:00-20:45 | Task 1: Equivalence finalisieren | 45m | Review + finalize |
| 20:45-21:30 | Task 2: Compliance CSV + Checker | 45m | CSV setup + simple code |
| 21:45-22:30 | Task 3: Devil's Advocate Prompt | 45m | Write prompt |
| 22:30-23:00 | Task 4: JSON Contract Doc | 30m | Document |
| 23:00-24:00 | Task 5-9: Start Gap-Aggregator + Tests | 60m | Core + tests |

**Phase 1 Output:**
- ✅ Equivalence Prompt v1.0
- ✅ Compliance Prompt skeleton  
- ✅ Devil's Advocate Prompt skeleton
- ✅ JSON Contract v1.0 doc
- ⚠️ Gap-Aggregator started (can be finished in Phase 2)

---

## 🔗 Dependencies & Handoff Points

**From Person 1 (DB/Enrichment):**
- Supplier data complete + cached
- External evidence API responses

**From Person 3 (Parsing):**
- Robust SKU parsing ✅
- Material-to-Company mappings ✅

**From Person 4 (Clustering):**
- Clusters with semantic similarity ✅
- Cluster quality metrics ✅

**From Person 5 (Orchestration):**
- Pipeline runs all components ✅
- Phase1Pipeline._analyze_cluster() calls equivalence agent

**To Person 1 (Phase 2):**
- Compliance-Agent prompt (needs regulatory data)
- Evidence requirements document

**To Person 5 (Phase 2):**
- All Agent-Prompts finalized
- JSON Contract v1.0
- Gap-Aggregator + Ranker for next phase

---

## 🚀 Success Criteria (Phase 1 EOD)

- [ ] Equivalence-Agent finalized + tested
- [ ] Compliance-Agent prompt skeleton written
- [ ] Devil's Advocate prompt skeleton written
- [ ] JSON Contract v1.0 documented (all schemas)
- [ ] All 4 prompts follow consistent format + error handling
- [ ] Gap-Aggregator implemented + unit-tested
- [ ] README updated with agent descriptions
- [ ] All new code follows existing test standards (pytest)
- [ ] No breaking changes to existing schemas.py imports

**Stretch Goals (if time):**
- [ ] Gap-Ranker implemented
- [ ] Arbiter rules skeleton
- [ ] Full integration test passing

---

## 📚 Useful Resources

**Agent Prompt Patterns:**
- Check `equivalence_agent.py` for existing structure
- Use `mock_equivalence_analysis()` for testing format

**JSON Parsing:**
- See `tests/test_parsing/test_equivalence_agent_real.py` for examples
- Test both mock + real Claude responses

**Claude API Docs:**
- https://docs.anthropic.com/
- Messages API for JSON mode (structured output)

**Schema Updates:**
- Always add docstring + examples to new schemas
- Use Pydantic for validation

---

## 🎓 Notes for Execution

1. **Start with Equivalence review** - It's already 80% done, just needs refinement
2. **Parallel Compliance + Devil's Advocate** - Similar structure, can iterate
3. **Gap-Aggregator is the hardest** - Start early if time allows
4. **Testing first** - Write tests alongside prompts (not after)
5. **Mock Claude responses** - Use `@patch` for reliability, no API calls in unit tests
6. **Versioning** - If you change JSON schemas, update `JSON_CONTRACT_V1.md` immediately
