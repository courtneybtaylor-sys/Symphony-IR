"""Ma'aT Governance Engine - Constitutional AI enforcement layer.

Evaluates actions against constitutional principles before execution.
All decisions are logged for full audit transparency.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GovernanceDecision(Enum):
    """Possible governance decisions."""

    APPROVE = "approve"
    DENY = "deny"
    FLAG = "flag"
    REQUIRE_REVIEW = "require_review"


@dataclass
class GovernanceResult:
    """Result of a governance evaluation."""

    decision: GovernanceDecision
    reason: str
    trust_score: float = 1.0
    violated_principles: List[str] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditEntry:
    """A single entry in the governance audit log."""

    timestamp: str
    action_type: str
    action_details: Dict[str, Any]
    decision: str
    reason: str
    trust_score: float
    violated_principles: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "action_type": self.action_type,
            "action_details": self.action_details,
            "decision": self.decision,
            "reason": self.reason,
            "trust_score": self.trust_score,
            "violated_principles": self.violated_principles,
        }


class MaaTGovernanceEngine:
    """Constitutional AI governance engine.

    Enforces principles:
    1. Harm Prevention - No destructive commands
    2. Privacy Protection - No exposed secrets
    3. Transparency - Actions must have clear descriptions
    4. Human Sovereignty - High-risk actions need human approval
    5. Fairness - Equitable treatment
    6. Accountability - Full audit trail
    """

    # Dangerous command patterns
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"rm\s+-rf\s+\*",
        r"drop\s+database",
        r"drop\s+table",
        r"truncate\s+table",
        r"format\s+[a-z]:",
        r"mkfs\.",
        r"dd\s+if=.*of=/dev/",
        r":\(\)\{.*\|.*&\s*\}",  # fork bomb
        r"chmod\s+-R\s+777\s+/",
        r"shutdown",
        r"reboot",
        r"init\s+0",
        r"kill\s+-9\s+-1",
    ]

    # Secret patterns
    SECRET_PATTERNS = [
        r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*['\"][^'\"]{8,}",
        r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]+",
        r"(?i)bearer\s+[a-zA-Z0-9\-_.]{20,}",
        r"sk-[a-zA-Z0-9]{20,}",
        r"(?i)aws[_-]?secret[_-]?access[_-]?key",
        r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
        r"ghp_[a-zA-Z0-9]{36}",
        r"gho_[a-zA-Z0-9]{36}",
    ]

    # High-risk action types requiring review
    HIGH_RISK_ACTIONS = [
        "execute_code",
        "network_request",
        "delete_file",
        "modify_system",
    ]

    def __init__(self, user_trust_score: float = 0.8):
        """Initialize the governance engine.

        Args:
            user_trust_score: Initial trust score for the user (0.0-1.0)
        """
        self.user_trust_score = max(0.0, min(1.0, user_trust_score))
        self._audit_log: List[AuditEntry] = []
        self._principles = {
            "harm_prevention": "Actions must not cause destruction or data loss",
            "privacy_protection": "No exposure of secrets, keys, or credentials",
            "transparency": "All actions must have clear, honest descriptions",
            "human_sovereignty": "High-risk actions require human approval",
            "fairness": "Equitable treatment in all operations",
            "accountability": "Complete audit trail for all decisions",
        }

    def evaluate_action(
        self,
        action_type: str,
        action_details: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        user_trust_score: Optional[float] = None,
    ) -> GovernanceResult:
        """Evaluate an action against constitutional principles.

        Args:
            action_type: Type of action (write_file, execute_code, network_request, data_access)
            action_details: Details about the action
            context: Additional context for evaluation
            user_trust_score: Override trust score for this evaluation

        Returns:
            GovernanceResult with decision and reasoning
        """
        context = context or {}
        trust = user_trust_score if user_trust_score is not None else self.user_trust_score
        violated = []
        required_actions = []

        # Check each constitutional principle
        harm_result = self._check_harm_prevention(action_type, action_details)
        if harm_result:
            violated.append("harm_prevention")

        privacy_result = self._check_privacy_protection(action_type, action_details)
        if privacy_result:
            violated.append("privacy_protection")

        transparency_result = self._check_transparency(action_type, action_details)
        if transparency_result:
            violated.append("transparency")

        sovereignty_result = self._check_human_sovereignty(
            action_type, action_details, trust
        )
        if sovereignty_result:
            violated.append("human_sovereignty")
            required_actions.append("Requires human review before execution")

        # Determine decision based on violations and trust
        if "harm_prevention" in violated:
            decision = GovernanceDecision.DENY
            reason = f"Blocked: {harm_result}"
        elif "privacy_protection" in violated:
            decision = GovernanceDecision.DENY
            reason = f"Blocked: {privacy_result}"
        elif "transparency" in violated:
            decision = GovernanceDecision.FLAG
            reason = f"Flagged: {transparency_result}"
        elif "human_sovereignty" in violated:
            decision = GovernanceDecision.REQUIRE_REVIEW
            reason = f"Review required: {sovereignty_result}"
        elif trust >= 0.95:
            decision = GovernanceDecision.APPROVE
            reason = "Auto-approved: High trust score"
        elif trust >= 0.5:
            if action_type in self.HIGH_RISK_ACTIONS:
                decision = GovernanceDecision.FLAG
                reason = f"Flagged for review: {action_type} with moderate trust ({trust:.2f})"
            else:
                decision = GovernanceDecision.APPROVE
                reason = "Approved: Moderate trust, low-risk action"
        else:
            decision = GovernanceDecision.REQUIRE_REVIEW
            reason = f"Low trust ({trust:.2f}): Manual review required"

        result = GovernanceResult(
            decision=decision,
            reason=reason,
            trust_score=trust,
            violated_principles=violated,
            required_actions=required_actions,
            metadata={
                "action_type": action_type,
                "checks_performed": [
                    "harm_prevention",
                    "privacy_protection",
                    "transparency",
                    "human_sovereignty",
                ],
            },
        )

        # Log to audit trail
        self._log_decision(action_type, action_details, result)

        return result

    def _check_harm_prevention(
        self, action_type: str, details: Dict[str, Any]
    ) -> Optional[str]:
        """Check for potentially destructive actions."""
        content = json.dumps(details, default=str).lower()

        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return f"Dangerous pattern detected: {pattern}"

        # Check for destructive file operations
        if action_type == "write_file":
            path = details.get("path", "")
            if any(
                p in path
                for p in ["/etc/", "/usr/", "/bin/", "/sbin/", "/boot/", "/sys/"]
            ):
                return f"Write to system directory blocked: {path}"

        return None

    def _check_privacy_protection(
        self, action_type: str, details: Dict[str, Any]
    ) -> Optional[str]:
        """Check for exposed secrets or credentials."""
        content = json.dumps(details, default=str)

        for pattern in self.SECRET_PATTERNS:
            match = re.search(pattern, content)
            if match:
                return f"Potential secret exposure detected: {pattern[:30]}..."

        return None

    def _check_transparency(
        self, action_type: str, details: Dict[str, Any]
    ) -> Optional[str]:
        """Check that actions have clear descriptions."""
        description = details.get("description", "")
        if not description and action_type in self.HIGH_RISK_ACTIONS:
            return "High-risk action lacks description"
        return None

    def _check_human_sovereignty(
        self, action_type: str, details: Dict[str, Any], trust: float
    ) -> Optional[str]:
        """Check if human approval is needed."""
        if action_type in self.HIGH_RISK_ACTIONS and trust < 0.7:
            return f"High-risk action '{action_type}' requires human approval (trust={trust:.2f})"
        return None

    def _log_decision(
        self,
        action_type: str,
        action_details: Dict[str, Any],
        result: GovernanceResult,
    ):
        """Record a decision in the audit log."""
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            action_type=action_type,
            action_details=action_details,
            decision=result.decision.value,
            reason=result.reason,
            trust_score=result.trust_score,
            violated_principles=result.violated_principles,
        )
        self._audit_log.append(entry)
        logger.debug(
            f"Governance: {result.decision.value} - {action_type} - {result.reason}"
        )

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get the complete audit log as a list of dictionaries."""
        return [entry.to_dict() for entry in self._audit_log]

    def export_audit_log(self, filepath: str):
        """Export the audit log to a JSON file.

        Args:
            filepath: Path to write the audit log JSON
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.get_audit_log(), indent=2, default=str)
        )
        logger.info(f"Audit log exported to {filepath}")

    def get_principles(self) -> Dict[str, str]:
        """Return the constitutional principles."""
        return dict(self._principles)
