from __future__ import annotations

from dataclasses import asdict

from .types import AudioFrame, GatewayEvent


class VoiceGateway:
    """Deterministic streaming state machine with interruption and retry controls."""

    def __init__(self, max_retries: int = 2) -> None:
        self.max_retries = max_retries
        self.events: list[GatewayEvent] = []
        self._last_sequence = -1
        self._speaking = False

    def receive(self, frame: AudioFrame) -> dict:
        if frame.sequence <= self._last_sequence:
            self.events.append(GatewayEvent("frame.duplicate", "ignored replayed frame", frame.sequence))
            return {"status": "duplicate", "events": [asdict(item) for item in self.events]}
        self._last_sequence = frame.sequence
        if self._speaking:
            self._speaking = False
            self.events.append(GatewayEvent("speech.interrupted", "caller barge-in stopped output", frame.sequence))
        self.events.append(GatewayEvent("frame.accepted", f"{len(frame.payload)} bytes", frame.sequence))
        transcript = frame.payload.decode("utf-8", errors="replace").strip()
        self.events.append(GatewayEvent("stt.completed", transcript, frame.sequence))
        response = self._respond(transcript, frame.language)
        self._speaking = True
        self.events.append(GatewayEvent("tts.started", response, frame.sequence))
        return {
            "status": "streaming",
            "transcript": transcript,
            "response": response,
            "language": frame.language,
            "events": [asdict(item) for item in self.events],
        }

    def provider_call(self, operation, failures_before_success: int = 0):
        for attempt in range(self.max_retries + 1):
            if attempt >= failures_before_success:
                self.events.append(GatewayEvent("provider.succeeded", operation))
                return {"status": "ok", "attempts": attempt + 1}
            self.events.append(GatewayEvent("provider.retry", operation))
        self.events.append(GatewayEvent("provider.failed", operation))
        return {"status": "failed", "attempts": self.max_retries + 1}

    @staticmethod
    def _respond(transcript: str, language: str) -> str:
        if language == "ar":
            return "تم استلام طلبك التجريبي. هل تريد المتابعة؟"
        return "Your synthetic request was received. Would you like to continue?"

