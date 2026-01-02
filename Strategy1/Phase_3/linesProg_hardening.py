import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def generar_grafico_progresion(ruta_summary):
    # 1. Cargar el CSV resumen
    df = pd.read_csv(ruta_summary)

    # 2. Mapeo de nombres para el TFM
    formated_names = {
        'gpt-oss-target': 'GPT-4o',
        'llama': 'Llama 3.2',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df['model'] = df['model'].map(formated_names)

    # 3. ORDENAR LOS NIVELES: Muy importante para que la línea tenga sentido
    # Definimos el orden lógico del hardening
    orden_hardening = ['Inductor', 'Estricto', 'Ultra']
    df['prompt_label'] = pd.Categorical(df['prompt_label'], categories=orden_hardening, ordered=True)
    df = df.sort_values('prompt_label')

    # 4. Crear el gráfico de líneas
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")

    # Dibujamos las líneas (una por modelo)
    line_plot = sns.lineplot(
        data=df, 
        x='prompt_label', 
        y='pass_rate', 
        hue='model', 
        marker='o',      # Añade puntos en cada nivel
        linewidth=3,     # Línea gruesa para que se vea bien
        markersize=10    # Puntos grandes
    )

    # 5. Personalización estética
    plt.title('Tendencia de Hardening: Evolución de la Seguridad', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Nivel de Restricción del System Prompt', fontsize=12)
    plt.ylabel('Tasa de Bloqueo Exitoso (Pass Rate %)', fontsize=12)
    
    # Zoom en la zona de interés para apreciar la caída de Llama
    plt.ylim(60, 105) 

    # Añadir leyenda fuera del gráfico
    plt.legend(title='Modelos', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()

    # 6. Guardar la imagen
    output_path = 'strategy1/hardening_progression_trend.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico de tendencia generado en: {output_path}")

# Ejecutar con tu archivo
generar_grafico_progresion('strategy1/summary_table.csv')