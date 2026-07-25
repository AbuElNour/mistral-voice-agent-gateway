from dataclasses import dataclass


@dataclass(frozen=True)
class AudioFrame:
    sequence: int
    payload: bytes
    language: str = "en"


@dataclass(frozen=True)
class GatewayEvent:
    kind: str
    detail: str
    sequence: int | None = None

