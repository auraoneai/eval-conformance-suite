import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_RUBRIC_SPEC = ROOT.parents[0] / "rubric-spec" / "src"
if LOCAL_RUBRIC_SPEC.exists():
    sys.path.insert(0, str(LOCAL_RUBRIC_SPEC))

from eval_conformance_suite.runner import run

def test_rubric_spec_adapter_passes():
    result = run("rubric_spec.adapters.inspect_ai")
    assert result["passed"], result
    assert len(result["cases"]) == 18
