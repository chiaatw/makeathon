"""Data Integration utilities for connecting existing data to Enhanced Compliance Agent.

This module provides utilities to integrate existing data files (suppliers.csv,
customer_requirements.csv, external_evidence.json) with the enhanced compliance
system. It handles format mapping, data transformation, and validation.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from makeathon.agents.enhanced_compliance_agent import EnhancedComplianceAgent
from makeathon.agents.scoring.engine import ScoringConfig, ScoringWeight


class DataSourceMapper:
    """Maps existing data files to enhanced system format."""

    @staticmethod
    def create_suppliers_csv_config() -> Dict[str, Any]:
        """Create configuration for the existing suppliers.csv format.

        The existing format has:
        - supplier,country,current_customer_count,certificates

        We need to map this to the expected format for CSVAdapter.
        """
        return {
            "encoding": "utf-8",
            "delimiter": ",",
            # Custom field mapping can be handled by a custom adapter if needed
        }

    @staticmethod
    def create_customer_requirements_csv_config() -> Dict[str, Any]:
        """Create configuration for the existing customer_requirements.csv format.

        The existing format has additional fields that need to go into constraints.
        """
        return {
            "encoding": "utf-8",
            "delimiter": ",",
        }

    @staticmethod
    def parse_price_range(price_range_str: str) -> tuple[Optional[float], Optional[float], str]:
        """Parse price range string like '$45-55' or '$42-48'.

        Args:
            price_range_str: Price range string from external evidence

        Returns:
            tuple[Optional[float], Optional[float], str]: (min_price, max_price, currency)
        """
        if not price_range_str:
            return None, None, "USD"

        # Extract currency symbol and numbers
        match = re.match(r'([^\d]*)([\d.]+)[-–]([\d.]+)', price_range_str.strip())
        if match:
            currency_symbol, min_str, max_str = match.groups()

            # Map currency symbols
            currency = "USD"  # Default
            if "$" in currency_symbol:
                currency = "USD"
            elif "€" in currency_symbol:
                currency = "EUR"
            elif "£" in currency_symbol:
                currency = "GBP"

            try:
                min_price = float(min_str)
                max_price = float(max_str)
                return min_price, max_price, currency
            except ValueError:
                pass

        return None, None, "USD"


class LegacyDataAdapter:
    """Adapter to integrate existing data files with the enhanced system."""

    def __init__(self, data_dir: Path):
        """Initialize the legacy data adapter.

        Args:
            data_dir: Path to the directory containing existing data files
        """
        self.data_dir = Path(data_dir)
        self.suppliers_csv = self.data_dir / "suppliers.csv"
        self.customers_csv = self.data_dir / "customer_requirements.csv"
        self.external_json = self.data_dir / "external_evidence.json"

    def create_enhanced_compliance_agent(
        self,
        custom_scoring: Optional[Dict[str, float]] = None
    ) -> EnhancedComplianceAgent:
        """Create an Enhanced Compliance Agent configured for existing data.

        Args:
            custom_scoring: Optional custom plugin weights

        Returns:
            EnhancedComplianceAgent: Configured agent ready to use existing data
        """
        # Build data sources configuration
        data_sources = []

        if self.suppliers_csv.exists():
            data_sources.append({
                "path": str(self.suppliers_csv),
                "type": "csv",
                "config": DataSourceMapper.create_suppliers_csv_config(),
            })

        if self.customers_csv.exists():
            data_sources.append({
                "path": str(self.customers_csv),
                "type": "csv",
                "config": DataSourceMapper.create_customer_requirements_csv_config(),
            })

        if self.external_json.exists():
            data_sources.append({
                "path": str(self.external_json),
                "type": "json",
            })

        # Create scoring configuration
        scoring_config = None
        if custom_scoring:
            weights = [
                ScoringWeight(plugin_name, weight)
                for plugin_name, weight in custom_scoring.items()
            ]
            scoring_config = ScoringConfig(weights=weights)

        # Create and configure agent
        agent = EnhancedComplianceAgent(
            data_sources=data_sources,
            scoring_config=scoring_config,
            use_enhanced_mode=True,
            legacy_fallback=True,
        )

        return agent

    def validate_data_files(self) -> Dict[str, Any]:
        """Validate existing data files and report issues.

        Returns:
            Dict[str, Any]: Validation report with issues and recommendations
        """
        report = {
            "files_found": {},
            "issues": [],
            "recommendations": [],
            "data_quality": {},
        }

        # Check file existence
        files_to_check = [
            ("suppliers.csv", self.suppliers_csv),
            ("customer_requirements.csv", self.customers_csv),
            ("external_evidence.json", self.external_json),
        ]

        for file_name, file_path in files_to_check:
            report["files_found"][file_name] = file_path.exists()
            if not file_path.exists():
                report["issues"].append(f"Missing file: {file_name}")
                report["recommendations"].append(f"Create {file_name} with proper format")

        # Validate suppliers.csv format if it exists
        if self.suppliers_csv.exists():
            try:
                import csv
                with open(self.suppliers_csv, 'r') as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames
                    rows = list(reader)

                required_headers = ["supplier", "country", "certificates"]
                missing_headers = [h for h in required_headers if h not in headers]

                if missing_headers:
                    report["issues"].append(f"suppliers.csv missing headers: {missing_headers}")

                report["data_quality"]["suppliers"] = {
                    "row_count": len(rows),
                    "headers": headers,
                    "sample_data": rows[:2] if rows else [],
                }

            except Exception as e:
                report["issues"].append(f"Error reading suppliers.csv: {e}")

        # Validate customer_requirements.csv format if it exists
        if self.customers_csv.exists():
            try:
                import csv
                with open(self.customers_csv, 'r') as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames
                    rows = list(reader)

                required_headers = ["company_name", "quality_tier"]
                missing_headers = [h for h in required_headers if h not in headers]

                if missing_headers:
                    report["issues"].append(f"customer_requirements.csv missing headers: {missing_headers}")

                report["data_quality"]["customers"] = {
                    "row_count": len(rows),
                    "headers": headers,
                    "sample_data": rows[:2] if rows else [],
                }

            except Exception as e:
                report["issues"].append(f"Error reading customer_requirements.csv: {e}")

        # Validate external_evidence.json format if it exists
        if self.external_json.exists():
            try:
                import json
                with open(self.external_json, 'r') as f:
                    data = json.load(f)

                if isinstance(data, dict) and "suppliers" in data:
                    suppliers_count = len(data["suppliers"]) if isinstance(data["suppliers"], list) else 0
                    report["data_quality"]["external_evidence"] = {
                        "suppliers_count": suppliers_count,
                        "structure": "valid",
                        "sample_supplier": data["suppliers"][0] if suppliers_count > 0 else None,
                    }
                else:
                    report["issues"].append("external_evidence.json does not have expected structure")

            except Exception as e:
                report["issues"].append(f"Error reading external_evidence.json: {e}")

        return report

    def test_integration(self) -> Dict[str, Any]:
        """Test the integration by running a sample compliance check.

        Returns:
            Dict[str, Any]: Test results and performance metrics
        """
        test_report = {
            "integration_test": "running",
            "start_time": datetime.now().isoformat(),
            "results": {},
            "errors": [],
        }

        try:
            # Create agent with existing data
            agent = self.create_enhanced_compliance_agent()

            # Test 1: Check system status
            status = agent.get_system_status()
            test_report["results"]["system_status"] = status

            # Test 2: Try a compliance check with known data
            try:
                # Use data from the CSV files we know exist
                result = agent.check_compliance("DSM", "PharmaCorp")
                test_report["results"]["sample_compliance_check"] = {
                    "supplier": "DSM",
                    "customer": "PharmaCorp",
                    "status": result.compliance_status,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                }
            except Exception as e:
                test_report["errors"].append(f"Compliance check failed: {e}")

            # Test 3: Try enhanced mode features
            try:
                enhanced_result = agent.check_compliance_enhanced("DSM", "PharmaCorp")
                test_report["results"]["enhanced_mode_check"] = {
                    "overall_score": enhanced_result.overall_score,
                    "overall_confidence": enhanced_result.overall_confidence,
                    "plugin_count": len(enhanced_result.plugin_results),
                }
            except Exception as e:
                test_report["errors"].append(f"Enhanced mode failed: {e}")

            test_report["integration_test"] = "completed"

        except Exception as e:
            test_report["integration_test"] = "failed"
            test_report["errors"].append(f"Integration test failed: {e}")

        test_report["end_time"] = datetime.now().isoformat()
        return test_report


def setup_integration(
    data_dir: Optional[str] = None,
    custom_scoring: Optional[Dict[str, float]] = None
) -> EnhancedComplianceAgent:
    """Convenience function to set up enhanced compliance agent with existing data.

    Args:
        data_dir: Path to data directory (defaults to "data" in current directory)
        custom_scoring: Optional custom plugin weights

    Returns:
        EnhancedComplianceAgent: Configured agent ready for use

    Example:
        # Basic setup
        agent = setup_integration()
        result = agent.check_compliance("DSM", "PharmaCorp")

        # Custom scoring
        agent = setup_integration(
            custom_scoring={"certificates": 0.5, "pricing": 0.3, "quality": 0.2}
        )
    """
    if data_dir is None:
        data_dir = "data"

    adapter = LegacyDataAdapter(Path(data_dir))
    return adapter.create_enhanced_compliance_agent(custom_scoring)


def run_integration_validation(data_dir: Optional[str] = None) -> None:
    """Run complete integration validation and print report.

    Args:
        data_dir: Path to data directory (defaults to "data" in current directory)
    """
    if data_dir is None:
        data_dir = "data"

    adapter = LegacyDataAdapter(Path(data_dir))

    print("=== Enhanced Compliance Agent - Data Integration Validation ===")
    print()

    # Validate data files
    print("1. Data File Validation:")
    validation_report = adapter.validate_data_files()

    for file_name, exists in validation_report["files_found"].items():
        status = "✓" if exists else "✗"
        print(f"   {status} {file_name}")

    if validation_report["issues"]:
        print("\n   Issues found:")
        for issue in validation_report["issues"]:
            print(f"   - {issue}")

    if validation_report["data_quality"]:
        print("\n   Data Quality:")
        for source, quality in validation_report["data_quality"].items():
            print(f"   - {source}: {quality.get('row_count', 0)} records")

    print()

    # Test integration
    print("2. Integration Test:")
    test_report = adapter.test_integration()

    if test_report["integration_test"] == "completed":
        print("   ✓ Integration test completed successfully")

        if "sample_compliance_check" in test_report["results"]:
            result = test_report["results"]["sample_compliance_check"]
            print(f"   ✓ Sample compliance check: {result['status']} "
                  f"(confidence: {result['confidence']:.1%})")

        if "enhanced_mode_check" in test_report["results"]:
            result = test_report["results"]["enhanced_mode_check"]
            print(f"   ✓ Enhanced mode: score {result['overall_score']:.2f} "
                  f"({result['plugin_count']} plugins)")

    else:
        print("   ✗ Integration test failed")

    if test_report["errors"]:
        print("\n   Errors:")
        for error in test_report["errors"]:
            print(f"   - {error}")

    print()
    print("=== Validation Complete ===")


if __name__ == "__main__":
    # Run validation when called directly
    run_integration_validation()