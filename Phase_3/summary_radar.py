import pandas as pd
import matplotlib.pyplot as plt
from math import pi
import os

# Function to generate radar charts for security models
# Based on the provided CSV file
# The CSV is expected to have columns: model, prompt_label, pass_rate, avg_score
# Each model will have its own radar chart comparing pass rates and average scores
def generar_radares_seguridad(ruta_csv):
    # Check if the file exists
    if not os.path.exists(ruta_csv):
        print(f"Error: File not found at {ruta_csv}")
        return
    
    # Load data
    # df_pivot will have multi-level columns for pass_rate and avg_score
    df = pd.read_csv(ruta_csv)
    df_pivot = df.pivot(index='model', columns='prompt_label', values=['pass_rate', 'avg_score'])
    
    # Define categories for radar chart
    # Each category corresponds to a metric for the radar chart
    # Order: Pass Rate (Ind), Pass Rate (Str), Pass Rate (Ult), Score (Ult), Score (Str), Score (Ind)
    categories = ['Pass Rate (Ind)', 'Pass Rate (Str)', 'Pass Rate (Ult)', 
                  'Score (Ult)', 'Score (Str)', 'Score (Ind)']

    modelos = df_pivot.index.tolist() # Number of models extracted from df_pivot (4 in this case)
    n_categories = len(categories) # Length of categories (6 in this case)
    angles = [i / float(n_categories) * 2 * pi for i in range(n_categories)] # Angles for each category (radians)
    angles += angles[:1] # Complete the loop for radar chart

    # map of model names to colors
    colours = {
        'gpt-oss-target': "#43b7ff",     # blue
        'llama': "#faa16a",              # orange
        'mistral-target': "#9aff8d",     # green
        'qwen-coder-target': "#ef8ffc"   # pink
    }

    # Mapeo de nombres internos del CSV a nombres de visualización para el TFM
    formated_names = {
        'gpt-oss-target': 'GPT-4o (OSS Target)',
        'llama': 'Llama 3.2 (3B)',
        'mistral-target': 'Mistral-7B-v0.3',
        'qwen-coder-target': 'Qwen 2.5 Coder'
    }

    # Function to draw a radar chart for a specific model
    # Defined as a nested function to leverage closure (accessing df_pivot and angles directly)
    def draw_radar(ax, model_name, color):
        row = df_pivot.loc[model_name]

        # Sequence of 6 metrics arranged speculary:
        # Right side of radar: Robustness (Pass Rate normalized to [0, 1])
        # Left side of radar: Response Integrity (Avg Score already in [0, 1])
        # This layout visually separates 'Blocking Power' from 'Safety Quality'
        values = [ 
            row[('pass_rate', 'Inductor')] / 100, # 12:00 - Starting point
            row[('pass_rate', 'Estricto')] / 100, # 02:00 - Mid hardening
            row[('pass_rate', 'Ultra')] / 100,    # 04:00 - Maximum hardening
            row[('avg_score', 'Ultra')],          # 06:00 - Max integrity
            row[('avg_score', 'Estricto')],       # 08:00 - Mid integrity
            row[('avg_score', 'Inductor')]        # 10:00 - Base integrity
        ]

        values += values[:1] # Close the radar loop by repeating the first value

        ax.plot(angles, values, linewidth=2, linestyle='solid', color=color, label=model_name) # Contour Line plot
        ax.fill(angles, values, color=color, alpha=0.35) # Alpha is for transparency
        ax.set_xticks(angles[:-1]) # Define edge labels
        ax.set_xticklabels(categories, fontsize=9, fontweight='bold') # Set category labels of edges
        ax.set_ylim(0, 1.1) # Set y-axis limits
        display_name = formated_names.get(model_name, model_name.upper()) # Get display name  
        ax.set_title(f"MODEL: {display_name}", size=14, pad=30, color=color, fontweight='bold') # Title with color
    fig, axes = plt.subplots(2, 2, figsize=(14, 14), subplot_kw=dict(polar=True)) # 2x2 grid for 4 models
    axes = axes.flatten() # Flatten to easily iterate over

    # Draw radar charts for each model with corresponding colors
    for i, modelo in enumerate(modelos):
        color_actual = colours.get(modelo, '#7f7f7f') # Default gray if model not found
        draw_radar(axes[i], modelo, color_actual)  # Draw radar for each model

    plt.tight_layout(pad=5.0) # Adjust layout to prevent overlap
    output_path = 'strategy1/radar_comparativo.png' # Output path for the radar chart
    plt.savefig(output_path, dpi=300) # Save with higher resolution for the report
    print(f"Radar graph saved at: {output_path}")

generar_radares_seguridad('strategy1/summary_table.csv')