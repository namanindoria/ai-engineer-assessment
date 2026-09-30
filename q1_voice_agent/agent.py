"""
Conversational State Machine and Grounded Dialogue Controller for Question 1.
Dynamically interfaces with Question 2 Hybrid Knowledge Base.
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple
from q2_knowledge_base.retriever import HybridRetriever
from q1_voice_agent.business_rules import UnderwritingRules
from q1_voice_agent.crm_webhook import CRMWebhookDispatcher, crm_dispatcher
from q1_voice_agent.llm_generator import GroundedLLMGenerator


class VoiceAgentSession:
    """
    Manages an active telephone / web call session.
    Tracks state machine, extracted slots, dynamic KB queries,
    conflicting details, and safe fallbacks.
    """

    STATES = [
        "GREETING",
        "COLLECTING_PROFILE",
        "SCREENING_HEALTH",
        "OBJECTION_OR_FAQ",
        "QUALIFICATION_DECISION",
        "ESCALATED",
        "COMPLETED"
    ]

    def __init__(self, session_id: str, retriever: Optional[HybridRetriever] = None, llm_generator: Optional[GroundedLLMGenerator] = None):
        self.session_id = session_id
        self.current_state = "GREETING"
        self.caller_name: Optional[str] = None
        self.caller_phone: str = "+1-555-0100"
        self.caller_age: Optional[int] = None
        self.stated_ages: List[int] = []  # For detecting conflicting details
        self.coverage_type: str = "Individual"
        self.pre_existing_conditions: List[str] = []
        self.conversation_history: List[Dict[str, str]] = []
        self.kb_citations_used: List[str] = []
        self.crm_action_result: Optional[Dict[str, Any]] = None
        self.is_human_escalated: bool = False
        self.call_duration_seconds: int = 0

        # Initialize Retriever
        if retriever is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            kb_path = os.path.join(base_dir, "data", "kb", "health_insurance_kb.json")
            retriever = HybridRetriever(kb_path=kb_path)
        self.retriever = retriever
        self.llm_generator = llm_generator or GroundedLLMGenerator()

    def _extract_age(self, text: str) -> Optional[int]:
        """Extracts integer age from utterance only when clearly indicating age."""
        # Pattern 1: "I am 34", "I'm 42", "turning 28", "age 65"
        m1 = re.search(r"\b(?:i(?:'m| am)|age is|age|turning|turned|am)\s*(\d{1,2})\b", text, re.IGNORECASE)
        if m1:
            age = int(m1.group(1))
            if 18 <= age <= 100:
                return age
        # Pattern 2: "34 years old", "42 yrs old", "28 yo"
        m2 = re.search(r"\b(\d{1,2})\s*(?:years old|yrs old|year old|yo)\b", text, re.IGNORECASE)
        if m2:
            age = int(m2.group(1))
            if 18 <= age <= 100:
                return age
        return None

    def _detect_escalation_intent(self, text: str) -> bool:
        """Detects if caller demands a human representative using strict phrase patterns."""
        patterns = [
            r"\b(?:speak|talk|transfer)\s+(?:to\s+)?(?:a\s+)?(?:human|person|specialist|representative|manager|operator|someone)\b",
            r"\b(?:human|real)\s+(?:agent|person|specialist|representative)\b",
            r"\b(?:transfer|connect)\s+me\s+(?:to\s+)?(?:a\s+)?(?:human|person|specialist)?\b",
            r"\b(?:speak\s+with\s+a\s+(?:real\s+)?person)\b",
            r"\b(?:licensed\s+specialist)\b",
            r"\b(?:get\s+me\s+a\s+human)\b"
        ]
        return any(re.search(pat, text, re.IGNORECASE) for pat in patterns)

    def _detect_objection_or_faq(self, text: str) -> bool:
        """Detects if utterance is a question or objection requiring KB retrieval with word boundaries."""
        triggers = [
            r"\bwhy\b", r"\bhow\b", r"\bwhat\b", r"\bdoes\s+this\b", r"\bdo\s+you\b",
            r"\bcover\b", r"\bcoverage\b", r"\bcost\b", r"\bexpensive\b",
            r"\bhmo\b", r"\bemployer\b", r"\bcompany\b", r"\brobot\b",
            r"\b(?:artificial\s+intelligence|ai)\b", r"\bcashless\b", r"\bhospital\b",
            r"\bdental\b", r"\bcardiac\b", r"\bwaiting\s+period\b", r"\bdeductible\b",
            r"\bexcess\b", r"\bgene\s+therapy\b", r"\bholistic\b", r"\broom\b", r"\bafford\b"
        ]
        return any(re.search(tr, text, re.IGNORECASE) for tr in triggers) or "?" in text

    def step(self, user_utterance: str) -> Dict[str, Any]:
        """
        Processes a single turn of user speech and returns the bot's response,
        grounding citations, current state, and any triggered business actions.
        """
        self.conversation_history.append({"speaker": "Customer", "text": user_utterance})
        self.call_duration_seconds += 12

        bot_reply = ""
        citation_info = None
        action_triggered = None

        # 1. Check for Immediate Human Escalation
        if self._detect_escalation_intent(user_utterance):
            self.current_state = "ESCALATED"
            self.is_human_escalated = True
            esc_data = {
                "customer_name": self.caller_name or "Valued Caller",
                "phone": self.caller_phone,
                "age": self.caller_age,
                "coverage_type": self.coverage_type,
                "pre_existing_conditions": self.pre_existing_conditions,
                "qualification_status": "ESCALATED_HUMAN",
                "recommended_plan": "Specialist Review Required",
                "call_duration_seconds": self.call_duration_seconds,
                "escalation_reason": f"Direct user escalation request: '{user_utterance}'",
                "notes": "Customer requested human transfer during qualification call."
            }
            res = crm_dispatcher.trigger_escalation_webhook(esc_data)
            self.crm_action_result = res
            bot_reply = (
                "I completely understand. I am transferring you directly to our Senior Underwriting Concierge "
                "team right now. A licensed specialist will be with you on this line immediately. Please hold for just a moment."
            )
            self.conversation_history.append({"speaker": "Agent", "text": bot_reply})
            return {
                "reply": bot_reply,
                "state": self.current_state,
                "citation": None,
                "action": res,
                "escalated": True
            }

        # 2. Check for Conflicting or Incomplete Age Details
        detected_age = self._extract_age(user_utterance)
        if detected_age is not None:
            self.stated_ages.append(detected_age)
            if len(self.stated_ages) > 1 and self.stated_ages[-1] != self.stated_ages[-2]:
                # Conflict detected!
                prev_age = self.stated_ages[-2]
                curr_age = self.stated_ages[-1]
                self.caller_age = curr_age
                bot_reply = (
                    f"Just to clarify, earlier you mentioned being {prev_age}, but you just stated {curr_age}. "
                    f"To make sure our underwriting evaluation is accurate, could you confirm your official date of birth?"
                )
                self.conversation_history.append({"speaker": "Agent", "text": bot_reply})
                return {
                    "reply": bot_reply,
                    "state": "COLLECTING_PROFILE",
                    "citation": None,
                    "action": {"type": "CONFLICT_DETECTED", "details": f"Ages stated: {prev_age} vs {curr_age}"},
                    "escalated": False
                }
            self.caller_age = detected_age

        # 3. Dynamic Knowledge Base Grounded Query (for Objections, FAQs, Policies)
        if self._detect_objection_or_faq(user_utterance):
            hits = self.retriever.search(user_utterance, top_k=2)
            gen_result = self.llm_generator.generate_response(
                user_query=user_utterance,
                retrieved_chunks=hits,
                conversation_history=self.conversation_history,
                caller_name=self.caller_name
            )
            bot_reply = gen_result["reply"]
            citation_info = gen_result["citation"]
            if citation_info:
                self.kb_citations_used.append(citation_info)

            self.conversation_history.append({"speaker": "Agent", "text": bot_reply})
            return {
                "reply": bot_reply,
                "state": self.current_state,
                "citation": citation_info,
                "action": None,
                "escalated": False,
                "model_used": gen_result.get("model_used")
            }

        # 4. Standard Qualification Workflow
        if self.current_state == "GREETING":
            self.current_state = "COLLECTING_PROFILE"
            bot_reply = (
                "Welcome to ApexCare Global Health Shield. My name is Alex. "
                "I can verify your eligibility and prepare a customized coverage quote in just two minutes. "
                "To get started, may I have your name and age?"
            )
        elif self.current_state == "COLLECTING_PROFILE":
            # Extract name if provided
            name_match = re.search(r"(?:my name is|i'm|i am|this is)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)", user_utterance, re.IGNORECASE)
            if name_match:
                self.caller_name = name_match.group(1).title()

            if "family" in user_utterance.lower():
                self.coverage_type = "Family"

            if self.caller_age is None:
                # Incomplete details: missing age
                bot_reply = f"Thank you, {self.caller_name or 'there'}. To verify your qualification, could you please confirm your current age?"
            elif self.caller_name is None:
                # Incomplete details: missing name
                bot_reply = f"Got it, {self.caller_age} years old. And may I have your full name so I can prepare your customized quote?"
            else:
                # Both name and age are known. Check eligibility boundaries
                if self.caller_age > UnderwritingRules.MAX_STANDARD_AGE:
                    self.current_state = "COMPLETED"
                    bot_reply = (
                        f"Thank you for sharing that. Because you are {self.caller_age}, our standard health shield cutoff is age 65. "
                        f"However, we offer our specialized ApexCare Senior Golden Shield designed specifically for ages 66 to 75. "
                        f"I will log your request in our system and arrange for our senior underwriting advisor to call you."
                    )
                    action_data = {
                        "customer_name": self.caller_name or "Applicant",
                        "phone": self.caller_phone,
                        "age": self.caller_age,
                        "coverage_type": self.coverage_type,
                        "qualification_status": "SENIOR_REFERRAL",
                        "recommended_plan": "ApexCare Senior Golden Shield",
                        "notes": f"Over standard age limit (Age {self.caller_age}). Routed to senior underwriting queue."
                    }
                    action_triggered = crm_dispatcher.create_lead(action_data)
                    self.crm_action_result = action_triggered
                else:
                    self.current_state = "SCREENING_HEALTH"
                    bot_reply = (
                        f"Got it, {self.caller_name or 'there'}. Do you or anyone you are enrolling have any ongoing pre-existing medical conditions, "
                        f"such as diabetes, hypertension, asthma, or recent surgeries?"
                    )
        elif self.current_state == "SCREENING_HEALTH":
            has_condition = any(c in user_utterance.lower() for c in ["yes", "asthma", "hypertension", "blood pressure", "diabetes", "cardiac"])
            if has_condition:
                self.pre_existing_conditions.append("Declared Chronic/Pre-existing Condition")

            # Finalize Qualification & Trigger Business Action
            self.current_state = "QUALIFICATION_DECISION"
            eligibility = UnderwritingRules.evaluate_eligibility(
                age=self.caller_age,
                has_pec=len(self.pre_existing_conditions) > 0,
                coverage_type=self.coverage_type
            )

            action_data = {
                "customer_name": self.caller_name or "Qualified Applicant",
                "phone": self.caller_phone,
                "age": self.caller_age,
                "coverage_type": self.coverage_type,
                "pre_existing_conditions": self.pre_existing_conditions,
                "qualification_status": eligibility["status"],
                "recommended_plan": eligibility["recommended_plan"],
                "estimated_monthly_premium": eligibility.get("monthly_premium_est"),
                "call_duration_seconds": self.call_duration_seconds,
                "notes": f"Lead qualified via automated voice agent. {eligibility.get('annual_max_benefit', '$1,000,000')} AMB tier."
            }
            action_triggered = crm_dispatcher.create_lead(action_data)
            self.crm_action_result = action_triggered

            pec_note = (
                " Note that pre-existing conditions have a 24-month waiting period as per policy rules."
                if len(self.pre_existing_conditions) > 0 else ""
            )

            bot_reply = (
                f"Great news! Based on your profile, you are pre-qualified for the {eligibility['recommended_plan']} with an "
                f"Annual Maximum Benefit of {eligibility.get('annual_max_benefit', '$1,000,000')}. Your estimated rate starts at "
                f"${eligibility.get('monthly_premium_est', 185.0)} per month with a $1,000 annual deductible.{pec_note} "
                f"I have created lead record #{action_triggered['lead_id']} and dispatched the complete schedule of benefits to your email. "
                f"Is there anything else I can clarify for you today?"
            )
        elif self.current_state == "QUALIFICATION_DECISION":
            if any(w in user_utterance.lower() for w in ["no", "thanks", "good", "all set", "bye"]):
                self.current_state = "COMPLETED"
                bot_reply = "Wonderful! Thank you for calling ApexCare Global Health. Have a healthy and pleasant day ahead!"
            else:
                bot_reply = "I would be happy to help. Feel free to ask any question about our network hospitals, deductibles, or claims."
        else:
            bot_reply = "Thank you for contacting ApexCare. If you need any further assistance, feel free to call back or visit our portal."

        self.conversation_history.append({"speaker": "Agent", "text": bot_reply})
        return {
            "reply": bot_reply,
            "state": self.current_state,
            "citation": citation_info,
            "action": action_triggered,
            "escalated": False
        }
