import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ecomove import MODES, WEEKDAYS, group_kpis, kpis, load  # noqa: E402

MICRO = ["Bike Share", "E-Scooter"]


def r(x, n=2):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), n) + 0.0


def main():
    df = load()
    F = {}

    F["data"] = {
        "rows": len(df), "cols_raw": 18, "nulls": int(df.isna().sum().sum() - df["CO2_per_kWh"].isna().sum()),
        "duplicates": int(df.drop(columns=["Record_ID"]).duplicated().sum()),
        "date_min": df["Date"].min().strftime("%d %B %Y"), "date_max": df["Date"].max().strftime("%d %B %Y"),
        "days_covered": int(df["Date"].nunique()),
        "days_in_range": int((df["Date"].max() - df["Date"].min()).days + 1),
        "missing_dates": [d.strftime("%d %B %Y") for d in pd.date_range(df["Date"].min(), df["Date"].max()).difference(df["Date"].unique())],
        "cities": int(df["City"].nunique()), "countries": int(df["Country"].nunique()),
        "modes": int(df["Transport_Mode"].nunique()), "route_types": int(df["Route_Type"].nunique()),
        "weather_types": int(df["Weather"].nunique()),
        "zero_energy_rows": int((df["Energy_Consumption_KWh"] == 0).sum()),
        "zero_energy_all_bikeshare": bool((df.loc[df["Energy_Consumption_KWh"] == 0, "Transport_Mode"] == "Bike Share").all()),
        "zero_complaint_rows": int((df["Accessibility_Complaints"] == 0).sum()),
        "zero_complaint_micro_rows": int(((df["Accessibility_Complaints"] == 0) & df["Transport_Mode"].isin(MICRO)).sum()),
        "zero_delay_rows": int((df["Average_Delay_Minutes"] == 0).sum()),
        "rows_per_day_mean":r(df.groupby("Date").size().mean(), 2),
        "event_rows": int((df["Event_Day"] == "Yes").sum()),
        "weekend_rows": int(df["Is_Weekend"].sum()),
        "rating_min": r(df["Customer_Rating"].min(), 1), "rating_max": r(df["Customer_Rating"].max(), 1),
        "ontime_min": r(df["On_Time_Percentage"].min(), 1), "ontime_max": r(df["On_Time_Percentage"].max(), 1),
    }

    net = kpis(df)
    F["network"] = {k: r(v, 2) for k, v in net.items()}

    m = df.groupby(["Transport_Mode", "YearMonth"], observed=True)["On_Time_Percentage"].mean().unstack(0)
    netm = df.groupby("YearMonth")["On_Time_Percentage"].mean()
    v1 = {"network_month_min": r(netm.min(), 1), "network_month_min_label": netm.idxmin().strftime("%B %Y"),
          "network_month_max": r(netm.max(), 1), "network_month_max_label": netm.idxmax().strftime("%B %Y"),
          "modes": {}}
    for mo in MODES:
        s = m[mo]
        v1["modes"][mo] = {"min": r(s.min(), 1), "max": r(s.max(), 1), "range": r(s.max() - s.min(), 1),
                           "mean": r(df.loc[df["Transport_Mode"] == mo, "On_Time_Percentage"].mean(), 1),
                           "min_rows_month": int(df[df["Transport_Mode"] == mo].groupby("YearMonth").size().min())}
    ranks = m.rank(axis=1, ascending=False)
    v1["bus_last_every_month"] = bool((ranks["Bus"] == 6).all())
    v1["bike_or_scooter_top_every_month"] = bool(((ranks["Bike Share"] == 1) | (ranks["E-Scooter"] == 1)).all())
    v1["months"] = int(len(m))
    v1["bus_max_below_tram_min"] = bool(m["Bus"].max() < m["Tram"].min())
    yo = df.groupby("Year")["On_Time_Percentage"].mean()
    v1["network_2024"] = r(yo[2024], 1); v1["network_2025"] = r(yo[2025], 1)
    v1["network_change"] = r(yo[2025] - yo[2024], 1)
    wn = df.groupby("Weather")["On_Time_Percentage"].mean()
    wm = df.pivot_table(index="Weather", columns="Transport_Mode", values="On_Time_Percentage", aggfunc="mean", observed=True)
    drop = wm.loc["Clear"] - wm.loc["Snow"]
    v1["weather"] = {"ontime": {w: r(wn[w], 1) for w in wn.index}, "records": {w: int((df["Weather"] == w).sum()) for w in wn.index},
                     "worst": wn.idxmin(), "best": wn.idxmax(), "spread": r(wn.max() - wn.min(), 1),
                     "snow_drop_by_mode": {mo: r(drop[mo], 1) for mo in MODES},
                     "snow_drop_min": r(drop.min(), 1), "snow_drop_max": r(drop.max(), 1),
                     "bus_snow": r(wm.loc["Snow", "Bus"], 1),
                     "rating_snow": r(df.loc[df["Weather"] == "Snow", "Customer_Rating"].mean(), 2),
                     "rating_clear": r(df.loc[df["Weather"] == "Clear", "Customer_Rating"].mean(), 2)}
    v1["corr_ontime_delay"] = r(df["On_Time_Percentage"].corr(df["Average_Delay_Minutes"]), 2)
    co = df.groupby("City")["On_Time_Percentage"].mean()
    v1["city_ontime_min"] = r(co.min(), 1); v1["city_ontime_max"] = r(co.max(), 1)
    F["v1_reliability_trend"] = v1

    wk = df.pivot_table(index="Transport_Mode", columns="Weekday", values="Passengers", aggfunc="mean", observed=True)
    idx = wk.div(df.groupby("Transport_Mode", observed=True)["Passengers"].mean(), axis=0) * 100
    v2 = {"index": {mo: {d: int(round(idx.loc[mo, d])) for d in WEEKDAYS} for mo in MODES},
          "weekday_mean_pax": r(df.loc[~df["Is_Weekend"], "Passengers"].mean(), 0),
          "weekend_mean_pax": r(df.loc[df["Is_Weekend"], "Passengers"].mean(), 0)}
    v2["weekend_drop_pct"] = r((1 - v2["weekend_mean_pax"] / v2["weekday_mean_pax"]) * 100, 1)
    wd = df.groupby(["Transport_Mode", "Is_Weekend"], observed=True)["Passengers"].mean().unstack()
    v2["weekend_drop_by_mode_pct"] = {mo: r((1 - wd.loc[mo, True] / wd.loc[mo, False]) * 100, 1) for mo in MODES}
    day = df.groupby("Weekday", observed=True)["Passengers"].mean()
    v2["busiest_day"] = day.idxmax(); v2["busiest_day_pax"] = r(day.max(), 0)
    v2["quietest_day"] = day.idxmin(); v2["quietest_day_pax"] = r(day.min(), 0)
    ot = df.groupby("Is_Weekend")["On_Time_Percentage"].mean()
    v2["ontime_weekday"] = r(ot[False], 1); v2["ontime_weekend"] = r(ot[True], 1)
    cmn = df.pivot_table(index="City", columns="Transport_Mode", values="Passengers", aggfunc="mean", observed=True)
    cidx = cmn.div(df.groupby("Transport_Mode", observed=True)["Passengers"].mean(), axis=1) * 100
    v2["city_index"] = {c: {"min": int(round(cidx.loc[c].min())), "max": int(round(cidx.loc[c].max())), "mean": r(cidx.loc[c].mean(), 0)} for c in cidx.index}
    order = cidx.mean(axis=1).sort_values()
    v2["city_top2"] = list(order.index[-2:][::-1]); v2["city_bottom"] = order.index[0]
    v2["top2_min_index"] = int(round(cidx.loc[v2["city_top2"]].min().min()))
    v2["top2_lead_every_mode"] = bool(all(set(cidx[m].sort_values().index[-2:]) == set(v2["city_top2"]) for m in cidx.columns))
    v2["city_country"] = df.groupby("City")["Country"].first().to_dict()
    v2["min_cell_rows"] = int(df.pivot_table(index="Transport_Mode", columns="Weekday", values="Passengers", aggfunc="size", observed=True).min().min())
    F["v2_weekday_pattern"] = v2

    ev = df.groupby(["Transport_Mode", "Event_Day"], observed=True)["Passengers"].agg(["mean", "size"]).unstack()
    v3 = {"modes": {}}
    for mo in MODES:
        no, yes = ev.loc[mo, ("mean", "No")], ev.loc[mo, ("mean", "Yes")]
        v3["modes"][mo] = {"normal": r(no, 0), "event": r(yes, 0), "uplift_pct": r((yes / no - 1) * 100, 1),
                           "extra_pax": r(yes - no, 0), "event_rows": int(ev.loc[mo, ("size", "Yes")])}
    ups = {mo: v3["modes"][mo]["uplift_pct"] for mo in MODES}
    v3["uplift_min"] = min(ups.values()); v3["uplift_max"] = max(ups.values())
    v3["uplift_min_mode"] = min(ups, key=ups.get); v3["uplift_max_mode"] = max(ups, key=ups.get)
    e_all = df.groupby("Event_Day")["Passengers"].mean()
    v3["overall_uplift_pct"] = r((e_all["Yes"] / e_all["No"] - 1) * 100, 1)
    rpp = df.groupby("Event_Day").apply(lambda x: x["Ticket_Revenue_EUR"].sum() / x["Passengers"].sum(), include_groups=False)
    v3["rev_per_pax_event"] = r(rpp["Yes"], 2); v3["rev_per_pax_normal"] = r(rpp["No"], 2)
    F["v3_event_uplift"] = v3

    cy = df.groupby(["City", "Year"]).apply(lambda x: x["Ticket_Revenue_EUR"].sum() / x["Operating_Cost_EUR"].sum() * 100, include_groups=False).unstack()
    v4 = {"cities": {c: {"2024": r(cy.loc[c, 2024], 1), "2025": r(cy.loc[c, 2025], 1),
                         "change": r(cy.loc[c, 2025] - cy.loc[c, 2024], 1)} for c in cy.index}}
    v4["fell_below_100"] = [c for c in cy.index if cy.loc[c, 2024] >= 100 and cy.loc[c, 2025] < 100]
    v4["rose_above_100"] = [c for c in cy.index if cy.loc[c, 2024] < 100 and cy.loc[c, 2025] >= 100]
    v4["above_100_2024"] = int((cy[2024] >= 100).sum()); v4["above_100_2025"] = int((cy[2025] >= 100).sum())
    ny = df.groupby("Year").apply(lambda x: x["Ticket_Revenue_EUR"].sum() / x["Operating_Cost_EUR"].sum() * 100, include_groups=False)
    v4["network_2024"] = r(ny[2024], 1); v4["network_2025"] = r(ny[2025], 1)
    mass_y = df[~df["Transport_Mode"].isin(MICRO)].groupby(["City", "Year"]).apply(
        lambda x: x["Ticket_Revenue_EUR"].sum() / x["Operating_Cost_EUR"].sum() * 100, include_groups=False).unstack()
    recs = df.groupby(["City", "Year"]).size().unstack()
    micro_rec = df[df["Transport_Mode"].isin(MICRO)].groupby(["City", "Year"]).size().unstack() / recs * 100
    for c in cy.index:
        v4["cities"][c].update({"mass_2024": r(mass_y.loc[c, 2024], 1), "mass_2025": r(mass_y.loc[c, 2025], 1),
                                "records_2024": int(recs.loc[c, 2024]), "records_2025": int(recs.loc[c, 2025]),
                                "micro_record_share_2024": r(micro_rec.loc[c, 2024], 0), "micro_record_share_2025": r(micro_rec.loc[c, 2025], 0)})
    v4["mass_min_any_city_year"] = r(mass_y.min().min(), 1)
    F["v4_city_recovery_change"] = v4

    e = df[df["Energy_Consumption_KWh"] > 0]
    v5 = {"modes": {}, "rows_used": int(len(e)), "rows_excluded_zero_kwh": int((df["Energy_Consumption_KWh"] == 0).sum())}
    for mo in [x for x in MODES if x != "Bike Share"]:
        g = e[e["Transport_Mode"] == mo]
        lx, ly = np.log10(g["Energy_Consumption_KWh"]), np.log10(g["CO2_Saved_KG"])
        v5["modes"][mo] = {"co2_per_kwh": r(g["CO2_Saved_KG"].sum() / g["Energy_Consumption_KWh"].sum(), 2),
                           "kwh_per_pax": r(g["Energy_Consumption_KWh"].sum() / g["Passengers"].sum(), 3),
                           "r_log": r(np.corrcoef(lx, ly)[0, 1], 2), "slope_log": r(np.polyfit(lx, ly, 1)[0], 2)}
    v5["network_co2_per_kwh"] = r(e["CO2_Saved_KG"].sum() / e["Energy_Consumption_KWh"].sum(), 2)
    v5["metro_vs_bus_ratio"] = r(v5["modes"]["Metro"]["co2_per_kwh"] / v5["modes"]["Bus"]["co2_per_kwh"], 1)
    bus = df[df["Transport_Mode"] == "Bus"]
    v5["bus_share_energy_pct"] = r(bus["Energy_Consumption_KWh"].sum() / df["Energy_Consumption_KWh"].sum() * 100, 1)
    v5["bus_share_co2_pct"] = r(bus["CO2_Saved_KG"].sum() / df["CO2_Saved_KG"].sum() * 100, 1)
    F["v5_energy_efficiency"] = v5

    v6 = {"modes": {}}
    for mo in MODES:
        g = df[df["Transport_Mode"] == mo]
        v6["modes"][mo] = {"rev_pp_median": r(g["Revenue_per_Passenger"].median(), 2),
                           "rev_pp_min": r(g["Revenue_per_Passenger"].min(), 2), "rev_pp_max": r(g["Revenue_per_Passenger"].max(), 2),
                           "cost_pp_median": r(g["Cost_per_Passenger"].median(), 2),
                           "cost_pp_min": r(g["Cost_per_Passenger"].min(), 2), "cost_pp_max": r(g["Cost_per_Passenger"].max(), 2),
                           "margin_pp_median": r((g["Revenue_per_Passenger"] - g["Cost_per_Passenger"]).median(), 2),
                           "loss_record_pct": r((g["Ticket_Revenue_EUR"] < g["Operating_Cost_EUR"]).mean() * 100, 1)}
    rt = df.groupby("Route_Type")["Revenue_per_Passenger"].median()
    v6["route_rev_pp_median_min"] = r(rt.min(), 2); v6["route_rev_pp_median_max"] = r(rt.max(), 2)
    F["v6_unit_economics"] = v6

    cities = group_kpis(df, "City").set_index("City")
    mass = df[~df["Transport_Mode"].isin(MICRO)]
    mass_cr = mass.groupby("City").apply(lambda x: x["Ticket_Revenue_EUR"].sum() / x["Operating_Cost_EUR"].sum() * 100, include_groups=False)
    micro_share = df[df["Transport_Mode"].isin(MICRO)].groupby("City")["Operating_Cost_EUR"].sum() / df.groupby("City")["Operating_Cost_EUR"].sum() * 100
    v7 = {"cities": {c: {"recovery": r(cities.loc[c, "cost_recovery_pct"], 1), "net": r(cities.loc[c, "net"], 0),
                         "mass_recovery": r(mass_cr[c], 1), "micro_cost_share": r(micro_share[c], 1)} for c in cities.index}}
    v7["mass_recovery_min"] = r(mass_cr.min(), 1); v7["mass_recovery_max"] = r(mass_cr.max(), 1)
    v7["micro_share_min"] = r(micro_share.min(), 1); v7["micro_share_min_city"] = micro_share.idxmin()
    v7["micro_share_max"] = r(micro_share.max(), 1); v7["micro_share_max_city"] = micro_share.idxmax()
    v7["corr_micro_share_vs_recovery"] = r(np.corrcoef(micro_share[cities.index], cities["cost_recovery_pct"])[0, 1], 2)
    v7["cities_below_100"] = int((cities["cost_recovery_pct"] < 100).sum())
    v7["cities_net_loss"] = int((cities["net"] < 0).sum())
    v7["paris_recovery_2dp"] = r(cities.loc["Paris", "cost_recovery_pct"], 2)
    v7["best_city"] = cities["cost_recovery_pct"].idxmax(); v7["worst_city"] = cities["cost_recovery_pct"].idxmin()
    v7["mass_network_recovery"] = r(mass["Ticket_Revenue_EUR"].sum() / mass["Operating_Cost_EUR"].sum() * 100, 1)
    F["v7_city_investment"] = v7

    cm = group_kpis(df, ["City", "Transport_Mode"])
    cm["label"] = cm["City"] + " " + cm["Transport_Mode"].astype(str)
    net_rate = net["complaints_per_1k"]
    hi_vol = cm["complaints"] >= cm["complaints"].median()
    hi_rate = cm["complaints_per_1k"] >= net_rate
    v8 = {"combos": int(len(cm)), "network_rate": r(net_rate, 2), "median_volume": r(cm["complaints"].median(), 0),
          "top_volume": cm.nlargest(3, "complaints")[["label", "complaints", "complaints_per_1k"]].round(2).values.tolist(),
          "top_rate": cm.nlargest(5, "complaints_per_1k")[["label", "complaints", "complaints_per_1k"]].round(2).values.tolist(),
          "q_high_high": cm.loc[hi_vol & hi_rate, "label"].tolist(),
          "n_high_high": int((hi_vol & hi_rate).sum()), "n_low_high": int((~hi_vol & hi_rate).sum()),
          "n_high_low": int((hi_vol & ~hi_rate).sum()), "n_low_low": int((~hi_vol & ~hi_rate).sum())}
    mode_rate = df.groupby("Transport_Mode", observed=True).apply(lambda x: x["Accessibility_Complaints"].sum() / x["Passengers"].sum() * 1000, include_groups=False)
    v8["mode_rate"] = {mo: r(mode_rate[mo], 2) for mo in MODES}
    bus_cm = cm[cm["Transport_Mode"] == "Bus"].set_index("City")["complaints_per_1k"]
    v8["bus_worst_city"] = bus_cm.idxmax(); v8["bus_worst_rate"] = r(bus_cm.max(), 2)
    q = cm.loc[hi_vol & hi_rate, "Transport_Mode"].astype(str).value_counts()
    v8["high_high_by_mode"] = {k: int(v) for k, v in q.items()}
    v8["metro_combos_above_rate"] = int(((cm["Transport_Mode"] == "Metro") & hi_rate).sum())
    v8["micro_combos_low_volume"] = int((cm["Transport_Mode"].isin(MICRO) & ~hi_vol).sum())
    F["v8_accessibility_matrix"] = v8

    mk = group_kpis(df, "Transport_Mode").set_index("Transport_Mode")
    mk["co2_per_pax"] = mk["co2_kg"] / mk["passengers"]
    F["v9_mode_profile"] = {mo: {"on_time": r(mk.loc[mo, "on_time_pct"], 1), "rating": r(mk.loc[mo, "rating"], 2),
                                  "recovery": r(mk.loc[mo, "cost_recovery_pct"], 1), "co2_per_pax": r(mk.loc[mo, "co2_per_pax"], 3),
                                  "complaints_per_1k": r(mk.loc[mo, "complaints_per_1k"], 2), "delay": r(mk.loc[mo, "delay_min"], 2),
                                  "pax_share": r(mk.loc[mo, "passengers"] / net["passengers"] * 100, 1)} for mo in MODES}
    prof = pd.DataFrame({"on_time": mk["on_time_pct"], "rating": mk["rating"], "recovery": mk["cost_recovery_pct"],
                         "co2_per_pax": mk["co2_per_pax"], "complaints": mk["complaints_per_1k"]})
    sc = (prof - prof.min()) / (prof.max() - prof.min())
    sc["complaints"] = 1 - sc["complaints"]
    for mo in MODES:
        F["v9_mode_profile"][mo]["lowest_scaled_score"] = r(sc.loc[mo].min(), 2)
        F["v9_mode_profile"][mo]["scaled_sum"] = r(sc.loc[mo].sum(), 2)
    F["v9_meta"] = {"highest_minimum_mode": sc.min(axis=1).idxmax(), "smallest_sum_mode": sc.sum(axis=1).idxmin()}

    be = df[(df["Transport_Mode"] == "Bus") & (df["Event_Day"] == "Yes")]
    F["dashboard_example_bus_event"] = {"records": int(len(be)), "on_time": r(be["On_Time_Percentage"].mean(), 1),
                                        "on_time_gap_vs_network": r(be["On_Time_Percentage"].mean() - net["on_time_pct"], 1),
                                        "rating": r(be["Customer_Rating"].mean(), 2),
                                        "min_month_records": int(be.groupby("YearMonth").size().min())}

    out = ROOT / "build" / "facts.json"
    out.write_text(json.dumps(F, indent=2, default=str), encoding="utf-8")
    print(json.dumps(F, indent=1, default=str))


if __name__ == "__main__":
    main()
