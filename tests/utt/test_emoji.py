import unittest

from fluctlight.utt.emoji import get_leading_emoji, strip_leading_emoji

class TestEmojiFunctions(unittest.TestCase):

    def test_get_leading_emoji(self):
        self.assertEqual(get_leading_emoji(":smile: Hello"), "smile")
        self.assertEqual(get_leading_emoji("Hello :smile:"), "")
        self.assertEqual(get_leading_emoji(""), "")
        
    def test_strip_leading_emoji(self):
        self.assertEqual(strip_leading_emoji(":smile: Hello"), " Hello")
        self.assertEqual(strip_leading_emoji("Hello :smile:"), "Hello :smile:")
        self.assertEqual(strip_leading_emoji(""), "")
        self.assertEqual(strip_leading_emoji(":smile:"), "")
        self.assertEqual(strip_leading_emoji(":smile: :joy: Hello"), " :joy: Hello")

if __name__ == "__main__":
    unittest.main()
