import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def generar_heatmaps_por_escenario(ruta_csv):
    if not os.path.exists(ruta_csv):
        print(f"Error: No se encuentra el archivo en {ruta_csv}")
        return

    # 1. Cargar y formatear datos
    df = pd.read_csv(ruta_csv)
    formated_names = {
        'gpt-oss-target': 'GPT-OSS (20B)',
        'llama': 'Llama 3.2',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df['model'] = df['model'].map(formated_names)

    # 2. Definir los escenarios y el orden
    escenarios = ['Inductor', 'Estricto', 'Ultra']
    
    # Creamos una figura con 3 subplots (1 fila, 3 columnas)
    fig, axes = plt.subplots(1, 3, figsize=(24, 8), sharey=True)

    for i, esc in enumerate(escenarios):
        # Filtrar datos por escenario
        df_esc = df[df['prompt_label'] == esc]
        
        # Pivotar: Filas=Modelos, Columnas=Técnicas
        pivot_df = df_esc.pivot(index='model', columns='tanda', values='success_rate')
        
        # Dibujar Heatmap en el subplot correspondiente
        sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="RdYlGn", 
                    ax=axes[i], cbar=(i == 2), vmin=0, vmax=100,
                    linewidths=.5)
        
        axes[i].set_title(f'ESCENARIO: {esc.upper()}', fontsize=15, fontweight='bold')
        axes[i].set_xlabel('Técnicas de Ataque', fontsize=10)
        axes[i].tick_params(axis='x', rotation=45)
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=12, fontweight='bold')
        else:
            axes[i].set_ylabel('')

    # 3. Ajuste final y guardado
    plt.suptitle('Evolución de la Resistencia por Escenario de Hardening', fontsize=20, fontweight='bold', y=1.05)
    plt.tight_layout()
    
    output_path = 'strategy1/heatmap_comparativo_escenarios.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Heatmap triple guardado en: {output_path}")

# Ejecución
generar_heatmaps_por_escenario('strategy1/tanda_perf.csv')