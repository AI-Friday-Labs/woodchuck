# Objective compliance evaluation

This report scores reproducible prompt compliance, not whether a response is factually correct, insightful, or genuinely funny. Those require the separate blinded quality protocol below.

## Score summary

- Responses scored: 71
- Mean / median: 92.4 / 93.0
- Range: 80-100
- Grades: A 57 / B 14 / C 0 / D 0 / F 0

## Rubric (100 points)

| Section | Points | Deterministic checks |
|---|---:|---|
| JSON and output structure | 30 | Parseable JSON (12), final block (6), and JSON coverage of estimate, assumptions, uncertainty, SI plus imperial units, haiku, and pirate summary (12) |
| Quantitative and scientific compliance | 25 | Numeric estimate, SI units, imperial units, consistent conversion, numeric uncertainty, and visible math/physics |
| Assumptions and evidence | 15 | Explicit and multiple assumptions, citation markers, and locatable sources/references |
| Creative requirements | 20 | Haiku present, three-line form, heuristic 5-7-5 check, pirate summary, and pirate dialect |
| Breadth and structure | 10 | Linguistics, history, physics/math, humor signal, and organized presentation |

The 5-7-5 test is a deterministic English syllable heuristic. Exact matches receive 6 points; each line within one syllable receives 3 points. It should be manually audited before using small score differences to declare a winner.

## Criterion pass rates

| Criterion | Passed | Rate | Weight |
|---|---:|---:|---:|
| `json_valid` | 71/71 | 100.0% | 12 |
| `json_final` | 69/71 | 97.2% | 6 |
| `json_estimate` | 71/71 | 100.0% | 2 |
| `json_assumptions` | 67/71 | 94.4% | 2 |
| `json_uncertainty` | 71/71 | 100.0% | 2 |
| `json_units` | 71/71 | 100.0% | 2 |
| `json_haiku` | 58/71 | 81.7% | 2 |
| `json_pirate` | 61/71 | 85.9% | 2 |
| `numeric_answer` | 71/71 | 100.0% | 3 |
| `si_units` | 71/71 | 100.0% | 4 |
| `imperial_units` | 71/71 | 100.0% | 4 |
| `consistent_conversion` | 71/71 | 100.0% | 6 |
| `numeric_uncertainty` | 70/71 | 98.6% | 4 |
| `transparent_math` | 71/71 | 100.0% | 4 |
| `explicit_assumptions` | 71/71 | 100.0% | 5 |
| `multiple_assumptions` | 71/71 | 100.0% | 3 |
| `citations` | 45/71 | 63.4% | 4 |
| `source_locator` | 19/71 | 26.8% | 3 |
| `haiku_present` | 71/71 | 100.0% | 5 |
| `haiku_three_lines` | 71/71 | 100.0% | 4 |
| `haiku_575` | 19/71 | 26.8% | 6 |
| `pirate_present` | 71/71 | 100.0% | 3 |
| `pirate_style` | 71/71 | 100.0% | 2 |
| `linguistics` | 63/71 | 88.7% | 2 |
| `history` | 67/71 | 94.4% | 2 |
| `physics_math` | 71/71 | 100.0% | 2 |
| `humor_signal` | 57/71 | 80.3% | 2 |
| `organized` | 71/71 | 100.0% | 2 |

## Model averages

