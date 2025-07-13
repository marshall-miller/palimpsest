from palobserver.rules import flags

def test_payment_rule_matches():
    text = "The invoice terms are Net-30."
    assert flags(text) == ["net_payment_conflict"]

def test_no_match():
    assert flags("Nothing interesting here") == []

