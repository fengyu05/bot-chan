import unittest

from botchan.intent.message_intent import (
    _EMOJI,
    _UNKNOWN,
    MessageIntent,
    create_intent,
    get_message_intent_by_emoji,
)


class TestMessageIntent(unittest.TestCase):
    def test_uppercase_key(self):
        intent = MessageIntent(key="testKey")
        self.assertEqual(intent.key, "TESTKEY")

    def test_key_is_required(self):
        with self.assertRaises(AssertionError):
            create_intent()

    def test_unknown_property(self):
        intent = MessageIntent(key="somekey", metadata={_UNKNOWN: True})
        self.assertTrue(intent.unknown)

        intent_no_unknown = MessageIntent(key="somekey")
        self.assertFalse(intent_no_unknown.unknown)

    def test_equal_wo_metadata(self):
        intent1 = MessageIntent(key="somekey")
        intent2 = MessageIntent(key="SomeKey")
        self.assertTrue(intent1.equal_wo_metadata(intent2))

        intent3 = MessageIntent(key="otherkey")
        self.assertFalse(intent1.equal_wo_metadata(intent3))

    def test_create_intent_with_default(self):
        intent = create_intent("test")
        self.assertEqual(intent.key, "TEST")

    def test_create_intent_unknown(self):
        intent = create_intent(unknown=True)
        self.assertEqual(intent.key, "")
        self.assertTrue(intent.unknown)

    def test_get_message_intent_by_emoji_found(self):
        intent = get_message_intent_by_emoji(":cat:")
        self.assertEqual(intent.key, "MIAO")
        self.assertEqual(intent.metadata[_EMOJI], "cat")

    def test_get_message_intent_by_emoji_not_found(self):
        intent = get_message_intent_by_emoji(":dog:")
        self.assertEqual(intent.key, "")
        self.assertTrue(intent.unknown)


if __name__ == "__main__":
    unittest.main()
