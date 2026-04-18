# Phase 1 Setup Guide

## Installation

### Prerequisites
- Python 3.11+
- SQLite (included with Python)
- Anthropic API key (optional, for real Claude analysis)

### Setup Steps

1. **Clone the repository**
   ```bash
   cd makeathon
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Activate:
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API (Optional)**
   ```bash
   cp .env.template .env
   # Edit .env and add: ANTHROPIC_API_KEY=your-key-here
   ```

5. **Verify installation**
   ```bash
   pytest tests/ -v
   ```

## Running the Pipeline

### Full Analysis
```bash
python run_phase1_pipeline.py
```

### Vitamin D Product Analysis
```bash
python run_vitamin_d_analysis.py
```

### Supplier Evidence Review
```bash
python run_supplier_evidence_analysis.py
```

## Test Suite

### Run all tests
```bash
pytest tests/ -v
```

### Run specific module tests
```bash
pytest tests/test_parsing/ -v
pytest tests/test_clustering/ -v
pytest tests/test_database/ -v
pytest tests/test_enrichment/ -v
pytest tests/test_equivalence_agent_real.py -v
```

### Run with coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

## Using the Claude API

### Development (Mock Mode - Default)
```python
from pipeline import Phase1Pipeline

pipeline = Phase1Pipeline(use_mock_api=True)
result = pipeline.run()
```

### Production (Real Claude API)
```python
from pipeline import Phase1Pipeline

# Make sure ANTHROPIC_API_KEY is set in .env
pipeline = Phase1Pipeline(use_mock_api=False)
result = pipeline.run()
```

## Troubleshooting

### Missing Database File
If you get "Database file not found":
```bash
# Ensure db/db.sqlite exists and is readable
ls -la db/db.sqlite
```

### Import Errors
```bash
# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

### API Errors
```bash
# Check API key
echo $ANTHROPIC_API_KEY  # On Windows: echo %ANTHROPIC_API_KEY%

# Test connection
python -c "from anthropic import Anthropic; print('OK')"
```

## Project Components

### Database (26 vitamin D products)
- **3 unique materials** across 22 companies
- **8 reference suppliers** with certifications
- Pharmaceutical-grade quality standards

### SKU Parsing
- Parses: `RM-C{company}-{substance}-{variant}-{hash}`
- Identifies vitamin D2 (ergocalciferol) and D3 (cholecalciferol)
- Extracts dosage information

### Clustering
- Groups products with 80%+ semantic similarity
- Identifies consolidation candidates
- Quality metrics: cohesion, separation, silhouette

### Consolidation Analysis
- Mock and real Claude API modes
- German-language reasoning
- Structured JSON output with confidence scores

## Data Files

### Database
- `db/db.sqlite` - SQLite supplement database (required)

### Supplier Evidence
- `data/external_evidence.json` - Cached supplier data

### Configuration
- `.env.template` - Template for environment variables
- `.gitignore` - Git exclusion rules

## Next Steps

After Phase 1 setup:

1. Configure real Claude API (if needed)
2. Review consolidation recommendations
3. Prepare for Phase 2 implementation
4. Plan integration with downstream systems

## Support

For issues or questions:
- Check test output: `pytest tests/ -v`
- Review implementation plan: `docs/superpowers/plans/`
- Examine data: `python run_vitamin_d_analysis.py`
