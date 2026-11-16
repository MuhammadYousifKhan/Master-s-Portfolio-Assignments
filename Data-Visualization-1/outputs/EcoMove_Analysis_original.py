# =============================================================================
# EcoMove Mobility - Data Visualisation Investigation (COM7021)
# Run from the folder containing assignquestion.xlsx
# Produces all figures used in the report into ./figs/
# =============================================================================
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
 
os.makedirs("figs", exist_ok=True)
plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 200, "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 12})
 
# Colour-blind-safe palette (Okabe-Ito)
MODE_COL = {"Metro": "#0072B2", "Tram": "#56B4E9", "Bus": "#D55E00",
            "Park and Ride": "#009E73", "Bike Share": "#E69F00", "E-Scooter": "#CC79A7"}
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#7f7f7f"
 
# ---------------------------------------------------------------- 1. LOAD
df = pd.read_excel("assignquestion.xlsx")
print("Shape:", df.shape)
df.info()
 
# ---------------------------------------------------------------- 2. CLEAN
print("\nMissing values:\n", df.isnull().sum())
print("Duplicate rows:", df.duplicated().sum(), "| duplicate IDs:", df["Record_ID"].duplicated().sum())
 
# Excel serial dates -> datetime
df["Date"] = pd.to_datetime(df["Date"], unit="D", origin="1899-12-30")
df["Year"], df["Month"] = df["Date"].dt.year, df["Date"].dt.month
df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
print("Date range:", df["Date"].min().date(), "to", df["Date"].max().date())
 
# Categorical consistency
for c in ["City", "Country", "Transport_Mode", "Route_Type", "Weather", "Event_Day"]:
    print(c, sorted(df[c].unique()))
print("Cities per country (max):", df.groupby("City")["Country"].nunique().max())
 
# Logical validation
print("Passengers < Trips:", (df["Passengers"] < df["Trips"]).sum())
print("On-time outside 0-100:", (~df["On_Time_Percentage"].between(0, 100)).sum())
print("Rating outside 1-5:", (~df["Customer_Rating"].between(1, 5)).sum())
print("Zero-energy records:", (df["Energy_Consumption_KWh"] == 0).sum(),
      "(all Bike Share:", df.loc[df["Energy_Consumption_KWh"] == 0, "Transport_Mode"].eq("Bike Share").all(), ")")
 
# Derived measures
df["Net_Revenue_EUR"] = df["Ticket_Revenue_EUR"] - df["Operating_Cost_EUR"]
 
# Outlier screen (IQR), pooled vs within transport mode
def iqr_out(s):
    q1, q3 = s.quantile([.25, .75]); i = q3 - q1
    return ((s < q1 - 1.5 * i) | (s > q3 + 1.5 * i)).sum()
for c in ["Passengers", "Ticket_Revenue_EUR", "Average_Delay_Minutes", "Customer_Rating"]:
    within = df.groupby("Transport_Mode")[c].apply(iqr_out).sum()
    print(f"IQR outliers {c}: pooled={iqr_out(df[c])}, within-mode={within}")
 
# ---------------------------------------------------------------- 3. KPIs
kpi = dict(passengers=df.Passengers.sum(), revenue=df.Ticket_Revenue_EUR.sum(),
           cost=df.Operating_Cost_EUR.sum(), co2=df.CO2_Saved_KG.sum(),
           delay=df.Average_Delay_Minutes.mean(), ontime=df.On_Time_Percentage.mean(),
           rating=df.Customer_Rating.mean(), complaints=df.Accessibility_Complaints.sum())
print("\nKPIs:", kpi)
 
# ---------------------------------------------------------------- FIG 1 time series
monthly = df.groupby("YearMonth").agg(Passengers=("Passengers", "sum"), Records=("Record_ID", "count"))
monthly["Per_Record"] = monthly["Passengers"] / monthly["Records"]
fig, ax = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
ax[0].plot(monthly.index, monthly["Passengers"] / 1e6, marker="o", color=BLUE)
ax[0].set_ylabel("Total passengers (millions)"); ax[0].set_title("Monthly passenger demand, 2024-2025")
ax[1].plot(monthly.index, monthly["Per_Record"], marker="s", color=ORANGE)
ax[1].set_ylabel("Passengers per service record"); ax[1].set_title("Average demand per record (removes the effect of record counts)")
ax[1].set_xlabel("Month")
plt.setp(ax[1].get_xticklabels(), rotation=60, ha="right")
for a in ax: a.grid(axis="y", alpha=.3)
plt.tight_layout(); plt.savefig("figs/fig1_monthly_trend.png"); plt.close()
 
