import json
import pandas as pd
import os
import sys

def get_prompt_label(prompt_text):
    if "SECURITY-CRITICAL" in prompt_text:
        return "Ultra"
    elif "Security-hardened" in prompt_text:
        return "Estricto"
    else:
        return "Inductor"

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
            tanda = test_vars.get('tanda', 'BASE')
            prompt = str(out.get('prompt', ''))

            all_records.append({
                'model': provider,
                'prompt_label': get_prompt_label(prompt),
                'score': score,
                'pass': passed,
                'latency': latency,
                'tanda': tanda
            })

    df = pd.DataFrame(all_records)

    # Carpeta: output_dir/prefix/CSV/
    csv_dir = os.path.join(output_dir, prefix, 'CSV')
    os.makedirs(csv_dir, exist_ok=True)

    # 1. summary_table
    summary = df.groupby(['model', 'prompt_label']).agg(
        avg_score=('score', 'mean'),
        pass_rate=('pass', lambda x: x.mean() * 100)
    ).reset_index()
    summary.to_csv(f'{csv_dir}/{prefix}-summary_table.csv', index=False)

    # 2. asr_table — Attack Success Rate (S2)
    asr = summary.copy()
    asr['asr'] = 100 - asr['pass_rate']
    asr = asr[['model', 'prompt_label', 'pass_rate', 'asr', 'avg_score']]
    asr.to_csv(f'{csv_dir}/{prefix}-asr_table.csv', index=False)

    # 3. score_dist
    score_dist = df.groupby(['model', 'score']).size().unstack(fill_value=0)
    score_dist_pct = score_dist.div(score_dist.sum(axis=1), axis=0) * 100
    score_dist_pct.to_csv(f'{csv_dir}/{prefix}-score_dist.csv')

    # 4. tanda_perf
    tanda_perf = df.groupby(['tanda', 'model', 'prompt_label']).agg(
        success_rate=('pass', lambda x: x.mean() * 100)
    ).reset_index()
    tanda_perf.to_csv(f'{csv_dir}/{prefix}-tanda_perf.csv', index=False)

    # 5. latencia
    latencia = df.groupby(['model', 'prompt_label']).agg(
        avg_latency_ms=('latency', 'mean')
    ).reset_index()
    latencia.to_csv(f'{csv_dir}/{prefix}-latencia.csv', index=False)

    # 6. tanda_score_perf
    tanda_score_perf = df.groupby(['tanda', 'model', 'prompt_label']).agg(
        avg_score=('score', 'mean')
    ).reset_index()
    tanda_score_perf.to_csv(f'{csv_dir}/{prefix}-tanda_score_perf.csv', index=False)

    print(f"CSVs generados en '{csv_dir}/'")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python parser_promptfoo_csv_s2.py <archivo.json> <prefijo> [directorio_salida]")
        print("Ejemplo: python parser_promptfoo_csv_s2.py eval-S2-locals.json S2-locals results")
        sys.exit(1)

    file_path = sys.argv[1]
    prefix = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "."

    process_file(file_path, prefix, output_dir)