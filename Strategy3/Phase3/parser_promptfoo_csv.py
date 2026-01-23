import json
import pandas as pd
import os

# --- 1. CONFIGURACIÓN DE RUTAS ---
output_dir = 'strategy3'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"📁 Carpeta '{output_dir}' creada.")

# Archivo de entrada
file_path = 'eval-KU3-2026-01-04T21_54_10.json' 
all_records = []

def get_prompt_label(prompt_text):
    if not prompt_text: return "Otros"
    pt = str(prompt_text).lower()
    if "architecture rules" in pt or "security-hardened summarization" in pt:
        return "Ultra"
    elif "secure summarization assistant" in pt:
        return "Estricto"
    elif "professional summarization assistant" in pt:
        return "Inductor"
    else:
        return "Otros"

# --- 2. PROCESAMIENTO ---
if not os.path.exists(file_path):
    print(f"❌ Error: El archivo {file_path} no existe.")
else:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    body = data.get('body', [])
    for row in body:
        outputs = row.get('outputs', [])
        for out in outputs:
            test_vars = out.get('testCase', {}).get('vars', {})
            if isinstance(test_vars, list):
                tanda = test_vars[1] if len(test_vars) > 1 else "BASE"
            else:
                tanda = test_vars.get('tanda', 'BASE')
            
            provider = out.get('provider', 'unknown')
            score = out.get('score', 0)
            latency = out.get('latencyMs', 0)
            
            prompt_content = out.get('prompt', '')
            prompt_text = prompt_content.get('raw', '') if isinstance(prompt_content, dict) else str(prompt_content)
            
            all_records.append({
                'model': provider,
                'prompt_label': get_prompt_label(prompt_text),
                'score': score,
                'latency': latency,
                'tanda': tanda
            })

    if all_records:
        df = pd.DataFrame(all_records)
        
        # --- Crear columna 'pass' para indicar éxito ---
        df['pass'] = df['score'] == 1.0
        
        # --- 3. EXPORTACIÓN A CSV CON RUTA DINÁMICA ---
        summary = df.groupby(['model', 'prompt_label']).agg(
            avg_score=('score', 'mean'),
            pass_rate=('pass', lambda x: x.mean() * 100)  # usar 'pass' aquí
        ).reset_index()
        summary.to_csv(os.path.join(output_dir, 'summary_table_S3.csv'), index=False)
        
        score_dist = df.groupby(['model', 'score']).size().unstack(fill_value=0)
        score_dist_pct = score_dist.div(score_dist.sum(axis=1), axis=0) * 100
        score_dist_pct.to_csv(os.path.join(output_dir, 'score_dist_S3.csv'))
        
        # --- Tasa de éxito por técnica (Tanda) ---
        tanda_perf = df.groupby(['tanda', 'model', 'prompt_label']).agg(
            success_rate=('pass', lambda x: x.mean() * 100)
        ).reset_index()
        tanda_perf.to_csv(os.path.join(output_dir, 'tanda_perf_S3.csv'), index=False)
        
        # --- Calidad por técnica (Tanda) ---
        tanda_score_perf = df.groupby(['tanda', 'model', 'prompt_label']).agg(
            avg_score=('score', 'mean')
        ).reset_index()
        tanda_score_perf.to_csv(os.path.join(output_dir, 'tanda_score_perf_S3.csv'), index=False)
        
        # --- Latencia promedio ---
        latencia = df.groupby(['model', 'prompt_label']).agg(
            avg_latency_ms=('latency', 'mean')
        ).reset_index()
        latencia.to_csv(os.path.join(output_dir, 'latencia_S3.csv'), index=False)
        
        print(f"\n✅ Procesamiento completado. Los CSVs se han guardado en: {output_dir}/")
        print(summary)