| Model | Results | Average | Median | Min | Max |
|---|---:|---:|---:|---:|---:|
| `openai/gpt-5.6-sol-pro` | 5 | 95.8 | 97.0 | 90 | 100 |
| `openai/gpt-5.6-luna` | 6 | 94.7 | 95.5 | 89 | 98 |
| `openai/gpt-5.6-terra` | 6 | 94.5 | 96.0 | 86 | 98 |
| `qwen/qwen3.7-max` | 1 | 94.0 | 94.0 | 94 | 94 |
| `openai/gpt-5.6-luna-pro` | 6 | 93.7 | 93.5 | 88 | 100 |
| `anthropic/claude-fable-5` | 5 | 93.4 | 94.0 | 91 | 94 |
| `anthropic/claude-sonnet-5` | 5 | 93.0 | 94.0 | 90 | 97 |
| `x-ai/grok-4.5` | 3 | 92.7 | 94.0 | 90 | 94 |
| `openai/gpt-5.6-terra-pro` | 6 | 92.7 | 95.0 | 80 | 97 |
| `deepseek/deepseek-v4-pro` | 2 | 91.0 | 91.0 | 89 | 93 |
| `anthropic/claude-opus-4.8` | 5 | 91.0 | 91.0 | 88 | 93 |
| `openai/gpt-5.6-sol` | 6 | 90.8 | 92.5 | 84 | 95 |
| `google/gemini-3.5-flash` | 4 | 90.5 | 90.0 | 88 | 94 |
| `z-ai/glm-5.2` | 2 | 90.0 | 90.0 | 90 | 90 |
| `moonshotai/kimi-k2.6` | 1 | 90.0 | 90.0 | 90 | 90 |
| `minimax/minimax-m3` | 1 | 90.0 | 90.0 | 90 | 90 |
| `google/gemini-3.1-pro-preview` | 3 | 89.0 | 89.0 | 88 | 90 |
| `google/gemini-3.1-flash-lite` | 4 | 88.0 | 88.0 | 85 | 91 |

## Family averages

| Family | Results | Average | Median | Min | Max |
|---|---:|---:|---:|---:|---:|
| qwen | 1 | 94.0 | 94.0 | 94 | 94 |
| openai | 35 | 93.6 | 95.0 | 80 | 100 |
| x-ai | 3 | 92.7 | 94.0 | 90 | 94 |
| anthropic | 15 | 92.5 | 93.0 | 88 | 97 |
| deepseek | 2 | 91.0 | 91.0 | 89 | 93 |
| z-ai | 2 | 90.0 | 90.0 | 90 | 90 |
| moonshotai | 1 | 90.0 | 90.0 | 90 | 90 |
| minimax | 1 | 90.0 | 90.0 | 90 | 90 |
| google | 11 | 89.2 | 89.0 | 85 | 94 |

## Every response

