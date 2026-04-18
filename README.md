# SupplySkip - AI-Powered Compliance Intelligence

**Google ADK + Gemini 2.5 Flash** powered supplier compliance system with real-time web intelligence and evidence caching.

## Overview

SupplySkip uses Google's Agent Development Kit (ADK) with Gemini 2.5 Flash to provide intelligent, real-time compliance checking for supplier evaluation. The system combines live web search, direct supplier website analysis, and sophisticated evidence caching to deliver comprehensive compliance insights.

## Architecture

### Core Technologies

- **Google ADK (Agent Development Kit)**: Multi-agent orchestration framework
- **Gemini 2.5 Flash**: High-performance language model for compliance analysis
- **Live Web Search**: Real-time Google Search integration
- **Evidence Cache**: Persistent supplier compliance data storage

### Agent System

The system operates through two specialized agents:

#### 1. ProducerAgent (`req_gatherer.py`)
- **Purpose**: Discovers EU/US compliance requirements for raw materials
- **Model**: Gemini 2.5 Flash
- **Capabilities**:
  - Live Google Search for regulatory requirements
  - URL content extraction from regulatory websites
  - Compliance standard identification (EFSA, 21 CFR 111, cGMP)

#### 2. SupplierAgent (`req_gatherer.py`)  
- **Purpose**: Analyzes specific supplier websites for compliance data
- **Model**: Gemini 2.5 Flash
- **Capabilities**:
  - Direct supplier website content analysis
  - Compliance certification extraction
  - Real-time supplier data validation

### Evidence Cache System

The evidence cache (`backend/enrichment/supplier_cache.py`) provides persistent storage for supplier compliance intelligence:

- **SupplierEvidence**: Structured compliance data (certifications, pricing, MOQ, lead times)
- **Query Interface**: Fast retrieval by supplier, substance, or certification
- **Cost Analysis**: Price range extraction and cost-effectiveness ranking
- **Premium Filtering**: USP and quality certification filtering

## Quick Start

### Basic Usage

```python
from req_gatherer import ProducerAgent, SupplierAgent

# Initialize agents
producer = ProducerAgent()
producer.set_up()

supplier = SupplierAgent()
supplier.set_up()

# Find compliance requirements
requirements = producer.query("EU compliance requirements for Vitamin D3")

# Analyze specific suppliers
compliance_data = supplier.query("Check DSM website for Vitamin D3 compliance certifications")
```

### Evidence Cache Integration

```python
from backend.enrichment.supplier_cache import SupplierEvidenceCache

# Load cached evidence
cache = SupplierEvidenceCache()
evidence = cache.load_evidence()

# Query by supplier
dsm_evidence = cache.get_evidence_for_supplier("DSM")
print(f"Certifications: {dsm_evidence.quality_certifications}")

# Find cost-effective suppliers
best_value = cache.get_most_cost_effective("Vitamin D3")
premium_suppliers = cache.get_premium_suppliers("Vitamin D3")
```

## Key Features

### 🌐 Live Web Search
- Real-time Google Search integration
- Dynamic regulatory requirement discovery
- Current compliance standard tracking

### 🏭 Supplier Website Analysis  
- Direct supplier website content extraction
- Automated compliance certification detection
- Real-time data validation

### 💾 Evidence Cache
- Persistent supplier intelligence storage
- Fast query and filtering capabilities
- Cost-effectiveness analysis

### 🎯 Compliance Focus
- **EU**: Pre-market authorization, EFSA safety, traceability requirements
- **US**: Post-market cGMP (21 CFR 111), ID/purity testing, supplier qualification

## Installation

```bash
# Install Google ADK dependencies
pip install google-adk

# Install Vertex AI requirements  
pip install vertexai

# Set up authentication
gcloud auth application-default login
```

## System Requirements

- Google Cloud Project with Vertex AI API enabled
- Agent Development Kit (ADK) access
- Gemini 2.5 Flash model access
