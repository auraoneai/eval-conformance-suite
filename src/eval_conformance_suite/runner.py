import argparse
import importlib
import json
from copy import deepcopy
from typing import Any, Callable

from rubric_spec import lint_rubric, validate_rubric

Case = tuple[str, Callable[[Any], tuple[bool, str]]]


def _criterion(
    criterion_id: str = "quality",
    scale_type: str = "binary",
    weight: float = 1.0,
    anchors: list[dict[str, Any]] | None = None,
    examples: list[dict[str, str]] | None = None,
    tie_break_rule: str = "none",
) -> dict[str, Any]:
    return {
        "criterion_id": criterion_id,
        "label": criterion_id.replace("_", " ").title(),
        "description": f"Score {criterion_id} using observable evidence.",
        "scale_type": scale_type,
        "weight": weight,
        "tie_break_rule": tie_break_rule,
        "anchors": anchors or [{"value": 0, "label": "fail"}, {"value": 1, "label": "pass"}],
        "examples": [{"input": "synthetic example", "output": "synthetic response", "score": "1"}]
        if examples is None
        else examples,
    }


def _rubric(criteria: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "version": "auraone-rubric-v1",
        "rubric_id": "synthetic-conformance-rubric",
        "label": "Synthetic conformance rubric",
        "tie_break_rule": "manual_review",
        "judge_prompt_contract": {
            "instruction": "Score every criterion and return JSON.",
            "output_format": "json",
            "required_fields": ["criterion_id", "score", "rationale"],
        },
        "provenance": {
            "source": "eval-conformance-suite",
            "created_by": "auraone",
            "created_at": "2026-05-12",
            "synthetic": True,
        },
        "criteria": criteria or [_criterion()],
    }


def _round_trip(adapter: Any, spec: dict[str, Any]) -> dict[str, Any]:
    return adapter.to_spec(adapter.from_spec(deepcopy(spec)))


def _validate(spec: dict[str, Any]) -> tuple[bool, str]:
    result = validate_rubric(spec)
    return result.ok, json.dumps(result.to_dict(), sort_keys=True)


def _case_minimal_binary(adapter: Any) -> tuple[bool, str]:
    spec = adapter.to_spec({"criteria": [{"id": "quality", "scale_type": "binary", "weight": 1.0}]})
    return _validate(spec)


def _case_ordinal_anchors(adapter: Any) -> tuple[bool, str]:
    spec = _rubric(
        [
            _criterion(
                "ordinal_quality",
                "ordinal",
                anchors=[{"value": 1, "label": "low"}, {"value": 2, "label": "medium"}, {"value": 3, "label": "high"}],
            )
        ]
    )
    out = _round_trip(adapter, spec)
    values = [anchor["value"] for anchor in out["criteria"][0]["anchors"]]
    return values == sorted(values), str(values)


def _case_likert_anchors(adapter: Any) -> tuple[bool, str]:
    anchors = [{"value": i, "label": f"level {i}"} for i in range(1, 6)]
    out = _round_trip(adapter, _rubric([_criterion("likert_quality", "likert", anchors=anchors)]))
    return len(out["criteria"][0]["anchors"]) == 5, str(out["criteria"][0]["anchors"])


def _case_continuous_endpoints(adapter: Any) -> tuple[bool, str]:
    anchors = [{"value": 0.0, "label": "minimum"}, {"value": 1.0, "label": "maximum"}]
    out = _round_trip(adapter, _rubric([_criterion("continuous_quality", "continuous", anchors=anchors)]))
    values = [anchor["value"] for anchor in out["criteria"][0]["anchors"]]
    return values == [0.0, 1.0], str(values)


def _case_reject_missing_version(_: Any) -> tuple[bool, str]:
    spec = _rubric()
    spec.pop("version")
    result = validate_rubric(spec)
    return (not result.ok and any(issue.path == "/version" for issue in result.errors)), json.dumps(result.to_dict(), sort_keys=True)


def _case_reject_unsupported_scale(_: Any) -> tuple[bool, str]:
    result = validate_rubric(_rubric([_criterion(scale_type="stars")]))
    return (not result.ok and any(issue.path.endswith("/scale_type") for issue in result.errors)), json.dumps(result.to_dict(), sort_keys=True)


def _case_reject_duplicate_ids(_: Any) -> tuple[bool, str]:
    result = validate_rubric(_rubric([_criterion("quality", weight=0.5), _criterion("quality", weight=0.5)]))
    return (not result.ok and any("duplicate" in issue.message for issue in result.errors)), json.dumps(result.to_dict(), sort_keys=True)


def _case_warn_weight_sum(_: Any) -> tuple[bool, str]:
    result = validate_rubric(_rubric([_criterion("quality", weight=0.75)]))
    return (result.ok and any(issue.path == "/criteria" for issue in result.warnings)), json.dumps(result.to_dict(), sort_keys=True)


def _case_preserve_provenance(adapter: Any) -> tuple[bool, str]:
    out = _round_trip(adapter, _rubric())
    return out.get("provenance", {}).get("synthetic") is True, json.dumps(out.get("provenance", {}), sort_keys=True)


