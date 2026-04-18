# Phase 1 Vitamin D Database Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement database-first vitamin D clustering with real SQLite data, SKU parsing, and Equivalence-Agent integration using Claude API.

**Architecture:** Extract vitamin D SKUs from existing SQLite database, parse substance details, cluster by similarity, and feed real clusters to Equivalence-Agent for consolidation analysis. Cache external supplier evidence for offline demo capability.

**Tech Stack:** Python 3.11, SQLAlchemy, SQLite, OpenAI embeddings or sentence-transformers, Claude API (Anthropic SDK), scikit-learn clustering

---

## File Structure

```
makeathon/
├── database/
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy models for 6-table structure
│   └── connection.py      # Database connection and session management
├── parsing/
│   ├── __init__.py
│   └── sku_parser.py      # Vitamin D SKU parsing logic
├── clustering/
│   ├── __init__.py
│   └── vitamin_d_cluster.py  # Clustering and grouping logic
├── enrichment/
│   ├── __init__.py
│   └── supplier_cache.py  # External evidence caching system
├── pipeline/
│   ├── __init__.py
│   └── phase1_pipeline.py # End-to-end orchestration
├── tests/
│   ├── test_database/
│   ├── test_parsing/
│   ├── test_clustering/
│   ├── test_enrichment/
│   └── test_pipeline/
├── data/
│   └── external_evidence.json  # Cached supplier compliance data
├── equivalence_agent.py   # Existing - enhance with Claude API
└── schemas.py            # Existing - keep as is
```

### Task 1: Database Models and Connection

**Files:**
- Create: `database/__init__.py`
- Create: `database/models.py`
- Create: `database/connection.py`
- Create: `tests/test_database/test_models.py`

- [ ] **Step 1: Write failing test for database connection**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Create database package structure**
- [ ] **Step 4: Implement SQLAlchemy models**
- [ ] **Step 5: Implement database connection**
- [ ] **Step 6: Run test to verify it passes**
- [ ] **Step 7: Commit database foundation**

### Task 2: SKU Parsing for Vitamin D

**Files:**
- Create: `parsing/__init__.py`
- Create: `parsing/sku_parser.py`
- Create: `tests/test_parsing/test_sku_parser.py`

- [ ] **Step 1: Write failing tests for SKU parsing**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Create parsing package structure**
- [ ] **Step 4: Implement ParsedSKU dataclass**
- [ ] **Step 5: Implement VitaminDSKUParser class**
- [ ] **Step 6: Run tests to verify they pass**
- [ ] **Step 7: Commit SKU parsing implementation**

### Task 3: Database Query for Vitamin D Products

**Files:**
- Create: `database/vitamin_d_queries.py`
- Create: `tests/test_database/test_vitamin_d_queries.py`

- [ ] **Step 1: Write failing test for vitamin D product extraction**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement VitaminDExtractor class**
- [ ] **Step 4: Update database __init__.py**
- [ ] **Step 5: Run tests to verify they pass**
- [ ] **Step 6: Create test script to explore real data**
- [ ] **Step 7: Run data exploration script**
- [ ] **Step 8: Commit database query implementation**

### Task 4: Clustering Engine for Vitamin D

**Files:**
- Create: `clustering/__init__.py`
- Create: `clustering/vitamin_d_cluster.py`
- Create: `tests/test_clustering/test_vitamin_d_cluster.py`

- [ ] **Step 1: Write failing tests for vitamin D clustering**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Create clustering package structure**
- [ ] **Step 4: Implement VitaminDCluster dataclass**
- [ ] **Step 5: Implement VitaminDClusterer class**
- [ ] **Step 6: Run tests to verify they pass**
- [ ] **Step 7: Commit clustering implementation**

### Task 5: Enhanced Equivalence-Agent with Claude API

**Files:**
- Modify: `equivalence_agent.py`
- Create: `tests/test_equivalence_agent_real.py`

- [ ] **Step 1: Write failing test for real Claude API integration**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Install Anthropic SDK**
- [ ] **Step 4: Add Claude API integration to equivalence_agent.py**
- [ ] **Step 5: Update call_equivalence_agent function**
- [ ] **Step 6: Create environment file template**
- [ ] **Step 7: Add .env to .gitignore if not already there**
- [ ] **Step 8: Run tests with mock (should pass)**
- [ ] **Step 9: Commit Claude API integration**

### Task 6: External Supplier Evidence Caching

**Files:**
- Create: `enrichment/__init__.py`
- Create: `enrichment/supplier_cache.py`
- Create: `data/external_evidence.json`
- Create: `tests/test_enrichment/test_supplier_cache.py`

- [ ] **Step 1: Write failing test for supplier evidence caching**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Create enrichment package structure**
- [ ] **Step 4: Create external evidence JSON file**
- [ ] **Step 5: Implement SupplierEvidence and SupplierEvidenceCache classes**
- [ ] **Step 6: Run tests to verify they pass**
- [ ] **Step 7: Create evidence exploration script**
- [ ] **Step 8: Run evidence exploration**
- [ ] **Step 9: Commit supplier evidence caching**

### Task 7: End-to-End Phase 1 Pipeline

**Files:**
- Create: `pipeline/__init__.py`
- Create: `pipeline/phase1_pipeline.py`
- Create: `tests/test_pipeline/test_phase1_pipeline.py`

- [ ] **Step 1: Write failing test for complete pipeline**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Create pipeline package structure**
- [ ] **Step 4: Implement Phase1Result dataclass**
- [ ] **Step 5: Implement Phase1Pipeline class**
- [ ] **Step 6: Run tests to verify they pass**
- [ ] **Step 7: Create pipeline demo script**
- [ ] **Step 8: Run complete pipeline demo**
- [ ] **Step 9: Commit end-to-end pipeline**

### Task 8: Final Integration and Documentation

**Files:**
- Modify: `README.md`
- Create: `requirements.txt`
- Create: `PHASE1_SETUP.md`

- [ ] **Step 1: Create requirements.txt**
- [ ] **Step 2: Update main README.md**
- [ ] **Step 3: Create Phase 1 setup guide**
- [ ] **Step 4: Run final verification tests**
- [ ] **Step 5: Run complete demo to verify everything works**
- [ ] **Step 6: Final commit**