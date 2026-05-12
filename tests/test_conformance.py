from eval_conformance_suite.runner import run

def test_rubric_spec_adapter_passes():
    assert run("rubric_spec.adapters.inspect_ai")["passed"]
