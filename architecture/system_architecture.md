# System Architecture & Technical Design

## 1. High-Level Architecture Diagram

```mermaid
flowchart TB
    subgraph Data_Tier [Data Collection & Knowledge Ingestion (Q2)]
        Raw_Docs["Unstructured Raw Inputs<br/>(HTML Scrapes, Dirty CSV, OCR TXT, PII Records)"]
        Parser["ETL Cleaner & Boilerplate Stripper"]
        Deduplicator["MinHash / Jaccard Deduplication"]
        PII_Masker["PII Redaction Engine<br/>(SSN, Email, Phone, Address)"]
        Standardizer["ISO Date & Terminology Normalizer"]
        KB_Store[("Structured JSON Knowledge Base<br/>27 Standardized Chunks")]

        Raw_Docs --> Parser --> Deduplicator --> PII_Masker --> Standardizer --> KB_Store
    end

    subgraph Hybrid_Retrieval [Hybrid Retrieval & Grounding Engine (Q2)]
        KB_Store --> BM25_Index["Okapi BM25 Lexical Index"]
        KB_Store --> Dense_Index["Dense TF-IDF / Subword Vector Index"]
        Query["User Utterance / Query"] --> BM25_Index
        Query --> Dense_Index
        BM25_Index --> Hybrid_Fusion["Score Fusion: 0.40 BM25 + 0.60 Dense + Category Boost"]
        Dense_Index --> Hybrid_Fusion
        Hybrid_Fusion --> Citations["Deterministic Grounded Citation Engine"]
    end

    subgraph Voice_Platform [Knowledge-Grounded Voice Agent (Q1)]
        Web_Caller["Web Calling Interface / WebRTC"]
        Speech_Rec["Streaming Speech-to-Text (ASR)"]
        Dialog_Engine["Conversational State Machine<br/>(Alex, ApexCare Concierge)"]
        TTS_Synth["Neural Text-to-Speech (TTS)"]
        Mock_CRM[("Mock CRM Database & Webhooks")]

        Web_Caller <--> Speech_Rec
        Speech_Rec --> Dialog_Engine
        Dialog_Engine <--> Hybrid_Fusion
        Dialog_Engine --> Citations
        Dialog_Engine --> TTS_Synth
        TTS_Synth --> Web_Caller
        Dialog_Engine -->|Lead Creation / Warm Escalation| Mock_CRM
    end

    subgraph Multilingual_Bots [Native-Language Financial Bots (Q3)]
        PH_Bot["🇵🇭 Philippines Bancassurance Bot<br/>(Taglish: Filipino-English Code-Switching)"]
        ID_Bot["🇮🇩 Indonesia Consumer Finance Bot<br/>(Colloquial Bahasa + East Java Accent Nuance)"]
        Reg_Lock["Strict Register Lock<br/>(Zero English Panic Fallback)"]

        PH_Bot --> Reg_Lock
        ID_Bot --> Reg_Lock
    end

    subgraph Real_Time_Nudges [Live Call Audio Insights & Nudges (Q4)]
        Audio_Stream["Real-Time Audio Stream Chunks (2.5s)"]
        Diarizer["Continuous Streaming ASR & Diarization"]
        Signal_Extractor["Signal Extractor<br/>(Cross-Sell, Compliance, Frustration)"]
        Nudge_Guardrails["Nudge Controls<br/>(Confidence >= 0.75, Cooldowns, TTL Expiry)"]
        Agent_HUD["Live Agent HUD / WebSocket Feed"]

        Audio_Stream --> Diarizer --> Signal_Extractor --> Nudge_Guardrails --> Agent_HUD
    end
```

## 2. Key Design Decisions & Trade-Offs

### A. Question 1: Dialogue State Machine vs Free-Form LLM Prompting
- **Decision**: Hybrid Finite State Machine (FSM) orchestrating intent recognition with dynamic Knowledge Base RAG retrieval.
- **Rationale**: Financial and healthcare lead qualification requires deterministic underwriting compliance (e.g., hard age cutoffs at 65, exact pre-existing condition waiting periods of 24 months). A pure unstructured prompt risks hallucinating rates or missing required disclosures. The FSM guarantees stage progression while delegating FAQs and objections to verified KB chunks.

### B. Question 2: Hybrid Retrieval (Lexical + Semantic)
- **Decision**: Blended Okapi BM25 (40%) and Dense Semantic Cosine Similarity (60%) with category intent boosting.
- **Rationale**: Pure vector embeddings frequently fail on exact alphanumeric policy references (e.g. `$2,500 deductible`, `Section 2.3`, `Semi-Private Room $400/day`). BM25 ensures exact token matching on numerical limits, while dense semantic vectors catch semantic synonyms (e.g. *cardiac* vs *hypertension*, *cost* vs *expensive*).

### C. Question 3: Code-Switching & Linguistic Register Lock
- **Decision**: Specialized phonetic and conversational prompt anchors rather than machine translation.
- **Rationale**: Direct machine translation in the Philippines produces archaic Tagalog that alienates younger urban borrowers, while in Indonesia it produces overly aggressive debt collection demands violating OJK guidelines. The Register Lock ensures that when an escalation or ambiguity occurs, the bot never reverts unprompted to textbook English.

### D. Question 4: Sub-400ms Streaming Chunk Architecture
- **Decision**: Decoupled chunked audio streaming pipeline with category debouncing.
- **Rationale**: Running heavy LLM prompts over an entire call post-facto provides zero value to an active live conversation. By segmenting incoming audio into 2.5-second streaming chunks and applying lightweight regex/NLP signal extraction (22ms) before generating targeted nudges (74ms), end-to-end latency remains below 320ms, allowing agent recommendations to appear before the caller finishes their thought.
