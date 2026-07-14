#!/usr/bin/env python3
"""
compare_cyberseceval_vs_seal.py

Compares CyberSecEval against SEAL using only:

    - run1
    - temperature = 0

Benchmark correspondence:

    SEAL S1 (Integrity)       <-> CyberSecEval logic-violating
    SEAL S2 (Confidentiality) <-> CyberSecEval security-violating

Outputs:

    comparison_S1-locals_vs_cyberseceval.csv
    comparison_S1-commercial_vs_cyberseceval.csv
    comparison_S2-locals_vs_cyberseceval.csv
    comparison_S2-commercial_vs_cyberseceval.csv
"""

import glob
import json
import pandas as pd

##############################################################################
# CONFIGURATION
##############################################################################

CYBERSECEVAL_JSON_GLOB = "runs_cyberseceval/full_stats_*.json"

SEAL_FILES = {

    "S1-locals":
        "Strategy1/Phase4_Evaluation/results/"
        "S1-locals-run1-temp0/CSV/"
        "S1-locals-run1-temp0-summary_table.csv",

    "S1-commercial":
        "Strategy1/Phase4_Evaluation/results/"
        "S1-commercial-run1-temp0/CSV/"
        "S1-commercial-run1-temp0-summary_table.csv",

    "S2-locals":
        "Strategy2/Phase4_Evaluation/results/"
        "S2-locals-run1-temp0/CSV/"
        "S2-locals-run1-temp0-summary_table.csv",

    "S2-commercial":
        "Strategy2/Phase4_Evaluation/results/"
        "S2-commercial-run1-temp0/CSV/"
        "S2-commercial-run1-temp0-summary_table.csv",
}

RISK_MAP = {
    "S1": "logic-violating",
    "S2": "security-violating",
}

##############################################################################
# MODEL NAME NORMALIZATION
##############################################################################

def normalize_model_name(raw_name: str):
    """
    Maps CyberSecEval model names to the names used in SEAL.
    """

    name = raw_name.lower()

    if "llama" in name:
        return "llama"

    if "mistral" in name:
        return "mistral-target"

    if "qwen" in name:
        return "qwen-coder-target"

    if "gpt-oss" in name:
        return "gpt-oss-target"

    if "deepseek" in name:
        return "deepseek-v3"

    if "haiku" in name:
        return "haiku"

    return raw_name


##############################################################################
# LOAD CYBERSECEVAL RESULTS
##############################################################################

def load_cyberseceval_asr(json_glob):

    rows = []

    paths = sorted(glob.glob(json_glob))

    if not paths:
        raise FileNotFoundError(
            f"No files found matching:\n{json_glob}"
        )

    for path in paths:

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for raw_model, model_data in data.items():

            model = normalize_model_name(raw_model)

            risk_stats = model_data.get(
                "stat_per_model_per_risk_category",
                {}
            )

            for risk_category, values in risk_stats.items():

                rows.append({

                    "model": model,

                    "raw_model": raw_model,

                    "risk_category": risk_category,

                    "cyberseceval_asr":
                        round(
                            values["injection_successful_percentage"] * 100,
                            4
                        ),

                    "n_total_cyberseceval":
                        values["total_count"]

                })

    cyber_df = pd.DataFrame(rows)

    print("\nDetected models in CyberSecEval:\n")
    print(
        cyber_df[
            ["raw_model", "model"]
        ]
        .drop_duplicates()
        .to_string(index=False)
    )

    return cyber_df


##############################################################################
# LOAD SEAL CSV
##############################################################################

def load_seal_csv(path):

    df = pd.read_csv(path)

    if "asr" not in df.columns:
        df["asr"] = (100 - df["pass_rate"]).round(4)

    columns = [
        c for c in [
            "model",
            "prompt_label",
            "pass_rate",
            "asr",
            "avg_score",
        ]
        if c in df.columns
    ]

    return df[columns]


##############################################################################
# BUILD COMPARISON
##############################################################################

def build_comparison(csv_path, risk_category, cyber_df):

    seal_df = load_seal_csv(csv_path)

    cyber_subset = cyber_df[
        cyber_df["risk_category"] == risk_category
    ][[
        "model",
        "cyberseceval_asr",
        "n_total_cyberseceval",
    ]]

    comparison = seal_df.merge(
        cyber_subset,
        on="model",
        how="left"
    )

    comparison.insert(
        0,
        "risk_category",
        risk_category
    )

    comparison["delta_seal_minus_cyberseceval"] = (
        comparison["asr"] -
        comparison["cyberseceval_asr"]
    ).round(4)

    return comparison


##############################################################################
# MAIN
##############################################################################

if __name__ == "__main__":

    cyber_df = load_cyberseceval_asr(
        CYBERSECEVAL_JSON_GLOB
    )

    print("\n========================================")
    print("CyberSecEval Summary")
    print("========================================")

    print(cyber_df.to_string(index=False))

    for benchmark_name, csv_path in SEAL_FILES.items():

        strategy = benchmark_name.split("-")[0]

        risk_category = RISK_MAP[strategy]

        comparison = build_comparison(
            csv_path,
            risk_category,
            cyber_df
        )

        output_csv = (
            f"comparison_{benchmark_name}_vs_cyberseceval.csv"
        )

        comparison.to_csv(
            output_csv,
            index=False
        )

        print("\n========================================")
        print(benchmark_name)
        print("========================================")

        print(comparison.to_string(index=False))

        print(f"\nSaved: {output_csv}")

    print("\nComparison completed successfully.")