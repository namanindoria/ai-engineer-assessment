"""
Latency Tracker and Metrics Calculator for Question 4 Real-Time Nudge Pipeline.
Measures P50, P90, P95, and P99 latency percentiles across:
- ASR Streaming Transcription
- Signal Extraction
- LLM / Nudge Generation
- WebSocket / UI Delivery
- End-to-End Latency (Audio Chunk -> Agent Screen)
"""

import time
from typing import List, Dict, Any, Optional
import numpy as np
from pydantic import BaseModel, Field


class LatencyRecord(BaseModel):
    chunk_id: str
    asr_ms: float
    signal_extraction_ms: float
    nudge_gen_ms: float
    delivery_ms: float
    end_to_end_ms: float
    timestamp: float = Field(default_factory=time.time)


class LatencyBenchmarkTracker:
    """Tracks latency samples across all pipeline stages."""

    def __init__(self):
        self.records: List[LatencyRecord] = []

    def record_chunk(
        self,
        chunk_id: str,
        asr_ms: float,
        signal_extraction_ms: float,
        nudge_gen_ms: float,
        delivery_ms: float
    ) -> LatencyRecord:
        e2e = round(asr_ms + signal_extraction_ms + nudge_gen_ms + delivery_ms, 2)
        rec = LatencyRecord(
            chunk_id=chunk_id,
            asr_ms=round(asr_ms, 2),
            signal_extraction_ms=round(signal_extraction_ms, 2),
            nudge_gen_ms=round(nudge_gen_ms, 2),
            delivery_ms=round(delivery_ms, 2),
            end_to_end_ms=e2e
        )
        self.records.append(rec)
        return rec

    def compute_percentiles(self) -> Dict[str, Any]:
        """Calculates P50, P90, P95, P99 across all pipeline stages."""
        if not self.records:
            return {"count": 0}

        stages = {
            "asr_transcription": [r.asr_ms for r in self.records],
            "signal_extraction": [r.signal_extraction_ms for r in self.records],
            "nudge_generation": [r.nudge_gen_ms for r in self.records],
            "ui_delivery": [r.delivery_ms for r in self.records],
            "end_to_end": [r.end_to_end_ms for r in self.records]
        }

        report = {"sample_count": len(self.records), "metrics": {}}

        for stage, values in stages.items():
            arr = np.array(values)
            report["metrics"][stage] = {
                "mean_ms": round(float(np.mean(arr)), 2),
                "min_ms": round(float(np.min(arr)), 2),
                "max_ms": round(float(np.max(arr)), 2),
                "p50_ms": round(float(np.percentile(arr, 50)), 2),
                "p90_ms": round(float(np.percentile(arr, 90)), 2),
                "p95_ms": round(float(np.percentile(arr, 95)), 2),
                "p99_ms": round(float(np.percentile(arr, 99)), 2),
            }

        return report
