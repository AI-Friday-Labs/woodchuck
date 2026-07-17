# Woodchuck

How much wood would a frontier model chuck? Woodchuck runs one deliberately overstuffed prompt across current text models and every reasoning effort they advertise, then scores each response with a deterministic compliance rubric.

**[Explore the benchmark →](https://ai-friday-labs.github.io/woodchuck/)**

## What is here

- **71 successful responses** from 18 models across 9 model families
- **The exact prompt and model matrix** used for every run
- **A deterministic 100-point compliance rubric** with row-level scores
- **Complete successful responses**, published without raw provider metadata
- **A standard-library Python runner**, with no package install required

The July 15, 2026 run cost $8.16 in core model charges. Its mean compliance score was 92.4. Two model/effort pairs earned 100: GPT-5.6 Luna Pro at `xhigh` and GPT-5.6 Sol Pro at `high`.

> The score measures prompt compliance, not truth, writing quality, or which model is “best.” This is one trial per model/effort pair, so latency is a snapshot rather than a stable benchmark.

## Repository map

| Path | Purpose |
|---|---|
| [`site/`](site/) | Static GitHub Pages site |
| [`results/`](results/) | Curated reports, scores, and 71 successful responses |
| [`config/`](config/) | Primary model matrix and recovery configurations |
| [`prompts/woodchuck.txt`](prompts/woodchuck.txt) | Byte-identical benchmark prompt |
| [`benchmark.py`](benchmark.py) | OpenRouter benchmark runner |
| [`score_results.py`](score_results.py) | Deterministic compliance scorer |
| [`package_successes.py`](package_successes.py) | Success-only publication packager |

Raw streams, failed attempts, provider metadata, local caches, and `.env` are excluded from git.

## Run the benchmark

Chuck uses Python 3.11+ and only the standard library.

```sh
cp .env.example .env
# Add your OpenRouter API key to .env
python3 benchmark.py --dry-run
python3 benchmark.py
```

Useful targeted commands:

```sh
python3 benchmark.py --only 'minimax' --limit 1
python3 benchmark.py --run-dir runs/20260715T120000Z
python3 -m unittest discover -v
```

The runner executes requests sequentially. Order is shuffled with a fixed seed, and each manifest records the exact prompt hash, request matrix, parameters, and live pricing snapshot. See [METHODOLOGY.md](METHODOLOGY.md) for the design and limitations.

## Rebuild the reports

`package_successes.py` reads the local raw run directories and creates a success-only `results/` package. It intentionally refuses to overwrite an existing package. `score_results.py` then regenerates the deterministic evaluation:

```sh
python3 package_successes.py
python3 score_results.py
python3 scripts/build_showcase.py
```

## Public-data boundary

Only source code, configuration, aggregate metrics, and successful visible responses are published. The ignored `runs/` directory may contain provider routing details and other request metadata and should stay local.

Built by [AI Friday New Orleans](https://aifri.day/). Contributions are welcome under the [MIT License](LICENSE).
