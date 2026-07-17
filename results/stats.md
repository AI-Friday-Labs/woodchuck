# Successful benchmark results

- Successful model/effort results: 71
- Core model cost: $8.158907529
- Tokens: 263,473 input / 487,968 output / 339,586 reasoning
- Sum of successful request time: 4913.768s

Core model cost is the direct sum of `cost_usd` for the included successful responses. It excludes failed and partial attempts, retries, preflight calls, interrupted calls, account reconciliation differences, and OpenRouter-level fees.

All 71 files use the same prompt. Four entries are complete recovery replacements: Luna, Terra, and Sol at `max` use a 65,536-token output ceiling; Claude Sonnet 5 uses a 12,000-token reasoning budget. Sol Pro `max` is omitted because it never completed.

## By family

| Family | Results | Core cost | Input | Output | Reasoning | Avg time |
|---|---:|---:|---:|---:|---:|---:|
| Anthropic | 15 | $1.398630 | 1,740 | 52,458 | 6,882 | 46.200s |
| DeepSeek | 2 | $0.014122 | 136 | 5,817 | 3,056 | 47.787s |
| Google | 11 | $0.190244 | 683 | 22,775 | 12,236 | 14.592s |
| MiniMax | 1 | $0.004167 | 240 | 3,435 | 1,570 | 43.311s |
| Moonshot AI | 1 | $0.024902 | 74 | 6,208 | 4,883 | 280.112s |
| OpenAI | 35 | $6.443511 | 259,560 | 380,003 | 300,207 | 95.626s |
| Qwen | 1 | $0.024171 | 76 | 5,437 | 3,705 | 104.577s |
| Z.ai | 2 | $0.028674 | 157 | 6,927 | 4,453 | 65.112s |
| xAI | 3 | $0.030486 | 807 | 4,908 | 2,594 | 19.842s |

## By model

| Model | Results | Core cost | Input | Output | Reasoning | Avg time |
|---|---:|---:|---:|---:|---:|---:|
| `anthropic/claude-fable-5` | 5 | $0.837000 | 580 | 16,624 | 1,977 | 47.698s |
| `anthropic/claude-opus-4.8` | 5 | $0.334950 | 580 | 13,282 | 1,466 | 38.513s |
| `anthropic/claude-sonnet-5` | 5 | $0.226680 | 580 | 22,552 | 3,439 | 52.390s |
| `deepseek/deepseek-v4-pro` | 2 | $0.014122 | 136 | 5,817 | 3,056 | 47.787s |
| `google/gemini-3.1-flash-lite` | 4 | $0.007586 | 249 | 5,016 | 2,025 | 6.856s |
| `google/gemini-3.1-pro-preview` | 3 | $0.088704 | 186 | 7,361 | 3,866 | 23.064s |
| `google/gemini-3.5-flash` | 4 | $0.093954 | 248 | 10,398 | 6,345 | 15.975s |
| `minimax/minimax-m3` | 1 | $0.004167 | 240 | 3,435 | 1,570 | 43.311s |
| `moonshotai/kimi-k2.6` | 1 | $0.024902 | 74 | 6,208 | 4,883 | 280.112s |
| `openai/gpt-5.6-luna` | 6 | $0.191814 | 432 | 31,897 | 25,437 | 38.371s |
| `openai/gpt-5.6-luna-pro` | 6 | $0.817412 | 101,150 | 119,377 | 100,668 | 96.732s |
| `openai/gpt-5.6-sol` | 6 | $1.118880 | 432 | 37,224 | 29,672 | 155.325s |
| `openai/gpt-5.6-sol-pro` | 5 | $2.097930 | 61,836 | 59,625 | 41,640 | 131.716s |
| `openai/gpt-5.6-terra` | 6 | $0.621495 | 432 | 41,361 | 32,473 | 68.956s |
| `openai/gpt-5.6-terra-pro` | 6 | $1.595980 | 95,278 | 90,519 | 70,317 | 88.673s |
| `qwen/qwen3.7-max` | 1 | $0.024171 | 76 | 5,437 | 3,705 | 104.577s |
| `x-ai/grok-4.5` | 3 | $0.030486 | 807 | 4,908 | 2,594 | 19.842s |
| `z-ai/glm-5.2` | 2 | $0.028674 | 157 | 6,927 | 4,453 | 65.112s |

## Every successful result

