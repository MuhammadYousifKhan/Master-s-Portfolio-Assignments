"""
Task 3 - Forecasting Error Risk (Probability)
COM7023 Maths for Data Science - Urban Resource Intelligence

Short-term forecasting errors are assumed to follow a normal
distribution:
    Error ~ N(mu=0, sigma=5)          (units)

Finds the probability of large deviations at +/-1, +/-2 and +/-3
standard deviations, to support risk management and contingency
planning around forecast buffers.
"""

import os
import numpy as np
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt

# ============================================================
# 1. SETUP: Define the forecast error distribution
# ============================================================

mu, sigma = 0, 5
thresholds = [5, 10, 15]   # +/-1, +/-2, +/-3 standard deviations

print("=" * 60)
print("TASK 3 - FORECASTING ERROR RISK (PROBABILITY)")
print("=" * 60)

print(f"\nForecast error ~ N(mu={mu}, sigma={sigma})")

# ============================================================
# 2. TAIL PROBABILITIES: P(|error| > threshold)
# ============================================================

print("\n" + "-" * 50)
print("TAIL PROBABILITIES")
print("-" * 50)

probabilities = {}
for t in thresholds:
    p = 2 * (1 - stats.norm.cdf(t, loc=mu, scale=sigma))
    probabilities[t] = p
    z = (t - mu) / sigma
    print(f"  z = {z:.1f}:  P(|error| > {t}) = {p:.4f}  ({p * 100:.2f}%)")

print("\n" + "-" * 50)
print("BUFFER COVERAGE (probability the error stays within the buffer)")
print("-" * 50)

for t in thresholds:
    p_in = 1 - probabilities[t]
    print(f"  P(|error| <= {t}) = {p_in:.4f}  ({p_in * 100:.2f}%)")

# ============================================================
# 3. VERIFICATION against scipy.stats.norm.cdf
# ============================================================

print("\n" + "-" * 50)
print("VERIFICATION AGAINST scipy.stats.norm.cdf")
print("-" * 50)

for t in thresholds:
    cdf_val = stats.norm.cdf(t, loc=mu, scale=sigma)
    print(f"  norm.cdf({t}, loc={mu}, scale={sigma}) = {cdf_val:.4f}")

# ============================================================
# 4. VISUALISATION - probability density curve with shaded bands
# ============================================================

print("\n" + "-" * 50)
print("GENERATING FIGURE...")
print("-" * 50)

sns.set_theme(style="whitegrid", palette="muted")

x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 1000)
y = stats.norm.pdf(x, mu, sigma)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y, color='#2c7bb6', linewidth=2.5, label=f'N({mu}, {sigma}²)')

# Shade only the tail regions (beyond each threshold), leaving the
# central +/-1 SD band unshaded. Each band is drawn once rather than
# stacked on top of each other, so the colours stay clean and distinct
# instead of blending into a muddy overlap where the tails meet.
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
for lo, hi, color in zip(thresholds[:-1], thresholds[1:], colors[:-1]):
    band = (np.abs(x) >= lo) & (np.abs(x) <= hi)
    ax.fill_between(x, y, where=band, color=color, alpha=0.5)
outer_band = np.abs(x) >= thresholds[-1]
ax.fill_between(x, y, where=outer_band, color=colors[-1], alpha=0.5)

for t, color in zip(thresholds, colors):
    ax.axvline(-t, color=color, linestyle='--', linewidth=1.5, alpha=0.8)
    ax.axvline(t, color=color, linestyle='--', linewidth=1.5, alpha=0.8)

# Annotate each threshold - spaced out vertically so the labels don't
# collide with each other in the low-probability part of the tail.
label_y = [0.030, 0.014, 0.0035]
for t, color, y_pos in zip(thresholds, colors, label_y):
    sd = t // sigma
    ax.annotate(f'±{sd}σ\n{probabilities[t] * 100:.2f}% beyond',
                xy=(t, y_pos), fontsize=9, ha='left', color=color, fontweight='bold')

ax.set_xlabel('Forecast Error (units)', fontsize=12)
ax.set_ylabel('Probability Density', fontsize=12)
ax.set_title('Task 3: Distribution of Forecast Errors (N(0, σ=5))\n'
             'Shaded Regions Show Probability of Large Deviations', fontsize=13)
ax.legend(loc='upper left')
plt.tight_layout()

os.makedirs('figures', exist_ok=True)
fig_path = 'figures/fig_task3_normal_curve.png'
plt.savefig(fig_path, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Figure saved to '{fig_path}'")

# ============================================================
# 5. RISK MANAGEMENT SUMMARY
# ============================================================

print("\n" + "-" * 50)
print("RISK MANAGEMENT SUMMARY")
print("-" * 50)

for t in thresholds:
    cov = (1 - probabilities[t]) * 100
    risk = probabilities[t] * 100
    print(f"  Buffer +/-{t}: covers {cov:.2f}% of days, risk of exceedance {risk:.2f}%")

print("\n" + "=" * 60)
print("TASK 3 COMPLETE")
print("=" * 60)
