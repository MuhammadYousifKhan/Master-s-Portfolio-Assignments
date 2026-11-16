from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "COM7021_EcoMove_Analysis.ipynb"

cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text.strip()))


def code(text):
    cells.append(nbf.v4.new_code_cell(text.strip()))


md("""
# COM7021 Data Visualisation: EcoMove urban mobility investigation

Student ID: **[STUDENT ID]**

This notebook explores the EcoMove City Transport Authority dataset and produces the static figures used in the report. The interactive dashboard is in `dashboard/app.py`.
""")

md("## 1. Set-up")
code("""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

warnings.filterwarnings("ignore")
pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)

FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)
MODES = ["Metro", "Tram", "Bus", "Park and Ride", "Bike Share", "E-Scooter"]
MICRO = ["Bike Share", "E-Scooter"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TOL = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377"]
MODE_COLOURS = dict(zip(MODES, TOL))
GREY = "#BBBBBB"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False, "figure.dpi": 100, "savefig.dpi": 150, "savefig.bbox": "tight",
})


def save(fig, name):
    fig.savefig(FIG_DIR / name, facecolor="white")
    plt.show()
""")

md("## 2. Loading the data")
code("""
raw = pd.read_excel("[5442] EcoMoveMobility.xlsx", sheet_name="Dataset")
print("Shape:", raw.shape)
print("Date column type before conversion:", raw["Date"].dtype)
raw.head(3).T
""")

md("## 3. Data quality checks")
code("""
quality = pd.DataFrame({
    "dtype": raw.dtypes.astype(str),
    "missing": raw.isna().sum(),
    "zeros": (raw == 0).sum(),
    "unique": raw.nunique(),
})
print(quality)
print("Duplicate rows (ignoring Record_ID):", raw.drop(columns="Record_ID").duplicated().sum())
print("Duplicate Record_IDs:", raw["Record_ID"].duplicated().sum())
""")

code("""
df = raw.copy()
df["Date"] = pd.to_datetime(df["Date"], unit="D", origin="1899-12-30")
full_range = pd.date_range(df["Date"].min(), df["Date"].max())
print("Date range:", df["Date"].min().date(), "to", df["Date"].max().date())
print("Days with no records:", [d.date() for d in full_range.difference(df["Date"].unique())])
print("On-time % range:", df["On_Time_Percentage"].min(), "-", df["On_Time_Percentage"].max())
print("Rating range:", df["Customer_Rating"].min(), "-", df["Customer_Rating"].max())
print("Negative values in numeric columns:", int((df.select_dtypes("number") < 0).sum().sum()))
print("Zero-energy rows by mode:", df.loc[df["Energy_Consumption_KWh"] == 0, "Transport_Mode"].value_counts().to_dict())
print("Zero-complaint rows by mode:", df.loc[df["Accessibility_Complaints"] == 0, "Transport_Mode"].value_counts().to_dict())
print("City-to-country pairs:", df.groupby("City")["Country"].nunique().max(), "country per city")
""")

md("## 4. Feature engineering")
code("""
df["YearMonth"] = df["Date"].dt.to_period("M").dt.to_timestamp()
df["Year"] = df["Date"].dt.year
df["Weekday"] = pd.Categorical(df["Date"].dt.day_name(), categories=WEEKDAYS, ordered=True)
df["Is_Weekend"] = df["Date"].dt.dayofweek >= 5
df["Transport_Mode"] = pd.Categorical(df["Transport_Mode"], categories=MODES, ordered=True)
df["Revenue_per_Passenger"] = df["Ticket_Revenue_EUR"] / df["Passengers"]
df["Cost_per_Passenger"] = df["Operating_Cost_EUR"] / df["Passengers"]
df["Is_Micromobility"] = df["Transport_Mode"].isin(MICRO)


def recovery(d):
    return d["Ticket_Revenue_EUR"].sum() / d["Operating_Cost_EUR"].sum() * 100


def complaints_per_1k(d):
    return d["Accessibility_Complaints"].sum() / d["Passengers"].sum() * 1000


print("Network cost recovery: %.2f%%" % recovery(df))
print("Network complaints per 1,000 passengers: %.2f" % complaints_per_1k(df))
df[["Revenue_per_Passenger", "Cost_per_Passenger"]].describe().round(2)
""")