| Model | Effort | Request profile | Core cost | Input | Output | Reasoning | Total time | Response |
|---|---|---|---:|---:|---:|---:|---:|---|
| `anthropic/claude-fable-5` | high | primary | $0.091410 | 116 | 1,805 | 0 | 28.595s | [view](responses/anthropic/claude-fable-5/high.md) |
| `anthropic/claude-fable-5` | low | primary | $0.060760 | 116 | 1,192 | 0 | 19.539s | [view](responses/anthropic/claude-fable-5/low.md) |
| `anthropic/claude-fable-5` | max | primary | $0.463460 | 116 | 9,246 | 1,854 | 123.469s | [view](responses/anthropic/claude-fable-5/max.md) |
| `anthropic/claude-fable-5` | medium | primary | $0.098960 | 116 | 1,956 | 0 | 31.815s | [view](responses/anthropic/claude-fable-5/medium.md) |
| `anthropic/claude-fable-5` | xhigh | primary | $0.122410 | 116 | 2,425 | 123 | 35.070s | [view](responses/anthropic/claude-fable-5/xhigh.md) |
| `anthropic/claude-opus-4.8` | high | primary | $0.031530 | 116 | 1,238 | 0 | 19.436s | [view](responses/anthropic/claude-opus-4.8/high.md) |
| `anthropic/claude-opus-4.8` | low | primary | $0.030055 | 116 | 1,179 | 17 | 18.227s | [view](responses/anthropic/claude-opus-4.8/low.md) |
| `anthropic/claude-opus-4.8` | max | primary | $0.177380 | 116 | 7,072 | 1,292 | 97.925s | [view](responses/anthropic/claude-opus-4.8/max.md) |
| `anthropic/claude-opus-4.8` | medium | primary | $0.038255 | 116 | 1,507 | 85 | 24.190s | [view](responses/anthropic/claude-opus-4.8/medium.md) |
| `anthropic/claude-opus-4.8` | xhigh | primary | $0.057730 | 116 | 2,286 | 72 | 32.786s | [view](responses/anthropic/claude-opus-4.8/xhigh.md) |
| `anthropic/claude-sonnet-5` | high | primary | $0.050472 | 116 | 5,024 | 980 | 63.062s | [view](responses/anthropic/claude-sonnet-5/high.md) |
| `anthropic/claude-sonnet-5` | low | primary | $0.013912 | 116 | 1,368 | 0 | 20.281s | [view](responses/anthropic/claude-sonnet-5/low.md) |
| `anthropic/claude-sonnet-5` | max | recovered: 12,000 reasoning-token budget | $0.073102 | 116 | 7,287 | 1,091 | 77.729s | [view](responses/anthropic/claude-sonnet-5/max.md) |
| `anthropic/claude-sonnet-5` | medium | primary | $0.017852 | 116 | 1,762 | 0 | 21.958s | [view](responses/anthropic/claude-sonnet-5/medium.md) |
| `anthropic/claude-sonnet-5` | xhigh | primary | $0.071342 | 116 | 7,111 | 1,368 | 78.920s | [view](responses/anthropic/claude-sonnet-5/xhigh.md) |
| `deepseek/deepseek-v4-pro` | high | primary | $0.009801 | 68 | 4,299 | 3,056 | 64.048s | [view](responses/deepseek/deepseek-v4-pro/high.md) |
| `deepseek/deepseek-v4-pro` | xhigh | primary | $0.004321 | 68 | 1,518 | 0 | 31.526s | [view](responses/deepseek/deepseek-v4-pro/xhigh.md) |
| `google/gemini-3.1-flash-lite` | high | primary | $0.003368 | 63 | 2,235 | 1,404 | 8.540s | [view](responses/google/gemini-3.1-flash-lite/high.md) |
| `google/gemini-3.1-flash-lite` | low | primary | $0.001342 | 62 | 884 | 120 | 8.300s | [view](responses/google/gemini-3.1-flash-lite/low.md) |
| `google/gemini-3.1-flash-lite` | medium | primary | $0.001896 | 62 | 1,254 | 501 | 5.986s | [view](responses/google/gemini-3.1-flash-lite/medium.md) |
| `google/gemini-3.1-flash-lite` | minimal | primary | $0.000980 | 62 | 643 | 0 | 4.597s | [view](responses/google/gemini-3.1-flash-lite/minimal.md) |
| `google/gemini-3.1-pro-preview` | high | primary | $0.042016 | 62 | 3,491 | 1,904 | 31.157s | [view](responses/google/gemini-3.1-pro-preview/high.md) |
| `google/gemini-3.1-pro-preview` | low | primary | $0.021256 | 62 | 1,761 | 845 | 16.486s | [view](responses/google/gemini-3.1-pro-preview/low.md) |
| `google/gemini-3.1-pro-preview` | medium | primary | $0.025432 | 62 | 2,109 | 1,117 | 21.549s | [view](responses/google/gemini-3.1-pro-preview/medium.md) |
| `google/gemini-3.5-flash` | high | primary | $0.031143 | 62 | 3,450 | 2,313 | 21.864s | [view](responses/google/gemini-3.5-flash/high.md) |
| `google/gemini-3.5-flash` | low | primary | $0.017661 | 62 | 1,952 | 1,233 | 12.520s | [view](responses/google/gemini-3.5-flash/low.md) |
| `google/gemini-3.5-flash` | medium | primary | $0.032493 | 62 | 3,600 | 2,799 | 20.278s | [view](responses/google/gemini-3.5-flash/medium.md) |
| `google/gemini-3.5-flash` | minimal | primary | $0.012657 | 62 | 1,396 | 0 | 9.238s | [view](responses/google/gemini-3.5-flash/minimal.md) |
| `minimax/minimax-m3` | default | primary | $0.004167 | 240 | 3,435 | 1,570 | 43.311s | [view](responses/minimax/minimax-m3/default.md) |
| `moonshotai/kimi-k2.6` | default | primary | $0.024902 | 74 | 6,208 | 4,883 | 280.112s | [view](responses/moonshotai/kimi-k2.6/default.md) |
| `openai/gpt-5.6-luna` | high | primary | $0.036060 | 72 | 5,998 | 4,660 | 41.947s | [view](responses/openai/gpt-5.6-luna/high.md) |
| `openai/gpt-5.6-luna` | low | primary | $0.006174 | 72 | 1,017 | 423 | 8.578s | [view](responses/openai/gpt-5.6-luna/low.md) |
| `openai/gpt-5.6-luna` | max | recovered: 65,536 output-token ceiling | $0.072006 | 72 | 11,989 | 10,358 | 84.039s | [view](responses/openai/gpt-5.6-luna/max.md) |
| `openai/gpt-5.6-luna` | medium | primary | $0.011202 | 72 | 1,855 | 1,025 | 13.140s | [view](responses/openai/gpt-5.6-luna/medium.md) |
| `openai/gpt-5.6-luna` | none | primary | $0.003474 | 72 | 567 | 0 | 4.566s | [view](responses/openai/gpt-5.6-luna/none.md) |
| `openai/gpt-5.6-luna` | xhigh | primary | $0.062898 | 72 | 10,471 | 8,971 | 77.958s | [view](responses/openai/gpt-5.6-luna/xhigh.md) |
| `openai/gpt-5.6-luna-pro` | high | primary | $0.099272 | 13,814 | 14,243 | 10,870 | 70.158s | [view](responses/openai/gpt-5.6-luna-pro/high.md) |
| `openai/gpt-5.6-luna-pro` | low | primary | $0.023014 | 4,528 | 3,081 | 1,161 | 11.546s | [view](responses/openai/gpt-5.6-luna-pro/low.md) |
| `openai/gpt-5.6-luna-pro` | max | primary | $0.401021 | 43,349 | 59,612 | 54,644 | 277.734s | [view](responses/openai/gpt-5.6-luna-pro/max.md) |
| `openai/gpt-5.6-luna-pro` | medium | primary | $0.040192 | 6,310 | 5,647 | 3,300 | 23.931s | [view](responses/openai/gpt-5.6-luna-pro/medium.md) |
| `openai/gpt-5.6-luna-pro` | none | primary | $0.015384 | 3,684 | 1,950 | 0 | 8.369s | [view](responses/openai/gpt-5.6-luna-pro/none.md) |
| `openai/gpt-5.6-luna-pro` | xhigh | primary | $0.238529 | 29,465 | 34,844 | 30,693 | 188.655s | [view](responses/openai/gpt-5.6-luna-pro/xhigh.md) |
| `openai/gpt-5.6-sol` | high | primary | $0.080490 | 72 | 2,671 | 1,552 | 56.131s | [view](responses/openai/gpt-5.6-sol/high.md) |
| `openai/gpt-5.6-sol` | low | primary | $0.052650 | 72 | 1,743 | 672 | 38.383s | [view](responses/openai/gpt-5.6-sol/low.md) |
| `openai/gpt-5.6-sol` | max | recovered: 65,536 output-token ceiling | $0.587850 | 72 | 19,583 | 17,610 | 537.950s | [view](responses/openai/gpt-5.6-sol/max.md) |
| `openai/gpt-5.6-sol` | medium | primary | $0.043320 | 72 | 1,432 | 516 | 31.759s | [view](responses/openai/gpt-5.6-sol/medium.md) |
| `openai/gpt-5.6-sol` | none | primary | $0.027840 | 72 | 916 | 0 | 17.364s | [view](responses/openai/gpt-5.6-sol/none.md) |
| `openai/gpt-5.6-sol` | xhigh | primary | $0.326730 | 72 | 10,879 | 9,322 | 250.364s | [view](responses/openai/gpt-5.6-sol/xhigh.md) |
| `openai/gpt-5.6-sol-pro` | high | primary | $0.564505 | 15,749 | 16,192 | 12,153 | 196.375s | [view](responses/openai/gpt-5.6-sol-pro/high.md) |
| `openai/gpt-5.6-sol-pro` | low | primary | $0.181920 | 6,318 | 5,011 | 1,957 | 50.083s | [view](responses/openai/gpt-5.6-sol-pro/low.md) |
| `openai/gpt-5.6-sol-pro` | medium | primary | $0.243345 | 7,983 | 6,781 | 3,601 | 82.368s | [view](responses/openai/gpt-5.6-sol-pro/medium.md) |
| `openai/gpt-5.6-sol-pro` | none | primary | $0.095685 | 4,221 | 2,486 | 0 | 26.353s | [view](responses/openai/gpt-5.6-sol-pro/none.md) |
| `openai/gpt-5.6-sol-pro` | xhigh | primary | $1.012475 | 27,565 | 29,155 | 23,929 | 303.404s | [view](responses/openai/gpt-5.6-sol-pro/xhigh.md) |
| `openai/gpt-5.6-terra` | high | primary | $0.052305 | 72 | 3,475 | 2,070 | 35.946s | [view](responses/openai/gpt-5.6-terra/high.md) |
| `openai/gpt-5.6-terra` | low | primary | $0.029670 | 72 | 1,966 | 516 | 20.101s | [view](responses/openai/gpt-5.6-terra/low.md) |
| `openai/gpt-5.6-terra` | max | recovered: 65,536 output-token ceiling | $0.347850 | 72 | 23,178 | 21,611 | 227.089s | [view](responses/openai/gpt-5.6-terra/max.md) |
| `openai/gpt-5.6-terra` | medium | primary | $0.047715 | 72 | 3,169 | 1,544 | 33.730s | [view](responses/openai/gpt-5.6-terra/medium.md) |
| `openai/gpt-5.6-terra` | none | primary | $0.015390 | 72 | 1,014 | 0 | 10.946s | [view](responses/openai/gpt-5.6-terra/none.md) |
| `openai/gpt-5.6-terra` | xhigh | primary | $0.128565 | 72 | 8,559 | 6,732 | 85.922s | [view](responses/openai/gpt-5.6-terra/xhigh.md) |
| `openai/gpt-5.6-terra-pro` | high | primary | $0.215018 | 12,375 | 12,272 | 8,334 | 74.652s | [view](responses/openai/gpt-5.6-terra-pro/high.md) |
| `openai/gpt-5.6-terra-pro` | low | primary | $0.118938 | 7,723 | 6,642 | 3,209 | 39.317s | [view](responses/openai/gpt-5.6-terra-pro/low.md) |
| `openai/gpt-5.6-terra-pro` | max | primary | $0.843202 | 49,089 | 48,032 | 45,854 | 269.631s | [view](responses/openai/gpt-5.6-terra-pro/max.md) |
| `openai/gpt-5.6-terra-pro` | medium | primary | $0.136438 | 8,123 | 7,742 | 4,420 | 58.125s | [view](responses/openai/gpt-5.6-terra-pro/medium.md) |
| `openai/gpt-5.6-terra-pro` | none | primary | $0.057398 | 4,767 | 3,032 | 0 | 12.761s | [view](responses/openai/gpt-5.6-terra-pro/none.md) |
| `openai/gpt-5.6-terra-pro` | xhigh | primary | $0.224988 | 13,201 | 12,799 | 8,500 | 77.550s | [view](responses/openai/gpt-5.6-terra-pro/xhigh.md) |
| `qwen/qwen3.7-max` | default | primary | $0.024171 | 76 | 5,437 | 3,705 | 104.577s | [view](responses/qwen/qwen3.7-max/default.md) |
| `z-ai/glm-5.2` | high | primary | $0.013399 | 79 | 3,020 | 1,862 | 31.840s | [view](responses/z-ai/glm-5.2/high.md) |
| `z-ai/glm-5.2` | xhigh | primary | $0.015276 | 78 | 3,907 | 2,591 | 98.385s | [view](responses/z-ai/glm-5.2/xhigh.md) |
| `x-ai/grok-4.5` | high | primary | $0.010108 | 269 | 1,627 | 781 | 18.369s | [view](responses/x-ai/grok-4.5/high.md) |
| `x-ai/grok-4.5` | low | primary | $0.009340 | 269 | 1,499 | 989 | 19.373s | [view](responses/x-ai/grok-4.5/low.md) |
| `x-ai/grok-4.5` | medium | primary | $0.011038 | 269 | 1,782 | 824 | 21.786s | [view](responses/x-ai/grok-4.5/medium.md) |