# ---------------------------------------------------------------- FIG 2 cities
city = df.groupby(["City", "Country"])["Passengers"].sum().reset_index().sort_values("Passengers")
ccol = dict(zip(sorted(df.Country.unique()), ["#0072B2", "#D55E00", "#009E73", "#E69F00", "#CC79A7", "#56B4E9"]))
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.barh(city["City"], city["Passengers"] / 1e6, color=[ccol[c] for c in city["Country"]])
for y, v in enumerate(city["Passengers"] / 1e6): ax.text(v + .03, y, f"{v:.2f}M", va="center", fontsize=9)
ax.set_xlabel("Total passengers (millions)"); ax.set_title("Passenger demand by city (coloured by country)")
ax.set_xlim(0, 5.2)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=v) for v in ccol.values()], labels=list(ccol.keys()),
          title="Country", loc="lower right", frameon=False)
plt.tight_layout(); plt.savefig("figs/fig2_city_demand.png"); plt.close()
 
# ---------------------------------------------------------------- FIG 3 distribution (box)
order = df.groupby("Transport_Mode")["Average_Delay_Minutes"].median().sort_values().index
fig, ax = plt.subplots(figsize=(9, 5.2))
sns.boxplot(data=df, x="Transport_Mode", y="Average_Delay_Minutes", order=order,
            hue="Transport_Mode", palette=MODE_COL, legend=False, ax=ax, fliersize=2, linewidth=1)
means = df.groupby("Transport_Mode")["Average_Delay_Minutes"].mean()
ax.scatter(range(len(order)), [means[m] for m in order], marker="D", color="white", edgecolor="black", zorder=5, label="Mean")
ax.set_xlabel("Transport mode"); ax.set_ylabel("Average delay (minutes)")
ax.set_title("Distribution of delay by transport mode"); ax.legend(frameon=False)
plt.tight_layout(); plt.savefig("figs/fig3_delay_boxplot.png"); plt.close()
 
# ---------------------------------------------------------------- FIG 4 scatter
fig, ax = plt.subplots(figsize=(9, 5.5))
for m, g in df.groupby("Transport_Mode"):
    ax.scatter(g["Average_Delay_Minutes"], g["Customer_Rating"], s=12, alpha=.45, color=MODE_COL[m], label=m)
b, a = np.polyfit(df["Average_Delay_Minutes"], df["Customer_Rating"], 1)
xs = np.linspace(0, df["Average_Delay_Minutes"].max(), 50)
ax.plot(xs, a + b * xs, color="black", lw=2, label="Linear fit")
r = df["Average_Delay_Minutes"].corr(df["Customer_Rating"])
ax.set_title(f"Delay versus customer rating (r = {r:.2f})")
ax.set_xlabel("Average delay (minutes)"); ax.set_ylabel("Customer rating (1-5)")
ax.legend(frameon=False, ncol=2, markerscale=2)
plt.tight_layout(); plt.savefig("figs/fig4_delay_vs_rating.png"); plt.close()
 
# ---------------------------------------------------------------- FIG 5 correlation heatmap
cols = ["Passengers", "Trips", "Average_Delay_Minutes", "On_Time_Percentage", "Ticket_Revenue_EUR",
        "Operating_Cost_EUR", "CO2_Saved_KG", "Energy_Consumption_KWh", "Customer_Rating", "Accessibility_Complaints"]
labels = ["Passengers", "Trips", "Delay", "On-time %", "Revenue", "Op. cost", "CO2 saved", "Energy", "Rating", "Complaints"]
corr = df[cols].corr()
fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, center=0,
            xticklabels=labels, yticklabels=labels, linewidths=.5, cbar_kws={"label": "Pearson r"}, ax=ax)
ax.set_title("Correlation matrix of service, financial and environmental measures")
plt.tight_layout(); plt.savefig("figs/fig5_correlation.png"); plt.close()
 
# ---------------------------------------------------------------- FIG 6 performance: net revenue by mode
fin = df.groupby("Transport_Mode").agg(Revenue=("Ticket_Revenue_EUR", "sum"), Cost=("Operating_Cost_EUR", "sum"))
fin["Net"] = fin.Revenue - fin.Cost; fin["Recovery"] = fin.Revenue / fin.Cost * 100
fin = fin.sort_values("Net")
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(fin.index, fin["Net"] / 1e6, color=[BLUE if v >= 0 else ORANGE for v in fin["Net"]])
for y, (n, rcv) in enumerate(zip(fin["Net"] / 1e6, fin["Recovery"])):
    ax.text(n + (.12 if n >= 0 else -.12), y, f"{n:+.2f}M ({rcv:.0f}% recovery)", va="center",
            ha="left" if n >= 0 else "right", fontsize=9)