md("## 5. Visualisation 1: reliability over time and by weather (small multiples and dot plot)")
code("""
monthly = df.groupby(["YearMonth", "Transport_Mode"], observed=True)["On_Time_Percentage"].mean().unstack()
network = df.groupby("YearMonth")["On_Time_Percentage"].mean()
weather = df.pivot_table(index="Weather", columns="Transport_Mode", values="On_Time_Percentage", aggfunc="mean", observed=True)
weather_net = df.groupby("Weather")["On_Time_Percentage"].mean().sort_values()
weather = weather.loc[weather_net.index]
fig = plt.figure(figsize=(16, 6.5))
grid = fig.add_gridspec(2, 4, width_ratios=[1, 1, 1, 1.15])
axes = [fig.add_subplot(grid[i // 3, i % 3]) for i in range(6)]
for ax in axes[1:]:
    ax.sharey(axes[0])
    ax.sharex(axes[0])
for ax, mode in zip(axes, MODES):
    for other in MODES:
        if other != mode:
            ax.plot(monthly.index, monthly[other], color=GREY, lw=0.8, alpha=0.6)
    ax.plot(network.index, network, color="black", lw=1, ls="--")
    ax.plot(monthly.index, monthly[mode], color=MODE_COLOURS[mode], lw=2.4)
    ax.set_title(f"{mode}  (mean {df.loc[df['Transport_Mode'] == mode, 'On_Time_Percentage'].mean():.1f}%)", fontsize=10.5)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.tick_params(axis="x", labelrotation=45, labelsize=8)
    if mode in MODES[:3]:
        ax.tick_params(axis="x", labelbottom=False)
axes[0].set_ylabel("Mean on-time %")
axes[3].set_ylabel("Mean on-time %")
wx = fig.add_subplot(grid[:, 3])
y = np.arange(len(weather))
wx.hlines(y, weather.min(axis=1), weather.max(axis=1), color=GREY, lw=1)
for mode in MODES:
    wx.scatter(weather[mode], y, color=MODE_COLOURS[mode], s=45, label=mode, zorder=3)
wx.scatter(weather_net, y, color="black", marker="D", s=40, label="Network", zorder=4)
wx.set_yticks(y, [f"{w}\\n({(df['Weather'] == w).sum():,} records)" for w in weather.index])
wx.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
wx.set_xlabel("Mean on-time %")
wx.set_title("On-time by weather and mode", fontsize=10.5)
wx.legend(loc="upper center", bbox_to_anchor=(0.45, -0.1), ncol=4, fontsize=8, frameon=False)
fig.suptitle("On-time performance by month and mode (dashed line = network average), and by weather",
             x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.tight_layout()
save(fig, "fig01_reliability_small_multiples.png")
rank = monthly.rank(axis=1, ascending=False)
print("Bus ranked last in", int((rank["Bus"] == 6).sum()), "of", len(rank), "months")
print(monthly.agg(["min", "max"]).round(1))
print("Snow minus Clear on-time by mode (points):", (weather.loc["Snow"] - weather.loc["Clear"]).round(1).to_dict())
print("Correlation of on-time percentage with delay minutes per record:", round(df["On_Time_Percentage"].corr(df["Average_Delay_Minutes"]), 2))
""")

