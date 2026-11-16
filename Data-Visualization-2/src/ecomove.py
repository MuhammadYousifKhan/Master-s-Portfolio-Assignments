from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "[5442] EcoMoveMobility.xlsx"

MODES = ["Metro", "Tram", "Bus", "Park and Ride", "Bike Share", "E-Scooter"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

TOL_BRIGHT = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377", "#BBBBBB"]
MODE_COLOURS = dict(zip(MODES, TOL_BRIGHT))


def load(path=DATA_PATH):
    df = pd.read_excel(path, sheet_name="Dataset")
    df["Date"] = pd.to_datetime(df["Date"], unit="D", origin="1899-12-30")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["YearMonth"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    df["Weekday"] = pd.Categorical(df["Date"].dt.day_name(), categories=WEEKDAYS, ordered=True)
    df["Is_Weekend"] = df["Date"].dt.dayofweek >= 5
    df["Transport_Mode"] = pd.Categorical(df["Transport_Mode"], categories=MODES, ordered=True)
    df["Revenue_per_Passenger"] = df["Ticket_Revenue_EUR"] / df["Passengers"]
    df["Cost_per_Passenger"] = df["Operating_Cost_EUR"] / df["Passengers"]
    df["Cost_Recovery_Pct"] = df["Ticket_Revenue_EUR"] / df["Operating_Cost_EUR"] * 100
    df["Passengers_per_Trip"] = df["Passengers"] / df["Trips"]
    df["CO2_per_kWh"] = np.where(df["Energy_Consumption_KWh"] > 0,
                                 df["CO2_Saved_KG"] / df["Energy_Consumption_KWh"].replace(0, np.nan),
                                 np.nan)
    return df


def kpis(d):
    pax = d["Passengers"].sum()
    rev = d["Ticket_Revenue_EUR"].sum()
    cost = d["Operating_Cost_EUR"].sum()
    return {
        "records": int(len(d)),
        "passengers": int(pax),
        "revenue": float(rev),
        "cost": float(cost),
        "net": float(rev - cost),
        "cost_recovery_pct": float(rev / cost * 100) if cost else np.nan,
        "on_time_pct": float(d["On_Time_Percentage"].mean()),
        "delay_min": float(d["Average_Delay_Minutes"].mean()),
        "rating": float(d["Customer_Rating"].mean()),
        "co2_kg": float(d["CO2_Saved_KG"].sum()),
        "energy_kwh": float(d["Energy_Consumption_KWh"].sum()),
        "complaints": int(d["Accessibility_Complaints"].sum()),
        "complaints_per_1k": float(d["Accessibility_Complaints"].sum() / pax * 1000) if pax else np.nan,
        "pax_per_record": float(pax / len(d)) if len(d) else np.nan,
    }


def group_kpis(d, by):
    rows = []
    for key, g in d.groupby(by, observed=True):
        r = kpis(g)
        if isinstance(by, (list, tuple)):
            r.update(dict(zip(by, key if isinstance(key, tuple) else (key,))))
        else:
            r[by] = key
        rows.append(r)
    return pd.DataFrame(rows)
