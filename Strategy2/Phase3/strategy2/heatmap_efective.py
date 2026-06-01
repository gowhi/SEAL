import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

def generar_heatmaps_resistencia_e2(ruta_csv):
    print(f"--- Iniciando: Heatmap de Resistencia E2 (% Success Rate) ---")
    
    # 1. Validación de la ruta
    if not os.path.exists(ruta_csv):
        print(f"❌ Error: No se encuentra el archivo en {ruta_csv}")
        return

    # Configuración de fuentes global
    mpl.rcParams.update({'font.family': 'sans-serif'})

    # 2. Cargar datos
    df = pd.read_csv(ruta_csv)
    
    # Mapeo de nombres para consistencia
    #formated_names = {
    #    'gpt-oss-target': 'GPT-OSS (20B)',
    #    'llama': 'Llama 3.2 (3B)',
    #    'mistral-target': 'Mistral-7B',
    #    'qwen-coder-target': 'Qwen 2.5'
    #}


    formated_names = {
        'gpt-oss-target': 'GPT-OSS',
        'llama': 'Llama',
        'mistral-target': 'Mistral',
        'qwen-coder-target': 'Qwen'
    }
    df['model'] = df['model'].map(formated_names)

    # 3. Configurar la figura (Triple Heatmap: Inductor, Estricto, Ultra)
    escenarios = ['Inductor', 'Estricto', 'Ultra']
    # Mantenemos el tamaño de figura (38, 14) para que sea idéntico al de E1
    fig, axes = plt.subplots(1, 3, figsize=(38, 14), sharey=True)

    for i, esc in enumerate(escenarios):
        # Filtrar por escenario
        df_esc = df[df['prompt_label'] == esc]
        
        if df_esc.empty:
            print(f"⚠️ Aviso: No hay datos para el escenario {esc}")
            continue
            
        pivot_df = df_esc.pivot(index='model', columns='tanda', values='success_rate')
        
        if i == 2:
            # --- BARRA DE COLOR GRANDE Y ANCHA (Consistente con E1) ---
            cbar_ax = fig.add_axes([0.94, 0.25, 0.03, 0.57]) 
            
            sns.heatmap(
                pivot_df, annot=True, fmt=".1f", cmap="RdYlGn", 
                ax=axes[i], cbar=True, cbar_ax=cbar_ax, vmin=0, vmax=100, 
                square=False, 
                annot_kws={"size": 22, "weight": "bold"}, 
                linewidths=1.5
            )
            cbar_ax.tick_params(labelsize=25) 
            cbar_ax.set_ylabel('% Bloqueo Total', fontsize=28, fontweight='bold', labelpad=20)
        else:
            sns.heatmap(
                pivot_df, annot=True, fmt=".1f", cmap="RdYlGn", 
                ax=axes[i], cbar=False, vmin=0, vmax=100, 
                square=False, 
                annot_kws={"size": 22, "weight": "bold"}, 
                linewidths=1.5
            )
        
        # Ajustes de etiquetas de los ejes (Alineación y Tamaños)
        axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        axes[i].set_title(f'NIVEL: {esc.upper()}', fontsize=30, fontweight='bold', pad=40)
        axes[i].set_xlabel('Técnicas Adversarias (Tandas)', fontsize=30, labelpad=20)
        axes[i].tick_params(axis='x', labelsize=26)
        
        if i == 0:
            axes[i].set_ylabel('Modelos Evaluados', fontsize=28, fontweight='bold', labelpad=80)
            axes[i].tick_params(axis='y', labelsize=24)
        else:
            axes[i].set_ylabel('')

    # 4. Título Principal (Formato idéntico al Escenario 1)
    plt.suptitle(r'Mapa de Resistencia E2: $\mathit{System\ Prompt\ Exfiltration}$' + '\n' + 
                 r'(% de Éxito en el Bloqueo Total por Técnica y Modelo)', 
                 fontsize=35, fontweight='bold', y=0.98)

    # 5. Ajuste de márgenes (Idéntico a E1 para simetría total)
    plt.subplots_adjust(left=0.22, top=0.82, wspace=0.15, right=0.92, bottom=0.25)

    # 6. Guardar el resultado
    if not os.path.exists('strategy2'):
        os.makedirs('strategy2')
        
    output_path = 'strategy2/heatmap_resistencia_E2_.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ ¡ÉXITO! Heatmap de Resistencia E2 guardado en: {output_path}")

# Ejecución
generar_heatmaps_resistencia_e2('strategy2/tanda_perf.csv')