ax.axvline(0, color="black", lw=.8)
ax.set_xlim(-9.8, 6.8); ax.set_xlabel("Ticket revenue minus operating cost (EUR millions)")
ax.set_title("Financial performance by mode: surplus (blue) and deficit (orange)")
plt.tight_layout(); plt.savefig("figs/fig6_net_revenue.png"); plt.close()
 
# ---------------------------------------------------------------- FIG 7 sustainability
env = df.groupby("Transport_Mode").agg(P=("Passengers", "sum"), CO2=("CO2_Saved_KG", "sum"),
                                       Acc=("Accessibility_Complaints", "sum"))
share = env / env.sum() * 100
share = share.sort_values("CO2", ascending=False)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.8))
x = np.arange(len(share)); w = .38
ax[0].bar(x - w / 2, share["P"], w, color=BLUE, label="Share of passengers")
ax[0].bar(x + w / 2, share["CO2"], w, color="#009E73", label="Share of CO2 saved")
ax[0].set_xticks(x); ax[0].set_xticklabels(share.index, rotation=30, ha="right")
ax[0].yaxis.set_major_formatter(mtick.PercentFormatter()); ax[0].legend(frameon=False)
ax[0].set_title("Passenger share vs CO2-saved share")
cpp = (df.groupby("Transport_Mode")["CO2_Saved_KG"].sum() / df.groupby("Transport_Mode")["Passengers"].sum()).sort_values()
ax[1].barh(cpp.index, cpp.values, color=[MODE_COL[m] for m in cpp.index])
for y, v in enumerate(cpp.values): ax[1].text(v + .003, y, f"{v:.3f}", va="center", fontsize=9)
ax[1].set_xlabel("kg CO2 saved per passenger"); ax[1].set_title("CO2 saved per passenger"); ax[1].set_xlim(0, .22)
plt.tight_layout(); plt.savefig("figs/fig7_sustainability.png"); plt.close()
 
# ---------------------------------------------------------------- FIG 8 weather x mode delay
pv = df.pivot_table(index="Transport_Mode", columns="Weather", values="Average_Delay_Minutes", aggfunc="mean")
pv = pv[["Clear", "Cloudy", "Windy", "Heatwave", "Rain", "Snow"]].loc[["Bus", "Park and Ride", "Tram", "Metro", "E-Scooter", "Bike Share"]]
fig, ax = plt.subplots(figsize=(9, 5))
sns.heatmap(pv, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=.5, cbar_kws={"label": "Average delay (min)"}, ax=ax)
ax.set_xlabel("Weather"); ax.set_ylabel("Transport mode"); ax.set_title("Average delay by transport mode and weather")
plt.tight_layout(); plt.savefig("figs/fig8_weather_delay.png"); plt.close()
 
# ---------------------------------------------------------------- FIG 9 accessibility
g = df.groupby(["Route_Type", "Transport_Mode"]).agg(A=("Accessibility_Complaints", "sum"), P=("Passengers", "sum"))
acc = (g["A"] / g["P"] * 1e5).unstack()
acc = acc[["Metro", "Tram", "Bus", "Park and Ride", "Bike Share", "E-Scooter"]]
fig, ax = plt.subplots(figsize=(9, 5))
sns.heatmap(acc, annot=True, fmt=".0f", cmap="Purples", linewidths=.5,
            cbar_kws={"label": "Complaints per 100,000 passengers"}, ax=ax)
ax.set_xlabel("Transport mode"); ax.set_ylabel("Route type")
ax.set_title("Accessibility complaints per 100,000 passengers")
plt.tight_layout(); plt.savefig("figs/fig9_accessibility.png"); plt.close()
 
# ---------------------------------------------------------------- Summary tables used in report
summary = df.groupby("Transport_Mode").agg(
    Passengers=("Passengers", "sum"), Avg_Delay=("Average_Delay_Minutes", "mean"),
    On_Time=("On_Time_Percentage", "mean"), Rating=("Customer_Rating", "mean"),
    Revenue=("Ticket_Revenue_EUR", "sum"), Cost=("Operating_Cost_EUR", "sum"),
    CO2=("CO2_Saved_KG", "sum"), Complaints=("Accessibility_Complaints", "sum")).round(2)
print(summary)
print(df.groupby("Weather")[["Average_Delay_Minutes", "On_Time_Percentage", "Customer_Rating"]].mean().round(2))
print(df.groupby("Event_Day")[["Average_Delay_Minutes", "On_Time_Percentage", "Customer_Rating"]].mean().round(2))
print("Figures saved to ./figs/")
 

