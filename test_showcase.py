import unittest

from scripts.build_showcase import clean_pirate


class PirateCleanupTests(unittest.TestCase):
    def test_flattens_light_markdown(self):
        self.assertEqual(
            clean_pirate("## Pirate summary\n\n**Arrr**, seven hundred pounds!"),
            "Pirate summary Arrr, seven hundred pounds!",
        )

    def test_truncates_on_a_word_boundary(self):
        self.assertEqual(clean_pirate("one two three four", limit=10), "one two…")


if __name__ == "__main__":
    unittest.main()
