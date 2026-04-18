"""Scoring and Prioritization Engine for Enhanced Compliance Agent.

This module implements a user-configurable scoring system that aggregates
plugin results with weighted factors to produce final compliance scores
and rankings. It supports multiple aggregation strategies and provides
detailed transparency into scoring decisions.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
import math

from makeathon.agents.core.data_models import PluginResult, ComplianceResult


@dataclass
class ScoringWeight:
    """Configuration for a plugin's weight in the overall score.

    Attributes:
        plugin_name: Name of the plugin this weight applies to
        weight: Numeric weight (typically 0.0-1.0, but can be higher)
        enabled: Whether this plugin contributes to the score
        min_confidence: Minimum confidence required to include this result
    """
    plugin_name: str
    weight: float
    enabled: bool = True
    min_confidence: float = 0.0


@dataclass
class ScoringConfig:
    """Configuration for the scoring engine.

    Attributes:
        weights: List of plugin weights and configurations
        aggregation_method: How to combine plugin scores ("weighted_average", "weighted_sum", "min", "product")
        confidence_penalty_factor: How much to penalize low confidence (0.0-1.0)
        blocking_issue_penalty: Score assigned when blocking issues are present
        normalize_final_score: Whether to normalize final score to 0.0-1.0 range
    """
    weights: List[ScoringWeight] = field(default_factory=list)
    aggregation_method: str = "weighted_average"
    confidence_penalty_factor: float = 0.2
    blocking_issue_penalty: float = 0.0
    normalize_final_score: bool = True

    def get_weight_for_plugin(self, plugin_name: str) -> Optional[ScoringWeight]:
        """Get the weight configuration for a specific plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Optional[ScoringWeight]: Weight config or None if not found
        """
        for weight in self.weights:
            if weight.plugin_name == plugin_name:
                return weight
        return None

    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """Check if a plugin is enabled for scoring.

        Args:
            plugin_name: Name of the plugin

        Returns:
            bool: True if enabled (or no config found, defaulting to enabled)
        """
        weight_config = self.get_weight_for_plugin(plugin_name)
        return weight_config.enabled if weight_config else True


class ScoringEngine:
    """Engine for scoring and prioritizing compliance results.

    This class takes plugin results and combines them into final compliance
    scores using user-configurable weights and aggregation strategies.
    It provides detailed reasoning chains and handles edge cases gracefully.
    """

    def __init__(self, config: Optional[ScoringConfig] = None):
        """Initialize the scoring engine.

        Args:
            config: Scoring configuration. If None, uses default weights.
        """
        self.config = config or self._create_default_config()
        self.logger = logging.getLogger(__name__)

        # Available aggregation methods
        self._aggregation_methods: Dict[str, Callable] = {
            "weighted_average": self._aggregate_weighted_average,
            "weighted_sum": self._aggregate_weighted_sum,
            "min": self._aggregate_minimum,
            "product": self._aggregate_product,
        }

    def _create_default_config(self) -> ScoringConfig:
        """Create default scoring configuration.

        Returns:
            ScoringConfig: Default configuration with balanced weights
        """
        return ScoringConfig(
            weights=[
                ScoringWeight("certificates", 0.4, enabled=True, min_confidence=0.8),
                ScoringWeight("pricing", 0.3, enabled=True, min_confidence=0.7),
                ScoringWeight("quality", 0.2, enabled=True, min_confidence=0.6),
                ScoringWeight("delivery", 0.1, enabled=True, min_confidence=0.6),
            ],
            aggregation_method="weighted_average",
            confidence_penalty_factor=0.2,
            blocking_issue_penalty=0.0,
        )

    def update_config(self, config: ScoringConfig) -> None:
        """Update the scoring configuration.

        Args:
            config: New scoring configuration
        """
        self.config = config
        self.logger.info("Updated scoring configuration")

    def _apply_confidence_penalty(self, score: float, confidence: float) -> float:
        """Apply confidence-based penalty to a score.

        Args:
            score: Original score (0.0-1.0)
            confidence: Confidence level (0.0-1.0)

        Returns:
            float: Adjusted score with confidence penalty applied
        """
        if self.config.confidence_penalty_factor == 0.0:
            return score

        # Penalty scales with how far confidence is below 1.0
        confidence_gap = max(0.0, 1.0 - confidence)
        penalty = confidence_gap * self.config.confidence_penalty_factor
        adjusted_score = score * (1.0 - penalty)

        return max(0.0, adjusted_score)

    def _filter_plugin_results(self, plugin_results: List[PluginResult]) -> List[PluginResult]:
        """Filter plugin results based on configuration.

        Args:
            plugin_results: List of plugin results to filter

        Returns:
            List[PluginResult]: Filtered results that meet criteria
        """
        filtered_results = []

        for result in plugin_results:
            # Check if plugin is enabled
            if not self.config.is_plugin_enabled(result.plugin_name):
                self.logger.debug(f"Skipping disabled plugin: {result.plugin_name}")
                continue

            # Check minimum confidence requirement
            weight_config = self.config.get_weight_for_plugin(result.plugin_name)
            min_confidence = weight_config.min_confidence if weight_config else 0.0

            if result.confidence < min_confidence:
                self.logger.debug(
                    f"Skipping {result.plugin_name} due to low confidence: "
                    f"{result.confidence:.2f} < {min_confidence:.2f}"
                )
                continue

            filtered_results.append(result)

        return filtered_results

    def _aggregate_weighted_average(
        self,
        weighted_scores: List[tuple[float, float]]
    ) -> tuple[float, List[str]]:
        """Aggregate scores using weighted average.

        Args:
            weighted_scores: List of (score, weight) tuples

        Returns:
            tuple[float, List[str]]: (final_score, reasoning_steps)
        """
        if not weighted_scores:
            return 0.0, ["No valid plugin results available"]

        total_weighted_score = sum(score * weight for score, weight in weighted_scores)
        total_weight = sum(weight for _, weight in weighted_scores)

        if total_weight == 0.0:
            return 0.0, ["All plugin weights are zero"]

        final_score = total_weighted_score / total_weight
        reasoning = [
            f"Weighted average: {total_weighted_score:.3f} / {total_weight:.3f} = {final_score:.3f}"
        ]

        return final_score, reasoning

    def _aggregate_weighted_sum(
        self,
        weighted_scores: List[tuple[float, float]]
    ) -> tuple[float, List[str]]:
        """Aggregate scores using weighted sum.

        Args:
            weighted_scores: List of (score, weight) tuples

        Returns:
            tuple[float, List[str]]: (final_score, reasoning_steps)
        """
        if not weighted_scores:
            return 0.0, ["No valid plugin results available"]

        final_score = sum(score * weight for score, weight in weighted_scores)
        reasoning = [f"Weighted sum: {final_score:.3f}"]

        return final_score, reasoning

    def _aggregate_minimum(
        self,
        weighted_scores: List[tuple[float, float]]
    ) -> tuple[float, List[str]]:
        """Aggregate scores using minimum (most restrictive).

        Args:
            weighted_scores: List of (score, weight) tuples

        Returns:
            tuple[float, List[str]]: (final_score, reasoning_steps)
        """
        if not weighted_scores:
            return 0.0, ["No valid plugin results available"]

        scores = [score for score, _ in weighted_scores]
        final_score = min(scores)
        reasoning = [f"Minimum score: {final_score:.3f} (most restrictive)"]

        return final_score, reasoning

    def _aggregate_product(
        self,
        weighted_scores: List[tuple[float, float]]
    ) -> tuple[float, List[str]]:
        """Aggregate scores using product (multiplicative).

        Args:
            weighted_scores: List of (score, weight) tuples

        Returns:
            tuple[float, List[str]]: (final_score, reasoning_steps)
        """
        if not weighted_scores:
            return 0.0, ["No valid plugin results available"]

        # Use weighted geometric mean
        product_sum = 0.0
        total_weight = 0.0

        for score, weight in weighted_scores:
            if score > 0:  # Avoid log(0)
                product_sum += weight * math.log(score)
                total_weight += weight

        if total_weight == 0.0:
            return 0.0, ["All weights are zero"]

        final_score = math.exp(product_sum / total_weight)
        reasoning = [f"Weighted geometric mean: {final_score:.3f}"]

        return final_score, reasoning

    def calculate_compliance_score(
        self,
        plugin_results: List[PluginResult]
    ) -> ComplianceResult:
        """Calculate overall compliance score from plugin results.

        Args:
            plugin_results: Results from compliance plugins

        Returns:
            ComplianceResult: Overall compliance assessment with detailed reasoning
        """
        reasoning_chain = []
        data_gaps = []

        # Filter plugin results based on configuration
        filtered_results = self._filter_plugin_results(plugin_results)

        if not filtered_results:
            return ComplianceResult(
                overall_score=0.0,
                overall_confidence=0.0,
                plugin_results=plugin_results,
                reasoning_chain=["No valid plugin results after filtering"],
                data_gaps=["No plugins provided usable results"],
                recommendations=["Check plugin configuration and data quality"],
            )

        # Check for blocking issues
        blocking_issues = []
        for result in filtered_results:
            blocking_issues.extend(result.blocking_issues)

        if blocking_issues:
            # If there are blocking issues, use penalty score
            final_score = self.config.blocking_issue_penalty
            reasoning_chain.append(f"Blocking issues present - score set to {final_score}")
            reasoning_chain.extend([f"Blocking: {issue}" for issue in blocking_issues])

            return ComplianceResult(
                overall_score=final_score,
                overall_confidence=1.0,  # High confidence in blocking assessment
                plugin_results=plugin_results,
                reasoning_chain=reasoning_chain,
                data_gaps=data_gaps,
                recommendations=[f"Resolve blocking issue: {issue}" for issue in blocking_issues],
            )

        # Prepare weighted scores
        weighted_scores = []
        confidence_values = []

        for result in filtered_results:
            # Get weight for this plugin
            weight_config = self.config.get_weight_for_plugin(result.plugin_name)
            weight = weight_config.weight if weight_config else 1.0

            # Apply confidence penalty to score
            adjusted_score = self._apply_confidence_penalty(result.score, result.confidence)

            weighted_scores.append((adjusted_score, weight))
            confidence_values.append(result.confidence)

            reasoning_chain.append(
                f"{result.plugin_name}: {result.score:.2f} "
                f"(confidence: {result.confidence:.2f}, weight: {weight:.2f}) "
                f"→ {adjusted_score:.3f}"
            )

        # Apply aggregation method
        aggregation_method = self._aggregation_methods.get(self.config.aggregation_method)
        if not aggregation_method:
            raise ValueError(f"Unknown aggregation method: {self.config.aggregation_method}")

        final_score, aggregation_reasoning = aggregation_method(weighted_scores)
        reasoning_chain.extend(aggregation_reasoning)

        # Normalize final score if requested
        if self.config.normalize_final_score and final_score > 1.0:
            original_score = final_score
            final_score = min(1.0, final_score)
            reasoning_chain.append(f"Normalized: {original_score:.3f} → {final_score:.3f}")

        # Calculate overall confidence as weighted average of plugin confidences
        total_weight = sum(weight for _, weight in weighted_scores)
        if total_weight > 0:
            overall_confidence = sum(
                conf * weight for conf, (_, weight) in zip(confidence_values, weighted_scores)
            ) / total_weight
        else:
            overall_confidence = 0.0

        # Generate recommendations based on results
        recommendations = []
        for result in filtered_results:
            if result.confidence < 0.8:
                recommendations.append(f"Improve data quality for {result.plugin_name}")
            if result.score < 0.5:
                recommendations.append(f"Address {result.plugin_name} compliance issues")

        return ComplianceResult(
            overall_score=final_score,
            overall_confidence=overall_confidence,
            plugin_results=plugin_results,
            reasoning_chain=reasoning_chain,
            data_gaps=data_gaps,
            recommendations=recommendations,
        )

    def rank_suppliers(
        self,
        compliance_results: List[tuple[str, ComplianceResult]],
        sort_by: str = "score"
    ) -> List[tuple[str, ComplianceResult]]:
        """Rank suppliers by compliance score or other criteria.

        Args:
            compliance_results: List of (supplier_name, result) tuples
            sort_by: Sorting criteria ("score", "confidence", "score_confidence")

        Returns:
            List[tuple[str, ComplianceResult]]: Ranked list of suppliers
        """
        if sort_by == "score":
            key_func = lambda x: x[1].overall_score
        elif sort_by == "confidence":
            key_func = lambda x: x[1].overall_confidence
        elif sort_by == "score_confidence":
            # Combine score and confidence with equal weighting
            key_func = lambda x: (x[1].overall_score + x[1].overall_confidence) / 2
        else:
            raise ValueError(f"Unknown sort criteria: {sort_by}")

        return sorted(compliance_results, key=key_func, reverse=True)

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current scoring configuration.

        Returns:
            Dict[str, Any]: Configuration summary for debugging/transparency
        """
        return {
            "aggregation_method": self.config.aggregation_method,
            "confidence_penalty_factor": self.config.confidence_penalty_factor,
            "blocking_issue_penalty": self.config.blocking_issue_penalty,
            "normalize_final_score": self.config.normalize_final_score,
            "plugin_weights": [
                {
                    "plugin": weight.plugin_name,
                    "weight": weight.weight,
                    "enabled": weight.enabled,
                    "min_confidence": weight.min_confidence,
                }
                for weight in self.config.weights
            ],
        }