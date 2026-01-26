import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

def generar_heatmap_calidad_scores(ruta_csv):
    if not os.path.exists(ruta_csv):
        print(f"Error: No se encuentra el archivo en {ruta_csv}")
        return

    # 1. Configuración de fuentes (idéntica al gráfico de resistencia)
    mpl.rcParams.update({'font.family': 'sans-serif'})

    # 2. Cargar datos
    df = pd.read_csv(ruta_csv)
    formated_names = {
        'gpt-oss-target': 'GPT-OSS',
        'llama': 'Llama',
        'mistral-target': 'Mistral',
        'qwen-coder-target': 'Qwen'
    }
    df['model'] = df['model'].map(formated_names)

    # 3. Configurar la figura (Triple Heatmap)
    # Usamos las mismas dimensiones (38, 14) para que en el TFM tengan el mismo tamaño
    escenarios = ['Inductor', 'Estricto', 'Ultra']
    fig, axes = plt.subplots(1, 3, figsize=(38, 14), sharey=True)

    for i, esc in enumerate(escenarios):
        df_esc = df[df['prompt_label'] == esc]
        pivot_df = df_esc.pivot(index='model', columns='tanda', values='avg_score')
        
        if i == 2:
            # Barra de color ancha y grande (coordenadas actualizadas para este gráfico)
            cbar_ax = fig.add_axes([0.94, 0.25, 0.03, 0.57]) 
            sns.heatmap(
                pivot_df, annot=True, fmt=".2f", cmap="YlGnBu", 
                ax=axes[i], cbar=True, cbar_ax=cbar_ax, vmin=0, vmax=1,
                square=False,
                annot_kws={"size": 22, "weight": "bold"}, 
                linewidths=1.5
            )
            cbar_ax.tick_params(labelsize=25) 
            cbar_ax.set_ylabel('Puntuación Media (0-1)', fontsize=28, fontweight='bold', labelpad=20)
        else:
            sns.heatmap(
                pivot_df, annot=True, fmt=".2f", cmap="YlGnBu", 
                ax=axes[i], cbar=False, vmin=0, vmax=1,
                square=False,
                annot_kws={"size": 22, "weight": "bold"}, 
                linewidths=1.5
            )
        
        # Ajustes de etiquetas (Iguales al gráfico anterior para simetría)
        axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        axes[i].set_title(f'CALIDAD: {esc.upper()}', fontsize=32, fontweight='bold', pad=40)
        axes[i].set_xlabel('Técnicas de Ataque', fontsize=30, labelpad=20)
        axes[i].tick_params(axis='x', labelsize=26)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=28, fontweight='bold', labelpad=80)
            axes[i].tick_params(axis='y', labelsize=24)
        else:
            axes[i].set_ylabel('')

    # 4. Título Principal (LaTeX corregido y más formal)
    plt.suptitle(r'Evaluación de la Calidad Defensiva E1: $\mathit{Tool\ Injection}$' + '\n' + 
                 r'(Integridad de la Respuesta: $\mathit{Average\ Score}$ por Técnica)', 
                 fontsize=40, fontweight='bold', y=0.98)

    # 5. Ajuste de márgenes (Idéntico para que los heatmaps midan lo mismo en píxeles)
    plt.subplots_adjust(left=0.22, top=0.82, wspace=0.15, right=0.92, bottom=0.25)

    output_path = 'strategy1/heatmap_calidad_scores.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Mapa de Calidad (Scores) generado con éxito en: {output_path}")

# Ejecución
generar_heatmap_calidad_scores('strategy1/tanda_score_perf.csv')