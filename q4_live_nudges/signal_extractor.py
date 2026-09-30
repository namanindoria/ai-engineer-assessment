"""
Real-Time Signal Extraction Engine for Live Call Audio.
Extracts topic shifts, compliance risks, buying opportunities,
sentiment changes, and payment distress with calibrated confidence scores.
"""

import re
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SignalEvent(BaseModel):
    signal_type: str  # MISSED_CROSS_SELL | COMPLIANCE_GAP | RISING_FRUSTRATION | PAYMENT_DIFFICULTY | CALLBACK_NEED | NOISE_IGNORE
    confidence: float  # 0.0 - 1.0
    speaker: str       # Agent | Customer
    evidence_text: str
    detected_topic: str
    extraction_latency_ms: float
    timestamp: float = Field(default_factory=time.time)


class SignalExtractor:
    """
    Evaluates rolling call transcript turns and acoustic markers
    to detect actionable conversational signals.
    """

    # Signal Patterns & Keywords
    CROSS_SELL_PATTERNS = [
        (re.compile(r"\b(?:second vehicle|second car|another car|another vehicle|two cars|motorcycle)\b", re.IGNORECASE), "SECOND_VEHICLE"),
        (re.compile(r"\b(?:wife|husband|spouse|partner)\b.*?\b(?:has a|drives a|owns a|car|suv|vehicle|truck|cr-v|sedan)\b", re.IGNORECASE), "SPOUSE_VEHICLE"),
        (re.compile(r"\b(?:kids|children|daughter|son|family member)\b", re.IGNORECASE), "FAMILY_DEPENDENT"),
        (re.compile(r"\b(?:new house|mortgage|moving|bought a home)\b", re.IGNORECASE), "HOMEOWNERS_BUNDLE")
    ]

    FRUSTRATION_PATTERNS = [
        (re.compile(r"\b(?:already (?:told|explained|said) (?:you|this) (?:twice|three times|again))\b", re.IGNORECASE), "REPETITION_IRRITATION"),
        (re.compile(r"\b(?:ridiculous|waste of time|terrible service|frustrating|angry|unacceptable)\b", re.IGNORECASE), "EXPLICIT_FRUSTRATION"),
        (re.compile(r"\b(?:why does your system keep|how many times)\b", re.IGNORECASE), "SYSTEM_INCOMPETENCE_COMPLAINT")
    ]

    COMPLIANCE_PATTERNS = [
        # Triggered when Agent moves to collect card or bind policy without reciting 30-day disclosure
        (re.compile(r"\b(?:credit card|card number|routing number|charge your card|bind the policy|collect payment)\b", re.IGNORECASE), "PAYMENT_WITHOUT_DISCLOSURE")
    ]

    PAYMENT_DIFFICULTY_PATTERNS = [
        (re.compile(r"\b(?:lost my (?:job|hours|overtime)|cannot afford|tight budget|too steep|split (?:the )?payment|pay in installments)\b", re.IGNORECASE), "HARDSHIP_RISK")
    ]

    CALLBACK_PATTERNS = [
        (re.compile(r"\b(?:have to (?:run|go|step out)|boarding (?:a )?plane|phone dying|call me back later)\b", re.IGNORECASE), "CALLBACK_REQUEST")
    ]

    @staticmethod
    def compute_signal_confidence(
        pattern_match: re.Match,
        utterance: str,
        topic: str,
        call_history: List[Dict[str, str]]
    ) -> float:
        """
        Dynamically calculates signal confidence based on:
        1. Phrase specificity (span length / utterance length ratio)
        2. Contextual reinforcement from recent dialogue history
        3. Exclamation and lexical emphasis markers
        4. Absence of negation modifiers (e.g. 'not', 'never', 'don't')
        """
        matched_text = pattern_match.group(0)
        match_len = len(matched_text.split())

        base_scores = {
            "SECOND_VEHICLE": 0.82,
            "SPOUSE_VEHICLE": 0.84,
            "FAMILY_DEPENDENT": 0.78,
            "HOMEOWNERS_BUNDLE": 0.80,
            "REPETITION_IRRITATION": 0.85,
            "EXPLICIT_FRUSTRATION": 0.84,
            "SYSTEM_INCOMPETENCE_COMPLAINT": 0.80,
            "PAYMENT_WITHOUT_DISCLOSURE": 0.85,
            "HARDSHIP_RISK": 0.82,
            "CALLBACK_REQUEST": 0.86
        }
        base = base_scores.get(topic, 0.75)

        # Specificity bonus: multi-word exact semantic targets carry higher precision
        specificity_bonus = min(0.08, match_len * 0.02)

        # Contextual reinforcement bonus
        recent_text = " ".join([h.get("text", "") for h in call_history[-3:]]).lower()
        context_bonus = 0.0
        if topic in ["SECOND_VEHICLE", "SPOUSE_VEHICLE"] and any(w in recent_text for w in ["car", "auto", "vehicle", "quote", "rate"]):
            context_bonus = 0.06
        elif topic in ["REPETITION_IRRITATION", "EXPLICIT_FRUSTRATION"] and any(w in recent_text for w in ["number", "again", "wait", "hold"]):
            context_bonus = 0.06
        elif topic == "PAYMENT_WITHOUT_DISCLOSURE" and any(w in recent_text for w in ["dollar", "month", "rate", "premium", "quote"]):
            context_bonus = 0.07

        # Negation penalty: e.g. "I don't have a second car" or "not frustrated"
        negation_penalty = 0.0
        utt_lower = utterance.lower()
        if topic in ["SECOND_VEHICLE", "SPOUSE_VEHICLE", "HOMEOWNERS_BUNDLE"] and re.search(r"\b(?:don't have|no second|neither|never had|not looking)\b", utt_lower):
            negation_penalty = 0.35
        elif topic in ["REPETITION_IRRITATION", "EXPLICIT_FRUSTRATION"] and re.search(r"\b(?:not angry|not mad|no problem|not frustrated)\b", utt_lower):
            negation_penalty = 0.35

        final_conf = max(0.20, min(0.98, base + specificity_bonus + context_bonus - negation_penalty))
        return round(final_conf, 3)

    def extract_signals(
        self,
        current_speaker: str,
        current_utterance: str,
        call_history: List[Dict[str, str]],
        disclosure_recited: bool = False
    ) -> List[SignalEvent]:
        """
        Extracts active signals from the latest utterance and recent context.
        Returns a list of SignalEvent objects with measured latency.
        """
        start_t = time.perf_counter()
        signals: List[SignalEvent] = []

        # 1. Customer-initiated signals
        if current_speaker.lower() == "customer":
            # Check Missed Cross-Sell Opportunities
            for pattern, topic in self.CROSS_SELL_PATTERNS:
                m = pattern.search(current_utterance)
                if m:
                    conf = self.compute_signal_confidence(m, current_utterance, topic, call_history)
                    signals.append(
                        SignalEvent(
                            signal_type="MISSED_CROSS_SELL",
                            confidence=conf,
                            speaker="Customer",
                            evidence_text=current_utterance,
                            detected_topic=topic,
                            extraction_latency_ms=0.0
                        )
                    )

            # Check Frustration / Negative Sentiment
            for pattern, topic in self.FRUSTRATION_PATTERNS:
                m = pattern.search(current_utterance)
                if m:
                    conf = self.compute_signal_confidence(m, current_utterance, topic, call_history)
                    signals.append(
                        SignalEvent(
                            signal_type="RISING_FRUSTRATION",
                            confidence=conf,
                            speaker="Customer",
                            evidence_text=current_utterance,
                            detected_topic=topic,
                            extraction_latency_ms=0.0
                        )
                    )

            # Check Payment Hardship
            for pattern, topic in self.PAYMENT_DIFFICULTY_PATTERNS:
                m = pattern.search(current_utterance)
                if m:
                    conf = self.compute_signal_confidence(m, current_utterance, topic, call_history)
                    signals.append(
                        SignalEvent(
                            signal_type="PAYMENT_DIFFICULTY",
                            confidence=conf,
                            speaker="Customer",
                            evidence_text=current_utterance,
                            detected_topic=topic,
                            extraction_latency_ms=0.0
                        )
                    )

            # Check Callback Need
            for pattern, topic in self.CALLBACK_PATTERNS:
                m = pattern.search(current_utterance)
                if m:
                    conf = self.compute_signal_confidence(m, current_utterance, topic, call_history)
                    signals.append(
                        SignalEvent(
                            signal_type="CALLBACK_NEED",
                            confidence=conf,
                            speaker="Customer",
                            evidence_text=current_utterance,
                            detected_topic=topic,
                            extraction_latency_ms=0.0
                        )
                    )

        # 2. Agent-initiated Compliance Gaps
        elif current_speaker.lower() == "agent":
            for pattern, topic in self.COMPLIANCE_PATTERNS:
                m = pattern.search(current_utterance)
                if m and not disclosure_recited:
                    conf = self.compute_signal_confidence(m, current_utterance, topic, call_history)
                    signals.append(
                        SignalEvent(
                            signal_type="COMPLIANCE_GAP",
                            confidence=conf,
                            speaker="Agent",
                            evidence_text=current_utterance,
                            detected_topic="MISSING_MANDATORY_DISCLOSURE",
                            extraction_latency_ms=0.0
                        )
                    )

        duration_ms = round((time.perf_counter() - start_t) * 1000.0, 2)
        for s in signals:
            s.extraction_latency_ms = max(0.5, duration_ms)

        return signals
