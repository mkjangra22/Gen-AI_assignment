import json
import statistics
from pathlib import Path

from .runner import JudgeRunner

def flip(w1, w2):
    # w2 is expressed in original A/B labels after reversing the displayed order.
    return w1 in {"A", "B"} and w2 in {"A", "B"} and w1 != w2

def run():
    suite = json.loads(
        Path("evaluation/judge_suite.json").read_text(encoding="utf-8")
    )

    runner = JudgeRunner()
    rows = []

    for case in suite:
        a = case["model_output_a"]
        b = case["model_output_b"]

        ab = runner.judge_pair(case, a, b, order="AB")
        ba_raw = runner.judge_pair(case, a, b, order="BA")

        # In BA, the displayed first candidate is original B.
        # Convert its winner back to original A/B labels.
        ba = dict(ba_raw)
        if ba.get("ok"):
            w = ba["verdict"]["winner"]
            if w == "A":
                ba["original_winner"] = "B"
            elif w == "B":
                ba["original_winner"] = "A"
            else:
                ba["original_winner"] = "tie"

        if ab.get("ok"):
            ab["original_winner"] = ab["verdict"]["winner"]

        flip_flag = (
            ab.get("ok") and ba.get("ok")
            and flip(ab["original_winner"], ba["original_winner"])
        )

        if ab.get("ok") and ba.get("ok"):
            if ab["original_winner"] == ba["original_winner"]:
                final = ab["original_winner"]
            else:
                final = "tie_due_to_position_disagreement"
        else:
            final = "judge_error"

        row = {
            "id": case["id"],
            "tag": case.get("tag"),
            "ab": ab,
            "ba": ba,
            "position_flip": flip_flag,
            "final_winner": final,
        }
        rows.append(row)

        runner.audit_log(row)

    valid = [r for r in rows if r["final_winner"] != "judge_error"]
    flips = [r for r in valid if r["position_flip"]]

    counts = {"A": 0, "B": 0, "tie_due_to_position_disagreement": 0}
    for r in valid:
        counts[r["final_winner"]] = counts.get(r["final_winner"], 0) + 1

    mean_a = statistics.mean(
        [r["ab"]["verdict"]["overall_score_a"] for r in valid if r.get("ab", {}).get("ok")]
    ) if valid else None
    mean_b = statistics.mean(
        [r["ab"]["verdict"]["overall_score_b"] for r in valid if r.get("ab", {}).get("ok")]
    ) if valid else None
    report = {
        "cases": len(rows),
        "valid_cases": len(valid),
        "pass_rate": len(valid) / len(rows) if rows else 0.0,
        "position_flip_rate": len(flips) / len(valid) if valid else None,
        "final_winner_counts": counts,
        "win_rate": {
            "A": counts.get("A", 0) / len(valid) if valid else None,
            "B": counts.get("B", 0) / len(valid) if valid else None,
        },
        "mean_score": {"A": mean_a, "B": mean_b},
        "declared_winner": (
            "A" if counts.get("A", 0) > counts.get("B", 0) else
            "B" if counts.get("B", 0) > counts.get("A", 0) else "tie"
        ),
        "generator_model": "configured externally",
        "judge_model": "configured externally; use a different family when possible",
        "rows": rows,
    }

    Path("results").mkdir(exist_ok=True)
    Path("results/judge_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    validation = validate(suite, rows)
    Path("results/judge_validation.json").write_text(
        json.dumps(validation, indent=2), encoding="utf-8"
    )

    print(json.dumps({
        "declared_winner": report["declared_winner"],
        "position_flip_rate": report["position_flip_rate"],
        "validation": validation,
    }, indent=2))

def validate(suite, rows):
    gold = {x["id"]: x.get("gold_winner") for x in suite if x.get("gold_winner")}
    predictions = {
        r["id"]: r["final_winner"]
        for r in rows
        if r["final_winner"] in {"A", "B"}
    }

    comparable = [
        (gold[i], predictions[i])
        for i in gold if i in predictions
    ]

    agreement = (
        sum(a == b for a, b in comparable) / len(comparable)
        if comparable else None
    )

    adversarial = [
        r for r in rows
        if next((x for x in suite if x["id"] == r["id"]), {}).get("tag")
        in {"verbose_but_wrong", "confidently_wrong"}
    ]

    return {
        "gold_agreement_rate": agreement,
        "gold_cases": len(comparable),
        "adversarial_cases": len(adversarial),
        "adversarial_wins_for_expected": sum(
            1 for r in adversarial
            if r["final_winner"] == next(
                (x["gold_winner"] for x in suite if x["id"] == r["id"]), None
            )
        ),
        "note": (
            "For stronger validation, repeat the same suite multiple times "
            "and calculate test-retest consistency."
        ),
    }

if __name__ == "__main__":
    run()
