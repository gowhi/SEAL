"""
generate_graphs_combined.py
Generates combined figures (locals + commercial side by side) for each
graph type across all three strategies.

Usage:
    python generate_graphs_combined.py <S1|S2|S3|ALL>

Output folder:
    results/combined/graphs/

Each output image contains both open-source and commercial panels
in a single figure, suitable for direct inclusion in the paper.

Structure assumed:
    Strategy1/Phase_3/results/S1-locals/CSV/
    Strategy1/Phase_3/results/S1-commercial/CSV/
    Strategy2/Phase3/results/S2-locals/CSV/
    Strategy2/Phase3/results/S2-commercial/CSV/
    Strategy3/Phase3/results/S3-locals/CSV/
    Strategy3/Phase3/results/S3-commercial/CSV/
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as ticker
import seaborn as sns

mpl.rcParams.update({'font.family': 'sans-serif'})

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

BASE = os.path.expanduser('~/Documentos/AIBench')

STRATEGIES = {
    'S1': {
        'label': 'S1: Direct Tool Injection (Integrity)',
        'locals': {
            'prefix': 'S1-locals',
            'csv_dir': os.path.join(BASE, 'Strategy1/Phase_3/results/S1-locals/CSV'),
            'model_map': {
                'gpt-oss-target':    'GPT-OSS',
                'llama':             'LLaMA 3.2',
                'mistral-target':    'Mistral',
                'qwen-coder-target': 'Qwen 2.5',
            },
        },
        'commercial': {
            'prefix': 'S1-commercial',
            'csv_dir': os.path.join(BASE, 'Strategy1/Phase_3/results/S1-commercial/CSV'),
            'model_map': {
                'haiku':       'Haiku 4.5',
                'deepseek-v3': 'DeepSeek V3',
            },
        },
        'score_dist_colors': {
            '0.0': '#e74c3c', '0.4': '#e67e22', '0.5': '#f1c40f',
            '0.6': '#f39c12', '0.9': '#a9dfbf', '1.0': '#27ae60',
        },
        'score_dist_legend': {
            '0.0': 'Critical (0.0)', '0.4': 'Partial Bypass (0.4)',
            '0.5': 'Inconclusive (0.5)', '0.6': 'Unsafe Leakage (0.6)',
            '0.9': 'Safe Tool Use (0.9)', '1.0': 'Explicit Block (1.0)',
        },
        'score_dist_order': ['0.0', '0.4', '0.5', '0.6', '0.9', '1.0'],
        'sar_metric': False,
    },
    'S2': {
        'label': 'S2: System Prompt Exfiltration (Confidentiality)',
        'locals': {
            'prefix': 'S2-locals',
            'csv_dir': os.path.join(BASE, 'Strategy2/Phase3/results/S2-locals/CSV'),
            'model_map': {
                'gpt-oss-target':    'GPT-OSS',
                'llama':             'LLaMA 3.2',
                'mistral-target':    'Mistral',
                'qwen-coder-target': 'Qwen 2.5',
            },
        },
        'commercial': {
            'prefix': 'S2-commercial',
            'csv_dir': os.path.join(BASE, 'Strategy2/Phase3/results/S2-commercial/CSV'),
            'model_map': {
                'haiku':       'Haiku 4.5',
                'deepseek-v3': 'DeepSeek V3',
            },
        },
        'score_dist_colors': {
            '0.0': '#e74c3c', '0.4': '#e67e22', '0.6': '#f39c12',
            '0.8': '#f1c40f', '1.0': '#27ae60',
        },
        'score_dist_legend': {
            '0.0': 'Secret Exposed (0.0)', '0.4': 'Metadata Leak (0.4)',
            '0.6': 'Unauth. Tool Exec. (0.6)', '0.8': 'Tool Mention (0.8)',
            '1.0': 'Perfect Block (1.0)',
        },
        'score_dist_order': ['0.0', '0.4', '0.6', '0.8', '1.0'],
        'sar_metric': False,
    },
    'S3': {
        'label': 'S3: Indirect Tool Injection & SDoS (Availability)',
        'locals': {
            'prefix': 'S3-locals',
            'csv_dir': os.path.join(BASE, 'Strategy3/Phase3/results/S3-locals/CSV'),
            'model_map': {
                'gpt-oss-target':    'GPT-OSS',
                'llama':             'LLaMA 3.2',
                'mistral-target':    'Mistral',
                'qwen-coder-target': 'Qwen 2.5',
            },
        },
        'commercial': {
            'prefix': 'S3-commercial',
            'csv_dir': os.path.join(BASE, 'Strategy3/Phase3/results/S3-commercial/CSV'),
            'model_map': {
                'haiku':       'Haiku 4.5',
                'deepseek-v3': 'DeepSeek V3',
            },
        },
        'score_dist_colors': {
            '0.0': '#e74c3c', '0.2': '#e67e22', '0.5': '#f1c40f', '1.0': '#27ae60',
        },
        'score_dist_legend': {
            '0.0': 'Context Hijacking (0.0)', '0.2': 'Partial Hijacking (0.2)',
            '0.5': 'Functional DoS (0.5)', '1.0': 'Full Success (1.0)',
        },
        'score_dist_order': ['0.0', '0.2', '0.5', '1.0'],
        'sar_metric': True,
    },
}

HARDENING_ORDER  = ['Inductor', 'Estricto', 'Ultra']
HARDENING_LABELS = {'Inductor': 'Level I', 'Estricto': 'Level S', 'Ultra': 'Level U'}

OUT_DIR = os.path.join(BASE, 'results/combined/graphs')


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


def save(fig, filename, dpi=300):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved: {path}')


# ─────────────────────────────────────────────
# 1. SEVERITY DISTRIBUTION
# ─────────────────────────────────────────────

def plot_severity_distribution(strat_key, scfg):
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    groups = [('locals', 'Open-Source Models'), ('commercial', 'Commercial Models')]

    for ax, (grp, grp_label) in zip(axes, groups):
        gcfg = scfg[grp]
        df = load_csv(gcfg['csv_dir'], gcfg['prefix'], 'score_dist')
        df = df.set_index('model')
        df.index = df.index.map(lambda x: gcfg['model_map'].get(x, x))
        df.columns = [str(float(c)) for c in df.columns]

        cols_order = scfg['score_dist_order']
        available = [c for c in cols_order if c in df.columns]
        df = df[available]
        colors = [scfg['score_dist_colors'].get(c, '#95a5a6') for c in df.columns]

        df.plot(kind='bar', stacked=True, color=colors, ax=ax,
                width=0.65, edgecolor='white', linewidth=0.5, legend=False)

        ax.set_title(grp_label, fontsize=13, fontweight='bold', pad=10)
        ax.set_ylabel('Evaluations (%)' if grp == 'locals' else '', fontsize=11)
        ax.set_xlabel('')
        ax.set_ylim(0, 100)
        ax.tick_params(axis='x', labelsize=11, rotation=0)
        ax.tick_params(axis='y', labelsize=11)

    # Shared legend on the right
    handles = [plt.Rectangle((0,0),1,1, color=scfg['score_dist_colors'].get(c,'#95a5a6'))
               for c in scfg['score_dist_order'] if c in scfg['score_dist_colors']]
    labels = [scfg['score_dist_legend'].get(c, c) for c in scfg['score_dist_order']
              if c in scfg['score_dist_colors']]
    fig.legend(handles, labels, title='Score / Outcome', fontsize=10, title_fontsize=11,
               bbox_to_anchor=(1.01, 0.9), loc='upper left', frameon=False)

    fig.suptitle(f'Global Distribution of Failure Severity\n{scfg["label"]}',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    save(fig, f'{strat_key}_severity_distribution.png')


# ─────────────────────────────────────────────
# 2. HARDENING TREND
# ─────────────────────────────────────────────

def plot_hardening_trend(strat_key, scfg):
    fig, axes = plt.subplots(1, 2, figsize=(16, 5), sharey=True)
    groups = [('locals', 'Open-Source Models'), ('commercial', 'Commercial Models')]
    ylabel = 'Pass Rate (%)'

    for ax, (grp, grp_label) in zip(axes, groups):
        gcfg = scfg[grp]
        df = load_csv(gcfg['csv_dir'], gcfg['prefix'], 'summary_table')
        df = apply_model_map(df, gcfg['model_map'])
        df['prompt_label'] = pd.Categorical(df['prompt_label'],
                                            categories=HARDENING_ORDER, ordered=True)
        df = df.sort_values('prompt_label')
        df['level'] = df['prompt_label'].map(HARDENING_LABELS)
        df['level'] = pd.Categorical(df['level'],
                                     categories=[HARDENING_LABELS[h] for h in HARDENING_ORDER],
                                     ordered=True)

        sns.set_style('whitegrid')
        sns.lineplot(data=df, x='level', y='pass_rate', hue='model',
                     marker='o', linewidth=2.5, markersize=8, ax=ax)

        ax.set_title(grp_label, fontsize=13, fontweight='bold')
        ax.set_xlabel('Hardening Level', fontsize=11)
        ax.set_ylabel(ylabel if grp == 'locals' else '', fontsize=11)
        ax.set_ylim(0, 105)
        ax.tick_params(labelsize=11)
        ax.legend(title='Model', fontsize=10, title_fontsize=10,
                  bbox_to_anchor=(1.02, 1), loc='upper left')

    fig.suptitle(f'Pass Rate by Hardening Level\n{scfg["label"]}',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    save(fig, f'{strat_key}_hardening_trend.png')


# ─────────────────────────────────────────────
# 3. HEATMAP PASS RATE — combined, shared y-labels
# ─────────────────────────────────────────────

def plot_heatmap_passrate(strat_key, scfg):
    """
    Layout: 6 panels (2 groups x 3 hardening levels)
    Row 0: locals  — Level I | Level S | Level U
    Row 1: commercial — Level I | Level S | Level U
    Y-axis labels (model names) shown only on leftmost column of each row.
    """
    fig, axes = plt.subplots(2, 3, figsize=(36, 16))
    cbar_label = 'Block Rate (%)'
    metric_col = 'success_rate'

    for row, grp in enumerate(['locals', 'commercial']):
        gcfg = scfg[grp]
        df = load_csv(gcfg['csv_dir'], gcfg['prefix'], 'tanda_perf')
        df = apply_model_map(df, gcfg['model_map'])
        grp_label = 'Open-Source' if grp == 'locals' else 'Commercial'

        for col, esc in enumerate(HARDENING_ORDER):
            ax = axes[row][col]
            df_esc = df[df['prompt_label'] == esc]
            pivot = df_esc.pivot(index='model', columns='tanda', values=metric_col)

            is_last_col = (col == 2)
            cbar_ax = None
            if row == 1 and is_last_col:
                cbar_ax = fig.add_axes([0.94, 0.12, 0.008, 0.76])

            sns.heatmap(pivot, annot=True, fmt='.0f', cmap='RdYlGn',
                        ax=ax, cbar=(row == 1 and is_last_col),
                        cbar_ax=cbar_ax,
                        vmin=0, vmax=100,
                        annot_kws={'size': 16, 'weight': 'bold'},
                        linewidths=1.0,
                        yticklabels=(col == 0))  # only show model names on left col

            if row == 1 and is_last_col and cbar_ax:
                cbar_ax.tick_params(labelsize=18)
                cbar_ax.set_ylabel(cbar_label, fontsize=20, fontweight='bold', labelpad=14)

            # Column titles (hardening level) only on top row
            if row == 0:
                ax.set_title(HARDENING_LABELS[esc], fontsize=22, fontweight='bold', pad=12)
            else:
                ax.set_title('')

            # Row label on the left
            if col == 0:
                ax.set_ylabel(grp_label, fontsize=18, fontweight='bold', labelpad=10)
                ax.tick_params(axis='y', labelsize=14)
            else:
                ax.set_ylabel('')
                ax.set_yticks([])

            # X-axis labels only on bottom row
            if row == 1:
                ax.set_xlabel('Attack Technique', fontsize=16, labelpad=10)
                ax.set_xticklabels(ax.get_xticklabels(),
                                   rotation=35, ha='right', fontsize=13)
            else:
                ax.set_xlabel('')
                ax.set_xticklabels([])

    title_prefix = 'Resistance Heatmap'
    fig.suptitle(f'{title_prefix}: Blocking Success Rate (%) by Attack Technique\n{scfg["label"]}',
                 fontsize=24, fontweight='bold', y=1.01)
    plt.subplots_adjust(left=0.10, right=0.92, top=0.93, bottom=0.12, hspace=0.08, wspace=0.05)
    save(fig, f'{strat_key}_heatmap_passrate.png')


# ─────────────────────────────────────────────
# 4. HEATMAP AVG SCORE — combined
# ─────────────────────────────────────────────

def plot_heatmap_avgscore(strat_key, scfg):
    fig, axes = plt.subplots(2, 3, figsize=(36, 16))

    for row, grp in enumerate(['locals', 'commercial']):
        gcfg = scfg[grp]
        df = load_csv(gcfg['csv_dir'], gcfg['prefix'], 'tanda_score_perf')
        df = apply_model_map(df, gcfg['model_map'])
        grp_label = 'Open-Source' if grp == 'locals' else 'Commercial'

        for col, esc in enumerate(HARDENING_ORDER):
            ax = axes[row][col]
            df_esc = df[df['prompt_label'] == esc]
            pivot = df_esc.pivot(index='model', columns='tanda', values='avg_score')

            cbar_ax = None
            if row == 1 and col == 2:
                cbar_ax = fig.add_axes([0.94, 0.12, 0.008, 0.76])

            sns.heatmap(pivot, annot=True, fmt='.2f', cmap='YlGnBu',
                        ax=ax, cbar=(row == 1 and col == 2),
                        cbar_ax=cbar_ax,
                        vmin=0, vmax=1,
                        annot_kws={'size': 16, 'weight': 'bold'},
                        linewidths=1.0,
                        yticklabels=(col == 0))

            if row == 1 and col == 2 and cbar_ax:
                cbar_ax.tick_params(labelsize=18)
                cbar_ax.set_ylabel('Average Score (0–1)', fontsize=20,
                                   fontweight='bold', labelpad=14)

            if row == 0:
                ax.set_title(HARDENING_LABELS[esc], fontsize=22, fontweight='bold', pad=12)
            else:
                ax.set_title('')

            if col == 0:
                ax.set_ylabel(grp_label, fontsize=18, fontweight='bold', labelpad=10)
                ax.tick_params(axis='y', labelsize=14)
            else:
                ax.set_ylabel('')
                ax.set_yticks([])

            if row == 1:
                ax.set_xlabel('Attack Technique', fontsize=16, labelpad=10)
                ax.set_xticklabels(ax.get_xticklabels(),
                                   rotation=35, ha='right', fontsize=13)
            else:
                ax.set_xlabel('')
                ax.set_xticklabels([])

    fig.suptitle(f'Quality Heatmap: Average Score by Attack Technique\n{scfg["label"]}',
                 fontsize=24, fontweight='bold', y=1.01)
    plt.subplots_adjust(left=0.10, right=0.92, top=0.93, bottom=0.12, hspace=0.08, wspace=0.05)
    save(fig, f'{strat_key}_heatmap_avgscore.png')


# ─────────────────────────────────────────────
# 5. LATENCY SCATTER — combined
# ─────────────────────────────────────────────

def plot_latency_scatter(strat_key, scfg):
    fig, axes = plt.subplots(1, 2, figsize=(22, 7))
    groups = [('locals', 'Open-Source Models'), ('commercial', 'Commercial Models')]
    ylabel = 'Pass Rate (%)'
    title_y = 'Latency–Security Trade-off'
    level_order = ['Level I', 'Level S', 'Level U']

    for ax, (grp, grp_label) in zip(axes, groups):
        gcfg = scfg[grp]
        summary = load_csv(gcfg['csv_dir'], gcfg['prefix'], 'summary_table')
        latencia = load_csv(gcfg['csv_dir'], gcfg['prefix'], 'latencia')
        df = pd.merge(summary, latencia, on=['model', 'prompt_label']).copy()
        df = apply_model_map(df, gcfg['model_map'])
        df['level'] = pd.Categorical(
            df['prompt_label'].map(HARDENING_LABELS),
            categories=level_order, ordered=True)

        sns.set_style('whitegrid')
        sns.scatterplot(data=df, x='avg_latency_ms', y='pass_rate',
                        hue='model', style='level',
                        hue_order=sorted(df['model'].unique()),
                        style_order=level_order,
                        s=280, alpha=0.85, edgecolor='black', zorder=3, ax=ax)

        ax.set_xscale('log')
        ax.set_ylim(0, 105)

        ticks_x = [500, 1000, 2000, 5000, 10000, 25000]
        ax.set_xticks(ticks_x)
        ax.set_xticklabels([str(t) for t in ticks_x], fontsize=10)
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())

        for _, row in df[df['prompt_label'] == 'Estricto'].iterrows():
            ax.text(row['avg_latency_ms'], row['pass_rate'] + 2,
                    row['model'], fontsize=8, fontweight='bold', ha='center',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

        ax.set_title(grp_label, fontsize=13, fontweight='bold')
        ax.set_xlabel('Average Latency (ms) — Log Scale', fontsize=11)
        ax.set_ylabel(ylabel if grp == 'locals' else '', fontsize=11)

        # Build ordered legend: models first, separator, then Level I → S → U
        handles, labels = ax.get_legend_handles_labels()
        model_names = sorted(df['model'].unique())
        model_h = [h for h, l in zip(handles, labels) if l in model_names]
        model_l = [l for l in labels if l in model_names]
        level_map = {l: h for h, l in zip(handles, labels) if l in level_order}
        level_h = [level_map[l] for l in level_order if l in level_map]
        level_l = [l for l in level_order if l in level_map]

        separator_h = plt.Line2D([], [], alpha=0)
        separator_l = ''

        ax.legend(
            model_h + [separator_h] + level_h,
            model_l + [separator_l] + level_l,
            title='Model / Level', fontsize=9, title_fontsize=10,
            bbox_to_anchor=(1.02, 1), loc='upper left',
            handletextpad=0.5, labelspacing=0.6,
        )

    fig.suptitle(f'{title_y}\n{scfg["label"]}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save(fig, f'{strat_key}_latency_scatter.png')


# ─────────────────────────────────────────────
# 6. RADAR CHART — per model, all strategies
# One radar per model showing PR and AS across
# all 3 hardening levels. Two figures: locals + commercial.
# Run with strat_key='RADAR' or called from main(ALL).
# ─────────────────────────────────────────────

RADAR_CATEGORIES = [
    'PR Ind.', 'PR Str.', 'PR Ult.',
    'AS Ult.', 'AS Str.', 'AS Ind.',
]

RADAR_STRATEGY_DIRS = {
    'S1': {'locals': 'S1-locals', 'commercial': 'S1-commercial',
           'locals_csv': os.path.join(BASE, 'Strategy1/Phase_3/results/S1-locals/CSV'),
           'comm_csv':   os.path.join(BASE, 'Strategy1/Phase_3/results/S1-commercial/CSV')},
    'S2': {'locals': 'S2-locals', 'commercial': 'S2-commercial',
           'locals_csv': os.path.join(BASE, 'Strategy2/Phase3/results/S2-locals/CSV'),
           'comm_csv':   os.path.join(BASE, 'Strategy2/Phase3/results/S2-commercial/CSV')},
    'S3': {'locals': 'S3-locals', 'commercial': 'S3-commercial',
           'locals_csv': os.path.join(BASE, 'Strategy3/Phase3/results/S3-locals/CSV'),
           'comm_csv':   os.path.join(BASE, 'Strategy3/Phase3/results/S3-commercial/CSV')},
}

RADAR_COLORS = {
    # locals
    'gpt-oss-target':    '#1f77b4',
    'llama':             '#ff7f0e',
    'mistral-target':    '#2ca02c',
    'qwen-coder-target': '#9467bd',
    # commercial
    'haiku':             '#d62728',
    'deepseek-v3':       '#17becf',
}

RADAR_MODEL_NAMES = {
    'gpt-oss-target':    'GPT-OSS (20B)',
    'llama':             'LLaMA 3.2 (3B)',
    'mistral-target':    'Mistral v0.3 (7B)',
    'qwen-coder-target': 'Qwen 2.5 Coder (7B)',
    'haiku':             'Claude Haiku 4.5',
    'deepseek-v3':       'DeepSeek V3',
}

RADAR_STRATEGY_LABELS = {
    'S1': 'Integrity (S1)',
    'S2': 'Confidentiality (S2)',
    'S3': 'Availability (S3)',
}


def _load_radar_data(grp_key):
    """Load and merge summary_table CSVs for all 3 strategies for one group."""
    frames = []
    for sk, sdirs in RADAR_STRATEGY_DIRS.items():
        csv_dir = sdirs['locals_csv'] if grp_key == 'locals' else sdirs['comm_csv']
        prefix  = sdirs['locals']     if grp_key == 'locals' else sdirs['commercial']
        try:
            df = load_csv(csv_dir, prefix, 'summary_table')
            df['strategy'] = sk
            frames.append(df)
        except FileNotFoundError as e:
            print(f'  Warning: {e}')
    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)


def _radar_values_for_model(df, model_id, strategy):
    """Extract 6 radar values for one model+strategy."""
    sub = df[(df['model'] == model_id) & (df['strategy'] == strategy)]
    if sub.empty:
        return None
    sub = sub.set_index('prompt_label')
    def _get(label, col):
        try:
            v = sub.loc[label, col]
            return float(v) / 100.0 if col == 'pass_rate' else float(v)
        except KeyError:
            return 0.0
    return [
        _get('Inductor', 'pass_rate'),
        _get('Estricto', 'pass_rate'),
        _get('Ultra',    'pass_rate'),
        _get('Ultra',    'avg_score'),
        _get('Estricto', 'avg_score'),
        _get('Inductor', 'avg_score'),
    ]


def plot_radar(grp_key):
    """
    Generate a radar summary figure for one group (locals or commercial).
    Layout: one subplot per model (2×2 for locals, 1×2 for commercial).
    Each subplot overlays S1, S2, S3 as separate radar traces.
    """
    from math import pi

    model_map = (STRATEGIES['S1']['locals']['model_map']
                 if grp_key == 'locals'
                 else STRATEGIES['S1']['commercial']['model_map'])

    df = _load_radar_data(grp_key)
    if df is None:
        print(f'  Skipping radar for {grp_key} — no data.')
        return

    model_ids = list(model_map.keys())
    n_models  = len(model_ids)
    n_cats    = len(RADAR_CATEGORIES)
    angles    = [i / float(n_cats) * 2 * pi for i in range(n_cats)]
    angles   += angles[:1]

    strategy_colors = {'S1': '#1f77b4', 'S2': '#e67e22', 'S3': '#27ae60'}
    strategy_styles = {'S1': '-', 'S2': '--', 'S3': '-.'}

    nrows = 2 if n_models > 2 else 1
    ncols = 2
    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(13, 13 if nrows == 2 else 7),
                             subplot_kw=dict(polar=True))
    axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]

    for i, model_id in enumerate(model_ids):
        ax = axes[i]
        model_color = RADAR_COLORS.get(model_id, '#7f7f7f')
        display_name = RADAR_MODEL_NAMES.get(model_id, model_id)

        for sk in ['S1', 'S2', 'S3']:
            vals = _radar_values_for_model(df, model_id, sk)
            if vals is None:
                continue
            vals += vals[:1]
            sc = strategy_colors[sk]
            ax.plot(angles, vals, linewidth=2,
                    linestyle=strategy_styles[sk],
                    color=sc, label=RADAR_STRATEGY_LABELS[sk])
            ax.fill(angles, vals, color=sc, alpha=0.10)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(RADAR_CATEGORIES, fontsize=11, fontweight='bold')
        ax.tick_params(axis='x', pad=12)
        ax.set_ylim(0, 1.1)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_title(display_name, size=13, pad=25,
                     color=model_color, fontweight='bold')
        ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15),
                  fontsize=9, frameon=True)

    # Hide unused subplots
    for j in range(n_models, len(axes)):
        axes[j].set_visible(False)

    grp_label = 'Open-Source Models' if grp_key == 'locals' else 'Commercial Models'
    fig.suptitle(f'Security Radar — {grp_label}\nPass Rate & Average Score across S1, S2, S3',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout(pad=4.0)
    save(fig, f'radar_{grp_key}.png')


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main(strat_key):
    if strat_key == 'RADAR':
        print(f'\n=== Generating radar charts ===')
        print(f'    Output dir: {OUT_DIR}\n')
        plot_radar('locals')
        plot_radar('commercial')
        print(f'\nDone. Radars saved to {OUT_DIR}/')
        return

    if strat_key == 'ALL':
        for sk in ['S1', 'S2', 'S3']:
            main(sk)
        plot_radar('locals')
        plot_radar('commercial')
        return

    if strat_key not in STRATEGIES:
        print(f'Unknown key "{strat_key}". Choose: S1 | S2 | S3 | RADAR | ALL')
        sys.exit(1)

    scfg = STRATEGIES[strat_key]
    print(f'\n=== Generating combined graphs for: {strat_key} ===')
    print(f'    Output dir: {OUT_DIR}\n')

    plot_severity_distribution(strat_key, scfg)
    plot_hardening_trend(strat_key, scfg)
    plot_heatmap_passrate(strat_key, scfg)
    plot_heatmap_avgscore(strat_key, scfg)
    plot_latency_scatter(strat_key, scfg)

    print(f'\nDone. All graphs saved to {OUT_DIR}/')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python generate_graphs_combined.py <S1|S2|S3|RADAR|ALL>')
        sys.exit(1)
    main(sys.argv[1].upper())