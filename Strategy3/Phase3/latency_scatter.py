import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

def generar_scatter_tradeoff_s3(ruta_summary, ruta_latencia, output_dir='strategy3'):
    if not os.path.exists(ruta_summary) or not os.path.exists(ruta_latencia):
        print(f"Error: Faltan archivos de entrada para {output_dir}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Cargar y Unir datos
    summary_df = pd.read_csv(ruta_summary)
    latencia_df = pd.read_csv(ruta_latencia)
    df_plot = pd.merge(summary_df, latencia_df, on=['model', 'prompt_label'])

    # 2. Formatear nombres para el TFM
    formated_names = {
        'gpt-oss-target': 'GPT-4o (OSS)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5 Coder'
    }
    df_plot['model'] = df_plot['model'].map(formated_names)

    # 3. Crear el gráfico
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")

    # Scatter plot: X=Latencia, Y=Pass Rate (Disponibilidad)
    scatter = sns.scatterplot(
        data=df_plot,
        x='avg_latency_ms',
        y='pass_rate',
        hue='model',
        style='prompt_label',
        s=350, 
        alpha=0.8,
        edgecolor='black',
        palette='magma' # Paleta cálida para diferenciar de otras estrategias
    )

    # 4. Escala Logarítmica para Latencia (necesaria por la gran diferencia de GPT)
    plt.xscale('log') 
    plt.ylim(-5, 105) 
    
    # Ajustamos los Ticks a tus resultados de S3 (de 900ms a 40s)
    ticks_locs = [1000, 2000, 5000, 10000, 20000, 40000]
    ticks_labels = ["1s", "2s", "5s", "10s", "20s", "40s"]
    plt.xticks(ticks_locs, ticks_labels)
    plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())

    # 5. Etiquetas de texto para cada punto
    for i in range(df_plot.shape[0]):
        plt.text(
            df_plot.avg_latency_ms[i], 
            df_plot.pass_rate[i] + 3, 
            f"{df_plot.prompt_label[i]}", 
            fontsize=8, 
            ha='center',
            fontweight='bold',
            alpha=0.7
        )

    plt.title('S3: Trade-off Eficiencia vs. Disponibilidad Semántica', fontsize=18, fontweight='bold', pad=25)
    plt.xlabel('Latencia Media (ms) - Escala Logarítmica', fontsize=13)
    plt.ylabel('Tasa de Disponibilidad Real (Pass Rate %)', fontsize=13)
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Modelos y Hardening')
    plt.tight_layout()
    
    # 6. Guardar
    output_path = os.path.join(output_dir, 'scatter_tradeoff_S3.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico de Trade-off S3 generado en: {output_path}")

# Ejecución
generar_scatter_tradeoff_s3('strategy3/summary_table_S3.csv', 'strategy3/latencia_S3.csv')