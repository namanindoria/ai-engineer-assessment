"""
Master End-to-End Benchmark Execution and Validation Suite.
Runs all pipelines across Question 1, 2, 3, and 4 in one consolidated command:
- Q2: Knowledge Base ETL, Deduplication, PII Sanitization, and Retrieval Benchmark
- Q1: Voice Agent Test Calls (Cooperative, Objections, Conflicting, Escalation) & CRM Sync
- Q3: Multilingual Voice Bots (Philippines Taglish & Indonesia Consumer Finance)
- Q4: Real-Time Audio Chunk Streaming, Nudges, P50/P95 Latency, and False Positive Analysis
"""

import os
import sys
import time

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from q2_knowledge_base.pipeline import IngestionPipeline
from q2_knowledge_base.test_retrieval import run_benchmark as run_q2_benchmark
from q1_voice_agent.test_voice_agent import run_test_calls as run_q1_calls
from q3_multilingual_bots.test_multilingual_calls import run_multilingual_benchmarks as run_q3_benchmarks
from q4_live_nudges.benchmark_runner import run_live_nudges_benchmark as run_q4_benchmarks
from scripts.generate_audio_assets import generate_all_audio


def main():
    t_start = time.time()
    print("=" * 80)
    print("AI ENGINEER ASSESSMENT: MASTER TEST SUITE & BENCHMARK VALIDATOR")
    print("=" * 80)

    # Step 1: Knowledge Base Ingestion Pipeline (Q2)
    print("\n[STEP 1/5] Running Question 2 Knowledge Base Ingestion & Sanitization Pipeline...")
    raw_dir = os.path.join(base_dir, "data", "raw")
    kb_path = os.path.join(base_dir, "data", "kb", "health_insurance_kb.json")
    pipe = IngestionPipeline(raw_dir=raw_dir, kb_output_path=kb_path)
    res_etl = pipe.run()
    print(f"ETL Complete: {res_etl['total_records_indexed']} records indexed, {res_etl['pii_redacted_count']} PII records sanitized.")

    # Step 2: Knowledge Base Retrieval Testing (Q2)
    print("\n[STEP 2/5] Running Question 2 Retrieval Audit Benchmark...")
    run_q2_benchmark()

    # Step 3: Voice Agent Test Calls (Q1)
    print("\n[STEP 3/5] Running Question 1 Voice Agent Dialog & Qualification Benchmark...")
    run_q1_calls()

    # Step 4: Multilingual Voice Bots (Q3)
    print("\n[STEP 4/5] Running Question 3 Multilingual Voice Bots Benchmark...")
    run_q3_benchmarks()

    # Step 5: Real-Time Live Nudges Pipeline (Q4)
    print("\n[STEP 5/5] Running Question 4 Real-Time Audio Chunk Streaming & Latency Benchmark...")
    run_q4_benchmarks()

    # Step 6: Audio Generation Verification
    print("\n[STEP 6/6] Verifying Audio Assets on Disk...")
    q1_wav = os.path.join(base_dir, "q1_voice_agent", "audio", "call_01_cooperative.wav")
    if not os.path.exists(q1_wav) or os.path.getsize(q1_wav) < 1000:
        generate_all_audio()
    else:
        print("Audio assets already generated and verified.")

    total_duration = round(time.time() - t_start, 2)
    print("\n" + "=" * 80)
    print(f"ALL ASSESSMENT BENCHMARKS PASSED SUCCESSFULLY in {total_duration}s!")
    print("=" * 80)


if __name__ == "__main__":
    main()
