"""
Mock CRM and Webhook Action Dispatcher for Voice Agent.
Handles lead creation, quotation generation, callback scheduling,
and human escalation dispatching.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class CRMLead(BaseModel):
    lead_id: str
    customer_name: str
    phone: str
    age: Optional[int]
    coverage_type: str
    pre_existing_conditions: List[str] = Field(default_factory=list)
    qualification_status: str  # QUALIFIED | SENIOR_REFERRAL | DISQUALIFIED | ESCALATED_HUMAN
    recommended_plan: str
    estimated_monthly_premium: Optional[float] = None
    call_duration_seconds: int = 0
    escalation_reason: Optional[str] = None
    callback_scheduled: Optional[str] = None
    notes: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class CRMWebhookDispatcher:
    """Dispatches business actions and stores records in mock CRM database."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            db_path = os.path.join(base_dir, "data", "crm_leads.json")
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load_leads(self) -> List[Dict[str, Any]]:
        with open(self.db_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_leads(self, leads: List[Dict[str, Any]]):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2)

    def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a qualified or screened lead in CRM."""
        leads = self._load_leads()
        lead_id = f"CRM-LEAD-2025-{len(leads) + 1:04d}"
        lead_data["lead_id"] = lead_id

        lead_obj = CRMLead(**lead_data)
        leads.append(lead_obj.model_dump())
        self._save_leads(leads)

        return {
            "success": True,
            "action": "LEAD_CREATED",
            "lead_id": lead_id,
            "crm_sync_status": "PROCESSED_200_OK",
            "message": f"Lead {lead_id} successfully created and synced with sales queue."
        }

    def trigger_escalation_webhook(self, escalation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches real-time human escalation webhook for live transfer."""
        leads = self._load_leads()
        esc_id = f"ESC-TICKET-2025-{len(leads) + 1:04d}"
        escalation_data["lead_id"] = esc_id
        escalation_data["qualification_status"] = "ESCALATED_HUMAN"

        lead_obj = CRMLead(**escalation_data)
        leads.append(lead_obj.model_dump())
        self._save_leads(leads)

        return {
            "success": True,
            "action": "HUMAN_ESCALATION_TRIGGERED",
            "ticket_id": esc_id,
            "target_queue": "Senior_Underwriting_Concierge",
            "priority": "HIGH",
            "message": "Call warm-transferred to licensed underwriter queue."
        }


crm_dispatcher = CRMWebhookDispatcher()
