import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

def generar_heatmap_calidad_e2(ruta_csv):
    print(f"--- Iniciando: Heatmap de Calidad/Integridad (E2) ---")
    
    # Verificar si el archivo existe
    if not os.path.exists(ruta_csv):
        print(f"❌ Error: No se encuentra el archivo en {ruta_csv}")
        return

    # Configuración de fuentes global para consistencia en el TFM
    mpl.rcParams.update({'font.family': 'sans-serif'})

    # 1. Cargar datos
    df = pd.read_csv(ruta_csv)
    
    # Mapeo de nombres para consistencia
    formated_names = {
        'gpt-oss-target': 'GPT-OSS',
        'llama': 'Llama',
        'mistral-target': 'Mistral',
        'qwen-coder-target': 'Qwen'
    }
    df['model'] = df['model'].map(formated_names)

    # 2. Configurar la figura (Triple Heatmap)
    # Dimensiones 38x14 para que coincida exactamente con los de Resistencia
    escenarios = ['Inductor', 'Estricto', 'Ultra']
    fig, axes = plt.subplots(1, 3, figsize=(38, 14), sharey=True)

    for i, esc in enumerate(escenarios):
        # Filtrar por escenario
        df_esc = df[df['prompt_label'] == esc]
        
        if df_esc.empty:
            print(f"⚠️ Aviso: No hay datos para el escenario {esc}")
            continue

        # Pivotar: Filas=Modelos, Columnas=Técnicas, Valores=AVG_SCORE
        pivot_df = df_esc.pivot(index='model', columns='tanda', values='avg_score')
        
        if i == 2:
            # --- BARRA DE COLOR GRANDE Y ANCHA ---
            cbar_ax = fig.add_axes([0.94, 0.25, 0.03, 0.5]) 
            
            sns.heatmap(
                pivot_df, annot=True, fmt=".2f", cmap="YlGnBu", 
                ax=axes[i], cbar=True, cbar_ax=cbar_ax, vmin=0, vmax=1,
                square=False,
                annot_kws={"size": 22, "weight": "bold"}, 
                linewidths=1.5
            )
            cbar_ax.tick_params(labelsize=25) 
            cbar_ax.set_ylabel('Puntuación Media (0-1)', fontsize=28, fontweight='bold', labelpad=20)
        else:
            sns.heatmap(
                pivot_df, annot=True, fmt=".2f", cmap="YlGnBu", 
                ax=axes[i], cbar=False, vmin=0, vmax=1,
                square=False,
                annot_kws={"size": 22, "weight": "bold"}, 
                linewidths=1.5
            )
        
        # Ajustes de etiquetas de los ejes (Idéntico a Resistencia)
        axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        axes[i].set_title(f'CALIDAD: {esc.upper()}', fontsize=32, fontweight='bold', pad=40)
        axes[i].set_xlabel('Técnicas Adversarias (Tandas)', fontsize=30, labelpad=20)
        axes[i].tick_params(axis='x', labelsize=26)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=28, fontweight='bold', labelpad=80)
            axes[i].tick_params(axis='y', labelsize=24)
        else:
            axes[i].set_ylabel('')

    # 3. Título Principal (Formato unificado E2)
    plt.suptitle(r'Evaluación de la Calidad Defensiva E2: $\mathit{System\ Prompt\ Exfiltration}$' + '\n' + 
                 r'(Integridad de la Respuesta: $\mathit{Average\ Score}$ por Técnica)', 
                 fontsize=35, fontweight='bold', y=0.98)
    
    # 4. Ajuste de márgenes para simetría total con el heatmap de resistencia
    plt.subplots_adjust(left=0.22, top=0.82, wspace=0.15, right=0.92, bottom=0.25)
    
    # 5. Guardar en la carpeta de estrategia 2
    if not os.path.exists('strategy2'):
        os.makedirs('strategy2')
        
    output_path = 'strategy2/heatmap_calidad_E2.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ ¡ÉXITO! Heatmap de Calidad E2 guardado en: {output_path}")

# Ejecución
generar_heatmap_calidad_e2('strategy2/tanda_score_perf.csv')