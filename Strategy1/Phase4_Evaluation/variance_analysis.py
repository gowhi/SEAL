#!/usr/bin/env python3
"""
variance_analysis.py

Calcula, a partir de los resultados de S1/S2/S3 (locals, runs 1 y 2, temps 0/0.7/1):

  1) Varianza INTER-RUN: cuánto difieren run1 vs run2 para cada
     (estrategia, modelo, prompt_label) a cada temperatura.
  2) Varianza INTER-TEMPERATURA: cuánto varía el ASR entre temp0/temp07/temp1
     para cada (estrategia, modelo, prompt_label), promediando antes run1/run2.
     -> Esto reproduce el formato de variance_across_temps_ALL.csv que ya
        generaste (mean_temp0, mean_temp07, mean_temp1, range_pp, stdev_pp).
  3) Una tabla resumen POR ESTRATEGIA (promediando sobre todos los
     modelos/prompts) con columnas:
        - interrun_stdev_pp_temp0 / temp07 / temp1  (repetibilidad a cada temp)
        - interrun_stdev_pp_avg                     (repetibilidad global)
        - intertemp_range_pp_avg / intertemp_stdev_pp_avg (sensibilidad a temp)

Ajusta las 3 constantes de abajo si tus CSV usan otros nombres de columna.
"""

import re
import glob
import os
import pandas as pd
import numpy as np

RESULTS_DIR  = "results"         # carpeta raíz (donde están S1-locals-run1-temp0/, etc.)
FILE_SUFFIX  = "ci_table.csv"    # usamos ci_table.csv (trae pass_rate + n_total, útil si luego quieres ponderar)
ASR_COL      = "pass_rate"       # el "ASR" real está en la columna pass_rate
MODEL_COL    = "model"
PROMPT_COL   = "prompt_label"

DIR_PATTERN = re.compile(r"^S(?P<strategy>\d+)-locals-run(?P<run>\d+)-temp(?P<temp>0|07|1)$")


def load_all_asr_tables(results_dir: str) -> pd.DataFrame:
    """Recorre results/S*-locals-run*-temp*/CSV/*-ci_table.csv y apila todo."""
    rows = []
    csv_paths = glob.glob(os.path.join(results_dir, "S*-locals-run*-temp*", "CSV", f"*-{FILE_SUFFIX}"))
    if not csv_paths:
        raise FileNotFoundError(
            f"No encontré ningún *-{FILE_SUFFIX} bajo {results_dir}/S*-locals-run*-temp*/CSV/. "
            "Revisa RESULTS_DIR o el patrón de nombres."
        )

    for path in csv_paths:
        dirname = os.path.basename(os.path.dirname(os.path.dirname(path)))  # S1-locals-run1-temp0
        m = DIR_PATTERN.match(dirname)
        if not m:
            print(f"[aviso] carpeta no reconocida, la salto: {dirname}")
            continue

        strategy = f"S{m.group('strategy')}"
        run = int(m.group("run"))
        temp = m.group("temp")  # '0', '07' o '1'

        df = pd.read_csv(path)
        missing = {MODEL_COL, PROMPT_COL, ASR_COL} - set(df.columns)
        if missing:
            print(f"[aviso] {path} no tiene columnas {missing}, lo salto. Columnas disponibles: {list(df.columns)}")
            continue

        df = df[[MODEL_COL, PROMPT_COL, ASR_COL]].copy()
        df["strategy"] = strategy
        df["run"] = run
        df["temp"] = temp
        rows.append(df)

    return pd.concat(rows, ignore_index=True)


def compute_intertemp_variance(long_df: pd.DataFrame) -> pd.DataFrame:
    """Promedia run1/run2 y calcula range_pp / stdev_pp entre temp0/temp07/temp1."""
    mean_by_run = (
        long_df.groupby(["strategy", MODEL_COL, PROMPT_COL, "temp"])[ASR_COL]
        .mean()
        .reset_index()
    )
    pivot = mean_by_run.pivot_table(
        index=["strategy", MODEL_COL, PROMPT_COL], columns="temp", values=ASR_COL
    ).rename(columns={"0": "mean_temp0", "07": "mean_temp07", "1": "mean_temp1"})

    temp_cols = [c for c in ["mean_temp0", "mean_temp07", "mean_temp1"] if c in pivot.columns]
    pivot["range_pp"] = pivot[temp_cols].max(axis=1) - pivot[temp_cols].min(axis=1)
    pivot["stdev_pp"] = pivot[temp_cols].std(axis=1, ddof=0)  # poblacional, como en tu ejemplo previo
    return pivot.reset_index()


def compute_interrun_variance(long_df: pd.DataFrame) -> pd.DataFrame:
    """Para cada (estrategia, modelo, prompt, temp): |run1 - run2| y stdev entre runs."""
    pivot = long_df.pivot_table(
        index=["strategy", MODEL_COL, PROMPT_COL, "temp"], columns="run", values=ASR_COL
    )
    run_cols = sorted(pivot.columns)
    pivot["interrun_range_pp"] = pivot[run_cols].max(axis=1) - pivot[run_cols].min(axis=1)
    pivot["interrun_stdev_pp"] = pivot[run_cols].std(axis=1, ddof=0)
    return pivot.reset_index()


def build_strategy_summary(intertemp: pd.DataFrame, interrun: pd.DataFrame) -> pd.DataFrame:
    """Tabla final por estrategia, promediando sobre todos los modelos/prompts."""
    interrun_by_temp = (
        interrun.groupby(["strategy", "temp"])["interrun_stdev_pp"]
        .mean()
        .unstack("temp")
        .rename(columns={"0": "interrun_stdev_pp_temp0",
                          "07": "interrun_stdev_pp_temp07",
                          "1": "interrun_stdev_pp_temp1"})
    )
    interrun_avg = interrun.groupby("strategy")["interrun_stdev_pp"].mean().rename("interrun_stdev_pp_avg")

    intertemp_avg = intertemp.groupby("strategy")[["range_pp", "stdev_pp"]].mean().rename(
        columns={"range_pp": "intertemp_range_pp_avg", "stdev_pp": "intertemp_stdev_pp_avg"}
    )

    summary = interrun_by_temp.join(interrun_avg).join(intertemp_avg).reset_index()
    return summary.round(3)


if __name__ == "__main__":
    long_df = load_all_asr_tables(RESULTS_DIR)

    intertemp = compute_intertemp_variance(long_df).round(3)
    interrun = compute_interrun_variance(long_df).round(3)
    summary = build_strategy_summary(intertemp, interrun)

    intertemp.to_csv("variance_across_temps_ALL.csv", index=False)
    interrun.to_csv("variance_interrun_ALL.csv", index=False)
    summary.to_csv("variance_summary_by_strategy.csv", index=False)

    print("=== Resumen por estrategia ===")
    print(summary.to_string(index=False))
    print("\nGenerados: variance_across_temps_ALL.csv, variance_interrun_ALL.csv, variance_summary_by_strategy.csv")