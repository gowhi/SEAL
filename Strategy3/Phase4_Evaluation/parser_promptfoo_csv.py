# =============================================================================
# parser_promptfoo_csv.py — Strategy 3: Indirect Tool Injection & SDoS (Availability)
# =============================================================================
# Phase 4 post-evaluation script for the SEAL pipeline.
# Parses the raw JSON output from Promptfoo and aggregates results into
# structured CSV datasets for downstream quantitative analysis.
#
# Strategy 3 specific: prompt label detection uses summarization-specific
# keywords; sar_table replaces asr_table to compute Semantic Availability Rate.
#
# Output CSVs generated per prefix:
#   - summary_table: average score and pass rate per model and hardening level
#   - sar_table:     Semantic Availability Rate (SAR = pass rate for S3)
#   - score_dist:    score distribution as percentage per model
#   - tanda_perf:    pass rate per attack batch, model, and hardening level
#   - latencia:      average latency per model and hardening level
#   - tanda_score_perf: average score per attack batch, model, and hardening level
#
# Usage: python parser_promptfoo_csv.py <eval.json> <prefix> [output_dir]
# Example: python parser_promptfoo_csv.py eval-S3-locals.json S3-locals results
# =============================================================================

import json
import pandas as pd
import os
import sys

def get_prompt_label(prompt_text):
    if not prompt_text:
        return "Otros"
    pt = str(prompt_text).lower()
    if "architecture rules" in pt or "security-hardened summarization" in pt:
        return "Ultra"
    elif "secure summarization assistant" in pt:
        return "Estricto"
    elif "professional summarization assistant" in pt:
        return "Inductor"
    else:
        return "Otros"

def process_file(file_path, prefix, output_dir):
    all_records = []

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    body = data.get('body', [])
    for row in body:
        outputs = row.get('outputs', [])
        for out in outputs:
            if out is None:
                continue
            provider = out.get('provider', 'unknown')
            score = out.get('score', 0)
            passed = out.get('pass', False)
            latency = out.get('latencyMs', 0)
            test_case = out.get('testCase') or {}
            test_vars = test_case.get('vars') or {}
            if isinstance(test_vars, list):
                tanda = test_vars[1] if len(test_vars) > 1 else 'BASE'
            else:
                tanda = test_vars.get('tanda', 'BASE')
            prompt_content = out.get('prompt', '')
            prompt_text = prompt_content.get('raw', '') if isinstance(prompt_content, dict) else str(prompt_content)

            all_records.append({
                'model': provider,
                'prompt_label': get_prompt_label(prompt_text),
                'score': score,
                'pass': passed,
                'latency': latency,
                'tanda': tanda
            })

    df = pd.DataFrame(all_records)

    csv_dir = os.path.join(output_dir, prefix, 'CSV')
    os.makedirs(csv_dir, exist_ok=True)

    summary = df.groupby(['model', 'prompt_label']).agg(
        avg_score=('score', 'mean'),
        pass_rate=('pass', lambda x: x.mean() * 100)
    ).reset_index()
    summary.to_csv(f'{csv_dir}/{prefix}-summary_table.csv', index=False)

    sar = summary.copy()
    sar['sar'] = sar['pass_rate']
    sar = sar[['model', 'prompt_label', 'pass_rate', 'sar', 'avg_score']]
    sar.to_csv(f'{csv_dir}/{prefix}-sar_table.csv', index=False)

    score_dist = df.groupby(['model', 'score']).size().unstack(fill_value=0)
    score_dist_pct = score_dist.div(score_dist.sum(axis=1), axis=0) * 100
    score_dist_pct.to_csv(f'{csv_dir}/{prefix}-score_dist.csv')

    tanda_perf = df.groupby(['tanda', 'model', 'prompt_label']).agg(
        success_rate=('pass', lambda x: x.mean() * 100)
    ).reset_index()
    tanda_perf.to_csv(f'{csv_dir}/{prefix}-tanda_perf.csv', index=False)

    latencia = df.groupby(['model', 'prompt_label']).agg(
        avg_latency_ms=('latency', 'mean')
    ).reset_index()
    latencia.to_csv(f'{csv_dir}/{prefix}-latencia.csv', index=False)

    tanda_score_perf = df.groupby(['tanda', 'model', 'prompt_label']).agg(
        avg_score=('score', 'mean')
    ).reset_index()
    tanda_score_perf.to_csv(f'{csv_dir}/{prefix}-tanda_score_perf.csv', index=False)

    print(f"CSVs generados en '{csv_dir}/'")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python parser_promptfoo_csv_s3.py <archivo.json> <prefijo> [directorio_salida]")
        print("Ejemplo: python parser_promptfoo_csv_s3.py eval-S3-locals.json S3-locals results")
        sys.exit(1)

    file_path = sys.argv[1]
    prefix = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "."

    process_file(file_path, prefix, output_dir)