md("## 6. Visualisation 2: when and where demand concentrates (heatmaps)")
code("""
weekday_mean = df.pivot_table(index="Transport_Mode", columns="Weekday", values="Passengers", aggfunc="mean", observed=True)
index = weekday_mean.div(df.groupby("Transport_Mode", observed=True)["Passengers"].mean(), axis=0) * 100
city_mean = df.pivot_table(index="City", columns="Transport_Mode", values="Passengers", aggfunc="mean", observed=True)
city_index = city_mean.div(df.groupby("Transport_Mode", observed=True)["Passengers"].mean(), axis=1) * 100
city_index = city_index.loc[city_index.mean(axis=1).sort_values(ascending=False).index]
country = df.groupby("City")["Country"].first()
city_index.index = [f"{c} ({country[c]})" for c in city_index.index]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(16, 5.6), gridspec_kw={"width_ratios": [1.15, 1]})
sns.heatmap(index, annot=True, fmt=".0f", cmap="cividis", vmin=70, vmax=115, linewidths=1, linecolor="white",
            cbar_kws={"label": "Demand index (mode average = 100)"}, ax=a1)
a1.set_xlabel("")
a1.set_ylabel("")
a1.set_title("By day of week and mode")
sns.heatmap(city_index, annot=True, fmt=".0f", cmap="cividis", vmin=70, vmax=140, linewidths=1, linecolor="white",
            cbar_kws={"label": "Demand index (mode average = 100)"}, ax=a2)
a2.set_xlabel("")
a2.set_ylabel("")
a2.tick_params(axis="x", labelrotation=30)
a2.set_title("By city and mode")
fig.suptitle("Passenger demand index: when and where demand concentrates", x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.tight_layout()
save(fig, "fig02_weekday_heatmap.png")
weekend = df.groupby(["Transport_Mode", "Is_Weekend"], observed=True)["Passengers"].mean().unstack()
print("Weekend drop by mode (%):")
print(((1 - weekend[True] / weekend[False]) * 100).round(1))
print("City demand index range within each mode:")
print(city_index.agg(["min", "max"]).round(0))
""")

md("## 7. Visualisation 3: event-day demand uplift (dumbbell)")
code("""
ev = df.pivot_table(index="Transport_Mode", columns="Event_Day", values="Passengers", aggfunc="mean", observed=True)
ev["Uplift"] = (ev["Yes"] / ev["No"] - 1) * 100
ev = ev.sort_values("Uplift")
fig, ax = plt.subplots(figsize=(9.5, 4.2))
y = np.arange(len(ev))
ax.hlines(y, ev["No"], ev["Yes"], color=GREY, lw=3)
ax.scatter(ev["No"], y, color="#4477AA", s=70, label="Normal day", zorder=3)
ax.scatter(ev["Yes"], y, color="#EE6677", s=70, label="Event day", zorder=3)
for i, (mode, row) in enumerate(ev.iterrows()):
    ax.text(row["Yes"] * 1.08, i, f"+{row['Uplift']:.1f}%", va="center", fontsize=9.5)
ax.set_yticks(y, ev.index)
ax.set_xscale("log")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set_xlim(200, 60000)
ax.set_xlabel("Mean passengers per record (log scale)")
ax.set_title("Passengers per record on event days versus normal days")
ax.legend(frameon=False, loc="lower right")
save(fig, "fig03_event_dumbbell.png")
ev.round(1)
""")

