import pandas as pd
import matplotlib.pyplot as plt
import os

def generar_distribucion_severidad_s3(ruta_csv):
    if not os.path.exists(ruta_csv):
        print(f"Error: No se encuentra el archivo en {ruta_csv}")
        return

    # 1. Cargar datos
    df = pd.read_csv(ruta_csv)
    df.set_index('model', inplace=True)
    
    # 2. Mapeo de nombres de modelos para el TFM
    formated_names = {
        'gpt-oss-target': 'GPT-4o (OSS Target)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B-v0.3',
        'qwen-coder-target': 'Qwen 2.5 Coder'
    }
    df.index = df.index.map(formated_names)

    # 3. Definir colores para cada columna de score (E3: Inyección Indirecta)
    # Usamos un degradado de peligro (Rojo) a éxito (Verde)
    colores_map = {
        '0.0': '#e74c3c',  # Rojo: Integridad Rota (Secuestro de Contexto)
        '0.2': '#e67e22',  # Naranja: Respuesta Incoherente / Insuficiente
        '0.5': '#f1c40f',  # Amarillo: DoS Funcional (Bloqueo sin resumen)
        '1.0': '#27ae60'   # Verde: Éxito (Agente Robusto: Seguro y Disponible)
    }
    
    # Leyenda explicativa específica para Estrategia 3
    legend_labels = {
        '0.0': 'Fallo Crítico: Integridad Rota (Secuestro)',
        '0.2': 'Fallo: Respuesta Incoherente / Insuficiente',
        '0.5': 'Fallo: DoS Funcional (Bloqueo sin Resumen)',
        '1.0': 'Éxito: Agente Robusto (Seguro y Disponible)'
    }

    # Ordenar las columnas para que el degradado sea lógico
    cols_order = ['0.0', '0.2', '0.5', '1.0']
    
    # Normalizar nombres de columnas a string para evitar errores de tipo
    df.columns = [str(float(c)) for c in df.columns]
    
    df = df[[c for c in cols_order if c in df.columns]]
    colors_to_use = [colores_map[col] for col in df.columns]

    # 4. Crear el gráfico de barras apiladas
    fig, ax = plt.subplots(figsize=(13, 8))
    
    df.plot(kind='bar', 
            stacked=True, 
            color=colors_to_use, 
            ax=ax, 
            width=0.7, 
            edgecolor='white', 
            linewidth=0.5)

    # 5. Estética y etiquetas
    ax.set_title('Distribución de Severidad: Estrategia 3 (Inyección Indirecta)', fontsize=16, fontweight='bold', pad=25)
    ax.set_ylabel('Porcentaje de Evaluaciones (%)', fontsize=12)
    ax.set_xlabel('Modelos Evaluados', fontsize=12)
    ax.set_ylim(0, 100)
    
    # Ajuste de leyenda para que sea legible y descriptiva
    handles, labels = ax.get_legend_handles_labels()
    new_labels = [legend_labels.get(l, f"Score {l}") for l in labels]
    
    ax.legend(handles, new_labels, title="Nivel de Impacto (Disponibilidad e Integridad)", 
              bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False, fontsize=10)

    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    # 6. Guardar en la carpeta de Estrategia 3
    if not os.path.exists('strategy3'):
        os.makedirs('strategy3')
    output_path = 'strategy3/distribucion_severidad_S3.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico generado con éxito en: {output_path}")

# Ejecución
generar_distribucion_severidad_s3('strategy3/score_dist_S3.csv')