"""
PII Detection and Redaction Module for Enterprise Knowledge Base Ingestion.
Ensures zero PII leakage into production vector stores, LLMs, or voice agents.
Supports US, Philippine, and Indonesian national identity and telecommunications formats.
"""

import re
from typing import Tuple, List, Dict


class PIISanitizer:
    """
    Detects and redacts sensitive PII patterns:
    - US Social Security Numbers (SSN)
    - Philippine PhilSys ID (16-digit PCN format)
    - Indonesian Nomor Induk Kependudukan (NIK: 16 digits)
    - Domestic and International Phone Numbers (US, PH +63, ID +62)
    - Email addresses
    - Physical Residential Street Addresses
    - Credit Card numbers
    - Customer Names in audit records
    """

    PATTERNS: Dict[str, re.Pattern] = {
        "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "PHILSYS_ID": re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b"),
        "INDONESIA_NIK": re.compile(r"\b(?:1[1-9]|21|[3-9]\d)\d{2}\d{6}\d{4}\b"),  # Standard 16-digit province-coded NIK
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "US_PHONE": re.compile(r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        "PH_PHONE": re.compile(r"\b(?:\+63[-.\s]?9\d{2}|09\d{2})[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        "ID_PHONE": re.compile(r"\b(?:\+62[-.\s]?8\d{2}|08\d{2})[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b"),
        "CREDIT_CARD": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
        "ADDRESS": re.compile(r"\b\d{1,5}\s+[A-Za-z0-9\s.,]+(?:Terrace|Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)[A-Za-z0-9\s,]*\d{5}\b", re.IGNORECASE)
    }

    @classmethod
    def sanitize(cls, text: str) -> Tuple[str, bool, List[str]]:
        """
        Sanitizes text by replacing PII matches with standard redaction tokens.
        
        Returns:
            sanitized_text: str
            has_pii: bool
            detected_types: List[str]
        """
        detected_types: List[str] = []
        sanitized = text

        for pii_type, pattern in cls.PATTERNS.items():
            matches = pattern.findall(sanitized)
            if matches:
                detected_types.append(pii_type)
                sanitized = pattern.sub(f"[REDACTED_{pii_type}]", sanitized)

        # Also redact sensitive sample audit names if present
        name_pattern = re.compile(r"(?:Applicant|Customer|Client):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", re.MULTILINE)
        if name_pattern.search(sanitized):
            detected_types.append("CUSTOMER_NAME")
            sanitized = name_pattern.sub(r"Applicant: [REDACTED_CUSTOMER_NAME]", sanitized)

        has_pii = len(detected_types) > 0
        return sanitized, has_pii, detected_types
