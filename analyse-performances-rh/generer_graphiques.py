"""Genere les 6 visualisations du rapport a partir des donnees brutes.
Sortie : assets/*.png
"""
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

df = pd.read_csv('data/HRDataset_v14.csv', encoding='utf-8-sig')
df['Department'] = df['Department'].str.strip()

BLUE, ORANGE, AQUA, YELLOW, VIOLET, RED = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#4a3aa7', '#e34948'
INK, INK2, MUTED, GRID, SURFACE = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#fcfcfb'

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Segoe UI', 'Arial'],
    'text.color': INK, 'axes.edgecolor': GRID, 'axes.labelcolor': INK2,
    'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.facecolor': SURFACE,
    'figure.facecolor': SURFACE, 'savefig.facecolor': SURFACE, 'font.size': 11,
})

def save(fig, name):
    fig.savefig(f'assets/{name}.png', dpi=180, bbox_inches='tight')
    plt.close(fig)

# 1. Histogramme engagement
fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.hist(df['EngagementSurvey'], bins=15, color=BLUE, edgecolor=SURFACE, linewidth=1.2)
mean_v, med_v = df['EngagementSurvey'].mean(), df['EngagementSurvey'].median()
ax.axvline(mean_v, color=RED, linestyle='--', linewidth=1.5, label=f'Moyenne = {mean_v:.2f}')
ax.axvline(med_v, color=VIOLET, linestyle=':', linewidth=1.5, label=f'Médiane = {med_v:.2f}')
ax.set_xlabel("Score d'engagement (EngagementSurvey)")
ax.set_ylabel("Nombre d'employés")
ax.spines[['top', 'right']].set_visible(False)
ax.legend(frameon=False)
ax.grid(axis='y', color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
save(fig, 'histogramme-engagement')

# 2. Boxplot salaire par departement
fig, ax = plt.subplots(figsize=(7.5, 4.8))
depts = df.groupby('Department')['Salary'].median().sort_values(ascending=False).index
data = [df.loc[df['Department'] == d, 'Salary'].values for d in depts]
ax.boxplot(data, vert=False, tick_labels=list(depts), patch_artist=True,
           medianprops=dict(color=RED, linewidth=2),
           boxprops=dict(facecolor=BLUE, alpha=0.35, edgecolor=BLUE),
           whiskerprops=dict(color=INK2), capprops=dict(color=INK2),
           flierprops=dict(marker='o', markerfacecolor=ORANGE, markeredgecolor=ORANGE, markersize=5, alpha=0.7))
ax.set_xlabel("Salaire annuel ($)")
ax.spines[['top', 'right']].set_visible(False)
ax.grid(axis='x', color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', ' ')))
save(fig, 'boxplot-salaire-departement')

# 3. Pie chart performance
fig, ax = plt.subplots(figsize=(5.5, 5.5))
order = ['Fully Meets', 'Exceeds', 'Needs Improvement', 'PIP']
counts = df['PerformanceScore'].value_counts().reindex(order)
labels_fr = ['Répond aux attentes', 'Dépasse les attentes', 'À améliorer', 'PIP (plan de redressement)']
colors = [BLUE, AQUA, YELLOW, RED]
wedges, texts, autotexts = ax.pie(counts, labels=None, colors=colors, autopct='%1.1f%%',
       startangle=90, pctdistance=0.75, wedgeprops=dict(edgecolor=SURFACE, linewidth=2))
for at in autotexts:
    at.set_color('white')
    at.set_fontweight('bold')
    at.set_fontsize(10)
ax.legend(wedges, [f'{l} (n={c})' for l, c in zip(labels_fr, counts)], loc='upper center',
          bbox_to_anchor=(0.5, -0.02), frameon=False, ncol=1)
save(fig, 'repartition-performance')

# 4. Barres engagement par departement
fig, ax = plt.subplots(figsize=(6.5, 4.2))
dept_eng = df.groupby('Department')['EngagementSurvey'].mean().sort_values()
bars = ax.barh(dept_eng.index, dept_eng.values, color=BLUE)
for b, v in zip(bars, dept_eng.values):
    ax.text(v + 0.03, b.get_y() + b.get_height()/2, f'{v:.2f}', va='center', color=INK2, fontsize=9)
ax.set_xlabel("Score d'engagement moyen")
ax.spines[['top', 'right']].set_visible(False)
ax.grid(axis='x', color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
ax.set_xlim(0, 5.5)
save(fig, 'barres-engagement-departement')

# 5. Boxplots absences / retards
fig, axes = plt.subplots(1, 2, figsize=(8, 4))
for ax_, col, title in [(axes[0], 'Absences', 'Absences (30 derniers jours)'),
                         (axes[1], 'DaysLateLast30', 'Retards (DaysLateLast30)')]:
    ax_.boxplot(df[col], patch_artist=True,
                medianprops=dict(color=RED, linewidth=2),
                boxprops=dict(facecolor=BLUE, alpha=0.35, edgecolor=BLUE),
                whiskerprops=dict(color=INK2), capprops=dict(color=INK2),
                flierprops=dict(marker='o', markerfacecolor=ORANGE, markeredgecolor=ORANGE, markersize=5))
    ax_.set_title(title, fontsize=10, color=INK)
    ax_.set_xticks([])
    ax_.spines[['top', 'right']].set_visible(False)
save(fig, 'boxplot-absences-retards')

# 6. Scatter retards x engagement colore par performance
fig, ax = plt.subplots(figsize=(6.5, 4.5))
color_map = {'Fully Meets': BLUE, 'Exceeds': AQUA, 'Needs Improvement': YELLOW, 'PIP': RED}
for cat, col in color_map.items():
    sub = df[df['PerformanceScore'] == cat]
    ax.scatter(sub['DaysLateLast30'], sub['EngagementSurvey'], color=col, alpha=0.7, s=35,
               label=cat, edgecolor=SURFACE, linewidth=0.5)
ax.set_xlabel('Jours de retard (30 derniers jours)')
ax.set_ylabel("Score d'engagement")
ax.spines[['top', 'right']].set_visible(False)
ax.grid(color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=9)
save(fig, 'scatter-retards-engagement')

print("OK - 6 graphiques generes dans assets/")
