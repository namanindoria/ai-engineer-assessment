# Question 2 — Knowledge Base Retrieval Benchmark Audit Table

| Test ID | Category | User Question | Retrieved Record | Source Reference | Confidence | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Q2-TEST-01** | Product Specifications | What is the annual maximum benefit and hospital room category for the Elite Diamond tier? | `kb_schedule_013`: ApexCare Elite Diamond - Room ... | `benefits_schedule_table.csv (Record: kb_schedule_013)` | 84.9% | **Correct** |
| **Q2-TEST-02** | Policy Rules & Waiting Periods | What is the waiting period for pre-existing cardiac conditions and hypertension? | `kb_policy_w_005`: SECTION 2: PRE-EXISTING CONDIT... | `underwriting_guidelines_dirty.txt (Record: kb_policy_w_005)` | 86.9% | **Correct** |
| **Q2-TEST-03** | Qualification / Underwriting Eligibility | Can an applicant aged 68 qualify for the Standard Health Shield plan? | `kb_qualific_004`: SECTION 1: AGE ELIGIBILITY AND... | `underwriting_guidelines_dirty.txt (Record: kb_qualific_004)` | 63.2% | **Correct** |
| **Q2-TEST-04** | FAQ & Claims Operations | How do I file for a direct cashless hospital admission at an accredited network hospital? | `kb_product__003`: Direct Cashless Billing at Net... | `apexcare_marketing_page.html (Record: kb_product__003)` | 69.8% | **Correct** |
| **Q2-TEST-05** | Objection Handling | Why should I purchase ApexCare private insurance if my employer already provides an HMO? | `kb_objectio_022`: FAQ: Why should I buy ApexCare... | `internal_objection_scripts_2024.docx (Record: kb_objectio_022)` | 81.9% | **Correct** |
| **Q2-TEST-06** | Exclusions & Unsupported Questions (Safe Fallback) | Does ApexCare cover experimental gene therapy or alternative overseas holistic treatments? | `kb_exclusio_027`: FAQ: Does ApexCare cover exper... | `policy_contract_exclusions.pdf (Record: kb_exclusio_027)` | 95.6% | **Correct** |
| **Q2-TEST-07** | Boundary & Ambiguous Benefit Inquiry | Does ApexCare cover routine dental care and cosmetic teeth whitening? | `kb_outpatie_006`: SECTION 3: OUTPATIENT, OPD, AN... | `underwriting_guidelines_dirty.txt (Record: kb_outpatie_006)` | 63.2% | **Partially Correct** |
| **Q2-TEST-08** | Out-of-Domain Non-Health Inquiry | Can I file an insurance claim for accidental collision damage to my motor vehicle? | `kb_objectio_022`: FAQ: Why should I buy ApexCare... | `internal_objection_scripts_2024.docx (Record: kb_objectio_022)` | 64.1% | **Incorrect (Safe Fallback Triggered)** |


## Detailed Question Audit & Grounding Analysis

### Q2-TEST-01: Product Specifications
- **User Question**: What is the annual maximum benefit and hospital room category for the Elite Diamond tier?
- **Retrieved Chunk**: `kb_schedule_013` (ApexCare Elite Diamond - Room Category)
- **Source Reference**: `benefits_schedule_table.csv (Record: kb_schedule_013)`
- **Official Citation**: `ApexCare Policy Corpus v2.0 | Source: benefits_schedule_table.csv [Record: kb_schedule_013] | Category: schedule_of_benefits | Confidence: 84.9%`
- **Content Excerpt**: *"Plan Tier: Elite Diamond | Benefit: Room Category | Limit: Executive Suite (up to $2500/day) | Deductible: Included in annual cap | Notes: Companion bed included...."*
- **Relevance Explanation**: Retrieved chunk directly answers query with high precision. Confidence: 84.9%. Matched key concepts: ['elite diamond', 'room category', 'executive suite'].
- **Verdict**: `Correct`

### Q2-TEST-02: Policy Rules & Waiting Periods
- **User Question**: What is the waiting period for pre-existing cardiac conditions and hypertension?
- **Retrieved Chunk**: `kb_policy_w_005` (SECTION 2: PRE-EXISTING CONDITIONS AND WAITING PERIODS)
- **Source Reference**: `underwriting_guidelines_dirty.txt (Record: kb_policy_w_005)`
- **Official Citation**: `ApexCare Policy Corpus v1.0 | Source: underwriting_guidelines_dirty.txt [Record: kb_policy_w_005] | Category: policy_waiting_periods | Confidence: 86.9%`
- **Content Excerpt**: *"(Note: in internal notes referred to as 'Pre-Existing Conditions (Pre-Existing Conditions (PEC))', 'Pre-Existing Conditions (PEC)', and 'chronic conditions') 2.1 Initial Waiting Period: General illness has a mandatory 30..."*
- **Relevance Explanation**: Retrieved chunk directly answers query with high precision. Confidence: 86.9%. Matched key concepts: ['cardiac', '24-month', 'pre-existing conditions (pec)', 'hypertension'].
- **Verdict**: `Correct`

### Q2-TEST-03: Qualification / Underwriting Eligibility
- **User Question**: Can an applicant aged 68 qualify for the Standard Health Shield plan?
- **Retrieved Chunk**: `kb_qualific_004` (SECTION 1: AGE ELIGIBILITY AND ENTRY RULES)
- **Source Reference**: `underwriting_guidelines_dirty.txt (Record: kb_qualific_004)`
- **Official Citation**: `ApexCare Policy Corpus v1.0 | Source: underwriting_guidelines_dirty.txt [Record: kb_qualific_004] | Category: qualification_age_rules | Confidence: 63.2%`
- **Content Excerpt**: *"1.1 Standard Health Shield entry age is minimum 18 years to maximum 65 years at next birthday. 1.2 Children from age 30 days to 24 years may be enrolled as dependent riders under an adult policyholder, provided they are ..."*
- **Relevance Explanation**: Retrieved chunk directly answers query with high precision. Confidence: 63.2%. Matched key concepts: ['age 65', '66 through 75', 'senior golden shield', 'ineligible'].
- **Verdict**: `Correct`

