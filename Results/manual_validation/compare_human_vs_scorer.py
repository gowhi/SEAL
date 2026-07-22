# =============================================================================
# compare_human_vs_scorer.py — Agreement analysis between human labels and
# the deterministic scorer's original pass/score.
# =============================================================================

import json
import argparse
from collections import Counter, defaultdict
from sklearn.metrics import cohen_kappa_score


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def short_id(sample_id):
    return sample_id.split("_")[-1]


def compare(blind_records, score_records, pass_threshold):
    score_lookup = {short_id(r["sample_id"]): r for r in score_records}

    matched = 0
    unmatched_blind = 0
    missing_human_label = 0

    exact_matches = 0
    score_discrepancies = 0
    pass_flips = 0
    pass_preserved = 0

    by_model = defaultdict(
        lambda: {
            "matched": 0,
            "exact": 0,
            "discrepancy": 0,
            "pass_flip": 0,
        }
    )

    pair_counter = Counter()
    details = []

    # Para Cohen's Kappa
    human_scores = []
    auto_scores = []

    def score_to_category(x):
        return int(round(x * 10))

    human_passes = []
    auto_passes = []

    for b in blind_records:

        sid = short_id(b["sample_id"])
        human = b.get("human_label")

        if sid not in score_lookup:
            unmatched_blind += 1
            continue

        if human is None:
            missing_human_label += 1
            continue

        matched += 1

        s = score_lookup[sid]

        auto_score = s.get("score_original")
        auto_pass = s.get("pass_original")
        model = b.get("model", "unknown")

        by_model[model]["matched"] += 1

        # Guardar para Kappa
        if auto_score is not None:
            human_scores.append(score_to_category(human))
            auto_scores.append(score_to_category(auto_score))

        if auto_pass is not None:
            human_passes.append(human >= pass_threshold)
            auto_passes.append(bool(auto_pass))

        if auto_score is not None and abs(human - auto_score) < 1e-6:
            exact_matches += 1
            by_model[model]["exact"] += 1
            continue

        score_discrepancies += 1
        by_model[model]["discrepancy"] += 1

        pair_counter[(human, auto_score)] += 1

        human_pass = human >= pass_threshold
        flips_pass = (
            auto_pass is not None
            and human_pass != bool(auto_pass)
        )

        if flips_pass:
            pass_flips += 1
            by_model[model]["pass_flip"] += 1
        else:
            pass_preserved += 1

        details.append(
            {
                "sample_id": b["sample_id"],
                "model": model,
                "human_label": human,
                "score_original": auto_score,
                "pass_original": auto_pass,
                "human_pass_derived": human_pass,
                "affects_pass_rate": flips_pass,
            }
        )

    kappa_scores = None
    kappa_pass = None

    if human_scores:
        kappa_scores = cohen_kappa_score(
            human_scores,
            auto_scores,
            weights="linear",
        )

    if human_passes:
        kappa_pass = cohen_kappa_score(
            human_passes,
            auto_passes,
        )

    return {
        "matched": matched,
        "unmatched_blind": unmatched_blind,
        "missing_human_label": missing_human_label,
        "exact_matches": exact_matches,
        "score_discrepancies": score_discrepancies,
        "pass_flips": pass_flips,
        "pass_preserved": pass_preserved,
        "by_model": dict(by_model),
        "pair_counts": pair_counter,
        "details": details,
        "kappa_scores": kappa_scores,
        "kappa_pass": kappa_pass,
    }


def print_summary(result, pass_threshold):

    matched = result["matched"]

    print(f"=== Resumen de acuerdo humano vs. scorer (umbral de pass: {pass_threshold}) ===")
    print(f"Casos emparejados:            {matched}")

    if result["unmatched_blind"]:
        print(f"  (sin match en scores.json):  {result['unmatched_blind']}")

    if result["missing_human_label"]:
        print(f"  (sin human_label todavia):   {result['missing_human_label']}")

    print()

    if matched == 0:
        print("No hay casos emparejados.")
        return

    exact = result["exact_matches"]
    disc = result["score_discrepancies"]

    print(f"Acuerdo exacto de score:       {exact}/{matched} ({100*exact/matched:.2f}%)")
    print(f"Discrepancias de score:        {disc}/{matched} ({100*disc/matched:.2f}%)")
    print()

    print(f"Cohen's κ (Pass/Fail):         {result['kappa_pass']:.4f}")
    print(f"Weighted Cohen's κ (Scores):   {result['kappa_scores']:.4f}")
    print()

    if disc:
        flips = result["pass_flips"]
        preserved = result["pass_preserved"]

        print(f"  De esas discrepancias, afectan al pass/fail (y por tanto al ASR): {flips}/{disc} ({100*flips/disc:.2f}%)")
        print(f"  De esas discrepancias, NO afectan al pass/fail (mismo bucket):    {preserved}/{disc} ({100*preserved/disc:.2f}%)")
        print()

    print("--- Por modelo ---")

    for model, stats in result["by_model"].items():
        m = stats["matched"]
        e = stats["exact"]
        d = stats["discrepancy"]
        f = stats["pass_flip"]

        print(
            f"  {model:15s}: {e}/{m} exacto ({100*e/m:.2f}%)  |  {d} discrepancias  |  {f} afectan al pass"
        )

    print()

    print("--- Patrones (human_label, score_original) mas frecuentes ---")

    for (h, a), n in result["pair_counts"].most_common(10):
        print(f"  ({h}, {a}): {n} casos")


def main():

    parser = argparse.ArgumentParser(
        description="Compare human labels (blind_*.json) against the deterministic scorer (scores_*.json)."
    )

    parser.add_argument("blind_json")
    parser.add_argument("scores_json")

    parser.add_argument(
        "--pass-threshold",
        type=float,
        default=0.5,
    )

    parser.add_argument(
        "--details-out",
        default=None,
    )

    args = parser.parse_args()

    blind_records = load_json(args.blind_json)
    score_records = load_json(args.scores_json)

    result = compare(
        blind_records,
        score_records,
        args.pass_threshold,
    )

    print_summary(result, args.pass_threshold)

    if args.details_out:
        with open(args.details_out, "w", encoding="utf-8") as f:
            json.dump(
                result["details"],
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"\n[OK] Detalle de discrepancias guardado en: {args.details_out}")

    print()
    print("--- Sample IDs con discrepancias ---")

    if not result["details"]:
        print("  Ninguna discrepancia.")
    else:
        for d in result["details"]:
            print(f'  "{d["sample_id"]}"')


if __name__ == "__main__":
    main()