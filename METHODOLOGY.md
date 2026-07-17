# Methodology

## Question

Every model received the same single user message from [`prompts/woodchuck.txt`](prompts/woodchuck.txt):

> You are an expert linguist, physicist, historian, mathematician, editor, and comedian. Explain how much wood a woodchuck would chuck if a woodchuck could chuck wood. Cite your assumptions, estimate uncertainty, provide SI and imperial units, write a haiku, summarize in pirate speech, then output JSON.

The prompt intentionally mixes research, quantitative reasoning, editing, humor, poetry, style transfer, and structured output. It is a compliance stress test, not a general intelligence test.

## Run design

- The prompt is byte-identical across requests. Its SHA-256 is stored in each local run manifest.
- The model matrix is fixed in [`config/benchmark.json`](config/benchmark.json).
- Every reasoning effort explicitly advertised by OpenRouter was tested. Models without discrete levels received one `default` run.
- Requests ran sequentially so jobs did not compete for the same local connection.
- Request order was shuffled with a fixed seed to reduce family-order bias.
- The primary matrix used a 16,384-token response cap. Four complete recovery responses used the documented alternate envelopes in [`config/diagnostics/`](config/diagnostics/).
- A response ending on the provider length limit was classified as partial and excluded from the published success set.

## Compliance score

[`score_results.py`](score_results.py) applies a deterministic 100-point rubric:

| Section | Points |
|---|---:|
| JSON and output structure | 30 |
| Quantitative and scientific compliance | 25 |
| Assumptions and evidence | 15 |
| Creative requirements | 20 |
| Breadth and organization | 10 |

The full criterion pass rates and every row-level score are in [`results/evaluation.md`](results/evaluation.md) and [`results/scores.csv`](results/scores.csv).

## What the score does not measure

Mechanical compliance cannot establish factual correctness, citation accuracy, calibrated uncertainty, prose quality, or whether a joke works. Small differences are especially weak evidence because:

- this is one trial per model/effort pair;
- the 5-7-5 haiku test uses an English syllable heuristic;
- model APIs do not share all sampling controls;
- models and provider routes change over time.

A meaningful quality comparison should blind model identities, use multiple judges from different model families, exclude self-family judging, and manually review disagreements. Cost and latency should remain separate axes.

## Reproducibility boundary

The repository publishes everything needed to inspect the prompt, matrix, scoring code, and successful visible outputs. Raw event streams and provider metadata remain local because they are large and may carry operational metadata that is irrelevant to the public result.
