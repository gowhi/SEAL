import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

def generar_grafico_progresion_e2(ruta_summary):
    print(f"--- Iniciando: Gráfico de Tendencia de Hardening (E2) ---")
    
    # 1. Validación de la ruta
    if not os.path.exists(ruta_summary):
        print(f"❌ Error: No se encuentra el archivo en {ruta_summary}")
        return

    # 2. Cargar el CSV resumen
    df = pd.read_csv(ruta_summary)

    # 3. Mapeo de nombres para el TFM (Consistente con tus otros gráficos de E2)
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

    # 5. Crear el gráfico (Mismo tamaño que E1: 10x6)
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")

    # Dibujamos las líneas con los mismos parámetros de E1
    line_plot = sns.lineplot(
        data=df, 
        x='prompt_label', 
        y='pass_rate', 
        hue='model', 
        marker='o',      
        linewidth=3,     
        markersize=10    
    )

    # 6. Personalización estética (Mismos tamaños que E1)
    plt.title(r'Tendencia de $\mathit{Hardening}$: Evolución de la Seguridad' + '\n' + 
              r'E2: $\mathit{System\ Prompt\ Exfiltration}$', 
              fontsize=18, fontweight='bold', pad=25)
    
    plt.xlabel(r'Nivel de Restricción del $\mathit{System\ Prompt}$', fontsize=18, labelpad=15)
    plt.ylabel(r'Tasa de Bloqueo Exitoso ($\mathit{Pass\ Rate\ \%}$)', fontsize=18, labelpad=15)

    # Ajustamos el límite para ver las caídas de seguridad en E2
    plt.ylim(0, 105) 

    # Leyenda fuera del gráfico (Mismos tamaños que E1)
    plt.legend(title='Modelos', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=14, title_fontsize=14)

    # Tamaño de los valores en los ejes (Ticks)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    plt.tight_layout()

    # 7. Guardar la imagen en la carpeta de estrategia 2
    if not os.path.exists('strategy2'):
        os.makedirs('strategy2')
        
    output_path = 'strategy2/hardening_progression_trend_E2.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico de tendencia E2 generado en: {output_path}")

# Ejecutar con el archivo de la carpeta strategy2
generar_grafico_progresion_e2('strategy2/summary_table.csv')