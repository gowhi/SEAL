import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

def generar_scatter_tradeoff_e2(ruta_summary, ruta_latencia):
    if not os.path.exists(ruta_summary) or not os.path.exists(ruta_latencia):
        print("Error: Faltan archivos de entrada en la carpeta strategy2")
        return

    # 1. Cargar y Unir datos
    summary_df = pd.read_csv(ruta_summary)
    latencia_df = pd.read_csv(ruta_latencia)
    df_plot = pd.merge(summary_df, latencia_df, on=['model', 'prompt_label'])

    # 2. Formatear nombres
    formated_names = {
        'gpt-oss-target': 'GPT-OSS (20B)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df_plot['model'] = df_plot['model'].map(formated_names)

    # 3. Crear el gráfico
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")

    # Scatter plot con estilo por nivel de hardening
    scatter = sns.scatterplot(
        data=df_plot,
        x='avg_latency_ms',
        y='pass_rate',
        hue='model',
        style='prompt_label',
        s=350, # Puntos muy visibles
        alpha=0.75,
        edgecolor='black',
        palette='viridis' # Una paleta distinta para diferenciar de E1
    )

    # 4. Escala Logarítmica para Latencia
    plt.xscale('log') 
    
    # IMPORTANTE: Eliminamos el zoom para ver la caída libre de los modelos en E2
    plt.ylim(-5, 105) 
    
    # Ticks legibles basados en tus resultados reales (900ms a 17s)
    plt.xticks([900, 1000, 5000, 10000, 17000], ["900ms", "1s", "5s", "10s", "17s"])
    plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())

    # 5. Etiquetas de los puntos para claridad total
    for i in range(df_plot.shape[0]):
        plt.text(
            df_plot.avg_latency_ms[i], 
            df_plot.pass_rate[i] + 2.5, 
            f"{df_plot.prompt_label[i]}", 
            fontsize=9, 
            ha='center',
            alpha=0.8
        )

    plt.title('E2: Trade-off Eficiencia vs. Confidencialidad', fontsize=18, fontweight='bold', pad=25)
    plt.xlabel('Latencia Media (ms) - Escala Logarítmica', fontsize=13)
    plt.ylabel('Tasa de Bloqueo Exitoso (Pass Rate %)', fontsize=13)
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Modelos y Hardening')
    plt.tight_layout()
    
    # 6. Guardar
    output_path = 'strategy2/scatter_tradeoff_E2.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico de Trade-off E2 generado en: {output_path}")

# Ejecución
generar_scatter_tradeoff_e2('strategy2/summary_table.csv', 'strategy2/latencia.csv')