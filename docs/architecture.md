# Eval Conformance Suite Architecture

`eval-conformance-suite` turns the `rubric-spec` conformance list into executable checks that frameworks can run to claim compatibility.

## Components

- The test modules under `src/eval_conformance_suite/tests/` define the canonical cases.
- `runner.py` loads a target adapter and executes the cases against it.
- `badge.py` renders deterministic SVG status badges for public documentation.

## Design Decisions

- Cases are plain Python functions so the suite can run inside CI without a service dependency.
- Reports preserve individual case names and messages, making failed conformance easy to debug.
- Badge generation is deterministic and does not depend on hosted state.
- Examples and fixtures are synthetic and intentionally small.
