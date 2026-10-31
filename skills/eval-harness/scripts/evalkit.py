#!/usr/bin/env python3
"""evalkit: score agent outputs against a golden set. Python stdlib only, no model calls.

You run your agent however you like (any model, any harness), write one JSON line per
trial to predictions.jsonl, and evalkit tells you whether it is ready to ship.

golden.jsonl, one line per task:
    {"id": "T01", "expected_action": "rebook", "should_escalate": false,
     "critical": false, "category": "rebooking"}

predictions.jsonl, one line per trial (k trials per task, same id repeated):
    {"id": "T01", "trial": 1, "action": "rebook", "escalated": false, "cost_usd": 0.012}

A trial is correct when:
    should_escalate is true  -> the agent escalated (its action is ignored)
    should_escalate is false -> the agent did not escalate and action == expected_action

Usage:
    python evalkit.py golden.jsonl predictions.jsonl
    python evalkit.py golden.jsonl predictions.jsonl --k 4 --json report.json
    python evalkit.py golden.jsonl predictions.jsonl --gate --min-pass-k 0.8 --baseline last.json --max-drop 0.02

Exit code 0 = gate passed (or no gate), 1 = gate failed, 2 = input error.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from math import comb


class InputError(Exception):
    pass


def load_jsonl(path: str) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise InputError(f"{path}:{n}: invalid JSON ({e.msg})") from None
    return rows


def pass_hat_k(n: int, c: int, k: int) -> float:
    """Unbiased estimate of P(all k i.i.d. trials succeed) from c successes in n trials.

    This is the pass^k metric from tau-bench (Yao et al., 2024): C(c, k) / C(n, k).
    """
    if k > n:
        raise InputError(f"k={k} is larger than the {n} trials recorded for a task")
    return comb(c, k) / comb(n, k)


def is_correct(gold: dict, pred: dict) -> bool:
    if gold.get("should_escalate"):
        return bool(pred.get("escalated"))
    return (not pred.get("escalated")) and pred.get("action") == gold.get("expected_action")


def score(golden: list[dict], preds: list[dict], k: int | None = None) -> dict:
    gold_by_id = {}
    for g in golden:
        if "id" not in g:
            raise InputError("every golden row needs an 'id'")
        if g["id"] in gold_by_id:
            raise InputError(f"duplicate golden id {g['id']}")
        gold_by_id[g["id"]] = g

    trials: dict[str, list[dict]] = defaultdict(list)
    for p in preds:
        if p.get("id") not in gold_by_id:
            raise InputError(f"prediction for unknown id {p.get('id')!r}")
        trials[p["id"]].append(p)

    missing = sorted(set(gold_by_id) - set(trials))
    if missing:
        raise InputError(f"no predictions for {len(missing)} task(s): {', '.join(missing[:5])}")

    n_per_task = {tid: len(ts) for tid, ts in trials.items()}
    min_n = min(n_per_task.values())
    k = k or min_n
    if k < 1:
        raise InputError("k must be at least 1")

    tp = fp = fn = 0
    total_cost = 0.0
    cost_seen = False
    correct_trials = total_trials = 0
    critical_errors: list[str] = []
    per_task = []
    by_cat: dict[str, list[float]] = defaultdict(list)

    for tid, gold in gold_by_id.items():
        ts = trials[tid]
        c = sum(is_correct(gold, t) for t in ts)
        n = len(ts)
        pk = pass_hat_k(n, c, k)
        correct_trials += c
        total_trials += n
        for t in ts:
            if "cost_usd" in t:
                cost_seen = True
                total_cost += float(t["cost_usd"])
            esc, should = bool(t.get("escalated")), bool(gold.get("should_escalate"))
            tp += esc and should
            fp += esc and not should
            fn += (not esc) and should
            if gold.get("critical") and not is_correct(gold, t):
                critical_errors.append(f"{tid}#{t.get('trial', '?')}")
        per_task.append({"id": tid, "trials": n, "correct": c, "pass_k": round(pk, 4)})
        by_cat[gold.get("category", "uncategorised")].append(pk)

    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    return {
        "tasks": len(gold_by_id),
        "trials": total_trials,
        "k": k,
        "pass_1": round(correct_trials / total_trials, 4),
        "pass_k": round(sum(t["pass_k"] for t in per_task) / len(per_task), 4),
        "escalation_precision": None if precision is None else round(precision, 4),
        "escalation_recall": None if recall is None else round(recall, 4),
        "total_cost_usd": round(total_cost, 4) if cost_seen else None,
        "cost_per_correct_usd": round(total_cost / correct_trials, 4) if cost_seen and correct_trials else None,
        "critical_errors": critical_errors,
        "by_category": {c: round(sum(v) / len(v), 4) for c, v in sorted(by_cat.items())},
        "per_task": sorted(per_task, key=lambda t: (t["pass_k"], t["id"])),
    }


def gate(report: dict, min_pass_k: float | None, min_recall: float | None,
         baseline: dict | None, max_drop: float) -> list[str]:
    fails = []
    if report["critical_errors"]:
        fails.append(f"{len(report['critical_errors'])} wrong outcome(s) on critical tasks: "
                     + ", ".join(report["critical_errors"][:5]))
    if min_pass_k is not None and report["pass_k"] < min_pass_k:
        fails.append(f"pass^{report['k']} {report['pass_k']:.3f} is below the floor {min_pass_k:.3f}")
    rec = report["escalation_recall"]
    if min_recall is not None and rec is not None and rec < min_recall:
        fails.append(f"escalation recall {rec:.3f} is below the floor {min_recall:.3f}")
    if baseline:
        if baseline.get("k") != report["k"]:
            fails.append(f"baseline used k={baseline.get('k')}, this run k={report['k']}; rerun with the same k")
        else:
            for key in ("pass_k", "pass_1"):
                if baseline.get(key) is not None and report[key] < baseline[key] - max_drop:
                    fails.append(f"{key} fell from {baseline[key]:.3f} to {report[key]:.3f} (allowed drop {max_drop:.3f})")
            if baseline.get("escalation_recall") is not None and rec is not None \
                    and rec < baseline["escalation_recall"] - max_drop:
                fails.append(f"escalation recall fell from {baseline['escalation_recall']:.3f} to {rec:.3f}")
    return fails


def fmt(x, pct=False):
    if x is None:
        return "n/a"
    return f"{100 * x:.1f}%" if pct else f"{x}"


def render(report: dict, fails: list[str] | None) -> str:
    r = report
    lines = [
        f"evalkit  {r['tasks']} tasks, {r['trials']} trials",
        "",
        f"  pass^1 (accuracy)          {fmt(r['pass_1'], True)}",
        f"  pass^{r['k']} (all {r['k']} trials right) {fmt(r['pass_k'], True)}",
        f"  escalation precision       {fmt(r['escalation_precision'], True)}",
        f"  escalation recall          {fmt(r['escalation_recall'], True)}",
        f"  cost per correct outcome   {'$' + format(r['cost_per_correct_usd'], '.4f') if r['cost_per_correct_usd'] is not None else 'n/a'}",
        f"  critical-task errors       {len(r['critical_errors'])}",
        "",
        "  by category (pass^k):",
    ]
    lines += [f"    {c:<24} {fmt(v, True)}" for c, v in r["by_category"].items()]
    worst = [t for t in r["per_task"] if t["pass_k"] < 1][:5]
    if worst:
        lines += ["", "  weakest tasks:"]
        lines += [f"    {t['id']:<10} {t['correct']}/{t['trials']} trials correct" for t in worst]
    if fails is not None:
        lines += ["", "GATE: PASS" if not fails else "GATE: FAIL"]
        lines += [f"  - {f}" for f in fails]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Score agent trials against a golden set. No model calls.")
    ap.add_argument("golden")
    ap.add_argument("predictions")
    ap.add_argument("--k", type=int, help="k for pass^k (default: the smallest trial count per task)")
    ap.add_argument("--json", help="write the full report to this path")
    ap.add_argument("--gate", action="store_true", help="apply release gates and exit 1 on failure")
    ap.add_argument("--min-pass-k", type=float)
    ap.add_argument("--min-recall", type=float, help="floor for escalation recall")
    ap.add_argument("--baseline", help="a previous --json report to compare against")
    ap.add_argument("--max-drop", type=float, default=0.02, help="allowed drop vs baseline (default 0.02)")
    args = ap.parse_args(argv)
    try:
        report = score(load_jsonl(args.golden), load_jsonl(args.predictions), args.k)
        baseline = None
        if args.baseline:
            with open(args.baseline, encoding="utf-8") as fh:
                baseline = json.load(fh)
    except (InputError, OSError, json.JSONDecodeError) as e:
        print(f"evalkit: {e}", file=sys.stderr)
        return 2
    fails = gate(report, args.min_pass_k, args.min_recall, baseline, args.max_drop) if args.gate else None
    sys.stdout.write(render(report, fails))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
