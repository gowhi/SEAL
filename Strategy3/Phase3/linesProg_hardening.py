import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def generar_grafico_progresion_s3(ruta_summary, carpeta_salida='strategy3'):
    if not os.path.exists(ruta_summary):
        print(f"Error: No se encuentra el archivo {ruta_summary}")
        return

    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # 1. Cargar el CSV resumen de Estrategia 3
    df = pd.read_csv(ruta_summary)

    # 2. Mapeo de nombres para el TFM
    formated_names = {
        'gpt-oss-target': 'GPT-OSS (20B)', 
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5 Coder'
    }
    df['model'] = df['model'].map(formated_names)

    # 3. ORDENAR LOS NIVELES (Inductor -> Estricto -> Ultra)
    orden_hardening = ['Inductor', 'Estricto', 'Ultra']
    df['prompt_label'] = pd.Categorical(df['prompt_label'], categories=orden_hardening, ordered=True)
    df = df.sort_values('prompt_label')

    # 4. Crear el gráfico de líneas
    plt.figure(figsize=(11, 7))
    sns.set_style("whitegrid")

    # Dibujamos las líneas de tendencia
    # Aquí 'pass_rate' representa la Tasa de Disponibilidad Real
    line_plot = sns.lineplot(
        data=df, 
        x='prompt_label', 
        y='pass_rate', 
        hue='model', 
        marker='o',      
        linewidth=3.5,     
        markersize=11    
    )

    # 5. Personalización estética
    plt.title('Efectividad del Hardening: Evolución de la Disponibilidad Semántica (S3)', fontsize=16, fontweight='bold', pad=25)
    plt.xlabel('Nivel de Restricción del System Prompt', fontsize=12)
    plt.ylabel('Tasa de Disponibilidad Real (Resumen Exitoso %)', fontsize=12)
    
    # Ajustamos el límite para ver claramente el 0% de Llama y el 100% de Qwen
    plt.ylim(-5, 105) 

    plt.legend(title='Modelos', bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False)
    plt.tight_layout()

    # 6. Guardar la imagen en la carpeta de estrategia 3
    output_path = os.path.join(carpeta_salida, 'hardening_trend_S3.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico de tendencia S3 generado en: {output_path}")

# Ejecución
generar_grafico_progresion_s3('strategy3/summary_table_S3.csv')