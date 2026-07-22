# =============================================================================
# scorer_results_parser.py — Extract original pass/score for agreement analysis
# =============================================================================
#
# Purpose:
#   Companion to manual_scorer_parser.py. Extracts the deterministic scorer's
#   pass/score (and reason, if available) from a Promptfoo eval.json, using
#   the exact same sample_id format as the blind extractor, so both files can
#   be joined on sample_id to compute human-vs-scorer agreement (Comment 2).
#
# Design:
#   - Generic: works with any eval.json following the standard Promptfoo
#     schema (head/body/outputs), regardless of attack strategy or model.
#   - Same sample_id construction as manual_scorer_parser.py:
#         f"{strategy_label}_{test_idx}_{promptIdx}_{id[:8]}"
#     This is what makes the two files joinable.
#   - Does NOT include any model output or prompt text — only the identifiers
#     needed to join, plus the scorer's own outcome.
#
# Usage:
#   python scorer_results_parser.py <eval.json> <strategy_label> [output.json]
#
# Example:
#   python scorer_results_parser.py eval-S2-commercial-run1-temp0.json \
#       S2_commercial_run1_temp0 scores_S2_commercial_run1_temp0.json
#
# =============================================================================

import json
import sys
import argparse


def extract_score_records(data, strategy_label):
    """
    Extract sample_id, pass, score (and reason, if present) for every
    interaction in a Promptfoo eval.json.

    Args:
        data (dict): The parsed eval.json structure (with 'head' and 'body').
        strategy_label (str): Strategy identifier (e.g., "S1", "S2", "S3"),
            must match the label used when generating the blind file for the
            same eval.json, so sample_id values line up exactly.

    Returns:
        list of dict, each with:
            - sample_id: identical construction to manual_scorer_parser.py
            - model
            - pass_original: boolean pass/fail from the scorer
            - score_original: numeric score from the scorer
            - reason: scorer's stated reason, if present in gradingResult
    """
    records = []
    body = data.get("body", [])

    for row in body:
        test_idx = row.get("testIdx")

        for out in row.get("outputs", []):
            if out is None:
                continue

            grading = out.get("gradingResult") or {}
            reason = grading.get("reason")

            record = {
                "sample_id": f"{strategy_label}_{test_idx}_{out.get('promptIdx')}_{(out.get('id') or '')[:8]}",
                "model": out.get("provider"),
                "pass_original": out.get("pass"),
                "score_original": out.get("score"),
                "reason": reason,
            }
            records.append(record)

    return records


def main():
    parser = argparse.ArgumentParser(
        description="Extract original pass/score from Promptfoo eval.json for agreement analysis."
    )
    parser.add_argument(
        "eval_json",
        help="Path to Promptfoo eval-*.json file"
    )
    parser.add_argument(
        "strategy_label",
        help="Strategy identifier (must match the label used for the blind file, e.g., S2_commercial_run1_temp0)"
    )
    parser.add_argument(
        "output_json",
        nargs="?",
        default=None,
        help="Output file path (default: scores_<strategy_label>.json)"
    )
    args = parser.parse_args()

    with open(args.eval_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = extract_score_records(data, args.strategy_label)

    output_path = args.output_json or f"scores_{args.strategy_label}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(records)} records extracted from {args.eval_json}")
    print(f"[OK] Saved to: {output_path}")


if __name__ == "__main__":
    main()