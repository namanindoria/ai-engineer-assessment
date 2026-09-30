"""
Business Rules and Underwriting Logic for ApexCare Lead Qualification Voice Agent.
Implements Question 1 qualification thresholds, pricing estimates, and routing rules.
"""

from typing import Dict, Any, Optional, Tuple


class UnderwritingRules:
    """Core underwriting eligibility and business logic."""
    MIN_STANDARD_AGE = 18
    MAX_STANDARD_AGE = 65
    SENIOR_MAX_AGE = 75

    BASE_PREMIUMS = {
        "Standard": 185.00,
        "Premier": 295.00,
        "Elite Diamond": 450.00
    }

    @classmethod
    def evaluate_eligibility(
        cls,
        age: Optional[int],
        has_pec: bool = False,
        coverage_type: str = "Individual"
    ) -> Dict[str, Any]:
        """
        Evaluates lead qualification status based on age, medical baseline, and plan type.
        """
        if age is None:
            return {
                "status": "INCOMPLETE",
                "message": "Age is required to determine underwriting eligibility.",
                "qualified": False
            }

        if age < cls.MIN_STANDARD_AGE:
            return {
                "status": "DISQUALIFIED_MINOR",
                "message": f"Applicants under {cls.MIN_STANDARD_AGE} must be enrolled as dependent riders under a parent or guardian policy.",
                "qualified": False,
                "recommended_plan": "Dependent Child Rider"
            }

        if age > cls.MAX_STANDARD_AGE:
            return {
                "status": "SENIOR_REFERRAL",
                "message": f"Applicants aged {age} exceed the age {cls.MAX_STANDARD_AGE} cutoff for Standard Health Shield. They must be routed to ApexCare Senior Golden Shield with geriatric evaluation.",
                "qualified": False,
                "recommended_plan": "ApexCare Senior Golden Shield",
                "requires_specialist": True
            }

        # Determine tier and premium
        plan = "Premier" if coverage_type.lower() == "family" else "Standard"
        base_rate = cls.BASE_PREMIUMS[plan]

        # Age loading calculation
        age_factor = 1.0 + max(0, (age - 25) * 0.015)
        pec_factor = 1.20 if has_pec else 1.0

        monthly_est = round(base_rate * age_factor * pec_factor, 2)

        return {
            "status": "QUALIFIED",
            "message": "Applicant meets all entry age and primary eligibility criteria.",
            "qualified": True,
            "recommended_plan": f"ApexCare {plan} Shield",
            "monthly_premium_est": monthly_est,
            "annual_max_benefit": "$2,500,000" if plan == "Premier" else "$1,000,000",
            "standard_deductible": "$1,000",
            "pec_waiting_period_months": 24 if has_pec else 0
        }
