import json
import pandas as pd
import os

# Archivos de entrada
files = ['strategy1/eval-3GI-2025-12-25T23_26_13.json', 'strategy1/eval-wP8-2025-12-23T16_29_33.json']
all_records = []

def get_prompt_label(prompt_text):
    """Clasifica el nivel de protección basado en el contenido del System Prompt."""
    if "SECURITY-CRITICAL" in prompt_text:
        return "Ultra"
    elif "Security-hardened" in prompt_text:
        return "Estricto"
    else:
        return "Inductor"

# Procesamiento de JSONs
for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Navegación por la estructura de promptfoo (body -> list -> outputs)
    body = data.get('body', [])
    for row in body:
        outputs = row.get('outputs', [])
        for out in outputs:
            provider = out.get('provider', 'unknown')
            score = out.get('score', 0)
            latency = out.get('latencyMs', 0)
            test_vars = out.get('testCase', {}).get('vars', {})
            tanda = test_vars.get('tanda', 'BASE')
            prompt = str(out.get('prompt', ''))
            
            all_records.append({
                'model': provider,
                'prompt_label': get_prompt_label(prompt),
                'score': score,
                'latency': latency,
                'tanda': tanda
            })

df = pd.DataFrame(all_records)

# 1. summary_table.csv: Rendimiento general por modelo y nivel de protección
summary = df.groupby(['model', 'prompt_label']).agg(
    avg_score=('score', 'mean'),
    pass_rate=('score', lambda x: (x >= 0.5).mean() * 100)
).reset_index()
summary.to_csv('strategy1/summary_table.csv', index=False)

# 2. score_dist.csv: Distribución de tipos de respuesta (Proporciones)
score_dist = df.groupby(['model', 'score']).size().unstack(fill_value=0)
score_dist_pct = score_dist.div(score_dist.sum(axis=1), axis=0) * 100
score_dist_pct.to_csv('strategy1/score_dist.csv')

# 3. tanda_perf.csv: Efectividad de cada técnica adversaria (Tandas de PyRIT)
tanda_perf = df.groupby(['tanda', 'model', 'prompt_label']).agg(
    success_rate=('score', lambda x: (x >= 0.5).mean() * 100)
).reset_index()
tanda_perf.to_csv('strategy1/tanda_perf.csv', index=False)

# 4. latencia.csv: Análisis de impacto en el rendimiento
latencia = df.groupby(['model', 'prompt_label']).agg(
    avg_latency_ms=('latency', 'mean')
).reset_index()
latencia.to_csv('strategy1/latencia.csv', index=False)

# 5. tanda_score_perf.csv: Calidad de la respuesta (promedio de score) por técnica
tanda_score_perf = df.groupby(['tanda', 'model', 'prompt_label']).agg(
    avg_score=('score', 'mean')
).reset_index()
tanda_score_perf.to_csv('strategy1/tanda_score_perf.csv', index=False)

print("Procesamiento completado. Los CSVs han sido generados.")