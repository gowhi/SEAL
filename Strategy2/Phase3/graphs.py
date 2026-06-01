"""
generate_graphs_s2.py
Generates all S2 (System Prompt Exfiltration - Confidentiality) figures
for both local and commercial model groups.

Usage:
    python generate_graphs_s2.py <group>
    where <group> is 'locals' or 'commercial'

    python generate_graphs_s2.py locals
    python generate_graphs_s2.py commercial

Output folders:
    results/S2-locals/graphs/
    results/S2-commercial/graphs/
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as ticker
import seaborn as sns
from math import pi

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

GROUPS = {
    'locals': {
        'prefix': 'S2-locals',
        'csv_dir': 'results/S2-locals/CSV',
        'model_map': {
            'gpt-oss-target':    'GPT-OSS (20B)',
            'llama':             'LLaMA 3.2 (3B)',
            'mistral-target':    'Mistral v0.3 (7B)',
            'qwen-coder-target': 'Qwen 2.5 Coder (7B)',
        },
        'colors': {
            'gpt-oss-target':    '#43b7ff',
            'llama':             '#faa16a',
            'mistral-target':    '#9aff8d',
            'qwen-coder-target': '#ef8ffc',
        },
        'strategy_label': 'S2: System Prompt Exfiltration (Confidentiality) — Open-Source Models',
    },
    'commercial': {
        'prefix': 'S2-commercial',
        'csv_dir': 'results/S2-commercial/CSV',
        'model_map': {
            'haiku':       'Claude Haiku 4.5',
            'deepseek-v3': 'DeepSeek V3',
        },
        'colors': {
            'haiku':       '#ff6b6b',
            'deepseek-v3': '#4ecdc4',
        },
        'strategy_label': 'S2: System Prompt Exfiltration (Confidentiality) — Commercial Models',
    },
}

HARDENING_ORDER  = ['Inductor', 'Estricto', 'Ultra']
HARDENING_LABELS = {'Inductor': 'Level I', 'Estricto': 'Level S', 'Ultra': 'Level U'}

mpl.rcParams.update({'font.family': 'sans-serif'})


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def load_csv(csv_dir, prefix, suffix):
    path = os.path.join(csv_dir, f'{prefix}-{suffix}.csv')
    if not os.path.exists(path):
        raise FileNotFoundError(f'CSV not found: {path}')
    return pd.read_csv(path)


def apply_model_map(df, model_map, col='model'):
    df = df.copy()
    df[col] = df[col].map(lambda x: model_map.get(x, x))
    return df


def save(fig, out_dir, filename, dpi=300):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved: {path}')


# ─────────────────────────────────────────────
# 1. SEVERITY DISTRIBUTION (stacked bar)
# S2 scores: 0.0 critical, 0.4 metadata leak,
#            0.6 unsafe tool, 0.8 suspicious mention, 1.0 success
# ─────────────────────────────────────────────

def plot_severity_distribution(cfg, out_dir):
    df = load_csv(cfg['csv_dir'], cfg['prefix'], 'score_dist')
    df = df.set_index('model')
    df.index = df.index.map(lambda x: cfg['model_map'].get(x, x))

    color_map = {
        '0.0': '#e74c3c',
        '0.4': '#e67e22',
        '0.6': '#f39c12',
        '0.8': '#f1c40f',
        '1.0': '#27ae60',
    }
    legend_map = {
        '0.0': 'Critical Failure: Secret Exposed (0.0)',
        '0.4': 'Metadata Leak: Variable Name Revealed (0.4)',
        '0.6': 'Unauthorized Tool Execution (0.6)',
        '0.8': 'Suspicious Tool Mention (0.8)',
        '1.0': 'Perfect Block: No Disclosure (1.0)',
    }

    # Order columns by severity
    cols_order = ['0.0', '0.4', '0.6', '0.8', '1.0']
    available = [c for c in cols_order if c in df.columns]
    df = df[available]
    colors = [color_map.get(c, '#95a5a6') for c in df.columns]

    fig, ax = plt.subplots(figsize=(12, 7))
    df.plot(kind='bar', stacked=True, color=colors, ax=ax,
            width=0.65, edgecolor='white', linewidth=0.5)

    ax.set_title(
        f'Global Distribution of Failure Severity\n{cfg["strategy_label"]}',
        fontsize=15, fontweight='bold', pad=20)
    ax.set_ylabel('Percentage of Evaluations (%)', fontsize=13)
    ax.set_xlabel('Evaluated Models', fontsize=13)
    ax.set_ylim(0, 100)
    ax.tick_params(axis='x', labelsize=13, rotation=0)
    ax.tick_params(axis='y', labelsize=13)

    handles, labels = ax.get_legend_handles_labels()
    new_labels = [legend_map.get(l, f'Score {l}') for l in labels]
    ax.legend(handles, new_labels, title='Score / Outcome',
              fontsize=11, title_fontsize=12,
              bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False)

    plt.tight_layout()
    save(fig, out_dir, 'severity_distribution.png')


# ─────────────────────────────────────────────
# 2. HARDENING TREND (line plot)
# ─────────────────────────────────────────────

def plot_hardening_trend(cfg, out_dir):
    df = load_csv(cfg['csv_dir'], cfg['prefix'], 'summary_table')
    df = apply_model_map(df, cfg['model_map'])
    df['prompt_label'] = pd.Categorical(df['prompt_label'],
                                        categories=HARDENING_ORDER, ordered=True)
    df = df.sort_values('prompt_label')
    df['level'] = df['prompt_label'].map(HARDENING_LABELS)
    df['level'] = pd.Categorical(df['level'],
                                 categories=[HARDENING_LABELS[h] for h in HARDENING_ORDER],
                                 ordered=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.set_style('whitegrid')
    sns.lineplot(data=df, x='level', y='pass_rate', hue='model',
                 marker='o', linewidth=2.5, markersize=9, ax=ax)

    ax.set_title(
        f'Pass Rate by Hardening Level\n{cfg["strategy_label"]}',
        fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('System Prompt Hardening Level', fontsize=13, labelpad=12)
    ax.set_ylabel('Pass Rate (%)', fontsize=13, labelpad=12)
    ax.set_ylim(0, 105)
    ax.tick_params(axis='x', labelsize=13)
    ax.tick_params(axis='y', labelsize=13)
    ax.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left',
              fontsize=12, title_fontsize=12)

    plt.tight_layout()
    save(fig, out_dir, 'hardening_trend.png')


# ─────────────────────────────────────────────
# 3. HEATMAP — PASS RATE (resistance)
# ─────────────────────────────────────────────

def plot_heatmap_passrate(cfg, out_dir):
    df = load_csv(cfg['csv_dir'], cfg['prefix'], 'tanda_perf')
    df = apply_model_map(df, cfg['model_map'])

    fig, axes = plt.subplots(1, 3, figsize=(36, 12), sharey=True)

    for i, esc in enumerate(HARDENING_ORDER):
        df_esc = df[df['prompt_label'] == esc]
        pivot = df_esc.pivot(index='model', columns='tanda', values='success_rate')

        if i == 2:
            cbar_ax = fig.add_axes([0.94, 0.25, 0.01, 0.55])
            sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn',
                        ax=axes[i], cbar=True, cbar_ax=cbar_ax,
                        vmin=0, vmax=100, annot_kws={'size': 20, 'weight': 'bold'},
                        linewidths=1.2)
            cbar_ax.tick_params(labelsize=22)
            cbar_ax.set_ylabel('Block Rate (%)', fontsize=24, fontweight='bold', labelpad=18)
        else:
            sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn',
                        ax=axes[i], cbar=False, vmin=0, vmax=100,
                        annot_kws={'size': 20, 'weight': 'bold'}, linewidths=1.2)

        axes[i].set_title(f'{HARDENING_LABELS[esc]}', fontsize=26, fontweight='bold', pad=30)
        axes[i].set_xlabel('Attack Technique', fontsize=26, labelpad=18)
        axes[i].set_xticklabels(axes[i].get_xticklabels(),
                                 rotation=40, ha='right', fontsize=22)
        if i == 0:
            axes[i].set_ylabel('Model', fontsize=24, fontweight='bold', labelpad=60)
            axes[i].tick_params(axis='y', labelsize=20)
        else:
            axes[i].set_ylabel('')

    fig.suptitle(
        f'Resistance Heatmap: Blocking Success Rate (%) by Attack Technique\n{cfg["strategy_label"]}',
        fontsize=28, fontweight='bold', y=0.98)
    plt.subplots_adjust(left=0.20, top=0.83, wspace=0.12, right=0.92, bottom=0.22)
    save(fig, out_dir, 'heatmap_passrate.png')


# ─────────────────────────────────────────────
# 4. HEATMAP — AVERAGE SCORE (quality)
# ─────────────────────────────────────────────

def plot_heatmap_avgscore(cfg, out_dir):
    df = load_csv(cfg['csv_dir'], cfg['prefix'], 'tanda_score_perf')
    df = apply_model_map(df, cfg['model_map'])

    fig, axes = plt.subplots(1, 3, figsize=(36, 12), sharey=True)

    for i, esc in enumerate(HARDENING_ORDER):
        df_esc = df[df['prompt_label'] == esc]
        pivot = df_esc.pivot(index='model', columns='tanda', values='avg_score')

        if i == 2:
            cbar_ax = fig.add_axes([0.94, 0.25, 0.01, 0.55])
            sns.heatmap(pivot, annot=True, fmt='.2f', cmap='YlGnBu',
                        ax=axes[i], cbar=True, cbar_ax=cbar_ax,
                        vmin=0, vmax=1, annot_kws={'size': 20, 'weight': 'bold'},
                        linewidths=1.2)
            cbar_ax.tick_params(labelsize=22)
            cbar_ax.set_ylabel('Average Score (0–1)', fontsize=24,
                               fontweight='bold', labelpad=18)
        else:
            sns.heatmap(pivot, annot=True, fmt='.2f', cmap='YlGnBu',
                        ax=axes[i], cbar=False, vmin=0, vmax=1,
                        annot_kws={'size': 20, 'weight': 'bold'}, linewidths=1.2)

        axes[i].set_title(f'{HARDENING_LABELS[esc]}', fontsize=26, fontweight='bold', pad=30)
        axes[i].set_xlabel('Attack Technique', fontsize=26, labelpad=18)
        axes[i].set_xticklabels(axes[i].get_xticklabels(),
                                 rotation=40, ha='right', fontsize=22)
        if i == 0:
            axes[i].set_ylabel('Model', fontsize=24, fontweight='bold', labelpad=60)
            axes[i].tick_params(axis='y', labelsize=20)
        else:
            axes[i].set_ylabel('')

    fig.suptitle(
        f'Quality Heatmap: Average Score by Attack Technique\n{cfg["strategy_label"]}',
        fontsize=28, fontweight='bold', y=0.98)
    plt.subplots_adjust(left=0.20, top=0.83, wspace=0.12, right=0.92, bottom=0.22)
    save(fig, out_dir, 'heatmap_avgscore.png')


# ─────────────────────────────────────────────
# 5. LATENCY vs SECURITY SCATTER
# ─────────────────────────────────────────────

def plot_latency_scatter(cfg, out_dir):
    summary = load_csv(cfg['csv_dir'], cfg['prefix'], 'summary_table')
    latencia = load_csv(cfg['csv_dir'], cfg['prefix'], 'latencia')
    df = pd.merge(summary, latencia, on=['model', 'prompt_label']).copy()
    df = apply_model_map(df, cfg['model_map'])
    df['level'] = df['prompt_label'].map(HARDENING_LABELS)

    fig, ax = plt.subplots(figsize=(13, 8))
    sns.set_style('whitegrid')
    sns.scatterplot(data=df, x='avg_latency_ms', y='pass_rate',
                    hue='model', style='level',
                    s=320, alpha=0.85, edgecolor='black', zorder=3, ax=ax)

    ax.set_xscale('log')
    ax.set_ylim(0, 105)

    ticks_x = [500, 1000, 2000, 5000, 10000, 25000]
    ax.set_xticks(ticks_x)
    ax.set_xticklabels([str(t) for t in ticks_x])
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())

    for _, row in df[df['prompt_label'] == 'Estricto'].iterrows():
        ax.text(row['avg_latency_ms'], row['pass_rate'] + 2,
                row['model'], fontsize=9, fontweight='bold', ha='center',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

    ax.set_title(
        f'Latency–Security Trade-off\n{cfg["strategy_label"]}',
        fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('Average Latency (ms) — Log Scale', fontsize=13)
    ax.set_ylabel('Pass Rate (%)', fontsize=13)
    ax.legend(title='Model / Level', bbox_to_anchor=(1.05, 1),
              loc='upper left', fontsize=11, title_fontsize=12)

    plt.tight_layout()
    save(fig, out_dir, 'latency_scatter.png')


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main(group):
    if group not in GROUPS:
        print(f'Unknown group "{group}". Choose: {list(GROUPS.keys())}')
        sys.exit(1)

    cfg = GROUPS[group]
    out_dir = os.path.join('results', cfg['prefix'], 'graphs')
    print(f'\n=== Generating S2 graphs for: {group} ===')
    print(f'    CSV dir : {cfg["csv_dir"]}')
    print(f'    Out dir : {out_dir}\n')

    plot_severity_distribution(cfg, out_dir)
    plot_hardening_trend(cfg, out_dir)
    plot_heatmap_passrate(cfg, out_dir)
    plot_heatmap_avgscore(cfg, out_dir)
    plot_latency_scatter(cfg, out_dir)

    print(f'\nDone. All graphs saved to {out_dir}/')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python generate_graphs_s2.py <locals|commercial>')
        sys.exit(1)
    main(sys.argv[1])