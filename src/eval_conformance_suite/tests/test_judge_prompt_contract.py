def run_case(adapter):
    spec=adapter.to_spec({"criteria":[{"id":"c","weight":1.0,"scale_type":"binary"}]})
    return bool(spec.get("criteria"))
