from main import supported


def test_context_number_unit_and_scale_must_match():
    fact = {
        "concept": "Assets",
        "context": "2024-09-28",
        "text": "100",
        "scale": "6",
        "unit": "USD",
    }
    assert supported(fact, fact)
    for field in fact:
        assert not supported({**fact, field: "wrong"}, fact)


def test_missing_citation_fields_not_silently_supported():
    fact = {"concept": "Assets", "context": "2024", "text": "100", "scale": "0", "unit": "USD"}
    assert not supported({}, fact)
