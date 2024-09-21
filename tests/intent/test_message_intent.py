import unittest

from botchan.intent.message_intent import MessageIntentType, get_message_intent_by_emoji, MessageIntent
class TestMessageIntent(unittest.TestCase):

    def test_message_intent_type_from_str(self):
        self.assertEqual(MessageIntentType.from_str("CHAT"), MessageIntentType.CHAT)
        self.assertEqual(MessageIntentType.from_str("KNOW"), MessageIntentType.KNOW)
        self.assertEqual(MessageIntentType.from_str("MIAO"), MessageIntentType.MIAO)
        self.assertEqual(MessageIntentType.from_str("EXPERT"), MessageIntentType.EXPERT)
        self.assertEqual(MessageIntentType.from_str("UNKNOWN"), MessageIntentType.UNKNOWN)
        with self.assertRaises(NotImplementedError):
            MessageIntentType.from_str("NON_EXISTENT")
    
    def test_get_message_intent_by_emoji(self):
        self.assertEqual(get_message_intent_by_emoji(":know:"), MessageIntentType.KNOW)
        self.assertEqual(get_message_intent_by_emoji(":cat:"), MessageIntentType.MIAO)
        self.assertEqual(get_message_intent_by_emoji(":nonexistent:"), MessageIntent(type=MessageIntentType.UNKNOWN))

    def test_message_intent_equality(self):
        intent1 = MessageIntent(type=MessageIntentType.CHAT, key="chat_key")
        intent2 = MessageIntent(type=MessageIntentType.CHAT, key="chat_key")
        intent3 = MessageIntent(type=MessageIntentType.KNOW, key="know_key")
        self.assertTrue(intent1 == intent2)
        self.assertFalse(intent1 == intent3)

if __name__ == '__main__':
    unittest.main()