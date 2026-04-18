"""
SKU parser for vitamin D raw materials.

This module parses raw material SKUs following the pattern:
RM-C{company_id}-{substance}-{variant}-{hash}

Example: RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1
          ↑  ↑  ↑                            ↑
          |  |  |                            └─ hash for uniqueness
          |  |  └──────────────────────────── substance-variant chain
          |  └───────────────────────────────── company ID
          └─────────────────────────────────── raw material prefix

Extracts:
- Company ID
- Substance (e.g., vitamin-d3, vitamin-d2)
- Variant (e.g., cholecalciferol-1000iu)
- Dosage information
- Normalized canonical name
"""

from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class ParsedSKU:
    """
    Parsed representation of a raw material SKU.

    Attributes:
        original_sku: The original SKU string
        company_id: Extracted company ID
        substance: Extracted substance (e.g., vitamin-d3)
        variant: Extracted variant/dosage info
        hash_value: Hash suffix for uniqueness
        is_vitamin_d: Boolean indicating if this is a vitamin D product
        canonical_name: Normalized, human-readable name
    """
    original_sku: str
    company_id: int
    substance: str
    variant: str
    hash_value: str
    is_vitamin_d: bool
    canonical_name: str

    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"ParsedSKU({self.canonical_name} | Company:{self.company_id})"

    def __repr__(self) -> str:
        """Return developer-friendly representation."""
        return (
            f"ParsedSKU(sku={self.original_sku}, "
            f"company_id={self.company_id}, "
            f"substance={self.substance}, "
            f"canonical={self.canonical_name})"
        )


