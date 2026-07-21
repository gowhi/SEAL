#!/usr/bin/env python3
"""
variance_analysis.py

Calcula, a partir de los resultados S1/S2/S3:

1) Varianza INTER-RUN:
   cuánto difieren run1 vs run2 para cada
   (estrategia, source, modelo, prompt_label) a cada temperatura.

2) Varianza INTER-TEMPERATURA:
   cuánto varía el ASR entre temp0/temp07/temp1 para cada
   (estrategia, source, modelo, prompt_label),
   promediando run1/run2.

3) Tabla resumen por:
   (estrategia, source)

   con:
   - interrun_stdev_pp_temp0
   - interrun_stdev_pp_temp07
   - interrun_stdev_pp_temp1
   - interrun_stdev_pp_avg
   - intertemp_range_pp_avg
   - intertemp_stdev_pp_avg

Ignora carpetas que no sean:
S1-locals-run1-temp0
S1-commercial-run2-temp07
etc.
"""

import re
import glob
import os
import pandas as pd


RESULTS_DIR = "results"

FILE_SUFFIX = "ci_table.csv"

ASR_COL = "pass_rate"
MODEL_COL = "model"
PROMPT_COL = "prompt_label"


# Acepta:
# S1-locals-run1-temp0
# S2-commercial-run2-temp07
# S3-locals-run1-temp1

DIR_PATTERN = re.compile(
    r"^S(?P<strategy>\d+)-"
    r"(?P<source>locals|commercial)-"
    r"run(?P<run>\d+)-"
    r"temp(?P<temp>0|07|1)$"
)


def load_all_asr_tables(results_dir):

    rows = []

    csv_paths = glob.glob(
        os.path.join(
            results_dir,
            "S*-*-run*-temp*",
            "CSV",
            f"*-{FILE_SUFFIX}"
        )
    )

    if not csv_paths:
        raise FileNotFoundError(
            f"No se encontraron archivos *-{FILE_SUFFIX}"
        )

    for path in csv_paths:

        dirname = os.path.basename(
            os.path.dirname(
                os.path.dirname(path)
            )
        )

        m = DIR_PATTERN.match(dirname)

        if not m:
            print(f"[skip] carpeta no reconocida: {dirname}")
            continue


        strategy = f"S{m.group('strategy')}"
        source = m.group("source")
        run = int(m.group("run"))
        temp = m.group("temp")


        df = pd.read_csv(path)


        missing = {
            MODEL_COL,
            PROMPT_COL,
            ASR_COL
        } - set(df.columns)


        if missing:
            print(
                f"[skip] {path} falta columnas {missing}"
            )
            continue


        df = df[
            [
                MODEL_COL,
                PROMPT_COL,
                ASR_COL
            ]
        ].copy()


        df["strategy"] = strategy
        df["source"] = source
        df["run"] = run
        df["temp"] = temp


        rows.append(df)


    return pd.concat(
        rows,
        ignore_index=True
    )



def compute_intertemp_variance(long_df):

    """
    Promedia run1/run2 y calcula variación entre temperaturas.
    """

    mean_by_run = (
        long_df
        .groupby(
            [
                "strategy",
                "source",
                MODEL_COL,
                PROMPT_COL,
                "temp"
            ]
        )[ASR_COL]
        .mean()
        .reset_index()
    )


    pivot = (
        mean_by_run
        .pivot_table(
            index=[
                "strategy",
                "source",
                MODEL_COL,
                PROMPT_COL
            ],
            columns="temp",
            values=ASR_COL
        )
        .rename(
            columns={
                "0": "mean_temp0",
                "07": "mean_temp07",
                "1": "mean_temp1"
            }
        )
    )


    temp_cols = [
        c for c in
        [
            "mean_temp0",
            "mean_temp07",
            "mean_temp1"
        ]
        if c in pivot.columns
    ]


    pivot["range_pp"] = (
        pivot[temp_cols].max(axis=1)
        -
        pivot[temp_cols].min(axis=1)
    )


    pivot["stdev_pp"] = (
        pivot[temp_cols]
        .std(axis=1, ddof=0)
    )


    return pivot.reset_index()



def compute_interrun_variance(long_df):

    """
    Diferencia run1 vs run2.
    """

    pivot = (
        long_df
        .pivot_table(
            index=[
                "strategy",
                "source",
                MODEL_COL,
                PROMPT_COL,
                "temp"
            ],
            columns="run",
            values=ASR_COL
        )
    )


    run_cols = sorted(
        pivot.columns
    )


    pivot["interrun_range_pp"] = (
        pivot[run_cols].max(axis=1)
        -
        pivot[run_cols].min(axis=1)
    )


    pivot["interrun_stdev_pp"] = (
        pivot[run_cols]
        .std(axis=1, ddof=0)
    )


    return pivot.reset_index()



def build_strategy_summary(intertemp, interrun):


    interrun_by_temp = (
        interrun
        .groupby(
            [
                "strategy",
                "source",
                "temp"
            ]
        )["interrun_stdev_pp"]
        .mean()
        .unstack("temp")
        .rename(
            columns={
                "0": "interrun_stdev_pp_temp0",
                "07": "interrun_stdev_pp_temp07",
                "1": "interrun_stdev_pp_temp1"
            }
        )
    )


    interrun_avg = (
        interrun
        .groupby(
            [
                "strategy",
                "source"
            ]
        )["interrun_stdev_pp"]
        .mean()
        .rename(
            "interrun_stdev_pp_avg"
        )
    )


    intertemp_avg = (
        intertemp
        .groupby(
            [
                "strategy",
                "source"
            ]
        )[
            [
                "range_pp",
                "stdev_pp"
            ]
        ]
        .mean()
        .rename(
            columns={
                "range_pp":
                    "intertemp_range_pp_avg",
                "stdev_pp":
                    "intertemp_stdev_pp_avg"
            }
        )
    )


    summary = (
        interrun_by_temp
        .join(interrun_avg)
        .join(intertemp_avg)
        .reset_index()
    )


    return summary.round(3)



if __name__ == "__main__":


    long_df = load_all_asr_tables(
        RESULTS_DIR
    )


    print("\nCasos cargados:")
    print(
        long_df[
            [
                "strategy",
                "source",
                "run",
                "temp"
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "strategy",
                "source",
                "run",
                "temp"
            ]
        )
        .to_string(index=False)
    )


    intertemp = compute_intertemp_variance(
        long_df
    ).round(3)


    interrun = compute_interrun_variance(
        long_df
    ).round(3)


    summary = build_strategy_summary(
        intertemp,
        interrun
    )


    intertemp.to_csv(
        "variance_across_temps_ALL.csv",
        index=False
    )


    interrun.to_csv(
        "variance_interrun_ALL.csv",
        index=False
    )


    summary.to_csv(
        "variance_summary_by_strategy_source.csv",
        index=False
    )


    print("\n=== Resumen por estrategia/source ===")
    print(
        summary.to_string(index=False)
    )


    print(
        "\nGenerados:"
        "\n - variance_across_temps_ALL.csv"
        "\n - variance_interrun_ALL.csv"
        "\n - variance_summary_by_strategy_source.csv"
    )