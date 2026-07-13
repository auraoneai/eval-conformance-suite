# Eval Conformance Suite Architecture

`eval-conformance-suite` turns the `rubric-spec` conformance list into executable checks that adapter maintainers can run before documenting compatibility.

## Components

- The test modules under `src/eval_conformance_suite/tests/` define the canonical cases.
- `runner.py` loads a target adapter and executes the cases against it.
- `badge.py` renders deterministic SVG status badges for public documentation.

## Design Decisions

- Cases are plain Python functions so the suite can run inside CI without a service dependency.
- Reports preserve individual case names and messages, making failed conformance easy to debug.
- Badge generation is deterministic and does not depend on hosted state.
- Examples and fixtures are synthetic and intentionally small.
- The target named by `--against` is imported and executed in-process. Only trusted adapter modules should be tested.
- The badge renderer does not consume a conformance report and currently emits a passing badge for the supplied label. Publication must be gated on a separate successful `run`.
- Passing these cases is evidence about the adapter's schema transformations, not the external framework's installation, runtime, security, or production behavior.
