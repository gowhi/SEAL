import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def generar_heatmaps_resistencia_s3(ruta_csv, carpeta_salida='strategy3'):
    print(f"--- Iniciando: Heatmap de Resistencia de Disponibilidad (S3) ---")
    
    # 1. Validación de la ruta
    if not os.path.exists(ruta_csv):
        print(f"❌ Error: No se encuentra el archivo en {ruta_csv}")
        return

    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # 2. Cargar datos
    df = pd.read_csv(ruta_csv)
    print(f"✅ Archivo '{ruta_csv}' cargado con éxito.")
    
    # Mapeo de nombres para consistencia en el TFM
    formated_names = {
        'gpt-oss-target': 'GPT-OSS (20B)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5 Coder'
    }
    df['model'] = df['model'].map(formated_names)

    # 3. Configurar la figura (Triple Heatmap: Inductor, Estricto, Ultra)
    escenarios = ['Inductor', 'Estricto', 'Ultra']
    fig, axes = plt.subplots(1, 3, figsize=(26, 9), sharey=True)

    for i, esc in enumerate(escenarios):
        # Filtrar por escenario
        df_esc = df[df['prompt_label'] == esc]
        
        if df_esc.empty:
            print(f"⚠️ Aviso: No hay datos para el escenario {esc}")
            continue
            
        # Pivotar: Filas=Modelos, Columnas=Técnicas, Valores=availability_rate
        # availability_rate: % de veces que el modelo logró resumir (Score 1.0)
        pivot_df = df_esc.pivot(index='model', columns='tanda', values='availability_rate')
        
        # Dibujar Heatmap (RdYlGn: Rojo = 0% disponibilidad, Verde = 100% disponibilidad)
        sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="RdYlGn", 
                    ax=axes[i], cbar=(i == 2), vmin=0, vmax=100,
                    linewidths=.5, annot_kws={"size": 10, "weight": "bold"})
        
        axes[i].set_title(f'NIVEL: {esc.upper()}', fontsize=18, fontweight='bold', pad=20)
        axes[i].set_xlabel('Técnicas Adversarias (Tandas)', fontsize=12)
        axes[i].tick_params(axis='x', rotation=45)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=14, fontweight='bold')
        else:
            axes[i].set_ylabel('')

    # 4. Estética Global
    plt.suptitle('S3: Mapa de Resistencia de la Disponibilidad Semántica\n(% de Éxito en Mantenimiento de Tarea bajo Inyección Indirecta)', 
                 fontsize=24, fontweight='bold', y=1.08)
    
    plt.tight_layout()
    
    # 5. Guardar el resultado
    output_path = os.path.join(carpeta_salida, 'heatmap_resistencia_S3.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ ¡ÉXITO! Heatmap de Resistencia S3 guardado en: {output_path}")

# --- LÍNEA DE EJECUCIÓN ---
# Nota: Usamos 'tanda_perf_S3.csv' que es el nombre que genera tu parser para esta estrategia
generar_heatmaps_resistencia_s3('strategy3/tanda_perf_S3.csv')