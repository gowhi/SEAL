# =============================================================================
# effect_size.py — Calculate absolute proportion differences (Δp)
# =============================================================================
#
# Purpose:
#   Given a CSV with Pass Rate confidence intervals per model and hardening
#   level, compute the absolute difference in pass rates (Δp) between hardening
#   levels. This quantifies the effect size of moving from Permissive (Inductor)
#   to Strict (Estricto) or Ultra hardening.
#
# Input:
#   CSV with columns: model, prompt_label, n_total, n_pass, pass_rate,
#   ci_lower_95, ci_upper_95, ci_width
#   where prompt_label is one of: Inductor, Estricto, Ultra
#
# Output:
#   CSV with columns: model, comparison, delta_p, delta_p_abs_value,
#   pass_rate_from, pass_rate_to, ci_lower_from, ci_upper_from,
#   ci_lower_to, ci_upper_to
#   where comparison is e.g. "Inductor -> Estricto"
#
# Usage:
#   python effect_size.py <input_csv> [output_csv]
#
# Example:
#   python effect_size.py S1-commercial-ci_table.csv S1-commercial-effect_size.csv
#
# =============================================================================

import pandas as pd
import sys
import argparse


def calculate_effect_sizes(df, strategy_label):
    """
    Calculate absolute proportion differences (Δp) between hardening levels.
    
    Args:
        df (pd.DataFrame): Input dataframe with columns model, prompt_label,
                          pass_rate, ci_lower_95, ci_upper_95, etc.
        strategy_label (str): Strategy identifier for reference (e.g., "S1").
    
    Returns:
        pd.DataFrame: Effect size table with comparisons between hardening levels.
    """
    results = []
    
    # Define the hardening order and comparisons to make
    hardening_order = ["Inductor", "Estricto", "Ultra"]
    comparisons = [
        ("Inductor", "Estricto"),
        ("Inductor", "Ultra"),
        ("Estricto", "Ultra"),
    ]
    
    # Group by model
    for model, group in df.groupby("model"):
        # Build a dict mapping hardening level -> row
        hardening_dict = {row["prompt_label"]: row for _, row in group.iterrows()}
        
        # Calculate all requested comparisons
        for level_from, level_to in comparisons:
            if level_from not in hardening_dict or level_to not in hardening_dict:
                # Skip if one of the levels is missing for this model
                continue
            
            row_from = hardening_dict[level_from]
            row_to = hardening_dict[level_to]
            
            pr_from = row_from["pass_rate"]
            pr_to = row_to["pass_rate"]
            delta_p = pr_to - pr_from
            
            results.append({
                "strategy": strategy_label,
                "model": model,
                "comparison": f"{level_from} → {level_to}",
                "delta_p": delta_p,
                "delta_p_pct": f"{delta_p:.2f}%",
                "pass_rate_from": pr_from,
                "pass_rate_to": pr_to,
                "ci_lower_from": row_from["ci_lower_95"],
                "ci_upper_from": row_from["ci_upper_95"],
                "ci_lower_to": row_to["ci_lower_95"],
                "ci_upper_to": row_to["ci_upper_95"],
                "ci_width_from": row_from["ci_width"],
                "ci_width_to": row_to["ci_width"],
            })
    
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate hardening effect sizes (absolute proportion differences)."
    )
    parser.add_argument(
        "input_csv",
        help="Input CSV with Pass Rate confidence intervals (e.g., S1-commercial-ci_table.csv)"
    )
    parser.add_argument(
        "output_csv",
        nargs="?",
        default=None,
        help="Output CSV path (default: <input>_effect_size.csv)"
    )
    parser.add_argument(
        "--strategy",
        default="",
        help="Strategy label for reference (optional, e.g., S1, S2, S3)"
    )
    args = parser.parse_args()
    
    # Infer strategy label from input filename if not provided
    strategy_label = args.strategy or (args.input_csv.split("-")[0] if "-" in args.input_csv else "")
    
    # Read input CSV
    df = pd.read_csv(args.input_csv)
    
    # Calculate effect sizes
    effect_sizes = calculate_effect_sizes(df, strategy_label)
    
    # Determine output path
    output_path = args.output_csv
    if output_path is None:
        base = args.input_csv.rsplit(".", 1)[0]
        output_path = f"{base}_effect_size.csv"
    
    # Write output
    effect_sizes.to_csv(output_path, index=False)
    
    print(f"[OK] Effect sizes calculated for {len(effect_sizes)} comparisons")
    print(f"[OK] Saved to: {output_path}")
    print()
    print(effect_sizes.to_string(index=False))


if __name__ == "__main__":
    main()