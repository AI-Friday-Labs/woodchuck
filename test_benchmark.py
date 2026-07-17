import unittest

import benchmark


class BenchmarkConfigurationTests(unittest.TestCase):
    def test_legacy_effort_matrix_builds_unchanged_payload(self):
        config = {
            "max_tokens": 16384,
            "shuffle_seed": 1,
            "models": [
                {
                    "id": "openai/example",
                    "family": "OpenAI",
                    "reasoning_efforts": ["max"],
                }
            ],
        }

        job = benchmark.build_jobs(config)[0]
        payload = benchmark.build_request_payload(job, config, "same prompt")

        self.assertEqual(job["reasoning_effort_label"], "max")
        self.assertEqual(payload["messages"], [{"role": "user", "content": "same prompt"}])
        self.assertEqual(payload["max_tokens"], 16384)
        self.assertEqual(payload["reasoning"], {"effort": "max", "exclude": False})

    def test_custom_run_can_reserve_answer_space_with_explicit_reasoning_budget(self):
        config = {
            "max_tokens": 16384,
            "shuffle_seed": 1,
            "models": [
                {
                    "id": "anthropic/example",
                    "family": "Anthropic",
                    "runs": [
                        {
                            "label": "budget-12000",
                            "max_tokens": 16384,
                            "reasoning": {"max_tokens": 12000, "exclude": False},
                        }
                    ],
                }
            ],
        }

        job = benchmark.build_jobs(config)[0]
        payload = benchmark.build_request_payload(job, config, "same prompt")

        self.assertIsNone(job["reasoning_effort"])
        self.assertEqual(job["reasoning_effort_label"], "budget-12000")
        self.assertEqual(payload["max_tokens"], 16384)
        self.assertEqual(payload["reasoning"], {"max_tokens": 12000, "exclude": False})

    def test_custom_run_can_override_total_completion_envelope(self):
        config = {
            "max_tokens": 16384,
            "shuffle_seed": 1,
            "models": [
                {
                    "id": "openai/example",
                    "family": "OpenAI",
                    "runs": [
                        {
                            "label": "max-65536",
                            "reasoning_effort": "max",
                            "max_tokens": 65536,
                        }
                    ],
                }
            ],
        }

        job = benchmark.build_jobs(config)[0]
        payload = benchmark.build_request_payload(job, config, "same prompt")

        self.assertEqual(payload["max_tokens"], 65536)
        self.assertEqual(payload["reasoning"], {"effort": "max", "exclude": False})


class CompletionClassificationTests(unittest.TestCase):
    def test_length_limited_content_is_partial(self):
        self.assertEqual(benchmark.classify_status("visible but cut off", None, "length"), "partial")

    def test_empty_or_error_response_is_failed(self):
        self.assertEqual(benchmark.classify_status("", None, "length"), "failed")
        self.assertEqual(benchmark.classify_status("content", "server error", "stop"), "failed")

    def test_stop_with_content_is_success(self):
        self.assertEqual(benchmark.classify_status("complete", None, "stop"), "success")


if __name__ == "__main__":
    unittest.main()
