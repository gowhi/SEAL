import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl

# new
mpl.rcParams.update({
    'font.size': 16,          # Tamaño de letra general
    'axes.titlesize': 20,     # Tamaño del título del eje
    'axes.labelsize': 18,     # Tamaño de los labels X/Y
    'xtick.labelsize': 16,    # Tamaño de ticks X
    'ytick.labelsize': 16,    # Tamaño de ticks Y
    'legend.fontsize': 16,    # Tamaño de la leyenda
    'legend.title_fontsize': 18, # Tamaño del título de la leyenda
})

def generar_scatter_tradeoff_final(ruta_summary, ruta_latencia):
    # 1. Cargar y unir (Usa copy() para evitar warnings de SettingWithCopy)
    summary_df = pd.read_csv(ruta_summary)
    latencia_df = pd.read_csv(ruta_latencia)
    df_plot = pd.merge(summary_df, latencia_df, on=['model', 'prompt_label']).copy()

    # 2. Formatear nombres
    formated_names = {
        'gpt-oss-target': 'GPT-OSS (20B)',
        'llama': 'Llama 3.2',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df_plot['model'] = df_plot['model'].map(formated_names)

    # 3. Crear el gráfico
    plt.figure(figsize=(14, 9))
    sns.set_style("whitegrid")

    # Dibujar los puntos
    scatter = sns.scatterplot(
        data=df_plot,
        x='avg_latency_ms',
        y='pass_rate',
        hue='model',
        style='prompt_label',
        s=350, 
        alpha=0.8,
        edgecolor='black',
        zorder=3
    )

    # 4. Configuración de ejes
    plt.xscale('log') 
    plt.ylim(60, 105) 
    
    # Ticks manuales para evitar que Matplotlib decida por nosotros
    ticks_x = [900, 1000, 1500, 5000, 10000, 25000]
    labels_x = ["900", "1k", "1.5k", "5k", "10k", "25k"]
    plt.xticks(ticks_x, labels_x)
    plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())

    # 5. Lógica de etiquetas sin solapamiento manual
    # Ordenamos por latencia para que el bucle tenga un sentido físico
    df_plot = df_plot.sort_values('avg_latency_ms')
    
# 6. Etiquetas de los puntos (Solo una por modelo para evitar duplicados)
    for i, row in df_plot.iterrows():
        # Solo ponemos el nombre si es el prompt_label 'Estricto' 
        # (o el que tú prefieras como principal)
        if row['prompt_label'] == 'Estricto':
            plt.text(
                row['avg_latency_ms'], 
                row['pass_rate'] + 1.5, # Un poco más arriba
                row['model'], 
                fontsize=10, 
                fontweight='bold',
                ha='center',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1)
            )
    # 6. Títulos (Sin LaTeX complejo para evitar el ValueError)
    plt.title('Trade-off Seguridad vs. Latencia (Zoom 60-100%)\nEscenario 1: Tool Injection', 
              fontsize=20, fontweight='bold', pad=25)
    
    plt.xlabel('Latencia Media (ms) - Escala Logarítmica', fontsize=18)
    plt.ylabel('Tasa de Bloqueo Exitoso (Pass Rate %)', fontsize=18)
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Modelos y Escenarios')
    plt.tight_layout()
    
    output_path = 'strategy1/scatter_seguridad_latencia_final_.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico generado con éxito en: {output_path}")

# Ejecutar
generar_scatter_tradeoff_final('strategy1/summary_table.csv', 'strategy1/latencia.csv')