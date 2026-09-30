"""
FastAPI Server Exposing Unified APIs and WebSockets for AI Engineer Assessment.
Powers the interactive Web Calling Interface, Knowledge Base Explorer,
Multilingual Voice Bots, and Real-Time Live Nudges Pipeline.
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from q2_knowledge_base.retriever import HybridRetriever
from q1_voice_agent.agent import VoiceAgentSession
from q1_voice_agent.crm_webhook import crm_dispatcher
from q4_live_nudges.streaming_pipeline import StreamingAudioChunkProcessor


base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
kb_path = os.path.join(base_dir, "data", "kb", "health_insurance_kb.json")
retriever = HybridRetriever(kb_path=kb_path)
active_sessions: Dict[str, VoiceAgentSession] = {}
q4_processor = StreamingAudioChunkProcessor()

app = FastAPI(title="AI Engineer Assessment - Unified Production System", version="2.0.0")

# Mount Static Directories
static_dir = os.path.join(base_dir, "server", "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount Audio Files
audio_mounts = {
    "/audio/q1": os.path.join(base_dir, "q1_voice_agent", "audio"),
    "/audio/q3/ph": os.path.join(base_dir, "q3_multilingual_bots", "philippines", "audio"),
    "/audio/q3/id": os.path.join(base_dir, "q3_multilingual_bots", "indonesia", "audio"),
    "/audio/q4": os.path.join(base_dir, "q4_live_nudges", "audio_chunks")
}
for route, path in audio_mounts.items():
    if os.path.exists(path):
        app.mount(route, StaticFiles(directory=path), name=route.replace("/", "_"))


class VoiceTurnRequest(BaseModel):
    session_id: str
    utterance: str


class StreamChunkRequest(BaseModel):
    speaker: str
    text: str


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"))


# -------------------------------------------------------------
# QUESTION 1: VOICE AGENT ENDPOINTS
# -------------------------------------------------------------
@app.post("/api/q1/call/start")
def start_call():
    import uuid
    sess_id = f"CALL-WEB-{uuid.uuid4().hex[:8]}"
    session = VoiceAgentSession(session_id=sess_id, retriever=retriever)
    active_sessions[sess_id] = session
    initial = session.step("Call Connected")
    return {
        "session_id": sess_id,
        "initial_message": initial["reply"],
        "state": initial["state"]
    }


@app.post("/api/q1/call/step")
def step_call(req: VoiceTurnRequest):
    session = active_sessions.get(req.session_id)
    if not session:
        session = VoiceAgentSession(session_id=req.session_id, retriever=retriever)
        active_sessions[req.session_id] = session

    res = session.step(req.utterance)
    return {
        "reply": res["reply"],
        "state": res["state"],
        "citation": res["citation"],
        "action": res["action"],
        "escalated": res["escalated"],
        "caller_profile": {
            "name": session.caller_name,
            "age": session.caller_age,
            "coverage_type": session.coverage_type,
            "conditions": session.pre_existing_conditions
        }
    }


@app.get("/api/q1/test-calls")
def get_q1_test_calls():
    calls_dir = os.path.join(base_dir, "q1_voice_agent", "test_calls")
    results = []
    for f in sorted(os.listdir(calls_dir)):
        if f.endswith(".json") and f != "test_calls_summary.json":
            with open(os.path.join(calls_dir, f), "r", encoding="utf-8") as fp:
                results.append(json.load(fp))
    return results


# -------------------------------------------------------------
# QUESTION 2: KNOWLEDGE BASE ENDPOINTS
# -------------------------------------------------------------
@app.get("/api/q2/search")
def search_kb(q: str = Query(..., description="Search query"), top_k: int = 3):
    results = retriever.search(q, top_k=top_k)
    return [r.model_dump() for r in results]


@app.get("/api/q2/records")
def get_kb_records():
    return [r.model_dump() for r in retriever.records]


@app.get("/api/q2/audit-benchmark")
def get_q2_audit():
    audit_file = os.path.join(base_dir, "q2_knowledge_base", "retrieval_benchmark_results.json")
    if os.path.exists(audit_file):
        with open(audit_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# -------------------------------------------------------------
# QUESTION 3: MULTILINGUAL BOTS ENDPOINTS
# -------------------------------------------------------------
@app.get("/api/q3/calls")
def get_q3_calls():
    ph_file1 = os.path.join(base_dir, "q3_multilingual_bots", "philippines", "test_call_ph_1_cooperative_taglish.json")
    ph_file2 = os.path.join(base_dir, "q3_multilingual_bots", "philippines", "test_call_ph_2_objection_bancassurance.json")
    id_file1 = os.path.join(base_dir, "q3_multilingual_bots", "indonesia", "test_call_id_1_cicilan_jatuh_tempo.json")
    id_file2 = os.path.join(base_dir, "q3_multilingual_bots", "indonesia", "test_call_id_2_regional_objection.json")

    calls = {}
    for key, path in [("ph_01", ph_file1), ("ph_02", ph_file2), ("id_01", id_file1), ("id_02", id_file2)]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                calls[key] = json.load(f)
    return calls


@app.get("/api/q3/configs")
def get_q3_configs():
    ph_cfg = os.path.join(base_dir, "q3_multilingual_bots", "philippines", "bot_config.json")
    id_cfg = os.path.join(base_dir, "q3_multilingual_bots", "indonesia", "bot_config.json")
    res = {}
    if os.path.exists(ph_cfg):
        with open(ph_cfg, "r", encoding="utf-8") as f:
            res["philippines"] = json.load(f)
    if os.path.exists(id_cfg):
        with open(id_cfg, "r", encoding="utf-8") as f:
            res["indonesia"] = json.load(f)
    return res


# -------------------------------------------------------------
# QUESTION 4: REAL-TIME NUDGES ENDPOINTS
# -------------------------------------------------------------
@app.post("/api/q4/stream-chunk")
def stream_audio_chunk(req: StreamChunkRequest):
    return q4_processor.process_audio_chunk(speaker=req.speaker, audio_text_chunk=req.text)


@app.get("/api/q4/scenarios")
def get_q4_scenarios():
    sc_dir = os.path.join(base_dir, "q4_live_nudges", "test_scenarios")
    scenarios = []
    for f in sorted(os.listdir(sc_dir)):
        if f.endswith(".json"):
            with open(os.path.join(sc_dir, f), "r", encoding="utf-8") as fp:
                scenarios.append(json.load(fp))
    return scenarios


@app.get("/api/q4/latency-report")
def get_q4_latency_report():
    rep_file = os.path.join(base_dir, "q4_live_nudges", "latency_report.json")
    if os.path.exists(rep_file):
        with open(rep_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@app.websocket("/ws/q4/live")
async def websocket_live_nudges(websocket: WebSocket):
    await websocket.accept()
    local_processor = StreamingAudioChunkProcessor()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            speaker = payload.get("speaker", "Customer")
            text = payload.get("text", "")
            res = local_processor.process_audio_chunk(speaker=speaker, audio_text_chunk=text)
            await websocket.send_json(res)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
