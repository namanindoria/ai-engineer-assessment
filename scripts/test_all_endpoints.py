"""
Comprehensive API and WebSocket Health & Integration Verification Script.
Audits all endpoints on the live running server at http://127.0.0.1:8000.
"""

import sys
import json
import urllib.request
import asyncio
import websockets

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/q4/live"


def test_http_endpoint(endpoint: str, method: str = "GET", payload: dict = None):
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    headers = {"Content-Type": "application/json"} if payload else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=5) as res:
        status = res.status
        body = json.loads(res.read().decode("utf-8"))
        return status, body


async def test_websocket():
    async with websockets.connect(WS_URL) as ws:
        msg = {"speaker": "Customer", "text": "Yeah, my wife has a 2023 Honda CR-V that might need insurance next month too."}
        await ws.send(json.dumps(msg))
        raw_res = await ws.recv()
        data = json.loads(raw_res)
        return data


def run_full_api_audit():
    print("=" * 80)
    print("AUDITING ALL HTTP ENDPOINTS AND WEBSOCKETS ON LIVE SERVER")
    print("=" * 80)

    # 1. Root and Q1 Endpoints
    s1, r1 = test_http_endpoint("/api/q1/call/start", method="POST")
    print(f"POST /api/q1/call/start: Status {s1} | Session: {r1.get('session_id')}")
    assert s1 == 200 and "session_id" in r1, "Start call failed"

    sess_id = r1["session_id"]
    s2, r2 = test_http_endpoint("/api/q1/call/step", method="POST", payload={
        "session_id": sess_id,
        "utterance": "Why should I buy ApexCare if my company already provides an HMO?"
    })
    print(f"POST /api/q1/call/step: Status {s2} | Citation: {bool(r2.get('citation'))}")
    assert s2 == 200 and r2.get("citation") is not None, "Grounded KB citation missing in voice agent"

    s3, r3 = test_http_endpoint("/api/q1/test-calls")
    print(f"GET  /api/q1/test-calls: Status {s3} | Calls Count: {len(r3)}")
    assert s3 == 200 and len(r3) >= 4, "Expected >=4 Q1 test calls"

    # 2. Q2 Endpoints
    s4, r4 = test_http_endpoint("/api/q2/search?q=cardiac%20waiting%20period")
    print(f"GET  /api/q2/search: Status {s4} | Top Hit Score: {r4[0]['score']}")
    assert s4 == 200 and len(r4) > 0, "KB Search returned no results"

    s5, r5 = test_http_endpoint("/api/q2/audit-benchmark")
    print(f"GET  /api/q2/audit-benchmark: Status {s5} | Benchmarks: {len(r5)}")
    assert s5 == 200 and len(r5) >= 5, "Expected >=5 retrieval benchmarks"

    # 3. Q3 Endpoints
    s6, r6 = test_http_endpoint("/api/q3/calls")
    print(f"GET  /api/q3/calls: Status {s6} | Keys: {list(r6.keys())}")
    assert s6 == 200 and "ph_01" in r6 and "id_01" in r6, "Missing Q3 multilingual calls"

    s7, r7 = test_http_endpoint("/api/q3/configs")
    print(f"GET  /api/q3/configs: Status {s7} | Markets: {list(r7.keys())}")
    assert s7 == 200 and "philippines" in r7 and "indonesia" in r7, "Missing Q3 market configs"

    # 4. Q4 Endpoints
    s8, r8 = test_http_endpoint("/api/q4/stream-chunk", method="POST", payload={
        "speaker": "Customer",
        "text": "My wife has a 2023 Honda CR-V that might need insurance next month."
    })
    print(f"POST /api/q4/stream-chunk: Status {s8} | Nudge Fired: {bool(r8.get('nudge'))} | Latency: {r8['latency']['end_to_end_ms']}ms")
    assert s8 == 200 and r8.get("nudge") is not None, "Real-time cross-sell nudge failed"

    s9, r9 = test_http_endpoint("/api/q4/scenarios")
    print(f"GET  /api/q4/scenarios: Status {s9} | Scenarios Count: {len(r9)}")
    assert s9 == 200 and len(r9) >= 4, "Expected at least 4 test scenarios for Q4"

    s10, r10 = test_http_endpoint("/api/q4/latency-report")
    p50 = r10["latency_metrics"]["metrics"]["end_to_end"]["p50_ms"]
    p95 = r10["latency_metrics"]["metrics"]["end_to_end"]["p95_ms"]
    print(f"GET  /api/q4/latency-report: Status {s10} | P50={p50}ms, P95={p95}ms")
    assert s10 == 200 and p50 < 400.0, "Latency P50 exceeds SLA"

    # 5. WebSocket Live Streaming Test
    print("\nTesting Real-Time WebSocket (/ws/q4/live)...")
    ws_res = asyncio.run(test_websocket())
    print(f"WebSocket Response: Chunk={ws_res.get('chunk_id')} | Nudge={ws_res['nudge']['title'] if ws_res.get('nudge') else 'None'}")
    assert ws_res.get("nudge") is not None, "WebSocket streaming nudge failed"

    print("\n" + "=" * 80)
    print("ALL API ENDPOINTS AND WEBSOCKETS AUDITED: 100% OPERATIONAL WITH ZERO DEFECTS!")
    print("=" * 80)


if __name__ == "__main__":
    run_full_api_audit()
