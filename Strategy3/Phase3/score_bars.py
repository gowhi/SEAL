import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

def generar_distribucion_severidad_e3(ruta_csv):
    if not os.path.exists(ruta_csv):
        print(f"❌ Error: No se encuentra el archivo en {ruta_csv}")
        return

    # Configuración de fuentes unificada (Mismos tamaños que E1 y E2)
    mpl.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 18,
        'axes.labelsize': 16,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
    })

    # 1. Cargar datos
    df = pd.read_csv(ruta_csv)
    df.set_index('model', inplace=True)
    
    # 2. Mapeo de nombres de modelos
    formated_names = {
        'gpt-oss-target': 'GPT-OSS (20B)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df.index = df.index.map(formated_names)

    # 3. Colores y Leyendas (E3: Inyección Indirecta y SDoS)
    colores_map = {
        '0.0': '#e74c3c',  # Rojo: Integridad Rota (Secuestro)
        '0.2': '#e67e22',  # Naranja: Respuesta Incoherente
        '0.5': '#f1c40f',  # Amarillo: DoS Funcional (Bloqueo)
        '1.0': '#27ae60'   # Verde: Éxito (Robusto)
    }
    
    legend_labels = {
        '0.0': 'Fallo Crítico: Integridad Rota (Secuestro)',
        '0.2': 'Fallo: Respuesta Incoherente',
        '0.5': 'Fallo: SDoS Funcional (Bloqueo sin Resumen)',
        '1.0': 'Éxito: Agente Robusto (Seguro y Disponible)'
    }

    # Normalizar columnas a string para asegurar el mapeo de colores
    df.columns = [str(float(c)) for c in df.columns]
    cols_order = ['0.0', '0.2', '0.5', '1.0']
    available_cols = [c for c in cols_order if c in df.columns]
    df = df[available_cols]
    colors_to_use = [colores_map[col] for col in df.columns]

    # 4. Crear el gráfico de barras apiladas (Tamaño 14x8 como los anteriores)
    fig, ax = plt.subplots(figsize=(14, 8))
    
    df.plot(kind='bar', 
            stacked=True, 
            color=colors_to_use, 
            ax=ax, 
            width=0.7, 
            edgecolor='white', 
            linewidth=0.5)

    # 5. Estética y Títulos (Cursiva segura y & fuera de $)
    titulo = (r'Distribución de Severidad de Fallos ($\mathit{Security\ Scores}$)' + '\n' + 
              r'E3: $\mathit{Indirect\ Tool\ Injection}$ & $\mathit{SDoS}$')
    
    ax.set_title(titulo, fontsize=20, fontweight='bold', pad=25)
    ax.set_ylabel('Porcentaje de Evaluaciones (%)', fontsize=16, labelpad=15)
    ax.set_xlabel('Modelos Evaluados', fontsize=16, labelpad=15)
    ax.set_ylim(0, 100)
    
    # 6. Ajuste de leyenda
    handles, labels = ax.get_legend_handles_labels()
    new_labels = [legend_labels.get(l, f"Score {l}") for l in labels]
    
    ax.legend(handles, new_labels, title="Nivel de Riesgo (Disponibilidad)", 
              fontsize=13, title_fontsize=14,
              bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False)

    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    # 7. Guardar en la carpeta de Estrategia 3
    if not os.path.exists('strategy3'): os.makedirs('strategy3')
    output_path = 'strategy3/distribucion_severidad_E3_final.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico de severidad E3 generado en: {output_path}")

# Ejecución
generar_distribucion_severidad_e3('strategy3/score_dist_S3.csv')