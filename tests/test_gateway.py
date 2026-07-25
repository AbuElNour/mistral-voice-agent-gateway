import unittest

from voice_gateway import AudioFrame, VoiceGateway


class GatewayTests(unittest.TestCase):
    def test_streams_english_response(self):
        result = VoiceGateway().receive(AudioFrame(1, b"hello"))
        self.assertEqual(result["status"], "streaming")
        self.assertIn("synthetic", result["response"])

    def test_switches_to_arabic(self):
        result = VoiceGateway().receive(AudioFrame(1, "مرحبا".encode(), "ar"))
        self.assertEqual(result["language"], "ar")
        self.assertIn("تم", result["response"])

    def test_barge_in_interrupts_output(self):
        gateway = VoiceGateway()
        gateway.receive(AudioFrame(1, b"first"))
        result = gateway.receive(AudioFrame(2, b"interrupt"))
        self.assertIn("speech.interrupted", [item["kind"] for item in result["events"]])

    def test_duplicate_frame_is_ignored(self):
        gateway = VoiceGateway()
        gateway.receive(AudioFrame(1, b"first"))
        self.assertEqual(gateway.receive(AudioFrame(1, b"replay"))["status"], "duplicate")

    def test_retry_is_bounded(self):
        self.assertEqual(VoiceGateway(max_retries=2).provider_call("tts", 5)["attempts"], 3)


if __name__ == "__main__":
    unittest.main()

