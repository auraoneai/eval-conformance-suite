# eval-conformance-suite

Run executable `rubric-spec` adapter checks before claiming schema compatibility.

`eval-conformance-suite` is for adapter maintainers and evaluation-platform integrators. Its differentiator is an executable, framework-neutral contract: it imports a target Python adapter module and runs 18 synthetic cases covering scale types, anchors, weights, tie-break rules, judge prompt contracts, provenance, validation errors, lint findings, deterministic serialization, and round-trip field preservation.

## Inspectable Output

- `run` writes a JSON report with the target module, overall pass state, and every case name, boolean result, and detail string.
- `badge` writes SVG text to stdout for a caller-supplied label.

The badge command does not run conformance or read a report; it currently renders a passing badge unconditionally. Generate and publish a badge only after independently confirming that the `run` JSON passed.

## Runtime Boundary

Checks run in the local Python process and make no built-in network requests or model calls. The `--against` value is imported with `importlib`, and the suite calls that module's `to_spec` and `from_spec` functions. Running against an untrusted adapter executes untrusted Python code.

## Install

```bash
python -m pip install eval-conformance-suite==0.1.2
```

`rubric-spec>=0.1.1` is installed as a dependency. For development from a clone:

```bash
python -m pip install -e .
```

## Quickstart

```bash
eval-conformance-suite run \
  --against rubric_spec.adapters.inspect_ai \
  > conformance.json

eval-conformance-suite badge \
  --against rubric_spec.adapters.inspect_ai \
  > rubric-spec-conformance.svg
```

The bundled CI also exercises the PromptFoo, DeepEval, LangSmith, and EvalKit adapters shipped by `rubric-spec`.

See [`docs/architecture.md`](docs/architecture.md) and the synthetic report template in [`examples/conformance_report_template.md`](examples/conformance_report_template.md).

## Release Status

Registry status verified July 13, 2026: version `0.1.2` is published on PyPI and tagged `v0.1.2` in the public repository. The project is alpha software. No framework certification, partnership, or adoption claim is made.

## Limits

Passing means the adapter satisfied this package's synthetic `rubric-spec` cases. It is not a framework benchmark, security audit, production-runtime test, or independent certification.

## Next Action

Run the suite against the trusted adapter module you intend to support, inspect all 18 case details, fix every failure, and publish a badge only after the JSON report passes.
