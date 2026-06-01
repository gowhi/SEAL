import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

def generar_heatmaps_por_escenario_tfm(ruta_csv):
    if not os.path.exists(ruta_csv):
        print(f"Error: No se encuentra el archivo en {ruta_csv}")
        return

    mpl.rcParams.update({'font.family': 'sans-serif'})

    df = pd.read_csv(ruta_csv)
    formated_names = {
        'gpt-oss-target': 'GPT-OSS',
        'llama': 'Llama',
        'mistral-target': 'Mistral',
        'qwen-coder-target': 'Qwen'
    }
    df['model'] = df['model'].map(formated_names)
    escenarios = ['Inductor', 'Estricto', 'Ultra']
    
    fig, axes = plt.subplots(1, 3, figsize=(38, 14), sharey=True)

    for i, esc in enumerate(escenarios):
        df_esc = df[df['prompt_label'] == esc]
        pivot_df = df_esc.pivot(index='model', columns='tanda', values='success_rate')
        
        if i == 2:
            # --- BLOQUE DE LA BARRA DE COLOR (GRANDE Y ANCHA) ---
            # [distancia_izquierda, distancia_inferior, ancho, alto]
            # Aumentamos el ancho a 0.03 y el alto a 0.5 para que destaque
            cbar_ax = fig.add_axes([0.94, 0.25, 0.01, 0.57]) 
            
            sns.heatmap(
                pivot_df, annot=True, fmt=".1f", cmap="RdYlGn", 
                ax=axes[i], cbar=True, cbar_ax=cbar_ax, vmin=0, vmax=100, 
                square=False, 
                annot_kws={"size": 22, "weight": "bold"}, 
                linewidths=1.5
            )
            # Números de la escala (0, 20, 40...)
            cbar_ax.tick_params(labelsize=25) 
            # Título vertical de la escala
            cbar_ax.set_ylabel('% Bloqueo Total', fontsize=28, fontweight='bold', labelpad=20)
        else:
            sns.heatmap(
                pivot_df, annot=True, fmt=".1f", cmap="RdYlGn", 
                ax=axes[i], cbar=False, vmin=0, vmax=100, 
                square=False, 
                annot_kws={"size": 22, "weight": "bold"}, 
                linewidths=1.5
            )
        
        # Ajustes de etiquetas de los ejes (sin cambios)
        axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        axes[i].set_title(f'ESCENARIO: {esc.upper()}', fontsize=30, fontweight='bold', pad=40)
        axes[i].set_xlabel('Técnicas de Ataque', fontsize=30, labelpad=20)
        axes[i].tick_params(axis='x', labelsize=26)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=28, fontweight='bold', labelpad=80)
            axes[i].tick_params(axis='y', labelsize=24)
        else:
            axes[i].set_ylabel('')

    plt.suptitle(r'Mapa de Resistencia E1: $\mathit{Tool\ Injection}$' + '\n' + 
                 r'(% de Éxito en el Bloqueo Total por Técnica y Modelo)', 
                 fontsize=35, fontweight='bold', y=0.98)

    plt.subplots_adjust(left=0.22, top=0.82, wspace=0.15, right=0.92, bottom=0.25)

    output_path = 'strategy1/heatmap_comparativo_escenarios_final.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Heatmap generado con la escala de color corregida en: {output_path}")

generar_heatmaps_por_escenario_tfm('strategy1/tanda_perf.csv')