# eval-conformance-suite

Executable rubric-spec v1 conformance checks and reproducible SVG badges. Inspect AI is documented as the first external adapter target. Reference badges can be hosted at `auraone.ai/conformance/<framework>.svg`.

## Quickstart

```bash
pip install eval-conformance-suite rubric-spec
eval-conformance-suite run --against rubric_spec.adapters.inspect_ai
eval-conformance-suite badge --against inspect_ai
```

The CI suite runs all bundled `rubric-spec` adapters: Inspect AI, PromptFoo, DeepEval, LangSmith, and EvalKit.

## What This Is Not

Not a benchmark. It only checks schema and adapter compliance using synthetic fixtures.
