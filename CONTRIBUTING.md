# Contributing

Issues and pull requests are welcome.

Before opening a pull request:

```sh
python3 -m unittest discover -v
python3 benchmark.py --dry-run
```

Please keep benchmark changes reproducible. If you change the prompt, model matrix, runner envelope, recovery policy, or scoring rubric, document the change in `METHODOLOGY.md` and do not mix the resulting scores with the July 15, 2026 run.

Never commit `.env`, raw `runs/` artifacts, API keys, or provider request metadata.
