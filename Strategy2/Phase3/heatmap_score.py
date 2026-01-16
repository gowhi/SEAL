import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def generar_heatmap_calidad_e2(ruta_csv):
    print(f"--- Iniciando: Heatmap de Calidad/Integridad (E2) ---")
    
    # Verificar si el archivo existe
    if not os.path.exists(ruta_csv):
        print(f"❌ Error: No se encuentra el archivo en {ruta_csv}")
        return

    # 1. Cargar datos
    df = pd.read_csv(ruta_csv)
    print(f"✅ Archivo cargado correctamente.")
    
    # Mapeo de nombres para consistencia en el TFM
    formated_names = {
        'gpt-oss-target': 'GPT-OSS (20B)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B',
        'qwen-coder-target': 'Qwen 2.5'
    }
    df['model'] = df['model'].map(formated_names)

    # 2. Configurar la figura (Triple Heatmap para ver la evolución de la calidad)
    escenarios = ['Inductor', 'Estricto', 'Ultra']
    fig, axes = plt.subplots(1, 3, figsize=(24, 8), sharey=True)

    for i, esc in enumerate(escenarios):
        # Filtrar por escenario (Nivel de protección)
        df_esc = df[df['prompt_label'] == esc]
        
        if df_esc.empty:
            print(f"⚠️ Aviso: No hay datos para el escenario {esc}")
            continue

        # Pivotar: Filas=Modelos, Columnas=Técnicas, Valores=AVG_SCORE
        pivot_df = df_esc.pivot(index='model', columns='tanda', values='avg_score')
        
        # Dibujar Heatmap (Cmap YlGnBu: Azul oscuro = Alta calidad/Seguridad)
        sns.heatmap(pivot_df, annot=True, fmt=".2f", cmap="YlGnBu", 
                    ax=axes[i], cbar=(i == 2), vmin=0, vmax=1,
                    linewidths=.5, annot_kws={"size": 9, "weight": "bold"})
        
        axes[i].set_title(f'PROTECCIÓN: {esc.upper()}', fontsize=16, fontweight='bold', pad=15)
        axes[i].set_xlabel('Técnicas Adversarias (PyRIT)', fontsize=11)
        axes[i].tick_params(axis='x', rotation=45)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=12, fontweight='bold')
        else:
            axes[i].set_ylabel('')

    # 3. Estética Global y Título
    plt.suptitle('E2: Integridad de la Confidencialidad por Técnica y Modelo\n(Promedio de Security Score: 1.0 = Bloqueo Perfecto / 0.0 = Exfiltración)', 
                 fontsize=22, fontweight='bold', y=1.08)
    
    plt.tight_layout()
    
    # 4. Guardar en la carpeta de estrategia 2
    if not os.path.exists('strategy2'):
        os.makedirs('strategy2')
        
    output_path = 'strategy2/heatmap_calidad_E2.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ ¡ÉXITO! Heatmap de Calidad E2 guardado en: {output_path}")

# --- EJECUCIÓN DEL SCRIPT ---
# Asegúrate de que el CSV existe en la subcarpeta strategy2/
generar_heatmap_calidad_e2('strategy2/tanda_score_perf.csv')