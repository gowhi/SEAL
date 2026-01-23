import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- HEATMAP DE CALIDAD/INTEGRIDAD PARA E3 ---
def generar_heatmap_calidad_e3(ruta_csv):
    print(f"--- Iniciando: Heatmap de Calidad/Integridad (E3) ---")
    
    if not os.path.exists(ruta_csv):
        print(f"❌ Error: No se encuentra el archivo en {ruta_csv}")
        return

    df = pd.read_csv(ruta_csv)
    print(f"✅ Archivo cargado correctamente.")
    
    # Mapear nombres de modelos
    formated_names = {
        'gpt-oss-target': 'GPT-OSS (20B)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df['model'] = df['model'].map(formated_names)

    # Escenarios de prompt
    escenarios = ['Inductor', 'Estricto', 'Ultra']
    fig, axes = plt.subplots(1, 3, figsize=(24, 8), sharey=True)

    for i, esc in enumerate(escenarios):
        df_esc = df[df['prompt_label'] == esc]
        if df_esc.empty:
            print(f"⚠️ No hay datos para el escenario {esc}")
            continue

        pivot_df = df_esc.pivot(index='model', columns='tanda', values='avg_score')
        sns.heatmap(pivot_df, annot=True, fmt=".2f", cmap="YlGnBu",
                    ax=axes[i], cbar=(i == 2), vmin=0, vmax=1,
                    linewidths=.5, annot_kws={"size": 9, "weight": "bold"})
        
        axes[i].set_title(f'PROTECCIÓN: {esc.upper()}', fontsize=16, fontweight='bold', pad=15)
        axes[i].set_xlabel('Técnicas Adversarias (Tandas)', fontsize=11)
        axes[i].tick_params(axis='x', rotation=45)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=12, fontweight='bold')
        else:
            axes[i].set_ylabel('')

    plt.suptitle('E3: Calidad de Respuesta frente a Inyección Indirecta y SDoS\n(1.0 = Bloqueo Perfecto / 0.0 = Ejecución Inadecuada)',
                 fontsize=22, fontweight='bold', y=1.08)
    
    plt.tight_layout()
    
    if not os.path.exists('strategy3'):
        os.makedirs('strategy3')
        
    output_path = 'strategy3/heatmap_calidad_E3.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Heatmap de Calidad E3 guardado en: {output_path}")


# --- HEATMAP DE RESISTENCIA (Success Rate) PARA E3 ---
def generar_heatmaps_resistencia_e3(ruta_csv):
    print(f"--- Iniciando: Heatmap de Resistencia (% Success Rate) E3 ---")
    
    if not os.path.exists(ruta_csv):
        print(f"❌ Error: No se encuentra el archivo en {ruta_csv}")
        return

    df = pd.read_csv(ruta_csv)
    print(f"✅ Archivo '{ruta_csv}' cargado con éxito.")
    
    formated_names = {
        'gpt-oss-target': 'GPT-OSS (20B)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df['model'] = df['model'].map(formated_names)

    escenarios = ['Inductor', 'Estricto', 'Ultra']
    fig, axes = plt.subplots(1, 3, figsize=(26, 9), sharey=True)

    for i, esc in enumerate(escenarios):
        df_esc = df[df['prompt_label'] == esc]
        if df_esc.empty:
            print(f"⚠️ No hay datos para el escenario {esc}")
            continue
            
        pivot_df = df_esc.pivot(index='model', columns='tanda', values='success_rate')
        sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="RdYlGn",
                    ax=axes[i], cbar=(i==2), vmin=0, vmax=100,
                    linewidths=.5, annot_kws={"size": 10, "weight": "bold"})
        
        axes[i].set_title(f'NIVEL: {esc.upper()}', fontsize=18, fontweight='bold', pad=20)
        axes[i].set_xlabel('Técnicas Adversarias (Tandas)', fontsize=12)
        axes[i].tick_params(axis='x', rotation=45)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=14, fontweight='bold')
        else:
            axes[i].set_ylabel('')

    plt.suptitle('E3: Resistencia frente a Inyección Indirecta y SDoS\n(% Éxito en Bloqueo/Detección por Técnica y Modelo)',
                 fontsize=24, fontweight='bold', y=1.08)
    
    plt.tight_layout()
    
    if not os.path.exists('strategy3'):
        os.makedirs('strategy3')
        
    output_path = 'strategy3/heatmap_resistencia_E3.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Heatmap de Resistencia E3 guardado en: {output_path}")


# --- EJECUCIÓN ---
generar_heatmap_calidad_e3('strategy3/tanda_score_perf_S3.csv')
generar_heatmaps_resistencia_e3('strategy3/tanda_perf_S3.csv')
