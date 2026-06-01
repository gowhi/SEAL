import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

# Configuración de nombres de modelos
MAPEO_MODELOS = {
    'gpt-oss-target': 'GPT-OSS',
    'llama': 'Llama',
    'mistral-target': 'Mistral',
    'qwen-coder-target': 'Qwen'
}

def generar_heatmap_calidad_e3(ruta_csv):
    print(f"--- Iniciando: Heatmap de Calidad/Integridad (E3) ---")
    if not os.path.exists(ruta_csv):
        print(f"❌ Error: No se encuentra {ruta_csv}")
        return

    mpl.rcParams.update({'font.family': 'sans-serif'})
    df = pd.read_csv(ruta_csv)
    df['model'] = df['model'].map(MAPEO_MODELOS)

    escenarios = ['Inductor', 'Estricto', 'Ultra']
    fig, axes = plt.subplots(1, 3, figsize=(38, 14), sharey=True)

    for i, esc in enumerate(escenarios):
        df_esc = df[df['prompt_label'] == esc]
        if df_esc.empty: continue

        pivot_df = df_esc.pivot(index='model', columns='tanda', values='avg_score')
        
        if i == 2:
            cbar_ax = fig.add_axes([0.94, 0.25, 0.03, 0.57]) 
            sns.heatmap(pivot_df, annot=True, fmt=".2f", cmap="YlGnBu", 
                        ax=axes[i], cbar=True, cbar_ax=cbar_ax, vmin=0, vmax=1,
                        square=False, annot_kws={"size": 22, "weight": "bold"}, linewidths=1.5)
            cbar_ax.tick_params(labelsize=25) 
            cbar_ax.set_ylabel('Puntuación Media (0-1)', fontsize=28, fontweight='bold', labelpad=20)
        else:
            sns.heatmap(pivot_df, annot=True, fmt=".2f", cmap="YlGnBu", 
                        ax=axes[i], cbar=False, vmin=0, vmax=1,
                        square=False, annot_kws={"size": 22, "weight": "bold"}, linewidths=1.5)
        
        axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        axes[i].set_title(f'CALIDAD: {esc.upper()}', fontsize=32, fontweight='bold', pad=40)
        axes[i].set_xlabel('Técnicas Adversarias (Tandas)', fontsize=30, labelpad=20)
        axes[i].tick_params(axis='x', labelsize=26)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=28, fontweight='bold', labelpad=80)
            axes[i].tick_params(axis='y', labelsize=24)

    # --- TÍTULO CON CURSIVA SEGURA ---
    # Usamos \it y escapamos el ampersand con \&
    # Para generar_heatmap_calidad_e3
    plt.suptitle(r'Evaluación de la Calidad Defensiva E3: $\mathit{Indirect\ Tool\ Injection\ &\ SDoS}$' + '\n' + 
             r'(Integridad de la Respuesta: Average Score por Técnica)', 
             fontsize=35, fontweight='bold', y=0.98)

    plt.subplots_adjust(left=0.22, top=0.82, wspace=0.15, right=0.92, bottom=0.25)
    
    if not os.path.exists('strategy3'): os.makedirs('strategy3')
    output_path = 'strategy3/heatmap_calidad_E3.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Heatmap de Calidad E3 guardado en: {output_path}")

def generar_heatmaps_resistencia_e3(ruta_csv):
    print(f"--- Iniciando: Heatmap de Resistencia (% Success Rate) E3 ---")
    if not os.path.exists(ruta_csv):
        print(f"❌ Error: No se encuentra {ruta_csv}")
        return

    mpl.rcParams.update({'font.family': 'sans-serif'})
    df = pd.read_csv(ruta_csv)
    df['model'] = df['model'].map(MAPEO_MODELOS)

    escenarios = ['Inductor', 'Estricto', 'Ultra']
    fig, axes = plt.subplots(1, 3, figsize=(38, 14), sharey=True)

    for i, esc in enumerate(escenarios):
        df_esc = df[df['prompt_label'] == esc]
        if df_esc.empty: continue
            
        pivot_df = df_esc.pivot(index='model', columns='tanda', values='success_rate')
        
        if i == 2:
            cbar_ax = fig.add_axes([0.94, 0.25, 0.03, 0.5]) 
            sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="RdYlGn", 
                        ax=axes[i], cbar=True, cbar_ax=cbar_ax, vmin=0, vmax=100,
                        square=False, annot_kws={"size": 22, "weight": "bold"}, linewidths=1.5)
            cbar_ax.tick_params(labelsize=25) 
            cbar_ax.set_ylabel('% Bloqueo Total', fontsize=28, fontweight='bold', labelpad=20)
        else:
            sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="RdYlGn", 
                        ax=axes[i], cbar=False, vmin=0, vmax=100,
                        square=False, annot_kws={"size": 22, "weight": "bold"}, linewidths=1.5)
        
        axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        axes[i].set_title(f'NIVEL: {esc.upper()}', fontsize=32, fontweight='bold', pad=40)
        axes[i].set_xlabel('Técnicas Adversarias (Tandas)', fontsize=30, labelpad=20)
        axes[i].tick_params(axis='x', labelsize=26)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=28, fontweight='bold', labelpad=80)
            axes[i].tick_params(axis='y', labelsize=24)

    # Para generar_heatmaps_resistencia_e3
    plt.suptitle(r'Mapa de Resistencia E3: $\mathit{Indirect\ Tool\ Injection\ &\ SDoS}$' + '\n' + 
             r'(% de Éxito en el Bloqueo Total por Técnica y Modelo)', 
             fontsize=35, fontweight='bold', y=0.98)
    
    plt.subplots_adjust(left=0.22, top=0.82, wspace=0.15, right=0.92, bottom=0.25)
    
    output_path = 'strategy3/heatmap_resistencia_E3_.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Heatmap de Resistencia E3 guardado en: {output_path}")

# --- EJECUCIÓN ---
if not os.path.exists('strategy3'): os.makedirs('strategy3')
generar_heatmap_calidad_e3('strategy3/tanda_score_perf_S3.csv')
generar_heatmaps_resistencia_e3('strategy3/tanda_perf_S3.csv')