"""
Philippines Taglish Dialogue Engine for Bancassurance and Life Insurance.
Handles natural code-switching, Philippine financial terminology,
cultural politeness (po/opo), and seamless native Taglish escalation.
"""

import re
from typing import Dict, Any, List, Optional


class PhilippinesBancassuranceBot:
    """
    Simulates a localized Bancassurance Lead Qualification & Cross-sell Voice Bot.
    Uses natural Taglish (Tagalog-English code-switching) without awkward literal translation.
    """

    def __init__(self, caller_name: Optional[str] = None):
        self.caller_name = caller_name
        self.current_state = "INIT"
        self.coverage_amount = "₱2,000,000"
        self.beneficiaries = []
        self.has_riders = False
        self.transcript: List[Dict[str, str]] = []

    def respond(self, user_utterance: str) -> Dict[str, Any]:
        """Processes customer utterance in Taglish/English and generates localized response."""
        self.transcript.append({"speaker": "Customer", "text": user_utterance})
        u_lower = user_utterance.lower()

        # Check for Human Escalation intent
        is_escalation = any(w in u_lower for w in ["makausap", "kausap", "human", "tao po", "transfer to human", "lipat sa tao", "ilipat sa tao", "totoong tao"])
        if is_escalation:
            self.current_state = "ESCALATED"
            reply = (
                "Opo, nauunawaan ko po nang lubos, Ma'am/Sir. Huwag po kayong mag-alala, "
                "ililipat ko po kayo agad-agad sa ating licensed Bancassurance Financial Specialist "
                "mula sa inyong servicing branch. Sandali lang po, paki-hold lang po ang linya."
            )
            self.transcript.append({"speaker": "Maria (Bot)", "text": reply})
            return {
                "reply": reply,
                "state": "ESCALATED",
                "escalated": True,
                "action": "TRANSFER_TO_BRANCH_SPECIALIST"
            }

        # Check for Objection: Budget & Fear of Policy Lapse
        if any(w in u_lower for w in ["budget", "mahal", "wala pa pera", "lapse", "kapos", "gastos"]):
            reply = (
                "Naiintindihan ko po kayo, Ma'am/Sir. Napaka-valid po ng concern ninyo lalo na sa panahon ngayon. "
                "Ang kagandahan po sa PhilCare Heritage plan natin, napaka-flexible po ng premium payment. "
                "May 31-day grace period po tayo kung sakaling ma-delay ang budget, at may Premium Holiday rider din "
                "para hindi po mag-lapse ang inyong coverage habang protektado pa rin ang inyong beneficiaries."
            )
            self.transcript.append({"speaker": "Maria (Bot)", "text": reply})
            return {
                "reply": reply,
                "state": "OBJECTION_HANDLED",
                "escalated": False,
                "action": "EXPLAIN_GRACE_PERIOD_RIDER"
            }

        # Check for Beneficiary / Children inquiry
        if any(w in u_lower for w in ["anak", "asawa", "beneficiary", "tagapagmana", "family"]):
            reply = (
                "Napakagandang plano po niyan, Ma'am/Sir. Pwedeng-pwede po nating ilagay ang inyong mga anak at asawa "
                "bilang primary beneficiaries. Guaranteed po na tax-free ang makukuhang coverage payout nila para sa kanilang "
                "education at kinabukasan kung may mangyari mang hindi inaasahan."
            )
            self.transcript.append({"speaker": "Maria (Bot)", "text": reply})
            return {
                "reply": reply,
                "state": "BENEFICIARY_CONFIGURED",
                "escalated": False,
                "action": "ATTACH_BENEFICIARIES"
            }

        # Check for Bank Referral / Auto-Debit
        if any(w in u_lower for w in ["bangko", "bank", "bpi", "referral", "branch", "auto-debit"]):
            reply = (
                "Tama po kayo! Dahil bank referral po ito galing sa inyong branch manager, eligible po kayo sa zero-fee "
                "automatic debit arrangement mula sa inyong savings account. Hindi niyo na po kailangang pumila buwan-buwan "
                "para magbayad ng premium."
            )
            self.transcript.append({"speaker": "Maria (Bot)", "text": reply})
            return {
                "reply": reply,
                "state": "BANK_REFERRAL_VERIFIED",
                "escalated": False,
                "action": "ENABLE_ADA"
            }

        # Default Greeting / Initiation
        if self.current_state == "INIT":
            self.current_state = "AWAITING_GOAL"
            reply = (
                "Magandang araw po! Ako po si Maria mula sa BPI-PhilCare Heritage Bancassurance. "
                "Tumatawag po ako kaugnay ng inyong inquiry sa ating life insurance coverage na may kasamang critical illness rider. "
                "Kumusta po kayo ngayon, Ma'am/Sir?"
            )
        else:
            reply = (
                "Salamat po sa impormasyon. Nais niyo po ba nating ipa-process ang proposal summary sa inyong email o branch, "
                "o may iba pa po kayong nais itanong tungkol sa ating policy terms?"
            )

        self.transcript.append({"speaker": "Maria (Bot)", "text": reply})
        return {
            "reply": reply,
            "state": self.current_state,
            "escalated": False,
            "action": None
        }
