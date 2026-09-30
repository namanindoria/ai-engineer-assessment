# Question 2 — Production-Ready Knowledge Base Technical Design Guide

## 1. Document Extraction & Cleaning Methodology

### A. Website Extraction & Boilerplate Stripping
- **Input Web Pages**: Enterprise healthcare brochures (HTML) contain significant non-content noise:
  - Sticky navigation headers (`<header>`, `<div class="top-nav-bar">`)
  - Marketing sidebar cross-promotions (`<aside class="marketing-sidebar">`)
  - Cookie consent banners and legal disclaimers (`<span class="cookie-banner">`)
  - Footer navigational trees (`<footer>`)
- **Cleaning Strategy**:
  - The ETL pipeline (`q2_knowledge_base/pipeline.py`) uses regex and DOM tree segmentation to isolate semantic `<main>` and `<section>` nodes.
  - All boilerplate wrappers are discarded before tokenization, eliminating duplicate promotional slogans (e.g. *"PROMOTION: Sign up this month..."*) that would otherwise skew TF-IDF keyword frequencies.

### B. Extraction Failures & Source Error Handling
- **Unstructured Text & Damaged OCR**: In raw underwriting guides, OCR scanners produce corrupted leaf data (e.g. `[CORRUPTED_PARAGRAPH_ENCODING_ERROR: \x00\xff NULL_BYTE_FAILURE]`).
- **Mitigation & Flagging**:
  - The pipeline scans for binary null bytes, unparseable glyphs, and damaged character sequences.
  - Rather than silently dropping or ingesting garbage tokens, the system injects a traceable flag:
    `[FLAGGED_SOURCE_ERROR: Unparseable corrupted OCR block omitted from indexing. Underwriter review required.]`
  - This preserves an audit trail while preventing corrupted embeddings from polluting the retrieval space.

### C. Deduplication Strategy (Exact & Near-Duplicate)
- **Exact Duplicates**: Evaluated via canonical MD5 content hashing of normalized whitespace tokens. Duplicate table rows (e.g. duplicate emergency evacuation limit lines in CSV) are dropped instantly.
- **Near-Duplicates**: Evaluated using token-level Jaccard similarity:
  $$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$
  When $J(A, B) \ge 0.70$ (e.g., FAQ-01 vs FAQ-03 where identical employer HMO rebuttals appear with minor phrasing differences), the pipeline keeps the authoritative source document and prunes the secondary scrape.

### D. Terminology & Date Standardization
- **Taxonomy Normalization**: Business documents use inconsistent, colloquial terminology. The pipeline maps these to canonical concepts:
  - `OPD` / `Ambulatory Care` $\rightarrow$ `Outpatient (OPD)`
  - `Excess` $\rightarrow$ `Deductible (Excess)`
  - `PEC` / `Chronic Baseline` $\rightarrow$ `Pre-Existing Conditions (PEC)`
- **Date Standardization**: Varied date formats (`15th Nov 2024`, `11/15/2024`, `12/01/2024`) are parsed and normalized into ISO 8601 strings (`2024-11-15`, `2024-12-01`).

### E. Personally Identifiable Information (PII) Protection
- **PII Detection Engine** (`q2_knowledge_base/pii_sanitizer.py`):
  - Ingested underwriter sample logs often contain sensitive client records.
  - The pipeline runs dual-pass regex and pattern recognition:
    - US Social Security Numbers (`\b\d{3}-\d{2}-\d{4}\b`) $\rightarrow$ `[REDACTED_SSN]`
    - Phone numbers (domestic/international) $\rightarrow$ `[REDACTED_PHONE]`
    - Email addresses $\rightarrow$ `[REDACTED_EMAIL]`
    - Residential street addresses $\rightarrow$ `[REDACTED_ADDRESS]`
    - Customer Names $\rightarrow$ `[REDACTED_CUSTOMER_NAME]`
  - Sets metadata flag `has_pii = True` and logs redacted types in `pii_types_redacted` for security compliance audits.

---

## 2. Knowledge-Base Schema & Taxonomy

### A. Document Schema Specification
Every indexed chunk conforms to the Pydantic model `KBRecord`:

```python
class KBRecord(BaseModel):
    record_id: str             # Unique identifier (e.g. kb_product_001, kb_policy_w_005)
    title: str                 # Descriptive title of chunk
    content: str               # Cleaned, standardized, and PII-redacted text
    category: str              # Taxonomy category
    source: str                # Source section name
    source_file: str           # Origin file name (e.g. underwriting_guidelines_dirty.txt)
    version: str               # Document or policy version (e.g. 1.0, 2.1)
    has_pii: bool              # Flag indicating if PII was detected and sanitized
    pii_types_redacted: List[str] # List of sanitized PII categories (SSN, PHONE, etc.)
    last_updated: str          # ISO 8601 standardized date string
    tags: List[str]            # Semantic search keywords
    token_count: int           # Word / token count
```

### B. Sample Production Record
```json
{
  "record_id": "kb_policy_w_005",
  "title": "SECTION 2: PRE-EXISTING CONDITIONS AND WAITING PERIODS",
  "content": "2.1 Initial Waiting Period: General illness has a mandatory 30-day waiting period from the policy inception date. Accidents have zero waiting period. 2.2 Specified Serious Illnesses: A 120-day waiting period applies to elective procedures. 2.3 Pre-Existing Conditions (PEC): Any medical condition diagnosed within 24 months prior is subject to a 24-month continuous coverage waiting period. 2.4 Cardiac and Cardiovascular conditions are covered after 24-month PEC waiting period subject to a standard 20% underwriting Deductible (Excess) loading.",
  "category": "policy_waiting_periods",
  "source": "SECTION 2: PRE-EXISTING CONDITIONS",
  "source_file": "underwriting_guidelines_dirty.txt",
  "version": "1.0",
  "has_pii": false,
  "pii_types_redacted": [],
  "last_updated": "2024-11-15",
  "tags": ["underwriting", "eligibility", "pec", "waiting_period", "deductible"],
  "token_count": 86
}
```

### C. Chunking Strategy
- **Hierarchical Structural Chunking**: Rather than arbitrary character-length splits (which sever tables and clause definitions), chunks are demarcated along document hierarchy boundaries (`<section>` elements in HTML, `SECTION X` headers in policy guides, and atomic benefit tier rows in CSV schedules).
- **Context Retention**: Each chunk retains parent tier headings and plan metadata, ensuring standalone semantic completeness.

---

## 3. Hybrid Retrieval & Citation Engine

### A. Retrieval Formula
Our production engine fuses lexical and semantic representations:
$$\text{Score}(q, d) = 0.40 \cdot \frac{\text{BM25}(q, d)}{\max(\text{BM25})} + 0.60 \cdot \text{CosineSim}(\vec{v}_q, \vec{v}_d) + \text{IntentBonus}$$
- **BM25 Lexical Search**: Uses Okapi BM25 ($k_1=1.5, b=0.75$) with Lucene-smoothed IDF to pinpoint exact numerical thresholds (e.g. `$2,500`, `24-month`, `65 years`).
- **Dense Subword TF-IDF Vector Cosine Similarity**: Captures synonymic intent (e.g., *heart condition* $\leftrightarrow$ *cardiovascular / hypertension*).
- **Intent Bonus**: $+0.08$ boost when 3 or more salient domain keywords co-occur.

### B. Citation Format
Every answer supplied to the Voice Agent or RAG Copilot includes a deterministic citation string:
```text
ApexCare Policy Corpus v{version} | Source: {source_file} [Record: {record_id}] | Category: {category} | Confidence: {score}%
```
This guarantees complete auditability back to official underwriting source files.
