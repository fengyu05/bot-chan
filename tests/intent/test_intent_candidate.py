import unittest

from fluctlight.intent.intent_candidate import (
    IntentCandidate,
    parse_intent_candidate_json,
)


class TestIntentCandidate(unittest.TestCase):
    def test_intent_candidate_creation(self):
        candidate = IntentCandidate(
            understanding="The user wants to order a pizza.",
            intent_primary="ORDER_FOOD",
            intent_secondary="CHAT",
        )
        self.assertEqual(candidate.understanding, "The user wants to order a pizza.")
        self.assertEqual(candidate.intent_primary, "ORDER_FOOD")
        self.assertEqual(candidate.intent_secondary, "CHAT")

    def test_preferred_json_serialization(self):
        candidate = IntentCandidate(
            understanding="The user wants to book a flight.",
            intent_primary="BOOK_FLIGHT",
        )
        expected_json = f"{{{candidate.model_dump_json()}}}"
        self.assertEqual(candidate.perfered_json_serialization, expected_json)

    def test_parse_intent_candidate_json_success(self):
        json_text = """
        {
            "understanding": "The user wants to listen to music.",
            "intent_primary": "PLAY_MUSIC",
            "intent_secondary": "SEARCH_MUSIC"
        }"""
        candidate = parse_intent_candidate_json(json_text)
        self.assertIsNotNone(candidate)
        assert candidate
        self.assertEqual(candidate.understanding, "The user wants to listen to music.")
        self.assertEqual(candidate.intent_primary, "PLAY_MUSIC")
        self.assertEqual(candidate.intent_secondary, "SEARCH_MUSIC")

    def test_parse_intent_candidate_json_invalid_json(self):
        invalid_json_text = "not a valid json"
        candidate = parse_intent_candidate_json(invalid_json_text)
        self.assertIsNone(candidate)

    def test_parse_intent_candidate_json_validation_error(self):
        incomplete_json_text = '{"understanding": "Trying to book a hotel."}'
        candidate = parse_intent_candidate_json(incomplete_json_text)
        self.assertIsNone(candidate)


if __name__ == "__main__":
    unittest.main()
