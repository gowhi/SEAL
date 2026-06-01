import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

def generar_grafico_progresion_e3(ruta_summary):
    print(f"--- Iniciando: Gráfico de Tendencia de Hardening (E3) ---")
    
    # 1. Validación de la ruta
    if not os.path.exists(ruta_summary):
        print(f"❌ Error: No se encuentra el archivo en {ruta_summary}")
        return

    # 2. Cargar el CSV resumen
    df = pd.read_csv(ruta_summary)

    # 3. Mapeo de nombres para el TFM (Consistente con E2 y E3)
    formated_names = {
        'gpt-oss-target': 'GPT-OSS (20B)', 
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df['model'] = df['model'].map(formated_names)

    # 4. ORDENAR LOS NIVELES
    orden_hardening = ['Inductor', 'Estricto', 'Ultra']
    df['prompt_label'] = pd.Categorical(df['prompt_label'], categories=orden_hardening, ordered=True)
    df = df.sort_values('prompt_label')

    # 5. Crear el gráfico (Tamaño unificado 10x6 o 11x7 según prefieras)
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")

    # Dibujamos las líneas con los mismos parámetros de E1/E2
    line_plot = sns.lineplot(
        data=df, 
        x='prompt_label', 
        y='pass_rate', 
        hue='model', 
        marker='o',      
        linewidth=3,     
        markersize=10    
    )

    # 6. Personalización estética (Mismos tamaños que E1 y E2)
    # Título con cursiva protegida y & fuera del bloque math para evitar errores
    plt.title(r'Tendencia de $\mathit{Hardening}$: Evolución de la Disponibilidad' + '\n' + 
              r'E3: $\mathit{Indirect\ Tool\ Injection}$ & $\mathit{SDoS}$', 
              fontsize=18, fontweight='bold', pad=25)
    
    plt.xlabel(r'Nivel de Restricción del $\mathit{System\ Prompt}$', fontsize=18, labelpad=15)
    plt.ylabel(r'Tasa de Disponibilidad Real ($\mathit{Pass\ Rate\ \%}$)', fontsize=18, labelpad=15)

    # Límite amplio para capturar caídas por SDoS
    plt.ylim(-5, 105) 

    # Leyenda fuera del gráfico
    plt.legend(title='Modelos', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=14, title_fontsize=14)

    # Tamaño de los valores en los ejes (Ticks) - Unificado a 16
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    plt.tight_layout()

    # 7. Guardar la imagen en la carpeta de estrategia 3
    if not os.path.exists('strategy3'):
        os.makedirs('strategy3')
        
    output_path = 'strategy3/hardening_progression_trend_E3.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico de tendencia E3 generado en: {output_path}")

# Ejecución
generar_grafico_progresion_e3('strategy3/summary_table_S3.csv')