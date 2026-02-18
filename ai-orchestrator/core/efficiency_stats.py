"""A/B Efficiency Statistics - Compiler ROI Measurement.

Calculates measurable impact of Prompt Compiler vs uncompiled prompts.
Tracks:
  - Token reduction
  - Latency improvement
  - Retry reduction
  - Cost savings

Usage:
    calculator = EfficiencyCalculator()
    report = calculator.generate_roi_report(compiled_runs, raw_runs)
    print(report)
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import mean, stdev
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Model pricing per 1M tokens (adjust per model)
MODEL_PRICING: Dict[str, Any] = {
    "anthropic": {
        "claude-opus-4": {"input_per_1m": 15.0, "output_per_1m": 75.0},
        "claude-sonnet-4": {"input_per_1m": 3.0, "output_per_1m": 15.0},
        "claude-haiku-4": {"input_per_1m": 0.25, "output_per_1m": 1.25},
    },
    "openai": {
        "gpt-4": {"input_per_1m": 30.0, "output_per_1m": 60.0},
        "gpt-4-turbo": {"input_per_1m": 10.0, "output_per_1m": 30.0},
        "gpt-3.5-turbo": {"input_per_1m": 0.5, "output_per_1m": 1.5},
    },
    "default": {"input_per_1m": 5.0, "output_per_1m": 15.0},
}


@dataclass
class RunStats:
    """Statistics for a set of runs."""

    run_count: int
    avg_input_tokens: float
    avg_output_tokens: float
    avg_total_tokens: float
    avg_duration_seconds: float
    avg_retries: float
    avg_repairs: float
    avg_cost_usd: float

    # Optional distribution stats
    stdev_tokens: Optional[float] = None
    stdev_duration: Optional[float] = None
    stdev_cost: Optional[float] = None


@dataclass
class ABComparison:
    """A/B comparison results."""

    compiled_stats: RunStats
    raw_stats: RunStats

    # Improvement metrics (positive = better)
    token_reduction_pct: float
    latency_reduction_pct: float
    retry_reduction_pct: float
    repair_reduction_pct: float
    cost_reduction_pct: float

    # Aggregate score
    efficiency_score: float

    # Confidence
    sample_size: int
    statistical_significance: str


class EfficiencyCalculator:
    """Calculate efficiency metrics for compiler A/B testing.

    Compares runs with compilation enabled vs disabled.
    """

    def __init__(self, pricing: Optional[Dict[str, Any]] = None):
        self.pricing = pricing or MODEL_PRICING

    def compute_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str = "default",
    ) -> float:
        """Calculate cost in USD.

        Args:
            input_tokens: Input token count
            output_tokens: Output token count
            model: Model identifier (e.g., "claude-sonnet-4")

        Returns:
            Cost in USD
        """
        pricing = None

        for provider, models in self.pricing.items():
            if provider == "default":
                continue
            if isinstance(models, dict) and model in models:
                pricing = models[model]
                break

        # Fallback to default
        if not pricing:
            pricing = self.pricing["default"]

        input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m"]
        output_cost = (output_tokens / 1_000_000) * pricing["output_per_1m"]

        return input_cost + output_cost

    def summarize_runs(self, runs: List[Dict[str, Any]]) -> RunStats:
        """Summarize statistics for a set of runs.

        Expected run format:
        {
            "run_id": str,
            "compile_enabled": bool,
            "total_input_tokens": int,
            "total_output_tokens": int,
            "duration_seconds": float,
            "retry_count": int,
            "repair_count": int,
            "model": str (optional)
        }
        """
        if not runs:
            return RunStats(
                run_count=0,
                avg_input_tokens=0,
                avg_output_tokens=0,
                avg_total_tokens=0,
                avg_duration_seconds=0,
                avg_retries=0,
                avg_repairs=0,
                avg_cost_usd=0,
            )

        input_tokens = [r["total_input_tokens"] for r in runs]
        output_tokens = [r["total_output_tokens"] for r in runs]
        total_tokens = [
            r["total_input_tokens"] + r["total_output_tokens"] for r in runs
        ]
        durations = [r["duration_seconds"] for r in runs]
        retries = [r["retry_count"] for r in runs]
        repairs = [r.get("repair_count", 0) for r in runs]

        costs = [
            self.compute_cost(
                r["total_input_tokens"],
                r["total_output_tokens"],
                r.get("model", "default"),
            )
            for r in runs
        ]

        stdev_tokens = stdev(total_tokens) if len(runs) > 1 else None
        stdev_duration = stdev(durations) if len(runs) > 1 else None
        stdev_cost = stdev(costs) if len(runs) > 1 else None

        return RunStats(
            run_count=len(runs),
            avg_input_tokens=mean(input_tokens),
            avg_output_tokens=mean(output_tokens),
            avg_total_tokens=mean(total_tokens),
            avg_duration_seconds=mean(durations),
            avg_retries=mean(retries),
            avg_repairs=mean(repairs),
            avg_cost_usd=mean(costs),
            stdev_tokens=stdev_tokens,
            stdev_duration=stdev_duration,
            stdev_cost=stdev_cost,
        )

    def compare(
        self,
        compiled_runs: List[Dict[str, Any]],
        raw_runs: List[Dict[str, Any]],
    ) -> ABComparison:
        """Compare compiled vs raw runs.

        Returns detailed A/B comparison with improvement metrics.
        """
        compiled_stats = self.summarize_runs(compiled_runs)
        raw_stats = self.summarize_runs(raw_runs)

        token_reduction = self._calc_reduction(
            raw_stats.avg_total_tokens, compiled_stats.avg_total_tokens
        )
        latency_reduction = self._calc_reduction(
            raw_stats.avg_duration_seconds, compiled_stats.avg_duration_seconds
        )
        retry_reduction = self._calc_reduction(
            raw_stats.avg_retries, compiled_stats.avg_retries
        )
        repair_reduction = self._calc_reduction(
            raw_stats.avg_repairs, compiled_stats.avg_repairs
        )
        cost_reduction = self._calc_reduction(
            raw_stats.avg_cost_usd, compiled_stats.avg_cost_usd
        )

        # Weighted aggregate efficiency score (normalized to 0-1)
        efficiency_score = (
            token_reduction * 0.3
            + latency_reduction * 0.2
            + retry_reduction * 0.2
            + cost_reduction * 0.3
        ) / 100.0

        # Statistical significance
        min_samples = 20
        total_samples = compiled_stats.run_count + raw_stats.run_count

        if total_samples < min_samples:
            significance = "insufficient_data"
        elif total_samples < 50:
            significance = "low_confidence"
        elif total_samples < 100:
            significance = "moderate_confidence"
        else:
            significance = "high_confidence"

        return ABComparison(
            compiled_stats=compiled_stats,
            raw_stats=raw_stats,
            token_reduction_pct=token_reduction,
            latency_reduction_pct=latency_reduction,
            retry_reduction_pct=retry_reduction,
            repair_reduction_pct=repair_reduction,
            cost_reduction_pct=cost_reduction,
            efficiency_score=efficiency_score,
            sample_size=total_samples,
            statistical_significance=significance,
        )

    def _calc_reduction(self, baseline: float, optimized: float) -> float:
        """Calculate reduction percentage. Positive = improvement."""
        if baseline == 0:
            return 0.0
        return ((baseline - optimized) / baseline) * 100.0

    def generate_roi_report(
        self,
        compiled_runs: List[Dict[str, Any]],
        raw_runs: List[Dict[str, Any]],
        format: str = "text",
    ) -> str:
        """Generate ROI report.

        Args:
            compiled_runs: Runs with compiler enabled
            raw_runs: Runs without compiler
            format: "text" or "json"

        Returns:
            Formatted report
        """
        comparison = self.compare(compiled_runs, raw_runs)

        if format == "json":
            return self._format_json_report(comparison)
        else:
            return self._format_text_report(comparison)

    def _format_text_report(self, comparison: ABComparison) -> str:
        """Format as human-readable text."""
        lines = []

        lines.append("=" * 60)
        lines.append("Prompt Compiler ROI Report")
        lines.append("=" * 60)
        lines.append("")

        lines.append(f"Sample Size: {comparison.sample_size} runs")
        lines.append(f"  - Compiled: {comparison.compiled_stats.run_count}")
        lines.append(f"  - Raw: {comparison.raw_stats.run_count}")
        lines.append(
            f"Confidence: {comparison.statistical_significance.replace('_', ' ').title()}"
        )
        lines.append("")

        lines.append("Key Improvements:")
        lines.append("-" * 60)
        lines.append(f"Token Reduction:    {comparison.token_reduction_pct:>6.1f}%")
        lines.append(f"Latency Reduction:  {comparison.latency_reduction_pct:>6.1f}%")
        lines.append(f"Retry Reduction:    {comparison.retry_reduction_pct:>6.1f}%")
        lines.append(f"Repair Reduction:   {comparison.repair_reduction_pct:>6.1f}%")
        lines.append(f"Cost Reduction:     {comparison.cost_reduction_pct:>6.1f}%")
        lines.append("")
        lines.append(f"Overall Efficiency Score: {comparison.efficiency_score:.3f}")
        lines.append("")

        lines.append("Detailed Statistics:")
        lines.append("-" * 60)
        lines.append("")

        lines.append("Compiled Runs:")
        lines.append(
            f"  Avg Tokens:   {comparison.compiled_stats.avg_total_tokens:>10,.0f}"
        )
        lines.append(
            f"  Avg Duration: {comparison.compiled_stats.avg_duration_seconds:>10.2f}s"
        )
        lines.append(
            f"  Avg Retries:  {comparison.compiled_stats.avg_retries:>10.2f}"
        )
        lines.append(
            f"  Avg Cost:     ${comparison.compiled_stats.avg_cost_usd:>10.4f}"
        )
        lines.append("")

        lines.append("Raw Runs:")
        lines.append(
            f"  Avg Tokens:   {comparison.raw_stats.avg_total_tokens:>10,.0f}"
        )
        lines.append(
            f"  Avg Duration: {comparison.raw_stats.avg_duration_seconds:>10.2f}s"
        )
        lines.append(f"  Avg Retries:  {comparison.raw_stats.avg_retries:>10.2f}")
        lines.append(f"  Avg Cost:     ${comparison.raw_stats.avg_cost_usd:>10.4f}")
        lines.append("")

        # Annual projections
        lines.append("Annual Projections (2,400 tasks/year):")
        lines.append("-" * 60)

        annual_compiled_cost = comparison.compiled_stats.avg_cost_usd * 2400
        annual_raw_cost = comparison.raw_stats.avg_cost_usd * 2400
        annual_savings = annual_raw_cost - annual_compiled_cost

        lines.append(f"Raw Cost:      ${annual_raw_cost:>10,.2f}")
        lines.append(f"Compiled Cost: ${annual_compiled_cost:>10,.2f}")
        lines.append(f"Annual Savings: ${annual_savings:>10,.2f}")
        lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def _format_json_report(self, comparison: ABComparison) -> str:
        """Format as JSON."""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sample_size": comparison.sample_size,
            "statistical_significance": comparison.statistical_significance,
            "improvements": {
                "token_reduction_pct": comparison.token_reduction_pct,
                "latency_reduction_pct": comparison.latency_reduction_pct,
                "retry_reduction_pct": comparison.retry_reduction_pct,
                "repair_reduction_pct": comparison.repair_reduction_pct,
                "cost_reduction_pct": comparison.cost_reduction_pct,
            },
            "efficiency_score": comparison.efficiency_score,
            "compiled_stats": {
                "run_count": comparison.compiled_stats.run_count,
                "avg_total_tokens": comparison.compiled_stats.avg_total_tokens,
                "avg_duration_seconds": comparison.compiled_stats.avg_duration_seconds,
                "avg_retries": comparison.compiled_stats.avg_retries,
                "avg_cost_usd": comparison.compiled_stats.avg_cost_usd,
            },
            "raw_stats": {
                "run_count": comparison.raw_stats.run_count,
                "avg_total_tokens": comparison.raw_stats.avg_total_tokens,
                "avg_duration_seconds": comparison.raw_stats.avg_duration_seconds,
                "avg_retries": comparison.raw_stats.avg_retries,
                "avg_cost_usd": comparison.raw_stats.avg_cost_usd,
            },
        }

        return json.dumps(report, indent=2)

    def export_comparison(self, comparison: ABComparison, filepath: str):
        """Export comparison to file."""
        report = self._format_json_report(comparison)

        with open(filepath, "w") as f:
            f.write(report)


class RunLedgerParser:
    """Parse run ledgers to extract stats for A/B analysis.

    Handles different ledger formats from the orchestrator.
    """

    @staticmethod
    def parse_ledger(ledger: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a run ledger into standardized format.

        Args:
            ledger: Raw run ledger

        Returns:
            Standardized run dict for EfficiencyCalculator
        """
        # Extract compilation flag
        compile_enabled = False
        ir_used = False

        for decision in ledger.get("decisions", []):
            if "compiler" in decision.get("action", "").lower():
                compile_enabled = True
            if "ir pipeline" in decision.get("action", "").lower():
                ir_used = True

        # Count total tokens from agent responses
        total_input = 0
        total_output = 0

        for response in ledger.get("agent_responses", []):
            metadata = response.get("metadata", {})
            estimated = metadata.get("estimated_tokens", 0)
            total_input += estimated
            # Estimate output tokens from response length
            output_len = len(response.get("output", ""))
            total_output += output_len // 4  # ~4 chars per token

        # Calculate duration from decisions
        decisions = ledger.get("decisions", [])
        if len(decisions) >= 2:
            start_time = decisions[0].get("timestamp")
            end_time = decisions[-1].get("timestamp")

            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time)
                    end_dt = datetime.fromisoformat(end_time)
                    duration = (end_dt - start_dt).total_seconds()
                except (ValueError, TypeError):
                    duration = 0
            else:
                duration = 0
        else:
            duration = 0

        # Count retries
        retry_count = sum(
            1
            for d in decisions
            if d.get("action") in ["retry", "phase_repeated"]
        )

        # Count repairs
        repair_count = sum(
            1
            for r in ledger.get("agent_responses", [])
            if r.get("metadata", {}).get("schema_repaired", False)
        )

        return {
            "run_id": ledger.get("run_id"),
            "compile_enabled": compile_enabled,
            "ir_used": ir_used,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "duration_seconds": duration,
            "retry_count": retry_count,
            "repair_count": repair_count,
            "model": "default",
        }

    @staticmethod
    def parse_ledger_file(filepath: str) -> Dict[str, Any]:
        """Parse a ledger from a JSON file."""
        with open(filepath) as f:
            ledger = json.load(f)
        return RunLedgerParser.parse_ledger(ledger)

    @staticmethod
    def parse_multiple_ledgers(
        filepaths: List[str],
    ) -> tuple:
        """Parse multiple ledgers and separate by compile status.

        Returns: (compiled_runs, raw_runs)
        """
        compiled_runs = []
        raw_runs = []

        for filepath in filepaths:
            try:
                run = RunLedgerParser.parse_ledger_file(filepath)
                if run["compile_enabled"]:
                    compiled_runs.append(run)
                else:
                    raw_runs.append(run)
            except Exception as e:
                logger.warning("Failed to parse ledger %s: %s", filepath, e)

        return compiled_runs, raw_runs
