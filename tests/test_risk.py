from decimal import Decimal as D

from app.common import explainability as risk


def test_empty():
    assert risk.score_risk(D(0), [], []) == (0, "No risk rules were triggered.")


def test_history():
    score, reason = risk.score_risk(D(301), [D(100)], [])
    assert score == 50
    assert "three times" in reason
    assert risk.score_risk(D(300), [D(100)], [])[0] == 0


def test_new_customer():
    assert risk.score_risk(D(1001), [], [])[0] == 30
    assert risk.score_risk(D(1000), [], [])[0] == 0


def test_stock():
    assert risk.score_risk(D(1), [], [(2, 1), (3, 1)])[0] == 20
    assert risk.score_risk(D(1), [], [(1, 1)])[0] == 0


def test_combined():
    assert risk.score_risk(D(400), [D(100)], [(2, 1)])[0] == 70


def test_cap(monkeypatch):
    # The specified rules reach at most 70; exercise the cap with increased rule weights.
    monkeypatch.setattr(risk, "HISTORY_POINTS", 100)
    assert risk.score_risk(D(400), [D(100)], [(2, 1)])[0] == 100