| Rank | Model | Effort | Score | Grade | JSON | Haiku lines | Syllables | Pirate | Response |
|---:|---|---|---:|:---:|:---:|---:|---|:---:|---|
| 1 | `openai/gpt-5.6-luna-pro` | xhigh | 100 | A | yes | 3 | 5/7/5 | yes | [view](responses/openai/gpt-5.6-luna-pro/xhigh.md) |
| 2 | `openai/gpt-5.6-sol-pro` | high | 100 | A | yes | 3 | 5/7/5 | yes | [view](responses/openai/gpt-5.6-sol-pro/high.md) |
| 3 | `openai/gpt-5.6-luna` | max | 98 | A | yes | 3 | 5/7/5 | yes | [view](responses/openai/gpt-5.6-luna/max.md) |
| 4 | `openai/gpt-5.6-luna` | medium | 98 | A | yes | 3 | 5/7/5 | yes | [view](responses/openai/gpt-5.6-luna/medium.md) |
| 5 | `openai/gpt-5.6-terra` | medium | 98 | A | yes | 3 | 5/7/5 | yes | [view](responses/openai/gpt-5.6-terra/medium.md) |
| 6 | `anthropic/claude-sonnet-5` | xhigh | 97 | A | yes | 3 | 5/7/5 | yes | [view](responses/anthropic/claude-sonnet-5/xhigh.md) |
| 7 | `openai/gpt-5.6-luna` | low | 97 | A | yes | 3 | 5/7/5 | yes | [view](responses/openai/gpt-5.6-luna/low.md) |
| 8 | `openai/gpt-5.6-luna-pro` | none | 97 | A | yes | 3 | 5/7/5 | yes | [view](responses/openai/gpt-5.6-luna-pro/none.md) |
| 9 | `openai/gpt-5.6-sol-pro` | low | 97 | A | yes | 3 | 5/6/4 | yes | [view](responses/openai/gpt-5.6-sol-pro/low.md) |
| 10 | `openai/gpt-5.6-sol-pro` | medium | 97 | A | yes | 3 | 5/7/4 | yes | [view](responses/openai/gpt-5.6-sol-pro/medium.md) |
| 11 | `openai/gpt-5.6-terra` | max | 97 | A | yes | 3 | 5/8/4 | yes | [view](responses/openai/gpt-5.6-terra/max.md) |
| 12 | `openai/gpt-5.6-terra` | xhigh | 97 | A | yes | 3 | 5/6/5 | yes | [view](responses/openai/gpt-5.6-terra/xhigh.md) |
| 13 | `openai/gpt-5.6-terra-pro` | high | 97 | A | yes | 3 | 5/6/5 | yes | [view](responses/openai/gpt-5.6-terra-pro/high.md) |
| 14 | `openai/gpt-5.6-terra-pro` | max | 97 | A | yes | 3 | 5/6/5 | yes | [view](responses/openai/gpt-5.6-terra-pro/max.md) |
| 15 | `openai/gpt-5.6-terra-pro` | xhigh | 97 | A | yes | 3 | 5/7/4 | yes | [view](responses/openai/gpt-5.6-terra-pro/xhigh.md) |
| 16 | `openai/gpt-5.6-sol` | max | 95 | A | yes | 3 | 5/7/4 | yes | [view](responses/openai/gpt-5.6-sol/max.md) |
| 17 | `openai/gpt-5.6-sol` | xhigh | 95 | A | yes | 3 | 5/6/5 | yes | [view](responses/openai/gpt-5.6-sol/xhigh.md) |
| 18 | `openai/gpt-5.6-sol-pro` | xhigh | 95 | A | yes | 3 | 5/6/5 | yes | [view](responses/openai/gpt-5.6-sol-pro/xhigh.md) |
| 19 | `openai/gpt-5.6-terra` | high | 95 | A | yes | 3 | 5/7/4 | yes | [view](responses/openai/gpt-5.6-terra/high.md) |
| 20 | `anthropic/claude-fable-5` | low | 94 | A | yes | 3 | 5/6/5 | yes | [view](responses/anthropic/claude-fable-5/low.md) |
| 21 | `anthropic/claude-fable-5` | max | 94 | A | yes | 3 | 5/6/4 | yes | [view](responses/anthropic/claude-fable-5/max.md) |
| 22 | `anthropic/claude-fable-5` | medium | 94 | A | yes | 3 | 5/6/5 | yes | [view](responses/anthropic/claude-fable-5/medium.md) |
| 23 | `anthropic/claude-fable-5` | xhigh | 94 | A | yes | 3 | 5/6/5 | yes | [view](responses/anthropic/claude-fable-5/xhigh.md) |
| 24 | `anthropic/claude-sonnet-5` | high | 94 | A | yes | 3 | 5/7/6 | yes | [view](responses/anthropic/claude-sonnet-5/high.md) |
| 25 | `anthropic/claude-sonnet-5` | max | 94 | A | yes | 3 | 5/6/6 | yes | [view](responses/anthropic/claude-sonnet-5/max.md) |
| 26 | `google/gemini-3.5-flash` | medium | 94 | A | yes | 3 | 5/6/5 | yes | [view](responses/google/gemini-3.5-flash/medium.md) |
| 27 | `openai/gpt-5.6-luna` | xhigh | 94 | A | yes | 3 | 5/6/5 | yes | [view](responses/openai/gpt-5.6-luna/xhigh.md) |
| 28 | `openai/gpt-5.6-luna-pro` | max | 94 | A | yes | 3 | 6/7/5 | yes | [view](responses/openai/gpt-5.6-luna-pro/max.md) |
| 29 | `openai/gpt-5.6-sol` | low | 94 | A | yes | 3 | 5/7/4 | yes | [view](responses/openai/gpt-5.6-sol/low.md) |
| 30 | `openai/gpt-5.6-terra` | none | 94 | A | yes | 3 | 5/7/4 | yes | [view](responses/openai/gpt-5.6-terra/none.md) |
| 31 | `qwen/qwen3.7-max` | default | 94 | A | yes | 3 | 5/6/5 | yes | [view](responses/qwen/qwen3.7-max/default.md) |
| 32 | `x-ai/grok-4.5` | high | 94 | A | yes | 3 | 5/6/6 | yes | [view](responses/x-ai/grok-4.5/high.md) |
| 33 | `x-ai/grok-4.5` | medium | 94 | A | yes | 3 | 5/6/6 | yes | [view](responses/x-ai/grok-4.5/medium.md) |
| 34 | `anthropic/claude-opus-4.8` | low | 93 | A | yes | 3 | 5/7/5 | yes | [view](responses/anthropic/claude-opus-4.8/low.md) |
| 35 | `anthropic/claude-opus-4.8` | medium | 93 | A | yes | 3 | 5/7/5 | yes | [view](responses/anthropic/claude-opus-4.8/medium.md) |
| 36 | `deepseek/deepseek-v4-pro` | high | 93 | A | yes | 3 | 5/7/5 | yes | [view](responses/deepseek/deepseek-v4-pro/high.md) |
| 37 | `openai/gpt-5.6-luna-pro` | medium | 93 | A | yes | 3 | 5/7/4 | yes | [view](responses/openai/gpt-5.6-luna-pro/medium.md) |
| 38 | `openai/gpt-5.6-terra-pro` | low | 93 | A | yes | 3 | 5/7/4 | yes | [view](responses/openai/gpt-5.6-terra-pro/low.md) |
| 39 | `openai/gpt-5.6-luna` | high | 92 | A | yes | 3 | 5/7/4 | yes | [view](responses/openai/gpt-5.6-luna/high.md) |
| 40 | `openai/gpt-5.6-terra-pro` | medium | 92 | A | yes | 3 | 5/6/5 | yes | [view](responses/openai/gpt-5.6-terra-pro/medium.md) |
| 41 | `anthropic/claude-fable-5` | high | 91 | A | yes | 3 | 5/6/5 | yes | [view](responses/anthropic/claude-fable-5/high.md) |
| 42 | `anthropic/claude-opus-4.8` | max | 91 | A | yes | 3 | 5/6/7 | yes | [view](responses/anthropic/claude-opus-4.8/max.md) |
| 43 | `google/gemini-3.1-flash-lite` | medium | 91 | A | yes | 3 | 5/7/5 | yes | [view](responses/google/gemini-3.1-flash-lite/medium.md) |
| 44 | `openai/gpt-5.6-sol` | high | 91 | A | yes | 3 | 5/7/5 | yes | [view](responses/openai/gpt-5.6-sol/high.md) |
| 45 | `anthropic/claude-opus-4.8` | high | 90 | A | yes | 3 | 5/6/5 | yes | [view](responses/anthropic/claude-opus-4.8/high.md) |
| 46 | `anthropic/claude-sonnet-5` | low | 90 | A | yes | 3 | 5/7/6 | yes | [view](responses/anthropic/claude-sonnet-5/low.md) |
| 47 | `anthropic/claude-sonnet-5` | medium | 90 | A | yes | 3 | 5/8/6 | yes | [view](responses/anthropic/claude-sonnet-5/medium.md) |
| 48 | `google/gemini-3.1-pro-preview` | high | 90 | A | yes | 3 | 5/6/4 | yes | [view](responses/google/gemini-3.1-pro-preview/high.md) |
| 49 | `google/gemini-3.5-flash` | high | 90 | A | yes | 3 | 5/6/5 | yes | [view](responses/google/gemini-3.5-flash/high.md) |
| 50 | `google/gemini-3.5-flash` | low | 90 | A | yes | 3 | 5/6/5 | yes | [view](responses/google/gemini-3.5-flash/low.md) |
| 51 | `minimax/minimax-m3` | default | 90 | A | yes | 3 | 5/6/4 | yes | [view](responses/minimax/minimax-m3/default.md) |
| 52 | `moonshotai/kimi-k2.6` | default | 90 | A | yes | 3 | 5/7/4 | yes | [view](responses/moonshotai/kimi-k2.6/default.md) |
| 53 | `openai/gpt-5.6-luna-pro` | low | 90 | A | yes | 3 | 6/7/5 | yes | [view](responses/openai/gpt-5.6-luna-pro/low.md) |
| 54 | `openai/gpt-5.6-sol-pro` | none | 90 | A | yes | 3 | 5/6/6 | yes | [view](responses/openai/gpt-5.6-sol-pro/none.md) |
| 55 | `x-ai/grok-4.5` | low | 90 | A | yes | 3 | 5/6/5 | yes | [view](responses/x-ai/grok-4.5/low.md) |
| 56 | `z-ai/glm-5.2` | high | 90 | A | yes | 3 | 4/7/4 | yes | [view](responses/z-ai/glm-5.2/high.md) |
| 57 | `z-ai/glm-5.2` | xhigh | 90 | A | yes | 3 | 4/7/5 | yes | [view](responses/z-ai/glm-5.2/xhigh.md) |
| 58 | `deepseek/deepseek-v4-pro` | xhigh | 89 | B | yes | 3 | 5/7/5 | yes | [view](responses/deepseek/deepseek-v4-pro/xhigh.md) |
| 59 | `google/gemini-3.1-flash-lite` | high | 89 | B | yes | 3 | 5/7/5 | yes | [view](responses/google/gemini-3.1-flash-lite/high.md) |
| 60 | `google/gemini-3.1-pro-preview` | low | 89 | B | yes | 3 | 5/7/5 | yes | [view](responses/google/gemini-3.1-pro-preview/low.md) |
| 61 | `openai/gpt-5.6-luna` | none | 89 | B | yes | 3 | 5/7/5 | yes | [view](responses/openai/gpt-5.6-luna/none.md) |
| 62 | `anthropic/claude-opus-4.8` | xhigh | 88 | B | yes | 3 | 4/7/5 | yes | [view](responses/anthropic/claude-opus-4.8/xhigh.md) |
| 63 | `google/gemini-3.1-pro-preview` | medium | 88 | B | yes | 3 | 5/6/5 | yes | [view](responses/google/gemini-3.1-pro-preview/medium.md) |
| 64 | `google/gemini-3.5-flash` | minimal | 88 | B | yes | 3 | 6/6/5 | yes | [view](responses/google/gemini-3.5-flash/minimal.md) |
| 65 | `openai/gpt-5.6-luna-pro` | high | 88 | B | yes | 3 | 5/6/5 | yes | [view](responses/openai/gpt-5.6-luna-pro/high.md) |
| 66 | `google/gemini-3.1-flash-lite` | low | 87 | B | yes | 3 | 5/7/5 | yes | [view](responses/google/gemini-3.1-flash-lite/low.md) |
| 67 | `openai/gpt-5.6-sol` | medium | 86 | B | yes | 3 | 5/6/4 | yes | [view](responses/openai/gpt-5.6-sol/medium.md) |
| 68 | `openai/gpt-5.6-terra` | low | 86 | B | yes | 3 | 5/7/4 | yes | [view](responses/openai/gpt-5.6-terra/low.md) |
| 69 | `google/gemini-3.1-flash-lite` | minimal | 85 | B | yes | 3 | 5/7/5 | yes | [view](responses/google/gemini-3.1-flash-lite/minimal.md) |
| 70 | `openai/gpt-5.6-sol` | none | 84 | B | yes | 3 | 5/6/5 | yes | [view](responses/openai/gpt-5.6-sol/none.md) |
| 71 | `openai/gpt-5.6-terra-pro` | none | 80 | B | yes | 3 | 4/7/4 | yes | [view](responses/openai/gpt-5.6-terra-pro/none.md) |

## Phase 2: blinded quality score

Mechanical compliance cannot decide whether the physics is sound, citations are trustworthy, uncertainty is well calibrated, prose is excellent, or the joke lands. For that, use a separate 100-point rubric:

- Factual and mathematical correctness: 30
- Quality and calibration of assumptions/uncertainty: 20
- Citation accuracy and source quality: 15
- Clarity, editing, and information architecture: 15
- Humor, haiku quality, and pirate-summary quality: 10
- JSON fidelity to the prose answer: 10

Recommended protocol: remove model names and cost metadata; randomize response order; have three judges from different model families score the same rubric; exclude a judge's score for its own family; use the median criterion score; manually review responses with judge spread above 15 points and the top ten overall. Keep compliance and quality separate, then publish a composite such as 40% compliance + 60% blinded quality. Cost and latency should remain separate axes rather than being folded into answer quality.

The row-level machine-readable details are in [scores.csv](scores.csv).
