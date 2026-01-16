import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def generar_heatmap_calidad_scores(ruta_csv):
    if not os.path.exists(ruta_csv):
        print(f"Error: No se encuentra el archivo en {ruta_csv}")
        return

    # 1. Cargar datos
    df = pd.read_csv(ruta_csv)
    
    # Mapeo de nombres para consistencia en el TFM
    formated_names = {
       'gpt-oss-target': 'GPT-OSS (20B)',
        'llama': 'Llama 3.2',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df['model'] = df['model'].map(formated_names)

    # 2. Configurar la figura (Triple Heatmap para ver la evolución de la calidad)
    escenarios = ['Inductor', 'Estricto', 'Ultra']
    fig, axes = plt.subplots(1, 3, figsize=(24, 8), sharey=True)

    for i, esc in enumerate(escenarios):
        # Filtrar por escenario
        df_esc = df[df['prompt_label'] == esc]
        
        # Pivotar: Filas=Modelos, Columnas=Técnicas, Valores=AVG_SCORE
        pivot_df = df_esc.pivot(index='model', columns='tanda', values='avg_score')
        
        # Dibujar Heatmap (Cmap YlGnBu es excelente para representar 'calidad')
        sns.heatmap(pivot_df, annot=True, fmt=".2f", cmap="YlGnBu", 
                    ax=axes[i], cbar=(i == 2), vmin=0, vmax=1,
                    linewidths=.5)
        
        axes[i].set_title(f'CALIDAD: {esc.upper()}', fontsize=15, fontweight='bold')
        axes[i].set_xlabel('Técnicas de Ataque', fontsize=10)
        axes[i].tick_params(axis='x', rotation=45)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=12, fontweight='bold')
        else:
            axes[i].set_ylabel('')

    # 3. Estética y Guardado
    plt.suptitle('Integridad de la Respuesta Defensiva (Average Score por Técnica)', 
                 fontsize=20, fontweight='bold', y=1.05)
    plt.tight_layout()
    
    output_path = 'strategy1/heatmap_calidad_scores.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Mapa B (Calidad) guardado en: {output_path}")

# Ejecución
generar_heatmap_calidad_scores('strategy1/tanda_score_perf.csv')