md("## 8. Visualisation 4: city cost recovery, 2024 versus 2025 (slope chart)")
code("""
yearly = df.groupby(["City", "Year"]).apply(recovery, include_groups=False).unstack()


def spread(values, gap=0.26):
    order = np.argsort(values, kind="stable")
    placed = np.array(values, dtype=float)
    for _ in range(500):
        moved = False
        for i in range(1, len(order)):
            lo, hi = order[i - 1], order[i]
            overlap = gap - (placed[hi] - placed[lo])
            if overlap > 1e-6:
                placed[lo] -= overlap / 2
                placed[hi] += overlap / 2
                moved = True
        if not moved:
            break
    return placed


right_pos = dict(zip(yearly.index, spread(yearly[2025].values)))
left_pos = dict(zip(yearly.index, spread(yearly[2024].values)))
fig, ax = plt.subplots(figsize=(8, 7.5))
for city, row in yearly.iterrows():
    a, b = row[2024], row[2025]
    if a >= 100 > b:
        colour, lw = "#EE6677", 2.4
    elif a < 100 <= b:
        colour, lw = "#4477AA", 2.4
    else:
        colour, lw = GREY, 1.4
    ax.plot([0, 1], [a, b], color=colour, lw=lw, marker="o")
    box = {"facecolor": "white", "edgecolor": "none", "pad": 0.4}
    ax.text(1.04, right_pos[city], f"{city} {b:.1f}%", va="center", fontsize=9, bbox=box,
            color=colour if colour != GREY else "#555555")
    ax.text(-0.04, left_pos[city], f"{city} {a:.1f}%", va="center", ha="right", fontsize=8.5, bbox=box, color="#555555")
ax.axhline(100, color="black", ls="--", lw=1)
ax.text(0.5, 99.75, "break-even (100%)", ha="center", fontsize=9)
ax.set_xticks([0, 1], ["2024", "2025"])
ax.set_xlim(-0.6, 1.6)
ax.set_ylabel("Cost recovery (ticket revenue / operating cost)")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.spines["bottom"].set_visible(False)
ax.set_title("City cost recovery: red = fell below break-even, blue = rose above")
save(fig, "fig04_city_recovery_slope.png")
yearly.assign(Change=yearly[2025] - yearly[2024]).round(1).sort_values("Change")
""")

md("## 9. Visualisation 5: energy used versus CO2 saved (log-log scatter)")
code("""
energy = df[df["Energy_Consumption_KWh"] > 0]
print("Rows excluded because Energy_Consumption_KWh = 0:", len(df) - len(energy))
fig, ax = plt.subplots(figsize=(9, 6))
rows = []
for mode in [m for m in MODES if m != "Bike Share"]:
    g = energy[energy["Transport_Mode"] == mode]
    eff = g["CO2_Saved_KG"].sum() / g["Energy_Consumption_KWh"].sum()
    ax.scatter(g["Energy_Consumption_KWh"], g["CO2_Saved_KG"], s=10, alpha=0.35, color=MODE_COLOURS[mode])
    lx, ly = np.log10(g["Energy_Consumption_KWh"]), np.log10(g["CO2_Saved_KG"])
    slope, intercept = np.polyfit(lx, ly, 1)
    xs = np.linspace(lx.min(), lx.max(), 50)
    ax.plot(10 ** xs, 10 ** (intercept + slope * xs), color=MODE_COLOURS[mode], lw=2.2,
            label=f"{mode}: {eff:.2f} kg CO2 per kWh")
    rows.append({"Mode": mode, "kg_CO2_per_kWh": eff, "r_log": np.corrcoef(lx, ly)[0, 1], "records": len(g)})
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Energy consumption per record (kWh, log scale)")
ax.set_ylabel("CO2 saved per record (kg, log scale)")
ax.set_title("Energy used against CO2 saved, by mode (Bike Share reports 0 kWh and is excluded)")
ax.legend(frameon=False, loc="upper left")
save(fig, "fig05_energy_co2_scatter.png")
pd.DataFrame(rows).round(2)
""")

md("## 10. Visualisation 6: revenue and cost per passenger (split violin)")
code("""
unit = df.melt(id_vars="Transport_Mode", value_vars=["Revenue_per_Passenger", "Cost_per_Passenger"],
               var_name="Measure", value_name="EUR")
unit["Measure"] = unit["Measure"].map({"Revenue_per_Passenger": "Revenue per passenger",
                                       "Cost_per_Passenger": "Cost per passenger"})
fig, ax = plt.subplots(figsize=(11, 5.2))
sns.violinplot(data=unit, x="Transport_Mode", y="EUR", hue="Measure", split=True, inner="quart",
               palette={"Revenue per passenger": "#228833", "Cost per passenger": "#AA3377"},
               log_scale=True, cut=0, density_norm="width", ax=ax)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"€{v:g}"))
ax.set_xlabel("")
ax.set_ylabel("EUR per passenger (log scale)")
ax.set_title("Distribution of revenue and cost per passenger by mode")
ax.legend(frameon=False, title="", loc="upper left")
save(fig, "fig06_unit_economics_violin.png")
summary = df.groupby("Transport_Mode", observed=True)[["Revenue_per_Passenger", "Cost_per_Passenger"]].median()
summary["Loss-making records %"] = df.groupby("Transport_Mode", observed=True).apply(
    lambda x: (x["Ticket_Revenue_EUR"] < x["Operating_Cost_EUR"]).mean() * 100, include_groups=False)
summary.round(2)
""")

