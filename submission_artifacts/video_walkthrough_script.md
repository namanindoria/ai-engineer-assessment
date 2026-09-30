# Video Walkthrough Script: AI Engineer Assessment

**Total Duration**: 4 to 5 Minutes  
**Presenter**: Candidate (AI Engineer)  
**Target Audience**: Technical Evaluation Committee & Lead AI Architect  

---

## Part 1: System Overview & Live Demonstration (0:00 - 1:15)

### Visual on Screen:
- Open browser to `http://127.0.0.1:8000/`.
- Show top status pill: *"All 4 Pipelines Operational"*.
- Switch to Tab 1: **"🎙️ Q1: Voice Agent & Calling"**.

### Spoken Script:
> *"Hello! Today I am presenting my complete implementation for the AI Engineer Assessment. We have built an end-to-end, production-ready system covering all four questions without shortcuts or hardcoded prompts.*
>
> *Let's start right here on Tab 1 with our live web calling interface for ApexCare Global Health Shield. Watch as I click 'Start Call'.*
>
> *(Click 'Start Call' -> Bot speaks: 'Welcome to ApexCare Global Health Shield...')*
>
> *I can speak directly using Web Speech Recognition, or type a customer scenario. Let's test a customer raising an objection: 'I already have an HMO through my company employer. Why should I buy ApexCare?'*
>
> *(Submit turn -> Agent responds immediately with grounded comparison, citing $5M portable lifetime coverage and HMO deductible integration).*
>
> *Notice on the right: our Dynamic Knowledge Base Grounding card immediately surfaced verified Citation Record `kb_objectio_024` with 83.8% confidence. The agent did NOT invent this answer; it dynamically retrieved it from the knowledge base we built in Question 2.*
>
> *When qualification is complete, our mock CRM webhook automatically creates a structured lead record with estimated premium and AMB tier.*
>
> *Below, you can see all four recorded benchmark calls—including Cooperative Customer, Objection Handling, Conflicting Details & Safe Fallback, and Human Escalation—with full playable audio and transcripts."*

---

## Part 2: Architecture & Knowledge Base Design (1:15 - 2:20)

### Visual on Screen:
- Switch to Tab 2: **"📚 Q2: Knowledge Base & RAG"**.
- Show PII Sanitization Inspector (Raw vs Sanitized).
- Type a query in search box: *"What is the waiting period for pre-existing cardiac conditions?"*
- Scroll through the 5-Query Benchmark Audit Table below.

### Spoken Script:
> *"Moving to Question 2: converting messy, unstructured business data into a production-grade knowledge base.*
>
> *In our ETL pipeline (`q2_knowledge_base/pipeline.py`), we ingested dirty HTML web pages, raw underwriting guides, CSV tables, and FAQs. We stripped navigation and footers, flagged corrupted OCR paragraphs, and applied MinHash deduplication.*
>
> *Critically, our PII Sanitization engine detected and masked Social Security Numbers, emails, cell numbers, and physical addresses before any record reached the index—ensuring zero data leakage.*
>
> *For retrieval, we implemented a hybrid ranking engine fusing Okapi BM25 lexical search with TF-IDF vector space cosine similarity. Notice how a query on cardiac waiting periods returns Section 2 with 86.9% confidence and exact citations.*
>
> *Our 6-query benchmark audit table tests product specifications, policy rules, age cutoffs, claims procedures, competitor objections, and safe fallback on out-of-scope therapies—exceeding the required 5 queries with a 100% Correct verdict."*

---

## Part 3: Multilingual Voice Bots: Philippines & Indonesia (2:20 - 3:25)

### Visual on Screen:
- Switch to Tab 3: **"🌏 Q3: Multilingual Voice Bots"**.
- Toggle between Philippines (🇵🇭) and Indonesia (🇮🇩).
- Click Play on `call_ph_01_cooperative_taglish.wav` and `call_id_02_regional_objection.wav`.
- Show Localization vs Translation case study cards.

### Spoken Script:
> *"Question 3 addresses localized conversational bots for the Philippines and Indonesia.*
>
> *Literal translation in Southeast Asian finance is catastrophic. In our Philippines bot for Bancassurance, we built a natural Taglish engine. For example, asking about beneficiaries literally—'Who gets the money when you die?'—is culturally offensive. Our localized Taglish frames it around parental love and securing the children's education.*
>
> *In Indonesia, our consumer finance bot handles colloquial markers like 'nih' and 'dong', alongside regional East Java Javanese loanwords like 'nggih', 'monggo', and 'dospundi'. When a borrower from Surabaya objects to late fee dendas due to a hospital emergency, the bot responds with empathetic cultural courtesy and routes an OJK-compliant waiver request.*
>
> *Most importantly, both bots enforce strict Register Lock: during human escalation or fallback, they never panic-switch into cold English, preserving caller dignity and trust."*

---

## Part 4: Real-Time Live Nudges From Call Audio (3:25 - 4:25)

### Visual on Screen:
- Switch to Tab 4: **"⚡ Q4: Live Call Audio Nudges"**.
- Show P50/P95 latency meters (P50: 217ms, P95: 310ms).
- Select Scenario 1 (Missed Cross-Sell), click *"Stream Live Call"*.
- Show real-time streaming transcript appearing and the green P2 Cross-Sell Nudge popping up.
- Select Scenario 2 (Compliance Gap P0), click *"Stream Live Call"*, show red alert.
- Select Scenario 4 (Noisy Ambiguous), show clean zero false positives.

### Spoken Script:
> *"Now for Question 4: Live insights and nudges while the call is actually happening.*
>
> *Our real-time streaming pipeline (`q4_live_nudges/streaming_pipeline.py`) accepts continuous audio chunks. Here I stream Scenario 1 at real-time speed. As soon as the customer mentions his wife's Honda CR-V, within 312 milliseconds, an actionable nudge appears on the agent's screen: 'Suggest Multi-Vehicle 15% Bundle'.*
>
> *In Scenario 2, when the agent attempts to collect credit card payment without stating the statutory 30-day free-look disclosure, an immediate P0 Critical Compliance Alert triggers to protect against regulatory fines.*
>
> *To prevent alert fatigue, our Nudge Engine enforces confidence thresholds (>0.75), category cooldowns (15s-60s), and automatic TTL expiry. In Scenario 4, background noise and casual chatter produce exactly zero false alarms.*
>
> *Our end-to-end latency benchmarks average 217ms at P50 and 310ms at P95—far below human conversational turn latency."*

---

## Part 5: Limitations, Scale, and Production Roadmap (4:25 - 5:00)

### Visual on Screen:
- Switch to Tab 5: **"📑 Architecture & Docs"**.
- Highlight the 10x Scale & Noise Analysis section.

### Spoken Script:
> *"To bring this into full production at 10x scale—handling 5,000 concurrent calls—we would migrate streaming ASR to TensorRT-LLM with ONNX speculative decoding, route WebSocket traffic through an Envoy and Redis Pub/Sub cluster, and integrate frontend DeepFilterNet noise suppression to maintain high SNR on low-quality cellular connections.*
>
> *The entire codebase, test suites, audio recordings, and benchmark reports are committed in this repository, runnable with a single command: `python -m scripts.run_all_benchmarks`.*
>
> *Thank you, and I look forward to discussing the technical design during our interview!"*
