import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl
import os

# 1. Configuración global (Idéntica a E1 y E2)
mpl.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 20,
    'axes.labelsize': 18,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'legend.fontsize': 16,
    'legend.title_fontsize': 18,
    'text.usetex': False 
})

def generar_scatter_tradeoff_s3(ruta_summary, ruta_latencia, output_dir='strategy3'):
    if not os.path.exists(ruta_summary) or not os.path.exists(ruta_latencia):
        print(f"Error: Faltan archivos en {output_dir}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df_plot = pd.merge(pd.read_csv(ruta_summary), pd.read_csv(ruta_latencia), on=['model', 'prompt_label']).copy()

    formated_names = {
        'gpt-oss-target': 'GPT-OSS (20B)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df_plot['model'] = df_plot['model'].map(formated_names)

    plt.figure(figsize=(14, 9))
    sns.set_style("whitegrid")

    scatter = sns.scatterplot(
        data=df_plot, x='avg_latency_ms', y='pass_rate',
        hue='model', style='prompt_label', s=350, alpha=0.8,
        edgecolor='black', zorder=3, palette='magma' 
    )

    plt.xscale('log') 
    plt.ylim(-5, 105) 
    
    ticks_locs = [1000, 2000, 5000, 10000, 20000, 40000]
    ticks_labels = ["1s", "2s", "5s", "10s", "20s", "40s"]
    plt.xticks(ticks_locs, ticks_labels)
    plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())

    df_plot = df_plot.sort_values('avg_latency_ms')
    for i, row in df_plot.iterrows():
        if row['prompt_label'] == 'Estricto':
            plt.text(
                row['avg_latency_ms'], row['pass_rate'] + 3, 
                row['model'], fontsize=10, fontweight='bold',
                ha='center', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1)
            )

    # --- TÍTULOS Y ETIQUETAS CORREGIDOS (MÁXIMA COMPATIBILIDAD) ---
    # Sacamos el '&' fuera de los símbolos $ para evitar el error de ParseFatalException
    plt.title('Trade-off Seguridad vs. Latencia (Disponibilidad)\n' + 
              r'Escenario 3: $\mathit{Indirect\ Tool\ Injection}$ & $\mathit{SDoS}$', 
              fontsize=20, fontweight='bold', pad=25)
    
    plt.xlabel('Latencia Media (ms) - Escala Logarítmica', fontsize=18)
    
    # Aplicamos cursiva a Pass Rate separando el bloque
    plt.ylabel(r'Tasa de Disponibilidad Real ($\mathit{Pass\ Rate}$ %)', fontsize=18)

    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Modelos y Hardening')
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'scatter_tradeoff_S3_final.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico S3 generado con éxito en: {output_path}")

# Ejecución
generar_scatter_tradeoff_s3('strategy3/summary_table_S3.csv', 'strategy3/latencia_S3.csv')