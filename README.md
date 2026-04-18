Agnes – AI Supply Chain Manager

Built at Q-Hack × Spherecast Hackathon 2026

Agnes is an AI-powered decision-support system for raw material sourcing in the Consumer Packaged Goods (CPG) industry. It identifies functionally equivalent components across fragmented supplier landscapes, verifies compliance requirements against external evidence, and produces explainable sourcing recommendations with full evidence trails.

The Problem
CPG companies regularly overpay for raw materials because sourcing is fragmented. The same ingredient — say, Vitamin D3 — may be purchased by 18 different product lines under 18 different internal SKUs, from 6 different suppliers, without anyone having visibility into the combined volume. The result: no negotiating leverage, no consolidation, and no systematic compliance verification.
Agnes solves this by reasoning across fragmented procurement data to surface consolidation opportunities — but only when compliance and quality requirements of the affected end products are genuinely met.

How Agnes Works
Agnes uses a multi-agent reasoning architecture where specialized agents argue against each other before a deterministic Arbiter issues a verdict. No single LLM gets to make the final call.
DB + External Evidence
        ↓
┌──────────────────────────────────────────────────────┐
│  LAYER 1 · DATA                                      │
│  SQLite: 61 companies · 1025 products · 40 suppliers │
└──────────────────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────────────────┐
│  LAYER 2 · PREPROCESSING                             │
│  SKU normalization · Embedding clustering            │
│  Fragmentation analysis                              │
└──────────────────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────────────────┐
│  LAYER 3 · MULTI-AGENT REASONING                     │
│  🟠 Equivalence Agent  – are these SKUs the same?    │
│  🟢 Compliance Agent   – does the supplier qualify?  │
│  🔴 Devil's Advocate   – what can go wrong?          │
│  🟣 Arbiter (deterministic) – final verdict          │
└──────────────────────────────────────────────────────┘
        ↓       ↕ evidence
┌──────────────────────────────────────────────────────┐
│  LAYER 4 · EXTERNAL ENRICHMENT                       │
│  Google ADK + Gemini 2.5 Flash · Supplier websites   │
│  Live web search · Evidence cache                    │
└──────────────────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────────────────┐
│  LAYER 5 · OUTPUT                                    │
│  Sourcing recommendation · Evidence trail            │
│  Information Gap list · React UI                     │
└──────────────────────────────────────────────────────┘
The Four Agents
AgentModelRole🟠 EquivalenceClaude (Anthropic)Identifies functionally interchangeable SKUs across companies and proposes supplier consolidation🟢 ComplianceRule-based + CSV dataChecks whether proposed suppliers meet quality and certification requirements of affected end products🔴 Devil's AdvocateClaude (Anthropic)Finds overlooked risks: single-sourcing dependency, missing certifications, geopolitical clustering, regulatory changes🟣 ArbiterDeterministic PythonIssues the final verdict based on objection severity — no LLM involved
Arbiter Decision Rules
Agent OutputsVerdictNo objections, confidence ≥ 0.7RECOMMENDEDOnly low-severity objections, confidence ≥ 0.6RECOMMENDED_WITH_CAVEATAt least one medium objectionREVIEW_REQUIREDAt least one high objectionBLOCKED_PENDING_EVIDENCE
Information Gap Loop
Every agent reports not just its verdict, but what it couldn't verify. Agnes surfaces this as a prioritized action list for the buyer:

"To raise confidence from 62% to 91%, I need: (1) Halal certificate for ADM, (2) Food-grade spec for SKU-42, (3) 2025 allergen report."


External Enrichment (Approach 2)
Agnes uses Google's Agent Development Kit (ADK) with Gemini 2.5 Flash to autonomously browse the web for real compliance evidence.
ProducerAgent researches what compliance a finished good requires (by visiting iHerb, Thrive Market, and similar product pages).
SupplierAgent visits each supplier's actual website to extract the certifications they explicitly state for a specific raw material.
The output — real URLs, real certification claims — is cached before the demo runs. Agnes never makes live web requests during presentation.
Development time:  python workflow_orchestrator.py → populates data/external_evidence.json
Demo time:         All agents read from cache → offline-capable, no network dependency

Tech Stack
LayerTechnologyLanguagePython 3.11DatabaseSQLite + SQLAlchemyLLM (Approach 1)Anthropic Claude (claude-opus-4-6)LLM (Approach 2)Google Gemini 2.5 Flash via Vertex AIAgent FrameworkGoogle ADK (Approach 2 enrichment)Clusteringscikit-learn AgglomerativeClusteringEmbeddingsOpenAI text-embedding-3-small / sentence-transformersBackend APIFastAPI + uvicornFrontendReact + TypeScript + Vite + shadcn/uiCachingJSON file cache (offline-demo-safe)OrchestrationPlain Python async — no LangChain

Database Schema
Company (61 rows)     – CPG brands (Centrum, NOW Foods, Thrive Market, ...)
Product (1025 rows)   – 149 finished goods + 876 raw materials
BOM (149 rows)        – one bill of materials per finished good
BOM_Component (1528)  – M:N: which raw materials go into which BOM
Supplier (40 rows)    – ingredient suppliers (ADM, Cargill, BASF, DSM, ...)
Supplier_Product (1633) – M:N: which suppliers provide which raw materials
Raw material SKUs encode the substance name directly:
RM-C1-calcium-citrate-05c28cc3   →  Company 1, Calcium Citrate
RM-C14-calcium-citrate-a3f91b2c  →  Company 14, same substance, different SKU
This fragmentation — the same ingredient under dozens of internal IDs — is the core problem Agnes solves.

