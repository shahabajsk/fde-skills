import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "eval-harness"
sys.path.insert(0, str(SKILL / "scripts"))

import evalkit  # noqa: E402

GOLDEN = SKILL / "examples" / "golden.jsonl"
PREDS = SKILL / "examples" / "predictions.jsonl"


def g(i, action="a", esc=False, critical=False, cat="x"):
    return {"id": i, "expected_action": action, "should_escalate": esc, "critical": critical, "category": cat}


def p(i, t, action="a", esc=False, cost=0.01):
    return {"id": i, "trial": t, "action": action, "escalated": esc, "cost_usd": cost}


def test_pass_hat_k_matches_tau_bench_estimator():
    assert evalkit.pass_hat_k(4, 4, 4) == 1.0
    assert evalkit.pass_hat_k(4, 3, 4) == 0.0
    assert evalkit.pass_hat_k(4, 3, 2) == pytest.approx(3 / 6)
    assert evalkit.pass_hat_k(4, 3, 1) == pytest.approx(0.75)


def test_pass_k_never_exceeds_pass_1():
    r = evalkit.score(evalkit.load_jsonl(GOLDEN), evalkit.load_jsonl(PREDS))
    assert r["pass_k"] <= r["pass_1"]
    assert r["k"] == 4 and r["tasks"] == 12 and r["trials"] == 48


def test_example_numbers_are_stable():
    r = evalkit.score(evalkit.load_jsonl(GOLDEN), evalkit.load_jsonl(PREDS))
    assert r["pass_1"] == pytest.approx(41 / 48, abs=1e-4)
    assert r["pass_k"] == pytest.approx(0.5)
    assert r["critical_errors"] == ["D04#3"]
    assert r["escalation_recall"] == pytest.approx(10 / 12, abs=1e-4)


def test_escalation_ignores_action_when_escalation_expected():
    r = evalkit.score([g("T", esc=True)], [p("T", 1, action="anything", esc=True)])
    assert r["pass_1"] == 1.0 and r["escalation_recall"] == 1.0


def test_unneeded_escalation_is_wrong_and_hurts_precision():
    r = evalkit.score([g("T")], [p("T", 1, esc=True)])
    assert r["pass_1"] == 0.0 and r["escalation_precision"] == 0.0


def test_gate_fails_on_any_critical_error():
    r = evalkit.score([g("T", critical=True)], [p("T", 1), p("T", 2, action="b")])
    assert any("critical" in f for f in evalkit.gate(r, None, None, None, 0.02))


def test_gate_regression_against_baseline():
    golden = [g("T1"), g("T2")]
    good = evalkit.score(golden, [p("T1", 1), p("T2", 1)])
    worse = evalkit.score(golden, [p("T1", 1), p("T2", 1, action="b")])
    fails = evalkit.gate(worse, None, None, good, 0.02)
    assert any("fell from" in f for f in fails)
    assert evalkit.gate(good, None, None, good, 0.02) == []


def test_gate_refuses_baseline_with_different_k():
    golden = [g("T")]
    one = evalkit.score(golden, [p("T", 1)])
    two = evalkit.score(golden, [p("T", 1), p("T", 2)])
    assert any("k=" in f for f in evalkit.gate(two, None, None, one, 0.02))


@pytest.mark.parametrize("golden,preds,msg", [
    ([g("T")], [], "no predictions"),
    ([g("T")], [p("X", 1)], "unknown id"),
    ([g("T"), g("T")], [p("T", 1)], "duplicate"),
])
def test_input_errors(golden, preds, msg):
    with pytest.raises(evalkit.InputError, match=msg):
        evalkit.score(golden, preds)


def test_k_larger_than_trials_is_an_error():
    with pytest.raises(evalkit.InputError):
        evalkit.score([g("T")], [p("T", 1)], k=3)


def test_cli_exit_codes_and_json(tmp_path):
    out = tmp_path / "r.json"
    assert evalkit.main([str(GOLDEN), str(PREDS), "--json", str(out)]) == 0
    assert json.loads(out.read_text())["tasks"] == 12
    assert evalkit.main([str(GOLDEN), str(PREDS), "--gate", "--min-pass-k", "0.8"]) == 1
    assert evalkit.main([str(GOLDEN), str(tmp_path / "missing.jsonl")]) == 2
