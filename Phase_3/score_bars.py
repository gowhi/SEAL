import pandas as pd
import matplotlib.pyplot as plt
import os

def generar_distribucion_severidad(ruta_csv):
    if not os.path.exists(ruta_csv):
        print(f"Error: No se encuentra el archivo en {ruta_csv}")
        return

    # 1. Cargar datos (Ya están en formato ancho: model, 0.0, 0.4, 0.5...)
    df = pd.read_csv(ruta_csv)
    df.set_index('model', inplace=True)
    
    # 2. Mapeo de nombres para el TFM
    formated_names = {
        'gpt-oss-target': 'GPT-4o (OSS Target)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B-v0.3',
        'qwen-coder-target': 'Qwen 2.5 Coder'
    }
    df.index = df.index.map(formated_names)

    # 3. Definir colores para cada columna de score
    # Usamos una paleta de Rojo (Peligro) a Verde (Seguro)
    colores_map = {
        '0.0': '#e74c3c',  # Rojo (Bypass total)
        '0.4': '#e67e22',  # Naranja oscuro
        '0.5': '#f1c40f',  # Amarillo
        '0.6': '#f39c12',  # Naranja
        '0.9': '#a9dfbf',  # Verde claro
        '1.0': '#27ae60'   # Verde oscuro (Bloqueo perfecto)
    }
    
    # Seleccionamos solo los colores de las columnas que existen en el CSV
    colors_to_use = [colores_map.get(col, '#95a5a6') for col in df.columns]

    # 4. Crear el gráfico de barras apiladas
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Como tus datos ya suman ~100 (son porcentajes), graficamos directo
    df.plot(kind='bar', 
            stacked=True, 
            color=colors_to_use, 
            ax=ax, 
            width=0.7, 
            edgecolor='white', 
            linewidth=0.5)

    # 5. Estética profesional
    ax.set_title('Distribución de Severidad de Fallos (Security Scores)', fontsize=15, fontweight='bold', pad=20)
    ax.set_ylabel('Porcentaje de Evaluaciones (%)', fontsize=12)
    ax.set_xlabel('Modelos Evaluados', fontsize=12)
    ax.set_ylim(0, 100)
    
    # Leyenda explicativa
    legend_labels = {
        '0.0': 'Bypass Total (Crítico)',
        '0.4': 'Riesgo Alto',
        '0.5': 'Riesgo Medio (Inseguro)',
        '0.6': 'Riesgo Bajo',
        '0.9': 'Casi Seguro',
        '1.0': 'Bloqueo Exitoso (Safe)'
    }
    handles, labels = ax.get_legend_handles_labels()
    new_labels = [legend_labels.get(l, f"Score {l}") for l in labels]
    
    ax.legend(handles, new_labels, title="Interpretación del Score", 
              bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False)

    plt.xticks(rotation=0) # Nombres de modelos en horizontal
    plt.tight_layout()
    
    # 6. Guardar
    output_path = 'strategy1/distribucion_severidad.png'
    plt.savefig(output_path, dpi=300)
    print(f"Gráfico de severidad generado con éxito en: {output_path}")

# Ejecución
generar_distribucion_severidad('strategy1/score_dist.csv')