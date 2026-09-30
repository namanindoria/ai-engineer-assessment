"""
Actionable Nudge Generation and Real-Time Control Engine.
Implements confidence filtering, cooldowns, duplicate suppression,
priority tiers (P0-P3), and TTL expiry to prevent alert fatigue.
"""

import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from q4_live_nudges.signal_extractor import SignalEvent


class LiveNudge(BaseModel):
    nudge_id: str
    priority: str          # P0_CRITICAL | P1_HIGH | P2_MEDIUM | P3_LOW
    category: str          # COMPLIANCE | RETENTION_SENTIMENT | CROSS_SELL | PAYMENT_SUPPORT
    title: str
    action_text: str       # Short, direct imperative command for agent
    confidence: float
    evidence: str
    ttl_seconds: int = 25
    created_at: float = Field(default_factory=time.time)
    expires_at: float = 0.0
    status: str = "ACTIVE" # ACTIVE | DISMISSED | EXPIRED | APPLIED


class NudgeEngine:
    """
    Manages active nudges with enterprise guardrails:
    - Minimum confidence threshold (default 0.75)
    - Cooldown period per category (e.g. 45s between cross-sell nudges)
    - Duplicate suppression
    - Priority sorting
    """

    CONFIDENCE_THRESHOLD = 0.75

    COOLDOWNS = {
        "MISSED_CROSS_SELL": 45.0,
        "COMPLIANCE_GAP": 15.0,  # Short cooldown because compliance is critical
        "RISING_FRUSTRATION": 30.0,
        "PAYMENT_DIFFICULTY": 40.0,
        "CALLBACK_NEED": 60.0
    }

    PRIORITIES = {
        "COMPLIANCE_GAP": ("P0_CRITICAL", "COMPLIANCE"),
        "RISING_FRUSTRATION": ("P1_HIGH", "RETENTION_SENTIMENT"),
        "PAYMENT_DIFFICULTY": ("P1_HIGH", "PAYMENT_SUPPORT"),
        "MISSED_CROSS_SELL": ("P2_MEDIUM", "CROSS_SELL"),
        "CALLBACK_NEED": ("P3_LOW", "OPERATIONS")
    }

    def __init__(self):
        self.active_nudges: List[LiveNudge] = []
        self.last_fired_times: Dict[str, float] = {}
        self.suppressed_events_count: int = 0
        self.nudge_counter: int = 0

    def process_signal(self, signal: SignalEvent) -> Optional[LiveNudge]:
        """
        Applies control filters. If signal qualifies, generates an actionable LiveNudge.
        """
        # 1. Confidence Threshold Filter
        if signal.confidence < self.CONFIDENCE_THRESHOLD:
            self.suppressed_events_count += 1
            return None

        # 2. Cooldown & Duplicate Suppression Filter
        now = time.time()
        cooldown_window = self.COOLDOWNS.get(signal.signal_type, 30.0)
        last_time = self.last_fired_times.get(signal.signal_type, 0.0)

        if (now - last_time) < cooldown_window:
            self.suppressed_events_count += 1
            return None

        # 3. Generate Actionable Recommendation
        self.nudge_counter += 1
        nudge_id = f"NDG-{now:.0f}-{self.nudge_counter:03d}"
        priority, category = self.PRIORITIES.get(signal.signal_type, ("P2_MEDIUM", "GENERAL"))

        if signal.signal_type == "COMPLIANCE_GAP":
            title = "Mandatory Disclosure Missing"
            action_text = (
                "🚨 Remind the agent before proceeding: Read the mandatory 30-day cooling-off "
                "and free-look disclosure before collecting payment details!"
            )
        elif signal.signal_type == "MISSED_CROSS_SELL":
            title = "Cross-Sell Opportunity Detected"
            action_text = (
                "⭐ Customer mentioned a second vehicle. Suggest the 15% Multi-Vehicle Family Bundle offer!"
            )
        elif signal.signal_type == "RISING_FRUSTRATION":
            title = "Customer Frustration Rising"
            action_text = (
                "⚠️ Acknowledge the concern before continuing: 'I understand your frustration with the system delay, "
                "let me personally take care of this right now.'"
            )
        elif signal.signal_type == "PAYMENT_DIFFICULTY":
            title = "Payment Hardship Alert"
            action_text = (
                "💡 Offer an approved payment-support or quarterly split-billing path."
            )
        elif signal.signal_type == "CALLBACK_NEED":
            title = "Customer Availability Constraint"
            action_text = (
                "📅 Customer needs to leave: Confirm preferred callback time before line disconnects."
            )
        else:
            title = f"Signal: {signal.signal_type}"
            action_text = f"Review customer note: {signal.evidence_text[:100]}"

        nudge = LiveNudge(
            nudge_id=nudge_id,
            priority=priority,
            category=category,
            title=title,
            action_text=action_text,
            confidence=signal.confidence,
            evidence=signal.evidence_text,
            ttl_seconds=30,
            created_at=now,
            expires_at=now + 30.0,
            status="ACTIVE"
        )

        self.last_fired_times[signal.signal_type] = now
        self.active_nudges.append(nudge)
        return nudge

    def prune_expired_nudges(self):
        """Removes expired nudges past their TTL."""
        now = time.time()
        for ndg in self.active_nudges:
            if ndg.status == "ACTIVE" and now > ndg.expires_at:
                ndg.status = "EXPIRED"
        self.active_nudges = [n for n in self.active_nudges if n.status == "ACTIVE"]