def _case_preserve_tie_break(adapter: Any) -> tuple[bool, str]:
    out = _round_trip(adapter, _rubric([_criterion(tie_break_rule="prefer_lower_risk")]))
    return out["criteria"][0].get("tie_break_rule") == "prefer_lower_risk", str(out["criteria"][0].get("tie_break_rule"))


def _case_preserve_judge_contract(adapter: Any) -> tuple[bool, str]:
    out = _round_trip(adapter, _rubric())
    fields = out.get("judge_prompt_contract", {}).get("required_fields", [])
    return "rationale" in fields and out.get("judge_prompt_contract", {}).get("output_format") == "json", json.dumps(out.get("judge_prompt_contract", {}), sort_keys=True)


def _case_round_trip_fields(adapter: Any) -> tuple[bool, str]:
    out = _round_trip(adapter, _rubric([_criterion("specificity", examples=[{"input": "synthetic", "output": "specific", "score": "1"}])]))
    criterion = out["criteria"][0]
    required = {"criterion_id", "label", "description", "scale_type", "weight", "tie_break_rule", "anchors", "examples"}
    return required.issubset(criterion), json.dumps(sorted(required - set(criterion)), sort_keys=True)


def _case_native_binary_to_spec(adapter: Any) -> tuple[bool, str]:
    out = adapter.to_spec({"checks": [{"id": "binary_native", "criterion": "Pass/fail quality", "weight": 1.0}]})
    return out["criteria"][0]["scale_type"] == "binary", out["criteria"][0]["scale_type"]


def _case_spec_ordinal_to_native(adapter: Any) -> tuple[bool, str]:
    native = adapter.from_spec(_rubric([_criterion("ordinal_quality", "ordinal", weight=1.0)]))
    out = adapter.to_spec(native)
    criterion = out["criteria"][0]
    return criterion["scale_type"] == "ordinal" and criterion["weight"] == 1.0, json.dumps(criterion, sort_keys=True)


def _case_deterministic_json(adapter: Any) -> tuple[bool, str]:
    out = _round_trip(adapter, _rubric())
    first = json.dumps(out, sort_keys=True, separators=(",", ":"))
    second = json.dumps(out, sort_keys=True, separators=(",", ":"))
    return first == second, first


def _case_path_aware_errors(_: Any) -> tuple[bool, str]:
    result = validate_rubric(_rubric([_criterion(criterion_id="")]))
    paths = [issue.path for issue in result.errors]
    return "/criteria/0/criterion_id" in paths, json.dumps(paths)


def _case_lint_findings(_: Any) -> tuple[bool, str]:
    spec = _rubric([_criterion("quality", examples=[])])
    spec["criteria"][0]["description"] = "Good and useful response."
    rules = {finding.rule for finding in lint_rubric(spec)}
    return {"R_VAGUE", "R_COMPOUND", "R_EXAMPLES"}.issubset(rules), json.dumps(sorted(rules))


def _case_synthetic_disclosure(adapter: Any) -> tuple[bool, str]:
    out = _round_trip(adapter, _rubric())
    return out.get("provenance", {}).get("synthetic") is True, json.dumps(out.get("provenance", {}), sort_keys=True)


CASES: list[Case] = [
    ("minimal_binary_rubric", _case_minimal_binary),
    ("ordinal_anchors_ascending", _case_ordinal_anchors),
    ("likert_five_levels", _case_likert_anchors),
    ("continuous_numeric_endpoints", _case_continuous_endpoints),
    ("reject_missing_version", _case_reject_missing_version),
    ("reject_unsupported_scale_type", _case_reject_unsupported_scale),
    ("reject_duplicate_criterion_ids", _case_reject_duplicate_ids),
    ("warn_weights_do_not_sum_to_one", _case_warn_weight_sum),
    ("preserve_top_level_provenance", _case_preserve_provenance),
    ("preserve_criterion_tie_break_rule", _case_preserve_tie_break),
    ("preserve_judge_prompt_contract", _case_preserve_judge_contract),
    ("round_trip_without_dropping_fields", _case_round_trip_fields),
    ("native_binary_to_spec_binary", _case_native_binary_to_spec),
    ("spec_ordinal_to_native_weighted", _case_spec_ordinal_to_native),
    ("deterministic_json_serialization", _case_deterministic_json),
    ("path_aware_validation_errors", _case_path_aware_errors),
    ("lint_vague_compound_missing_examples", _case_lint_findings),
    ("synthetic_data_disclosure", _case_synthetic_disclosure),
]


def run(against: str) -> dict[str, Any]:
    adapter = importlib.import_module(against)
    results = []
    for name, fn in CASES:
        passed, detail = fn(adapter)
        results.append({"name": name, "passed": bool(passed), "detail": detail})
    return {"against": against, "passed": all(case["passed"] for case in results), "cases": results, "synthetic": True}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="eval-conformance-suite")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--against", required=True)
    badge_parser = sub.add_parser("badge")
    badge_parser.add_argument("--against", required=True)
    args = parser.parse_args(argv)
    if args.cmd == "badge":
        print(__import__("eval_conformance_suite.badge", fromlist=["badge"]).badge(args.against, True))
        return 0
    result = run(args.against)
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
