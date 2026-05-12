import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_RUBRIC_SPEC = ROOT.parents[0] / "rubric-spec" / "src"
if LOCAL_RUBRIC_SPEC.exists():
    sys.path.insert(0, str(LOCAL_RUBRIC_SPEC))

from eval_conformance_suite.runner import run

def test_all_rubric_spec_adapters_pass():
    adapters = [
        "rubric_spec.adapters.inspect_ai",
        "rubric_spec.adapters.promptfoo",
        "rubric_spec.adapters.deepeval",
        "rubric_spec.adapters.langsmith",
        "rubric_spec.adapters.evalkit",
    ]
    for adapter in adapters:
        result = run(adapter)
        assert result["passed"], result
        assert len(result["cases"]) == 18