class VitaminDSKUParser:
    """
    Parser for vitamin D raw material SKUs.

    Parses SKUs in the format: RM-C{company_id}-{substance}-{variant}-{hash}
    Identifies vitamin D products and extracts standardized information.
    """

    # Vitamin D substance identifiers
    VITAMIN_D_KEYWORDS = {
        'vitamin-d3', 'vitamin-d2', 'cholecalciferol', 'ergocalciferol',
        'd3', 'd2', 'calcitriol', 'calcifediol', 'dihydrotachysterol'
    }

    # Dosage pattern (e.g., 1000iu, 400iu, 5000iu)
    DOSAGE_PATTERN = r'(\d+)\s*(?:iu|ius|ui|ue)'

    # Form/type pattern (e.g., cholecalciferol, ergocalciferol)
    FORM_KEYWORDS = {
        'cholecalciferol': 'Cholecalciferol',
        'ergocalciferol': 'Ergocalciferol',
        'calcitriol': 'Calcitriol',
        'calcifediol': 'Calcifediol',
        'dihydrotachysterol': 'Dihydrotachysterol',
    }

    def parse(self, sku: str) -> ParsedSKU:
        """
        Parse a raw material SKU.

        Args:
            sku: SKU string to parse

        Returns:
            ParsedSKU object with extracted information

        Raises:
            ValueError: If SKU format is invalid
        """
        sku_lower = sku.lower()
        parts = sku_lower.split('-')

        # Validate basic structure: RM, C{id}, ...substance..., ...variant..., hash
        if len(parts) < 5 or parts[0] != 'rm':
            raise ValueError(
                f"Invalid SKU format: {sku}\n"
                f"Expected format: RM-C{{company_id}}-{{substance}}-{{variant}}-{{hash}}"
            )

        # Extract company ID from C{id}
        try:
            if not parts[1].startswith('c'):
                raise ValueError("Missing company ID prefix 'C'")
            company_id = int(parts[1][1:])
        except (ValueError, IndexError):
            raise ValueError(f"Invalid company ID in SKU: {sku}")

        # Hash is always the last part and should be 8 hex digits
        if len(parts[-1]) != 8 or not all(c in '0123456789abcdef' for c in parts[-1]):
            raise ValueError(f"Invalid or missing hash in SKU: {sku}")

        hash_value = parts[-1]

        # Everything between company_id and hash needs to be split into substance and variant
        # Typical pattern: [substance_parts...] [variant_parts...] [hash]
        remaining_parts = parts[2:-1]  # Exclude RM, C{id}, and hash

        if len(remaining_parts) < 2:
            raise ValueError(
                f"SKU must have substance and variant: {sku}\n"
                f"Format: RM-C{{id}}-{{substance}}-{{variant}}-{{hash}}"
            )

        # Substance is typically shorter and comes first (e.g., vitamin-d3)
        # Variant is longer (e.g., cholecalciferol-1000iu)
        # Split heuristic: substance is first 1-2 parts, variant is the rest
        if len(remaining_parts) == 2:
            substance = remaining_parts[0]
            variant = remaining_parts[1]
        else:
            # If more parts, substance is likely first part(s), variant is rest
            # Find the boundary by looking for known form keywords
            substance_parts = []
            variant_parts = []
            found_variant = False

            for part in remaining_parts:
                if found_variant:
                    variant_parts.append(part)
                else:
                    # Check if this looks like the start of a variant
                    if any(form in part for form in self.FORM_KEYWORDS):
                        found_variant = True
                        variant_parts.append(part)
                    else:
                        substance_parts.append(part)

            if not variant_parts:
                # If no form keywords found, split at midpoint
                split_idx = (len(remaining_parts) + 1) // 2
                substance_parts = remaining_parts[:split_idx]
                variant_parts = remaining_parts[split_idx:]

            substance = '-'.join(substance_parts)
            variant = '-'.join(variant_parts)

        # Determine if this is vitamin D
        is_vitamin_d = self._is_vitamin_d(substance, variant)

        # Generate canonical name
        canonical_name = self._generate_canonical_name(substance, variant, is_vitamin_d)

        return ParsedSKU(
            original_sku=sku,
            company_id=company_id,
            substance=substance,
            variant=variant,
            hash_value=hash_value,
            is_vitamin_d=is_vitamin_d,
            canonical_name=canonical_name
        )

    def _is_vitamin_d(self, substance: str, variant: str) -> bool:
        """
        Determine if this is a vitamin D product.

        Args:
            substance: Substance string
            variant: Variant string

        Returns:
            True if this is a vitamin D product
        """
        combined = f"{substance}-{variant}".lower()

        # Check for vitamin D keywords
        for keyword in self.VITAMIN_D_KEYWORDS:
            if keyword in combined:
                return True

        return False

    def _generate_canonical_name(
        self, substance: str, variant: str, is_vitamin_d: bool
    ) -> str:
        """
        Generate a normalized canonical name.

        Args:
            substance: Substance string
            variant: Variant string
            is_vitamin_d: Whether this is a vitamin D product

        Returns:
            Normalized, human-readable name
        """
        if not is_vitamin_d:
            # Non-vitamin D: capitalize substance and variant
            parts = [p.capitalize() for p in (substance + "-" + variant).split("-")]
            return " ".join(parts)

        # For vitamin D, create a standardized format
        form = self._extract_form(substance, variant)
        dosage = self._extract_dosage(variant)
        vitamin_type = self._extract_vitamin_type(substance)

        # Build canonical name
        if form and dosage:
            return f"Vitamin {vitamin_type} ({form}) {dosage} IU"
        elif form:
            return f"Vitamin {vitamin_type} ({form})"
        elif dosage:
            return f"Vitamin {vitamin_type} {dosage} IU"
        else:
            return f"Vitamin {vitamin_type}"

    def _extract_form(self, substance: str, variant: str) -> Optional[str]:
        """Extract the form/type of vitamin D (e.g., Cholecalciferol)."""
        combined = f"{substance}-{variant}".lower()

        for keyword, display_name in self.FORM_KEYWORDS.items():
            if keyword in combined:
                return display_name

        return None

    def _extract_dosage(self, variant: str) -> Optional[str]:
        """Extract dosage from variant string."""
        match = re.search(self.DOSAGE_PATTERN, variant, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _extract_vitamin_type(self, substance: str) -> str:
        """Extract vitamin D type (D2 or D3)."""
        substance_lower = substance.lower()

        if 'd3' in substance_lower or 'cholecalciferol' in substance_lower:
            return 'D3'
        elif 'd2' in substance_lower or 'ergocalciferol' in substance_lower:
            return 'D2'
        else:
            # Default to D3 if unclear
            return 'D'
