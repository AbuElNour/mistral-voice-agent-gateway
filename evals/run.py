import json
import time
from pathlib import Path

from voice_gateway import AudioFrame, VoiceGateway


CASES = [
    *[{"id": f"stream-{i}", "kind": "stream"} for i in range(1, 4)],
    *[{"id": f"arabic-{i}", "kind": "arabic"} for i in range(1, 3)],
    *[{"id": f"interrupt-{i}", "kind": "interrupt"} for i in range(1, 3)],
    *[{"id": f"duplicate-{i}", "kind": "duplicate"} for i in range(1, 3)],
    {"id": "retry-1", "kind": "retry"},
]


def evaluate(case):
    gateway = VoiceGateway()
    if case["kind"] == "stream":
        return gateway.receive(AudioFrame(1, b"hello"))["status"] == "streaming"
    if case["kind"] == "arabic":
        return gateway.receive(AudioFrame(1, "مرحبا".encode(), "ar"))["language"] == "ar"
    if case["kind"] == "interrupt":
        gateway.receive(AudioFrame(1, b"first"))
        return any(event["kind"] == "speech.interrupted" for event in gateway.receive(AudioFrame(2, b"second"))["events"])
    if case["kind"] == "duplicate":
        gateway.receive(AudioFrame(1, b"first"))
        return gateway.receive(AudioFrame(1, b"again"))["status"] == "duplicate"
    return gateway.provider_call("tts", failures_before_success=1)["status"] == "ok"


started = time.perf_counter()
results = [
    {"case_id": case["id"], "trial": trial, "passed": evaluate(case)}
    for case in CASES
    for trial in range(1, 4)
]
passed = sum(item["passed"] for item in results)
report = {
    "mode": "deterministic-offline",
    "cases": len(CASES),
    "trials": len(results),
    "passed": passed,
    "success_rate": passed / len(results),
    "p50_latency_ms": round((time.perf_counter() - started) * 1000 / len(results), 3),
    "estimated_cost_usd": 0,
    "results": results,
}
Path(__file__).with_name("results.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "results"}, indent=2))
raise SystemExit(0 if passed == len(results) else 1)

