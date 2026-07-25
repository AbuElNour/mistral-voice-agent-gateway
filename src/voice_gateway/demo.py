import json

from .gateway import VoiceGateway
from .types import AudioFrame


def main():
    gateway = VoiceGateway()
    print(json.dumps(gateway.receive(AudioFrame(1, b"hello synthetic agent")), indent=2, ensure_ascii=False))
    print(json.dumps(gateway.receive(AudioFrame(2, "مرحبا".encode(), "ar")), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