md("## 11. Visualisation 7: city cost recovery with and without micromobility (lollipop KPI)")
code("""
city = pd.DataFrame({
    "All modes": df.groupby("City").apply(recovery, include_groups=False),
    "Mass transit only": df[~df["Is_Micromobility"]].groupby("City").apply(recovery, include_groups=False),
    "Micromobility share of cost %": df[df["Is_Micromobility"]].groupby("City")["Operating_Cost_EUR"].sum()
    / df.groupby("City")["Operating_Cost_EUR"].sum() * 100,
}).sort_values("All modes")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5), sharey=True, gridspec_kw={"width_ratios": [2.2, 1]})
y = np.arange(len(city))
ax1.hlines(y, city["All modes"], city["Mass transit only"], color=GREY, lw=2)
ax1.scatter(city["All modes"], y, color="#EE6677", s=60, zorder=3, label="All modes")
ax1.scatter(city["Mass transit only"], y, color="#4477AA", marker="D", s=50, zorder=3, label="Mass transit only")
ax1.axvline(100, color="black", ls="--", lw=1)
ax1.set_yticks(y, city.index)
ax1.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax1.set_xlabel("Cost recovery (revenue / operating cost)")
ax1.set_title("Cost recovery by city")
ax1.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=2)
ax2.barh(y, city["Micromobility share of cost %"], color="#CCBB44")
for i, v in enumerate(city["Micromobility share of cost %"]):
    ax2.text(v + 0.1, i, f"{v:.1f}%", va="center", fontsize=9)
ax2.set_xlim(0, 12)
ax2.set_xlabel("Share of city operating cost")
ax2.set_title("Micromobility share of cost")
fig.tight_layout()
save(fig, "fig07_city_recovery_lollipop.png")
print("Correlation between micromobility cost share and city cost recovery: %.2f"
      % city["Micromobility share of cost %"].corr(city["All modes"]))
city.round(1)
""")

md("## 12. Visualisation 8: accessibility priority matrix (bubble chart)")
code("""
cm = df.groupby(["City", "Transport_Mode"], observed=True).agg(
    complaints=("Accessibility_Complaints", "sum"), passengers=("Passengers", "sum")).reset_index()
cm["per_1k"] = cm["complaints"] / cm["passengers"] * 1000
net_rate = complaints_per_1k(df)
median_vol = cm["complaints"].median()
fig, ax = plt.subplots(figsize=(10, 6.5))
for mode in MODES:
    g = cm[cm["Transport_Mode"] == mode]
    ax.scatter(g["complaints"], g["per_1k"], s=np.sqrt(g["passengers"]) / 4, color=MODE_COLOURS[mode],
               alpha=0.75, edgecolor="white", label=mode)
ax.axvline(median_vol, color="black", ls=":", lw=1)
ax.axhline(net_rate, color="black", ls="--", lw=1)
ax.set_xscale("log")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.text(0.99, 0.98, "High volume and high rate:\\nact first", transform=ax.transAxes, ha="right", va="top",
        fontsize=9.5, fontweight="bold")
ax.text(0.30, 0.98, "Low volume, high rate:\\ntargeted fixes", transform=ax.transAxes, ha="left", va="top", fontsize=9.5)
for _, r in cm.nlargest(2, "per_1k").iterrows():
    ax.annotate(f"{r['City']} {r['Transport_Mode']}", (r["complaints"], r["per_1k"]), xytext=(8, -3),
                textcoords="offset points", fontsize=8.5)
bus = cm[cm["Transport_Mode"] == "Bus"]
top_bus = bus.loc[bus["per_1k"].idxmax()]
ax.annotate("All 12 city Bus services", (top_bus["complaints"], top_bus["per_1k"]), xytext=(40, 25),
            textcoords="offset points", fontsize=9, color="#228833", fontweight="bold",
            arrowprops={"arrowstyle": "-", "color": "#228833"})
for _, r in cm.nlargest(1, "complaints").iterrows():
    ax.annotate(f"{r['City']} {r['Transport_Mode']}", (r["complaints"], r["per_1k"]), xytext=(-10, 10),
                textcoords="offset points", fontsize=8.5, ha="right")
ax.set_xlabel("Total accessibility complaints, 2024-2025 (log scale)")
ax.set_ylabel("Complaints per 1,000 passengers")
ax.set_title(f"Accessibility priority matrix: 72 city-mode services (dashed = network rate {net_rate:.2f})")
leg = ax.legend(frameon=False, loc="lower left", ncol=3)
for h in leg.legend_handles:
    h.set_sizes([50])
save(fig, "fig08_accessibility_matrix.png")
cm["high_volume"] = cm["complaints"] >= median_vol
cm["high_rate"] = cm["per_1k"] >= net_rate
print(cm[cm["high_volume"] & cm["high_rate"]]["Transport_Mode"].astype(str).value_counts())
""")

