"""
Task 1 - Steady-State Resource Demand (Linear Algebra)
COM7023 Maths for Data Science - Urban Resource Intelligence

Solves the 4x4 linear system:
  2x1 -  x2 +  x3       = 120
  -x1 + 3x2       - x4  = 150
   x1 +  x2 + 2x3 - x4  = 180
        -x2 +  x3 + 2x4 = 140

Interprets x1..x4 as equilibrium daily demand per zone.
"""

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# ============================================================
# 1. SETUP: Define the system Ax = b
# ============================================================

# Coefficient matrix A (4x4)
A = np.array([
    [ 2, -1,  1,  0],
    [-1,  3,  0, -1],
    [ 1,  1,  2, -1],
    [ 0, -1,  1,  2]
], dtype=float)

# Right-hand side vector b
b = np.array([120, 150, 180, 140], dtype=float)

print("=" * 60)
print("TASK 1 - STEADY-STATE RESOURCE DEMAND")
print("=" * 60)

print("\nMatrix A (coefficients):")
print(A)
print("\nVector b (demand targets):")
print(b)

# ============================================================
# 2. CHECK EXISTENCE & UNIQUENESS OF SOLUTION
# ============================================================

# 2a. Determinant - must be non-zero for a unique solution
det_A = np.linalg.det(A)
print("\n" + "-" * 50)
print("EXISTENCE & UNIQUENESS CHECKS")
print("-" * 50)
print(f"det(A) = {det_A:.4f}")
if det_A != 0:
    print("=> det(A) != 0 -> A is invertible, so a UNIQUE solution exists.")
else:
    print("=> det(A) = 0 -> System may have no solution or infinitely many.")

# 2b. Rank - full rank confirms linear independence
rank_A = np.linalg.matrix_rank(A)
print(f"\nrank(A) = {rank_A}")
print(f"Matrix size: {A.shape[0]}x{A.shape[1]}")
if rank_A == A.shape[0]:
    print("=> Full rank -> all rows are linearly independent.")
else:
    print("=> Rank deficient -> some equations may be redundant.")

# 2c. Condition number - numerical stability
cond_A = np.linalg.cond(A)
print(f"\nCondition number kappa(A) = {cond_A:.4f}")
if cond_A < 100:
    print("=> Well-conditioned (kappa < 100) - solution is numerically stable.")
elif cond_A < 1000:
    print("=> Moderately conditioned - small rounding errors may appear.")
else:
    print("=> Ill-conditioned (kappa >= 1000) - solution may be sensitive to rounding.")

# ============================================================
# 3. SOLVE THE SYSTEM
# ============================================================

print("\n" + "-" * 50)
print("SOLUTION")
print("-" * 50)

# 3a. Solve via numpy.linalg.solve (uses LAPACK - stable, efficient)
x = np.linalg.solve(A, b)

# Label the solutions
zone_labels = ['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4']
print("\nEquilibrium daily demand per zone (x1..x4):")
for i, (label, val) in enumerate(zip(zone_labels, x), 1):
    print(f"  x{i} ({label}) = {val:.4f}  units/day")

# 3b. Verification - check that Ax is approx b
print("\nVerification (A @ x should equal b):")
print(f"  Residual (max error): {np.max(np.abs(A @ x - b)):.2e}")
print("  => Solution checks out (error approx machine precision).")

# ============================================================
# 4. INTERPRETATION
# ============================================================

print("\n" + "-" * 50)
print("INTERPRETATION")
print("-" * 50)
print(f"""
- All four zones have unique, stable equilibrium demands.
- Zone demands range from {x.min():.1f} to {x.max():.1f} units/day.
- The zone with highest demand: {zone_labels[np.argmax(x)]} ({x.max():.1f})
- The zone with lowest demand:  {zone_labels[np.argmin(x)]} ({x.min():.1f})
- A unique solution means planners can predict resource needs
  with certainty - the system converges to one fixed state.
""")

# ============================================================
# 5. VISUALISATION - Seaborn bar chart
# ============================================================

print("-" * 50)
print("GENERATING FIGURE...")
print("-" * 50)

sns.set_theme(style="whitegrid", palette="muted")

fig, ax = plt.subplots(figsize=(8, 5))

# Create the bar plot
bar_colors = sns.color_palette("muted", n_colors=4)
bars = ax.bar(zone_labels, x, color=bar_colors, edgecolor='black', linewidth=0.5)

# Add value labels on top of each bar
for bar, val in zip(bars, x):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{val:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Labels and title
ax.set_xlabel('Urban Zone', fontsize=12)
ax.set_ylabel('Equilibrium Daily Demand (units)', fontsize=12)
ax.set_title('Steady-State Resource Demand by Urban Zone', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(x) * 1.2)  # headroom for labels

# Add a horizontal reference line for the average
avg_demand = np.mean(x)
ax.axhline(avg_demand, color='gray', linestyle='--', linewidth=1, alpha=0.7,
           label=f'Average ({avg_demand:.1f})')
ax.legend(fontsize=10)

plt.tight_layout()

# Save figure at >=150 dpi as required
fig_path = 'figures/fig_task1_zone_demands.png'
plt.savefig(fig_path, dpi=150)
print(f"Figure saved to '{fig_path}'")

# Also show the print (will be visible when running)
# plt.show()   # uncomment to display interactively

print("\n" + "=" * 60)
print("TASK 1 COMPLETE")
print("=" * 60)