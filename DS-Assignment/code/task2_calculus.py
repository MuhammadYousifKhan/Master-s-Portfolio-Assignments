"""
Task 2 - Demand Over Time (Differential Calculus)
COM7023 Maths for Data Science - Urban Resource Intelligence

Analyses the demand function for a high-density residential zone:
    D(t) = 4t^3 - 18t^2 + 24t + 90        (t in hours, 0 <= t <= 4)

Finds the first and second derivatives, locates and classifies the
critical points, finds the inflection point, and identifies the
intervals where demand is increasing or decreasing.
"""

import os
import numpy as np
import sympy as sp
import seaborn as sns
import matplotlib.pyplot as plt

# ============================================================
# 1. SETUP: Define D(t) symbolically for verification
# ============================================================

t_sym = sp.Symbol('t')
D_sym = 4*t_sym**3 - 18*t_sym**2 + 24*t_sym + 90

print("=" * 60)
print("TASK 2 - DEMAND OVER TIME (CALCULUS)")
print("=" * 60)

print(f"\nDemand function: D(t) = 4t^3 - 18t^2 + 24t + 90")
print(f"Domain: t >= 0 (t in hours)")

# ============================================================
# 2. DERIVATIVES (power rule)
# ============================================================

print("\n" + "-" * 50)
print("DERIVATIVES")
print("-" * 50)

D_prime_sym = sp.diff(D_sym, t_sym)     # rate of change of demand
print(f"\nD'(t) = {D_prime_sym}")
print("      = 12t^2 - 36t + 24")

D_double_sym = sp.diff(D_prime_sym, t_sym)   # concavity
print(f"\nD''(t) = {D_double_sym}")
print("       = 24t - 36")

# ============================================================
# 3. CRITICAL POINTS: solve D'(t) = 0
# ============================================================

print("\n" + "-" * 50)
print("CRITICAL POINTS")
print("-" * 50)

critical_points = sorted(sp.solve(sp.Eq(D_prime_sym, 0), t_sym))
print(f"\nSolving D'(t) = 0  ->  t = {critical_points}")

for cp in critical_points:
    d_val = D_sym.subs(t_sym, cp)
    d2_val = D_double_sym.subs(t_sym, cp)
    if d2_val < 0:
        kind = "local MAXIMUM (D'' < 0)"
    elif d2_val > 0:
        kind = "local MINIMUM (D'' > 0)"
    else:
        kind = "inconclusive (D'' = 0)"
    print(f"  t = {float(cp):.1f}:  D = {float(d_val):.2f},  D'' = {float(d2_val):.2f}  ->  {kind}")

# ============================================================
# 4. INFLECTION POINT: solve D''(t) = 0
# ============================================================

print("\n" + "-" * 50)
print("INFLECTION POINT")
print("-" * 50)

inflection_points = sp.solve(sp.Eq(D_double_sym, 0), t_sym)
for ip in inflection_points:
    d_val = D_sym.subs(t_sym, ip)
    print(f"\nSolving D''(t) = 0  ->  t = {float(ip):.1f}")
    print(f"  D = {float(d_val):.2f}  (concavity changes from down to up here)")

# ============================================================
# 5. INTERVALS OF INCREASE / DECREASE
# ============================================================

print("\n" + "-" * 50)
print("INTERVALS OF INCREASE / DECREASE")
print("-" * 50)

# Test the sign of D'(t) at the midpoint of each interval formed
# by the domain boundaries and the critical points found above.
boundaries = [0.0] + [float(cp) for cp in critical_points] + [4.0]
for i in range(len(boundaries) - 1):
    lo, hi = boundaries[i], boundaries[i + 1]
    mid = (lo + hi) / 2
    slope = D_prime_sym.subs(t_sym, mid)
    trend = "increasing" if slope > 0 else "decreasing"
    print(f"  {lo:.1f} < t < {hi:.1f}:  D'({mid:.2f}) = {float(slope):.2f}  ->  demand is {trend}")

# ============================================================
# 6. VALUE TABLE (sanity check across the 4-hour window)
# ============================================================

print("\n" + "-" * 50)
print("VALUE TABLE")
print("-" * 50)

sample_times = [0, 0.5, 1, 1.5, 2, 2.5, 3, 4]
for tv in sample_times:
    d_val = D_sym.subs(t_sym, tv)
    d1_val = D_prime_sym.subs(t_sym, tv)
    d2_val = D_double_sym.subs(t_sym, tv)
    print(f"  t={tv:.1f}: D={float(d_val):.2f}, D'={float(d1_val):.2f}, D''={float(d2_val):.2f}")

# ============================================================
# 7. VISUALISATION - Seaborn line plots
# ============================================================

print("\n" + "-" * 50)
print("GENERATING FIGURE...")
print("-" * 50)

sns.set_theme(style="whitegrid", palette="muted")

# Turn the symbolic expressions into fast numeric functions for plotting
D_func = sp.lambdify(t_sym, D_sym, 'numpy')
D_prime_func = sp.lambdify(t_sym, D_prime_sym, 'numpy')

t_range = np.linspace(0, 4, 200)
D_curve = D_func(t_range)
D_prime_curve = D_prime_func(t_range)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

# Top panel: D(t) with the critical points and inflection point marked
crit_colors = ['#d7191c', '#fdae61']
crit_labels = ['Local max', 'Local min']
ax1.plot(t_range, D_curve, color='#2c7bb6', linewidth=2, label='D(t)')
for cp, color, label in zip(critical_points, crit_colors, crit_labels):
    d_val = float(D_sym.subs(t_sym, cp))
    ax1.scatter(float(cp), d_val, color=color, s=80, zorder=5,
                label=f'{label} (t={float(cp):.0f}, D={d_val:.0f})')
for ip in inflection_points:
    ax1.axvline(float(ip), color='gray', linestyle=':', alpha=0.6,
                label=f'Inflection (t={float(ip):.1f})')
ax1.set_ylabel('Demand D(t) (units/hour)', fontsize=11)
ax1.set_title('Demand Over Time - D(t) with Critical Points', fontsize=13, fontweight='bold')
ax1.legend(fontsize=9, loc='lower right')

# Bottom panel: D'(t) with increasing/decreasing regions shaded
ax2.plot(t_range, D_prime_curve, color='#d7191c', linewidth=2, label="D'(t)")
ax2.axhline(0, color='black', linewidth=0.5, alpha=0.5)
ax2.fill_between(t_range, 0, D_prime_curve, where=(D_prime_curve > 0),
                  color='green', alpha=0.15, label='Increasing')
ax2.fill_between(t_range, 0, D_prime_curve, where=(D_prime_curve < 0),
                  color='red', alpha=0.15, label='Decreasing')
ax2.set_xlabel('Time t (hours)', fontsize=11)
ax2.set_ylabel("D'(t) (units/hour²)", fontsize=11)
ax2.set_title("D'(t) - Rate of Change of Demand", fontsize=13, fontweight='bold')
ax2.legend(fontsize=9, loc='upper right')

plt.tight_layout()

# Make sure the figures folder exists before saving
os.makedirs('figures', exist_ok=True)
fig_path = 'figures/fig_task2_demand_curve.png'
plt.savefig(fig_path, dpi=150)
plt.close(fig)
print(f"Figure saved to '{fig_path}'")

print("\n" + "=" * 60)
print("TASK 2 COMPLETE")
print("=" * 60)
