"""
Task 4 - Consumption by Building Type (Statistics)
COM7023 Maths for Data Science - Urban Resource Intelligence

Tests whether daily average resource consumption differs between three
residential building types (Apartments, Terraced houses, Detached
houses) using a one-way ANOVA, with Shapiro-Wilk and Levene's tests to
check the assumptions first, and Tukey HSD as the post-hoc test.
"""

import os
import numpy as np
import scipy.stats as stats
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# ============================================================
# 1. SETUP: The three consumption samples
# ============================================================

apartments = np.array([16.8, 17.2, 16.5, 17.9, 18.1, 17.4, 16.9, 17.6])
terraced = np.array([18.4, 18.9, 19.1, 18.7, 19.3, 18.6, 19.0, 18.8, 19.2, 18.5])
detached = np.array([20.1, 19.7, 20.4, 19.9, 20.6, 20.2])
groups = {'Apartments': apartments, 'Terraced': terraced, 'Detached': detached}

print("=" * 60)
print("TASK 4 - CONSUMPTION BY BUILDING TYPE (STATISTICS)")
print("=" * 60)

# ============================================================
# 2. DESCRIPTIVE STATISTICS PER GROUP
# ============================================================

print("\n" + "-" * 60)
print("1. DESCRIPTIVE STATISTICS PER GROUP")
print("-" * 60)

print(f"{'Group':<12} {'n':<6} {'Mean':<10} {'SD':<10} {'Min':<8} {'Max':<8}")
print("-" * 60)
for name, d in groups.items():
    print(f"{name:<12} {len(d):<6} {d.mean():<10.4f} {d.std(ddof=1):<10.4f} {d.min():<8.2f} {d.max():<8.2f}")

# ============================================================
# 3. ASSUMPTION CHECKS
# ============================================================

print("\n" + "-" * 60)
print("2. ASSUMPTION CHECKS")
print("-" * 60)

print("2a. Normality Check (Shapiro-Wilk):")
print("    H0: Data follows a normal distribution")
print("    H1: Data does NOT follow a normal distribution")
print(f"{'Group':<12} {'W-statistic':<16} {'p-value':<16} {'Normal?'}")
print("-" * 55)

shapiro_results = {}
for name, d in groups.items():
    w, p = stats.shapiro(d)
    shapiro_results[name] = (w, p)
    print(f"{name:<12} {w:<16.4f} {p:<16.4f} {'Yes' if p > 0.05 else 'No'}")

all_normal = all(p > 0.05 for _, p in shapiro_results.values())
print(f"\n  -> {'All groups appear normally distributed' if all_normal else 'Not all groups are normally distributed'} (p > 0.05).")

print("\n2b. Equal Variances Check (Levene's Test):")
print("    H0: All group variances are equal")
print("    H1: At least one group variance differs")

lev_stat, lev_p = stats.levene(apartments, terraced, detached)
print(f"    Levene statistic = {lev_stat:.4f}")
print(f"    p-value          = {lev_p:.4f}")

equal_var = lev_p > 0.05
print(f"\n  -> Variances are {'equal' if equal_var else 'not equal'} (p {'>' if equal_var else '<='} 0.05) - "
      f"{'standard ANOVA is appropriate.' if equal_var else 'consider Welch ANOVA.'}")

# ============================================================
# 4. ONE-WAY ANOVA
# ============================================================

print("\n" + "-" * 60)
print("3. ONE-WAY ANOVA")
print("-" * 60)

print("    H0: mean_apartments = mean_terraced = mean_detached (all means equal)")
print("    H1: At least one group mean differs from the others")
print("    alpha = 0.05")

f_stat, anova_p = stats.f_oneway(apartments, terraced, detached)
print(f"\n    F-statistic = {f_stat:.4f}")
print(f"    p-value     = {anova_p:.6f}")

reject_h0 = anova_p < 0.05
print(f"\n  -> p = {anova_p:.6f} {'<' if reject_h0 else '>='} 0.05 -> {'REJECT H0.' if reject_h0 else 'FAIL TO REJECT H0.'}")
if reject_h0:
    print("  -> There is a statistically significant difference in mean daily")
    print("     consumption between building types.")

# ============================================================
# 5. POST-HOC ANALYSIS (Tukey HSD)
# ============================================================

print("\n" + "-" * 60)
print("4. POST-HOC ANALYSIS (Tukey HSD)")
print("-" * 60)

all_vals = np.concatenate([apartments, terraced, detached])
all_labels = ['Apartments'] * len(apartments) + ['Terraced'] * len(terraced) + ['Detached'] * len(detached)
tukey = pairwise_tukeyhsd(all_vals, all_labels, alpha=0.05)
print(tukey)

print("\nTukey HSD interpretation:")
print("  Groups sharing the same letter/reject=False are NOT significantly different.")
print("  Groups with reject=True have significantly different means.")

# ============================================================
# 6. VISUALISATION - Boxplot by building type
# ============================================================

print("\n" + "-" * 60)
print("5. VISUALISATION - Boxplot by Building Type")
print("-" * 60)

sns.set_theme(style="whitegrid", palette="muted")

df = pd.DataFrame({'Building Type': all_labels, 'Daily Consumption (units)': all_vals})

fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x='Building Type', y='Daily Consumption (units)',
            hue='Building Type', palette='muted', width=0.6, legend=False, ax=ax)
sns.stripplot(data=df, x='Building Type', y='Daily Consumption (units)',
              color='black', alpha=0.5, size=6, ax=ax)

for i, name in enumerate(['Apartments', 'Terraced', 'Detached']):
    ax.plot(i, groups[name].mean(), 'D', color='red', markersize=8, zorder=5)

ax.set_title('Task 4: Daily Water Consumption by Building Type\n(Red diamonds = group means)',
             fontsize=13, fontweight='bold')
plt.tight_layout()

os.makedirs('figures', exist_ok=True)
fig_path = 'figures/fig_task4_boxplot.png'
plt.savefig(fig_path, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Figure saved: {fig_path}")

# ============================================================
# 7. SUMMARY OF FINDINGS
# ============================================================

print("\n" + "-" * 60)
print("6. SUMMARY OF FINDINGS")
print("-" * 60)

for name in ['Apartments', 'Terraced', 'Detached']:
    d = groups[name]
    print(f"  {name}: mean = {d.mean():.2f}, n = {len(d)}")

n_total = len(all_vals)
df_between = len(groups) - 1
df_within = n_total - len(groups)
print(f"  ANOVA:      F({df_between},{df_within}) = {f_stat:.2f}, p = {anova_p:.6f}")
print("  Tukey HSD:  See table above for pairwise comparisons.")

print("\n  Key interpretation:")
print("  - Detached homes show the highest consumption, suggesting they are")
print("    the priority segment for efficiency interventions.")
print("  - Apartments show the lowest consumption, likely due to shared")
print("    infrastructure and smaller living spaces.")
print("  - Terraced homes fall in between, but may differ significantly")
print("    from both other groups (check Tukey HSD results).")

print("\n" + "=" * 60)
print("TASK 4 COMPLETE")
print("=" * 60)
