def test_schema_compliance(adapter):
    assert adapter.to_spec({"criteria":[{"id":"c","weight":1.0}]})["version"] == "auraone-rubric-v1"