md("## 13. Visualisation 9: mode performance profiles (radar small multiples)")
code("""
prof = pd.DataFrame({
    "On-time %": df.groupby("Transport_Mode", observed=True)["On_Time_Percentage"].mean(),
    "Rating": df.groupby("Transport_Mode", observed=True)["Customer_Rating"].mean(),
    "Cost recovery": df.groupby("Transport_Mode", observed=True).apply(recovery, include_groups=False),
    "CO2 saved per passenger": df.groupby("Transport_Mode", observed=True).apply(
        lambda x: x["CO2_Saved_KG"].sum() / x["Passengers"].sum(), include_groups=False),
    "Low complaint rate": df.groupby("Transport_Mode", observed=True).apply(complaints_per_1k, include_groups=False),
})
scaled = (prof - prof.min()) / (prof.max() - prof.min())
scaled["Low complaint rate"] = 1 - scaled["Low complaint rate"]
labels = list(scaled.columns)
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
angles += angles[:1]
fig, axes = plt.subplots(2, 3, figsize=(12, 8), subplot_kw={"polar": True})
for ax, mode in zip(axes.flat, MODES):
    vals = scaled.loc[mode].tolist()
    vals += vals[:1]
    ax.plot(angles, vals, color=MODE_COLOURS[mode], lw=2)
    ax.fill(angles, vals, color=MODE_COLOURS[mode], alpha=0.25)
    ax.set_xticks(angles[:-1], labels, fontsize=8)
    ax.tick_params(axis="x", pad=10)
    ax.set_yticks([0.25, 0.5, 0.75, 1], [])
    ax.set_ylim(0, 1)
    ax.set_title(mode, fontsize=11, pad=14, loc="center")
fig.suptitle("Mode profiles across five KPIs (0 = worst mode, 1 = best mode on each axis)",
             x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.tight_layout()
save(fig, "fig09_mode_radar.png")
prof.round(3)
""")

md("## 14. Summary table of headline indicators by mode")
code("""
headline = pd.DataFrame({
    "Passenger share %": df.groupby("Transport_Mode", observed=True)["Passengers"].sum() / df["Passengers"].sum() * 100,
    "On-time %": prof["On-time %"],
    "Cost recovery %": prof["Cost recovery"],
    "kg CO2 per kWh": energy.groupby("Transport_Mode", observed=True).apply(
        lambda x: x["CO2_Saved_KG"].sum() / x["Energy_Consumption_KWh"].sum(), include_groups=False),
    "Complaints per 1k": prof["Low complaint rate"],
}).round(2)
headline
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"]["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}

if __name__ == "__main__":
    NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
    nbf.write(nb, OUT)
    print("Notebook written:", OUT)
