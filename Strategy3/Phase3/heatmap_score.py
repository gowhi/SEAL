import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def generar_heatmap_disponibilidad_s3(ruta_csv, carpeta_salida='strategy3'):
    print(f"--- Iniciando: Heatmap de Disponibilidad y Resiliencia (S3) ---")
    
    # Verificar si el archivo existe
    if not os.path.exists(ruta_csv):
        print(f"❌ Error: No se encuentra el archivo en {ruta_csv}")
        return

    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # 1. Cargar datos
    df = pd.read_csv(ruta_csv)
    print(f"✅ Archivo cargado correctamente.")
    
    # Mapeo de nombres para consistencia en el TFM
    formated_names = {
        'gpt-oss-target': 'GPT-4o (OSS)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5 Coder'
    }
    df['model'] = df['model'].map(formated_names)

    # 2. Configurar la figura (Triple Heatmap: Inductor, Estricto, Ultra)
    escenarios = ['Inductor', 'Estricto', 'Ultra']
    fig, axes = plt.subplots(1, 3, figsize=(24, 8), sharey=True)

    for i, esc in enumerate(escenarios):
        # Filtrar por escenario
        df_esc = df[df['prompt_label'] == esc]
        
        if df_esc.empty:
            print(f"⚠️ Aviso: No hay datos para el escenario {esc}")
            continue

        # Pivotar usando 'availability_rate' que es lo que tiene tu tanda_perf_S3.csv
        # availability_rate: 0 a 100
        pivot_df = df_esc.pivot(index='model', columns='tanda', values='availability_rate')
        
        # Dibujar Heatmap (Cmap YlGnBu: Azul oscuro = Alta Disponibilidad)
        sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="YlGnBu", 
                    ax=axes[i], cbar=(i == 2), vmin=0, vmax=100,
                    linewidths=.5, annot_kws={"size": 9, "weight": "bold"})
        
        axes[i].set_title(f'PROTECCIÓN: {esc.upper()}', fontsize=16, fontweight='bold', pad=15)
        axes[i].set_xlabel('Técnicas Adversarias (PyRIT)', fontsize=11)
        axes[i].tick_params(axis='x', rotation=45)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=12, fontweight='bold')
        else:
            axes[i].set_ylabel('')

    # 3. Estética Global y Título
    plt.suptitle('S3: Tasa de Disponibilidad Semántica por Técnica y Modelo (%)\n(100% = Resumen entregado a pesar del ataque / 0% = Bloqueo o Secuestro)', 
                 fontsize=22, fontweight='bold', y=1.08)
    
    plt.tight_layout()
    
    output_path = os.path.join(carpeta_salida, 'heatmap_disponibilidad_S3.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ ¡ÉXITO! Heatmap de Disponibilidad S3 guardado en: {output_path}")

# --- EJECUCIÓN ---
# Nota: Usamos 'tanda_perf_S3.csv' que es el nombre que aparece en tu tree
generar_heatmap_disponibilidad_s3('strategy3/tanda_perf_S3.csv')