### Q2-TEST-04: FAQ & Claims Operations
- **User Question**: How do I file for a direct cashless hospital admission at an accredited network hospital?
- **Retrieved Chunk**: `kb_product__003` (Direct Cashless Billing at Network Hospitals)
- **Source Reference**: `apexcare_marketing_page.html (Record: kb_product__003)`
- **Official Citation**: `ApexCare Policy Corpus v2.1 | Source: apexcare_marketing_page.html [Record: kb_product__003] | Category: product_specifications | Confidence: 69.8%`
- **Content Excerpt**: *"ApexCare maintains a global network of over 14,500 accredited medical centers. For planned admissions, cashless authorization must be requested at least 48 hours prior to admission via our member portal or telephone conc..."*
- **Relevance Explanation**: Retrieved chunk directly answers query with high precision. Confidence: 69.8%. Matched key concepts: ['cashless', 'network hospital', 'pre-authorization', '48 hours'].
- **Verdict**: `Correct`

### Q2-TEST-05: Objection Handling
- **User Question**: Why should I purchase ApexCare private insurance if my employer already provides an HMO?
- **Retrieved Chunk**: `kb_objectio_022` (FAQ: Why should I buy ApexCare private health insurance if I alre...)
- **Source Reference**: `internal_objection_scripts_2024.docx (Record: kb_objectio_022)`
- **Official Citation**: `ApexCare Policy Corpus v1.0 | Source: internal_objection_scripts_2024.docx [Record: kb_objectio_022] | Category: objection_handling | Confidence: 81.9%`
- **Content Excerpt**: *"Question: Why should I buy ApexCare private health insurance if I already have basic HMO or group coverage from my employer?
Answer: Employer group insurance is tied directly to your employment and typically has low limi..."*
- **Relevance Explanation**: Retrieved chunk directly answers query with high precision. Confidence: 81.9%. Matched key concepts: ['employer group', 'hmo', 'portable', 'guaranteed renewable', 'deductible'].
- **Verdict**: `Correct`

### Q2-TEST-06: Exclusions & Unsupported Questions (Safe Fallback)
- **User Question**: Does ApexCare cover experimental gene therapy or alternative overseas holistic treatments?
- **Retrieved Chunk**: `kb_exclusio_027` (FAQ: Does ApexCare cover experimental gene therapy or overseas ho...)
- **Source Reference**: `policy_contract_exclusions.pdf (Record: kb_exclusio_027)`
- **Official Citation**: `ApexCare Policy Corpus v1.0 | Source: policy_contract_exclusions.pdf [Record: kb_exclusio_027] | Category: exclusions_and_limits | Confidence: 95.6%`
- **Content Excerpt**: *"Question: Does ApexCare cover experimental gene therapy or overseas holistic treatments?
Answer: Official policy statement: ApexCare adheres strictly to FDA and national medical board approved allopathic treatments. Expe..."*
- **Relevance Explanation**: Retrieved chunk directly answers query with high precision. Confidence: 95.6%. Matched key concepts: ['experimental', 'holistic', 'excluded', 'strictly excluded'].
- **Verdict**: `Correct`

### Q2-TEST-07: Boundary & Ambiguous Benefit Inquiry
- **User Question**: Does ApexCare cover routine dental care and cosmetic teeth whitening?
- **Retrieved Chunk**: `kb_outpatie_006` (SECTION 3: OUTPATIENT, OPD, AND DENTAL RULES)
- **Source Reference**: `underwriting_guidelines_dirty.txt (Record: kb_outpatie_006)`
- **Official Citation**: `ApexCare Policy Corpus v1.0 | Source: underwriting_guidelines_dirty.txt [Record: kb_outpatie_006] | Category: outpatient_rules | Confidence: 63.2%`
- **Content Excerpt**: *"Terminology Note: In contract schedules, Outpatient services are designated as 'Outpatient (OPD)' (Outpatient Department) or 'Outpatient (OPD) care'. 3.1 Ambulatory specialist consultations are covered up to $150 per vis..."*
- **Relevance Explanation**: Retrieved chunk contains related policy context but lacks explicit elective cosmetic terms. Confidence: 63.2%. Correctly identifies boundary limitation.
- **Verdict**: `Partially Correct`

### Q2-TEST-08: Out-of-Domain Non-Health Inquiry
- **User Question**: Can I file an insurance claim for accidental collision damage to my motor vehicle?
- **Retrieved Chunk**: `kb_objectio_022` (FAQ: Why should I buy ApexCare private health insurance if I alre...)
- **Source Reference**: `internal_objection_scripts_2024.docx (Record: kb_objectio_022)`
- **Official Citation**: `ApexCare Policy Corpus v1.0 | Source: internal_objection_scripts_2024.docx [Record: kb_objectio_022] | Category: objection_handling | Confidence: 64.1%`
- **Content Excerpt**: *"Question: Why should I buy ApexCare private health insurance if I already have basic HMO or group coverage from my employer?
Answer: Employer group insurance is tied directly to your employment and typically has low limi..."*
- **Relevance Explanation**: Out-of-domain query correctly rejected. No target domain concepts matched. Triggers GroundedLLMGenerator safe refusal fallback without hallucinations.
- **Verdict**: `Incorrect (Safe Fallback Triggered)`

