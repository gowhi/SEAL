import json
import pandas as pd
import os

# Archivo de entrada de la Estrategia 2
files = ['eval-Mvb-2026-01-02T00_26_29.json']
output_dir = 'strategy2'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

all_records = []

# Procesamiento de JSON
for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    prompts_meta = data.get('head', {}).get('prompts', [])
    body = data.get('body', [])
    
    for row in body:
        outputs = row.get('outputs', [])
        for out_idx, out in enumerate(outputs):
            # Identificación de modelo y prompt por el índice de la cabecera
            p_info = prompts_meta[out_idx]
            p_label = p_info.get('label', 'unknown').capitalize()
            p_model = p_info.get('provider', 'unknown')
            
            # Datos de evaluación
            grading = out.get('gradingResult', {})
            score = grading.get('score', 0)
            is_pass = grading.get('pass', False)
            latency = out.get('latencyMs', 0)
            
            # Variables de ataque (Tanda de PyRIT)
            test_vars = out.get('testCase', {}).get('vars', {})
            tanda = test_vars.get('tanda', 'BASE')
            
            all_records.append({
                'model': p_model,
                'prompt_label': p_label,
                'score': score,
                'pass': 1 if is_pass else 0,
                'latency': latency,
                'tanda': tanda
            })

df = pd.DataFrame(all_records)

# --- GENERACIÓN DE LOS 5 REPORTES ---

# 1. Rendimiento general (Radar)
summary = df.groupby(['model', 'prompt_label']).agg(
    avg_score=('score', 'mean'),
    pass_rate=('pass', lambda x: x.mean() * 100)
).reset_index()
summary.to_csv(f'{output_dir}/summary_table.csv', index=False)

# 2. Distribución de severidad
score_dist = df.groupby(['model', 'score']).size().unstack(fill_value=0)
score_dist_pct = score_dist.div(score_dist.sum(axis=1), axis=0) * 100
score_dist_pct.to_csv(f'{output_dir}/score_dist.csv')

# 3. Tasa de éxito por técnica (Tanda)
tanda_perf = df.groupby(['tanda', 'model', 'prompt_label']).agg(
    success_rate=('pass', lambda x: x.mean() * 100)
).reset_index()
tanda_perf.to_csv(f'{output_dir}/tanda_perf.csv', index=False)

# 4. ANÁLISIS DE LATENCIA (Nuevo)
latencia = df.groupby(['model', 'prompt_label']).agg(
    avg_latency_ms=('latency', 'mean')
).reset_index()
latencia.to_csv(f'{output_dir}/latencia.csv', index=False)

# 5. CALIDAD POR TÉCNICA (Nuevo)
tanda_score_perf = df.groupby(['tanda', 'model', 'prompt_label']).agg(
    avg_score=('score', 'mean')
).reset_index()
tanda_score_perf.to_csv(f'{output_dir}/tanda_score_perf.csv', index=False)

print(f"Los 5 CSVs de la Estrategia 2 han sido generados en '{output_dir}/'")