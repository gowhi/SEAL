import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def generar_heatmaps_resistencia_e2(ruta_csv):
    # Forzamos a Python a encontrar la ruta relativa correcta
    if not os.path.exists(ruta_csv):
        print(f"❌ Error: No se encuentra el archivo en {ruta_csv}")
        print(f"Directorio actual: {os.getcwd()}")
        return

    # 1. Cargar y formatear datos
    df = pd.read_csv(ruta_csv)
    
    # Formateo de nombres para el TFM
    formated_names = {
        'gpt-oss-target': 'GPT-4o (20B)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df['model'] = df['model'].map(formated_names)

    # 2. Configurar la figura
    escenarios = ['Inductor', 'Estricto', 'Ultra']
    fig, axes = plt.subplots(1, 3, figsize=(26, 9), sharey=True)

    for i, esc in enumerate(escenarios):
        # Filtrar por escenario
        df_esc = df[df['prompt_label'] == esc]
        
        if df_esc.empty:
            print(f"⚠️ Aviso: No hay datos para el escenario {esc}")
            continue
            
        # Pivotar: Filas=Modelos, Columnas=Técnicas
        pivot_df = df_esc.pivot(index='model', columns='tanda', values='success_rate')
        
        # Dibujar Heatmap (Rojo -> Verde)
        sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="RdYlGn", 
                    ax=axes[i], cbar=(i == 2), vmin=0, vmax=100,
                    linewidths=.5, annot_kws={"size": 10, "weight": "bold"})
        
        axes[i].set_title(f'NIVEL: {esc.upper()}', fontsize=18, fontweight='bold', pad=20)
        axes[i].set_xlabel('Técnicas Adversarias (Tandas)', fontsize=12)
        axes[i].tick_params(axis='x', rotation=45)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=14, fontweight='bold')
        else:
            axes[i].set_ylabel('')

    # 3. Estética final
    plt.suptitle('E2: Mapa de Resistencia a la Exfiltración de Secretos\n(% de Éxito en Bloqueo Total por Técnica y Modelo)', 
                 fontsize=24, fontweight='bold', y=1.08)
    
    plt.tight_layout()
    
    # 4. Guardar el resultado
    output_path = 'strategy2/heatmap_resistencia_E2.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ ¡Éxito! Heatmap Triple guardado en: {output_path}")

# EJECUCIÓN: Usamos la ruta que muestra tu comando 'tree'
generar_heatmaps_resistencia_e2('strategy2/tanda_perf.csv')