Project Structure
.
├── backend/
│   ├── agents/
│   │   ├── compliance_agent.py       # Compliance checking logic
│   │   └── simple_compliance_checker.py
│   ├── api/
│   │   ├── main.py                   # FastAPI app
│   │   ├── models.py                 # Pydantic DTOs
│   │   └── services.py               # Job orchestration
│   ├── analysis/
│   │   └── fragmentation_analyzer.py
│   ├── clustering/
│   │   └── vitamin_d_cluster.py
│   ├── enrichment/
│   │   └── supplier_cache.py         # Evidence cache manager
│   └── parsing/
│       └── sku_parser.py
├── agents/                           # Enhanced agent architecture
│   ├── engine/compliance_engine.py
│   └── scoring/engine.py
├── data/
│   ├── external_evidence.json        # Cached web evidence (supplier certs, pricing)
│   ├── suppliers.csv                 # Supplier master data
│   └── customer_requirements.csv    # Company compliance requirements
├── database/
│   ├── connection.py
│   ├── models.py                     # SQLAlchemy ORM
│   └── vitamin_d_queries.py
├── pipeline/
│   └── phase1_pipeline.py            # End-to-end Approach 1 orchestration
├── Frontend/                         # React UI (Vite + shadcn)
├── db/
│   └── db.sqlite                     # Provided dataset
├── equivalence_agent.py              # 🟠 Equivalence Agent
├── devils_advocate_agent.py          # 🔴 Devil's Advocate Agent
├── schemas.py                        # JSON contract between agents
├── req_gatherer.py                   # Google ADK agent definitions (Approach 2)
├── workflow_orchestrator.py          # Approach 2 async orchestration
└── requirements.txt

Setup
Prerequisites

Python 3.11+
Node.js 18+
Anthropic API key
(Optional, for Approach 2) Google Cloud project with Vertex AI enabled

1. Clone and install
bashgit clone https://github.com/your-org/agnes-makeathon.git
cd agnes-makeathon

pip install -r requirements.txt
2. Environment variables
bash# Required for Approach 1 (multi-agent reasoning)
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Required for Approach 2 (web enrichment)
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
3. Backend
bashuvicorn backend.api.main:app --reload --port 8000
4. Frontend
bashcd Frontend
npm install
npm run dev
# → http://localhost:8080

Running the Analysis
Approach 1 – Multi-Agent Pipeline (offline, demo-safe)
bash# Run end-to-end analysis on Vitamin D3 cluster
python run_vitamin_d_demo.py

# Run Phase 1 pipeline with mock agents (no API key needed)
python run_phase1_pipeline.py

# Run with real Claude API
python -c "
from pipeline.phase1_pipeline import Phase1Pipeline
pipeline = Phase1Pipeline(use_mock_api=False)
result = pipeline.run()
print(result.execution_summary)
"
Approach 2 – Live Web Enrichment (requires GCP)
bash# Fetch real compliance data from supplier websites and cache it
python workflow_orchestrator.py

# Output: data/external_evidence.json populated with real URLs and cert data
Run Approach 2 once to populate the cache. All subsequent demo runs use the cache.
Test the Agents Individually
bash# Equivalence Agent
python equivalence_agent.py

# Devil's Advocate Agent
python devils_advocate_agent.py

# Full integration test
python final_integration_test.py

Demo: Vitamin D3 Consolidation
The demo walks through a real sourcing scenario with Vitamin D3 / Cholecalciferol.
Setup: 18 SKUs across 12 companies, 6 suppliers (DSM, BASF, Fermenta, Zhejiang Medicine, Prinova USA, Ashland), 4 end products with Halal certification.
What Agnes finds:

Equivalence Agent → all 18 SKUs are the same substance, recommends consolidation to DSM
Compliance Agent → DSM has USP, ISO 9001, FDA-registered — but no public Halal certificate
Devil's Advocate → 4 of the affected end products are Halal-certified; single-sourcing to DSM creates geopolitical risk (US-only production); medium supply chain concentration
Arbiter → BLOCKED_PENDING_EVIDENCE
Information Gap → "Resolve: (1) Halal certificate for DSM Vitamin D3, (2) designated backup supplier. Two procurement tickets. Estimated 2 business days."


Agent JSON Contract
All agents communicate through a shared schema defined in schemas.py:
json{
  "agent": "equivalence | compliance | devils_advocate",
  "verdict": "PROPOSED | RECOMMENDED | RECOMMENDED_WITH_CAVEAT | REVIEW_REQUIRED | BLOCKED_PENDING_EVIDENCE",
  "confidence": 0.74,
  "reasoning": "2-3 sentence justification",
  "claims": [
    {
      "claim": "DSM holds USP certification for Vitamin D3",
      "evidence_url": "https://www.dsm.com/...",
      "verified": true
    }
  ],
  "objections": [
    { "issue": "Halal certificate not publicly listed for DSM", "severity": "high" }
  ],
  "missing_evidence": [
    {
      "what": "Current Halal certificate for DSM Vitamin D3",
      "why_it_matters": "4 of 6 end products carry Halal certification",
      "confidence_lift_if_provided": 0.18
    }
  ]
}
Hallucination control: Agents may only set "verified": true when an evidence_url is present. All unverifiable claims must be placed in missing_evidence instead. The Devil's Advocate prompt explicitly prohibits invented citations.

Hackathon Context
Built at Q-Hack 2026 for the Spherecast challenge: designing an AI-powered decision-support system for sourcing in the CPG industry. The dataset covers 61 companies, 1025 products, and 40 suppliers in the supplement space.
Challenge emphasis: reasoning quality, trustworthiness, hallucination control, external evidence sourcing, substitution logic, compliance inference, and scalability.
