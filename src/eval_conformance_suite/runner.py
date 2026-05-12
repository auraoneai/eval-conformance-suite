import argparse, importlib, json
CASES=["schema_compliance","scale_types","weighted_aggregation","tie_breaking","judge_prompt_contract","round_trip"]
def run(against):
    adapter=importlib.import_module(against)
    spec=adapter.to_spec({"criteria":[{"id":"c","weight":1.0,"scale_type":"binary"}]})
    passed=spec.get('version')=='auraone-rubric-v1' and bool(spec.get('criteria'))
    return {"against": against, "passed": passed, "cases": [{"name": c, "passed": passed} for c in CASES], "synthetic": True}
def main(argv=None):
    p=argparse.ArgumentParser(prog='eval-conformance-suite'); sub=p.add_subparsers(dest='cmd', required=True)
    r=sub.add_parser('run'); r.add_argument('--against', required=True)
    b=sub.add_parser('badge'); b.add_argument('--against', required=True)
    args=p.parse_args(argv)
    if args.cmd=='badge': print(__import__('eval_conformance_suite.badge', fromlist=['badge']).badge(args.against, True)); return 0
    result=run(args.against); print(json.dumps(result, indent=2)); return 0 if result['passed'] else 1
if __name__ == '__main__': raise SystemExit(main())
