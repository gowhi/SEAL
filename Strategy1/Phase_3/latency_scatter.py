import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def generar_scatter_tradeoff_final(ruta_summary, ruta_latencia):
    # 1. Cargar los CSVs
    summary_df = pd.read_csv(ruta_summary)
    latencia_df = pd.read_csv(ruta_latencia)

    # 2. Unir los datos
    df_plot = pd.merge(summary_df, latencia_df, on=['model', 'prompt_label'])

    # 3. Formatear nombres
    formated_names = {
        'gpt-oss-target': 'GPT-OSS (20B)',
        'llama': 'Llama 3.2',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df_plot['model'] = df_plot['model'].map(formated_names)

    # 4. Crear el gráfico
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")

    scatter = sns.scatterplot(
        data=df_plot,
        x='avg_latency_ms',
        y='pass_rate',
        hue='model',
        style='prompt_label',
        s=300, # Puntos grandes para que se vean bien en la memoria
        alpha=0.8,
        edgecolor='black'
    )

    # 5. Escala Logarítmica y Zoom
    plt.xscale('log') 
    plt.ylim(60, 105) # Empezamos en 60 para ver el detalle de la seguridad
    
    # Ticks legibles para la escala logarítmica
    plt.xticks([900, 1000, 1500, 5000, 10000, 25000], ["900", "1k", "1.5k", "5k", "10k", "25k"])
    plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())

    # 6. Etiquetas de los puntos
    for i in range(df_plot.shape[0]):
        plt.text(
            df_plot.avg_latency_ms[i], 
            df_plot.pass_rate[i] + 0.8, 
            f"{df_plot.model[i]}", 
            fontsize=8, 
            fontweight='bold',
            ha='center'
        )

    plt.title('Trade-off Seguridad vs. Latencia (Zoom 60-100%)', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Latencia Media (ms) - Escala Logarítmica', fontsize=13)
    plt.ylabel('Tasa de Bloqueo Exitoso (Pass Rate %)', fontsize=13)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Modelos y Escenarios')

    plt.tight_layout()
    
    output_path = 'strategy1/scatter_seguridad_latencia_final.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico final generado en: {output_path}")

# Ejecución
generar_scatter_tradeoff_final('strategy1/summary_table.csv', 'strategy1/latencia.csv')