import unittest

import score_results


class JsonExtractionTests(unittest.TestCase):
    def test_final_fenced_json_is_valid_and_final(self):
        candidate = score_results.json_candidate('Explanation\n```json\n{"answer": 42}\n```')
        self.assertIsNotNone(candidate)
        self.assertTrue(candidate.final)
        self.assertEqual(candidate.value, {"answer": 42})

    def test_trailing_verdict_means_json_is_not_final(self):
        candidate = score_results.json_candidate(
            '```json\n{"answer": 42}\n```\nFinal verdict: definitely 42.'
        )
        self.assertIsNotNone(candidate)
        self.assertFalse(candidate.final)


class CreativeExtractionTests(unittest.TestCase):
    def test_three_line_prose_haiku_beats_compressed_json_copy(self):
        text = '''## Haiku
Wood beneath bright paws
Groundhog weighs the stubborn log
Spring wind moves the chips

## Pirate Summary
Arrr, timber!

```json
{"haiku":"Wood beneath bright paws, Groundhog weighs the stubborn log, Spring wind moves the chips"}
```'''
        candidate = score_results.json_candidate(text)
        self.assertEqual(
            score_results.extract_haiku(text, candidate),
            [
                "Wood beneath bright paws",
                "Groundhog weighs the stubborn log",
                "Spring wind moves the chips",
            ],
        )

    def test_known_haiku_counts_as_575(self):
        lines = [
            "Wood beneath bright paws",
            "Groundhog weighs the stubborn log",
            "Spring wind moves the chips",
        ]
        self.assertEqual([score_results.line_syllables(line) for line in lines], [5, 7, 5])


class StructuredComplianceTests(unittest.TestCase):
    def test_structured_kg_and_lb_conversion(self):
        candidate = score_results.JsonCandidate(
            {
                "si": {"value": 317.5, "unit": "kg"},
                "imperial": {"value": 700, "unit": "lb"},
            },
            0,
            1,
            True,
        )
        self.assertTrue(score_results.has_structured_conversion(candidate))

    def test_structured_kg_and_short_ton_conversion(self):
        candidate = score_results.JsonCandidate(
            {"si": {"value": 7100, "unit": "kg"}, "imperial": {"short_tons": 7.8}},
            0,
            1,
            True,
        )
        self.assertTrue(score_results.has_structured_conversion(candidate))

    def test_numbered_assumptions_are_multiple(self):
        text = """## Assumptions

1. Chuck means move material.
2. Wood arrives in manageable pieces.
3. The period is one burrow excavation.

## Result

About 318 kg.
"""
        self.assertTrue(score_results.multiple_assumptions(text, None))


if __name__ == "__main__":
    unittest.main()
