import pandas as pd
import matplotlib.pyplot as plt
from math import pi
import os

def generar_radares_estrategia2(ruta_csv, carpeta_salida='strategy2'):
    if not os.path.exists(ruta_csv):
        print(f"Error: No se encuentra el archivo {ruta_csv}")
        return
    
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    # 1. Carga y limpieza
    df = pd.read_csv(ruta_csv)
    
    # Forzamos el orden de las etiquetas para que el radar sea coherente
    label_order = ['Inductor', 'Estricto', 'Ultra']
    df['prompt_label'] = pd.Categorical(df['prompt_label'], categories=label_order, ordered=True)
    
    # Pivotamos los datos
    df_pivot = df.pivot(index='model', columns='prompt_label', values=['pass_rate', 'avg_score'])
    
    # 2. Configuración del Radar
    categories = ['Pass Rate (Ind)', 'Pass Rate (Str)', 'Pass Rate (Ult)', 
                  'Score (Ult)', 'Score (Str)', 'Score (Ind)']

    modelos = df_pivot.index.tolist()
    n_categories = len(categories)
    angles = [i / float(n_categories) * 2 * pi for i in range(n_categories)]
    angles += angles[:1]

    colours = {
        'gpt-oss-target': "#43b7ff",     # Azul (MoE)
        'llama': "#faa16a",              # Naranja (Denso 3B)
        'mistral-target': "#9aff8d",     # Verde (Denso 7B)
        'qwen-coder-target': "#ef8ffc"   # Rosa (Coder 7B)
    }

    formated_names = {
        'gpt-oss-target': 'GPT-4o (OSS Target)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B-v0.3',
        'qwen-coder-target': 'Qwen 2.5 Coder'
    }

    # 3. Función de dibujo
    def draw_radar(ax, model_name, color):
        try:
            row = df_pivot.loc[model_name]
            # Mapeo: Derecha = Bloqueo total (ASR), Izquierda = Calidad (Score)
            values = [ 
                row[('pass_rate', 'Inductor')] / 100, 
                row[('pass_rate', 'Estricto')] / 100, 
                row[('pass_rate', 'Ultra')] / 100,    
                row[('avg_score', 'Ultra')],          
                row[('avg_score', 'Estricto')],       
                row[('avg_score', 'Inductor')]        
            ]
            values += values[:1]

            ax.plot(angles, values, linewidth=2, linestyle='solid', color=color)
            ax.fill(angles, values, color=color, alpha=0.3)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=8, fontweight='bold')
            ax.set_ylim(0, 1.1)
            
            display_name = formated_names.get(model_name, model_name.upper())
            ax.set_title(f"{display_name}", size=12, pad=20, color=color, fontweight='bold')
        except KeyError as e:
            print(f"Error procesando modelo {model_name}: Faltan datos de etiquetas.")

    # 4. Generación del gráfico
    fig, axes = plt.subplots(2, 2, figsize=(13, 13), subplot_kw=dict(polar=True))
    axes = axes.flatten()

    for i, modelo in enumerate(modelos):
        color_actual = colours.get(modelo, '#7f7f7f')
        draw_radar(axes[i], modelo, color_actual)

    plt.suptitle("Estrategia 2: Exfiltración de Secretos (Confidencialidad)\nAnálisis de Robustez Agéntica y Calidad de Respuesta", 
                 fontsize=18, fontweight='bold', y=1.02)
    
    plt.tight_layout(pad=3.0)
    output_path = f'{carpeta_salida}/radar_comparativo_E2.png'
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    print(f"Gráfico de radar guardado en: {output_path}")

# Ejecución
generar_radares_estrategia2('strategy2/summary_table.csv')