"""
Schema definitions for the Knowledge Base and Retrieval Engine.
Complies with Question 2 requirements and enterprise RAG standards.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class KBRecord(BaseModel):
    """
    Standardized Knowledge Base Record Schema.
    Matches the specification in Question 2:
    - record_id: unique identifier (e.g. kb_product_001)
    - title: descriptive title of chunk
    - content: sanitized, standardized chunk text
    - category: taxonomy category
    - source: source document / section name
    - source_file: file path or URL
    - version: document version (e.g. 1.0, 2.1)
    - has_pii: boolean indicating if PII was detected and redacted
    - pii_types_redacted: list of PII types found (e.g. ['SSN', 'PHONE'])
    - last_updated: ISO-8601 date string
    - tags: semantic indexing tags
    - token_count: estimated token count of chunk
    """
    record_id: str = Field(..., description="Unique record identifier")
    title: str = Field(..., description="Clean record title")
    content: str = Field(..., description="Cleaned, normalized, and redacted content")
    category: str = Field(..., description="Taxonomy classification category")
    source: str = Field(..., description="Source section or document identifier")
    source_file: str = Field(..., description="Origin file name")
    version: str = Field(default="1.0", description="Document or policy version")
    has_pii: bool = Field(default=False, description="Flag indicating if PII was detected and redacted")
    pii_types_redacted: List[str] = Field(default_factory=list, description="Types of PII sanitized")
    last_updated: str = Field(..., description="ISO 8601 standardized date")
    tags: List[str] = Field(default_factory=list, description="Search keywords and taxonomy tags")
    token_count: int = Field(default=0, description="Word/token count")


class RetrievalResult(BaseModel):
    """Result returned by the Hybrid Retrieval Engine."""
    record_id: str
    title: str
    content: str
    category: str
    source: str
    source_file: str
    version: str
    score: float
    bm25_score: float
    dense_score: float
    citation: str
    matched_terms: List[str] = Field(default_factory=list)


class RetrievalAudit(BaseModel):
    """Audit schema for evaluating retrieval accuracy."""
    test_id: str
    user_question: str
    retrieved_chunk: Optional[RetrievalResult]
    source_reference: str
    relevance_explanation: str
    verdict: str  # 'Correct' | 'Partially Correct' | 'Incorrect'
