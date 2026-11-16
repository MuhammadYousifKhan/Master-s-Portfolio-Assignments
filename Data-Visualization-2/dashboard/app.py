import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ecomove import MODE_COLOURS, MODES, WEEKDAYS, group_kpis, kpis, load

MASS_TRANSIT = ["Metro", "Tram", "Bus", "Park and Ride"]
EVENT_COLOURS = {"Yes": "#EE6677", "No": "#4477AA"}
FONT = dict(family="Calibri, Arial, sans-serif", size=13)

st.set_page_config(page_title="EcoMove Mobility Decision Dashboard", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 2.2rem; max-width: 1500px;}
    div[data-testid="stMetric"] {background: #f4f6f8; border-left: 4px solid #4477AA;
        padding: 10px 14px; border-radius: 4px;}
    div[data-testid="stMetricValue"] {font-size: 1.55rem;}
    div[data-testid="stMetricLabel"] p {font-size: 0.85rem; color: #44505c;}
    h1 {font-size: 1.9rem !important; padding-bottom: 0;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_data():
    return load()


def qp(name, options):
    raw = st.query_params.get(name)
    if not raw:
        return list(options)
    picked = [x for x in raw.split(",") if x in options]
    return picked or list(options)


def layout(fig, height=430, **kw):
    fig.update_layout(
        height=height,
        font=FONT,
        margin=dict(l=10, r=10, t=60, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.04, x=0),
        **kw,
    )
    fig.update_xaxes(gridcolor="#e6e9ed", zeroline=False)
    fig.update_yaxes(gridcolor="#e6e9ed", zeroline=False)
    return fig


def show(fig):
    st.plotly_chart(fig, width="stretch")


full = get_data()
net = kpis(full)
_fe = full[full["Energy_Consumption_KWh"] > 0]
net_co2_kwh = _fe["CO2_Saved_KG"].sum() / _fe["Energy_Consumption_KWh"].sum()

st.title("EcoMove Mobility Decision Dashboard")
st.markdown(
    "For senior managers: route planning, reliability, sustainability, accessibility and "
    "investment decisions across the EcoMove network, 2024 to 2025."
)

with st.sidebar:
    st.header("Filters")
    dmin, dmax = full["Date"].min().date(), full["Date"].max().date()
    date_range = st.slider("Date range", min_value=dmin, max_value=dmax, value=(dmin, dmax), format="MMM YYYY")
    countries = sorted(full["Country"].unique())
    sel_countries = st.multiselect("Country", countries, default=qp("country", countries))
    city_opts = sorted(full.loc[full["Country"].isin(sel_countries), "City"].unique())
    sel_cities = st.multiselect("City", city_opts, default=qp("city", city_opts))
    sel_modes = st.multiselect("Transport mode", MODES, default=qp("mode", MODES))
    routes = sorted(full["Route_Type"].unique())
    sel_routes = st.multiselect("Route type", routes, default=qp("route", routes))
    weathers = sorted(full["Weather"].unique())
    sel_weather = st.multiselect("Weather", weathers, default=qp("weather", weathers))
    event_opts = ["All", "Event days", "Normal days"]
    event_default = {"Yes": 1, "No": 2}.get(st.query_params.get("event"), 0)
    sel_event = st.radio("Event day", event_opts, index=event_default)

mask = (
    full["Date"].dt.date.between(date_range[0], date_range[1])
    & full["Country"].isin(sel_countries)
    & full["City"].isin(sel_cities)
    & full["Transport_Mode"].isin(sel_modes)
    & full["Route_Type"].isin(sel_routes)
    & full["Weather"].isin(sel_weather)
)
if sel_event == "Event days":
    mask &= full["Event_Day"] == "Yes"
elif sel_event == "Normal days":
    mask &= full["Event_Day"] == "No"
d = full[mask].copy()
d["Transport_Mode"] = d["Transport_Mode"].cat.remove_unused_categories()

with st.sidebar:
    st.caption(f"{len(d):,} of {len(full):,} records selected")

if d.empty:
    st.warning("No records match the current filters. Widen the selection in the sidebar.")
    st.stop()

k = kpis(d)
ee = d[d["Energy_Consumption_KWh"] > 0]
co2_kwh = ee["CO2_Saved_KG"].sum() / ee["Energy_Consumption_KWh"].sum() if len(ee) else np.nan

c = st.columns(6)
c[0].metric("Passengers", f"{k['passengers'] / 1e6:,.2f} M",
            f"{(k['passengers'] / net['passengers'] - 1) * 100:+.1f}% vs network", delta_color="off")
c[1].metric("Cost recovery", f"{k['cost_recovery_pct']:.1f}%",
            f"{k['cost_recovery_pct'] - net['cost_recovery_pct']:+.1f} pp vs network")
c[2].metric("On-time", f"{k['on_time_pct']:.1f}%", f"{k['on_time_pct'] - net['on_time_pct']:+.1f} pp vs network")
c[3].metric("Mean rating", f"{k['rating']:.2f} / 5", f"{k['rating'] - net['rating']:+.2f} vs network")
if np.isnan(co2_kwh):
    c[4].metric("CO2 saved per kWh", "n/a", "no energy-reporting records", delta_color="off")
else:
    c[4].metric("CO2 saved per kWh", f"{co2_kwh:.2f} kg", f"{co2_kwh - net_co2_kwh:+.2f} kg vs network")
c[5].metric("Complaints / 1,000 pax", f"{k['complaints_per_1k']:.2f}",
            f"{k['complaints_per_1k'] - net['complaints_per_1k']:+.2f} vs network", delta_color="inverse")

tabs = st.tabs(["Route planning", "Reliability", "Sustainability", "Accessibility", "Investment"])

with tabs[0]:
    left, right = st.columns(2)
    with left:
        st.subheader("Demand index by weekday and mode")
        piv = d.pivot_table(index="Transport_Mode", columns="Weekday", values="Passengers", aggfunc="mean", observed=True)
        piv = piv.reindex(columns=WEEKDAYS)
        idx = piv.div(d.groupby("Transport_Mode", observed=True)["Passengers"].mean(), axis=0) * 100
        fig = go.Figure(go.Heatmap(
            z=idx.values, x=WEEKDAYS, y=[str(m) for m in idx.index], colorscale="cividis",
            text=np.round(idx.values, 0), texttemplate="%{text:.0f}", textfont=dict(size=12),
            colorbar=dict(title="Index"),
            hovertemplate="%{y} on %{x}<br>Demand index: %{z:.0f}<extra></extra>"))
        fig.update_yaxes(autorange="reversed", title="Transport mode")
        fig.update_xaxes(title="Weekday")
        show(layout(fig))
        wk = idx[["Saturday", "Sunday"]].mean(axis=1)
        wd = idx[["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]].mean(axis=1)
        gap = (wk - wd).sort_values()
        stacked = idx.stack()
        peak = stacked.idxmax()
        st.caption(
            f"Index = mean passengers per record divided by that mode's own mean, x100. The biggest weekend drop is "
            f"{gap.index[0]} ({gap.iloc[0]:.0f} index points relative to its weekday level); the strongest single cell is "
            f"{peak[0]} on {peak[1]} ({stacked.max():.0f})."
        )
    with right:
        st.subheader("Mean passengers per record by route type")
        rt = d.groupby(["Route_Type", "Event_Day"], observed=True)["Passengers"].mean().reset_index()
        order = rt.groupby("Route_Type")["Passengers"].mean().sort_values().index.tolist()
        fig = go.Figure()
        for ev, lab in [("No", "Normal day"), ("Yes", "Event day")]:
            s = rt[rt["Event_Day"] == ev].set_index("Route_Type").reindex(order)
            fig.add_trace(go.Scatter(
                x=s["Passengers"], y=order, mode="markers", name=lab,
                marker=dict(size=14, color=EVENT_COLOURS[ev], line=dict(width=1, color="white")),
                hovertemplate="%{y}<br>" + lab + ": %{x:,.0f} passengers per record<extra></extra>"))
        fig.update_xaxes(title="Mean passengers per record")
        fig.update_yaxes(title="Route type")
        show(layout(fig))
        piv2 = rt.pivot(index="Route_Type", columns="Event_Day", values="Passengers")
        if {"Yes", "No"} <= set(piv2.columns) and len(piv2.dropna()):
            lift = ((piv2["Yes"] / piv2["No"] - 1) * 100).dropna().sort_values()
            st.caption(
                f"Highest-demand route type is {order[-1]}. Event-day uplift is largest on {lift.index[-1]} "
                f"({lift.iloc[-1]:+.1f}%) and smallest on {lift.index[0]} ({lift.iloc[0]:+.1f}%)."
            )
        else:
            st.caption(f"Highest-demand route type is {order[-1]}. Both event and normal days are needed to show uplift.")

with tabs[1]:
    left, right = st.columns([3, 2])
    with left:
        st.subheader("Monthly on-time percentage by mode")
        mo = d.groupby(["YearMonth", "Transport_Mode"], observed=True)["On_Time_Percentage"].agg(["mean", "size"]).reset_index()
        fig = go.Figure()
        for m in d["Transport_Mode"].cat.categories:
            s = mo[mo["Transport_Mode"] == m]
            fig.add_trace(go.Scatter(
                x=s["YearMonth"], y=s["mean"], mode="lines+markers", name=m,
                line=dict(color=MODE_COLOURS[m], width=2), marker=dict(size=5), customdata=s["size"],
                hovertemplate="%{x|%b %Y}<br>" + m + ": %{y:.1f}% on time (%{customdata} records)<extra></extra>"))
        fig.update_xaxes(title="Month")
        fig.update_yaxes(title="Mean on-time (%)")
        show(layout(fig, 450))
        mm = d.groupby("Transport_Mode", observed=True)["On_Time_Percentage"].mean().sort_values()
        thin = int(mo.groupby("Transport_Mode")["size"].min().min())
        lead = (
            f"Lowest mean on-time in this selection: {mm.index[0]} ({mm.iloc[0]:.1f}%); highest: {mm.index[-1]} ({mm.iloc[-1]:.1f}%)."
            if len(mm) > 1 else f"Mean on-time for {mm.index[0]} in this selection is {mm.iloc[0]:.1f}%."
        )
        st.caption(f"{lead} Some mode-months contain as few as {thin} records, so monthly movements are noisy.")
    with right:
        st.subheader("Mean on-time percentage by weather")
        w = d.groupby("Weather")["On_Time_Percentage"].agg(["mean", "size"]).sort_values("mean")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=w["mean"], y=w.index, mode="markers", marker=dict(size=15, color="#4477AA"),
            customdata=w["size"], name="Weather",
            hovertemplate="%{y}: %{x:.2f}% on time (%{customdata} records)<extra></extra>"))
        fig.add_vline(x=k["on_time_pct"], line_dash="dash", line_color="#666",
                      annotation_text="Selection mean", annotation_position="top")
        fig.update_xaxes(title="Mean on-time (%)")
        fig.update_yaxes(title="Weather")
        show(layout(fig, 450, showlegend=False))
        spread = w["mean"].iloc[-1] - w["mean"].iloc[0]
        st.caption(
            f"Weather with the lowest on-time is {w.index[0]} ({w['mean'].iloc[0]:.1f}%); the highest is "
            f"{w.index[-1]} ({w['mean'].iloc[-1]:.1f}%), a spread of {spread:.1f} points."
        )

with tabs[2]:
    left, right = st.columns([3, 2])
    with left:
        st.subheader("Energy use versus CO2 saved")
        fig = go.Figure()
        for m in ee["Transport_Mode"].cat.categories:
            s = ee[ee["Transport_Mode"] == m]
            if s.empty:
                continue
            fig.add_trace(go.Scatter(
                x=s["Energy_Consumption_KWh"], y=s["CO2_Saved_KG"], mode="markers", name=m,
                marker=dict(size=6, color=MODE_COLOURS[m], opacity=0.55),
                customdata=np.stack([s["City"], s["Date"].dt.strftime("%d %b %Y")], axis=1),
                hovertemplate=m + "<br>%{customdata[0]}, %{customdata[1]}<br>Energy: %{x:,.0f} kWh<br>CO2 saved: %{y:,.0f} kg<extra></extra>"))
        fig.update_xaxes(type="log", title="Energy consumption (kWh, log scale)")
        fig.update_yaxes(type="log", title="CO2 saved (kg, log scale)")
        show(layout(fig, 450))
        zero = d[d["Energy_Consumption_KWh"] == 0]
        zm = sorted(set(zero["Transport_Mode"].astype(str)))
        st.caption(
            f"Records with 0 kWh are excluded because log axes cannot show zero: {len(zero):,} records in this selection"
            f"{' (all ' + zm[0] + ')' if len(zm) == 1 else ''}. Bike Share records report 0 kWh, so Bike Share cannot be compared on energy efficiency."
        )
    with right:
        st.subheader("CO2 saved per kWh by mode")
        eg = ee.groupby("Transport_Mode", observed=True).agg(co2=("CO2_Saved_KG", "sum"), kwh=("Energy_Consumption_KWh", "sum"))
        eg["r"] = eg["co2"] / eg["kwh"]
        eg = eg.sort_values("r")
        fig = go.Figure(go.Bar(
            x=eg["r"], y=eg.index.astype(str), orientation="h",
            marker_color=[MODE_COLOURS[m] for m in eg.index],
            text=[f"{v:.2f}" for v in eg["r"]], textposition="outside",
            hovertemplate="%{y}: %{x:.2f} kg CO2 saved per kWh<extra></extra>"))
        fig.update_xaxes(title="kg CO2 saved per kWh", range=[0, eg["r"].max() * 1.18])
        fig.update_yaxes(title="Transport mode")
        show(layout(fig, 450))
        if len(eg) > 1:
            st.caption(
                f"{eg.index[-1]} saves {eg['r'].iloc[-1]:.2f} kg CO2 per kWh versus {eg['r'].iloc[0]:.2f} for "
                f"{eg.index[0]}, a ratio of {eg['r'].iloc[-1] / eg['r'].iloc[0]:.1f} to 1 (ratio of totals, zero-kWh rows excluded)."
            )
        else:
            st.caption(f"{eg.index[0]} saves {eg['r'].iloc[0]:.2f} kg CO2 per kWh (ratio of totals, zero-kWh rows excluded).")

with tabs[3]:
    st.subheader("Accessibility priority matrix: city and mode combinations")
    gk = group_kpis(d, ["City", "Transport_Mode"])
    gk["Transport_Mode"] = gk["Transport_Mode"].astype(str)
    fig = go.Figure()
    smax = gk["passengers"].max()
    for m in d["Transport_Mode"].cat.categories:
        s = gk[gk["Transport_Mode"] == m]
        fig.add_trace(go.Scatter(
            x=s["complaints"], y=s["complaints_per_1k"], mode="markers", name=m,
            marker=dict(color=MODE_COLOURS[m], opacity=0.8, line=dict(width=1, color="white"),
                        size=s["passengers"], sizemode="area", sizeref=2 * smax / (46 ** 2), sizemin=6),
            customdata=np.stack([s["City"], s["passengers"], s["records"]], axis=1),
            hovertemplate="<b>%{customdata[0]} / " + m + "</b><br>Complaints: %{x:,.0f}<br>"
                          "Per 1,000 passengers: %{y:.2f}<br>Passengers: %{customdata[1]:,.0f}<br>"
                          "Records: %{customdata[2]}<extra></extra>"))
    med = gk["complaints"].median()
    fig.add_vline(x=med, line_dash="dash", line_color="#666")
    fig.add_hline(y=k["complaints_per_1k"], line_dash="dash", line_color="#666")
    fig.add_annotation(x=med, y=0, xref="x", yref="paper", text="Median volume", showarrow=False,
                       xanchor="left", yanchor="bottom", xshift=4, font=dict(color="#555"))
    fig.add_annotation(x=0, y=k["complaints_per_1k"], xref="paper", yref="y", text="Selection rate", showarrow=False,
                       xanchor="left", yanchor="bottom", yshift=3, font=dict(color="#555"))
    fig.update_xaxes(title="Total accessibility complaints (count)")
    fig.update_yaxes(title="Complaints per 1,000 passengers")
    show(layout(fig, 520))
    worst = gk[(gk["complaints"] > med) & (gk["complaints_per_1k"] > k["complaints_per_1k"])]
    worst = worst.sort_values("complaints_per_1k", ascending=False)
    top = gk.sort_values("complaints_per_1k", ascending=False).iloc[0]
    msg = (
        f"{len(worst)} of {len(gk)} city-mode combinations sit above both the median volume ({med:,.0f} complaints) "
        f"and the selection rate ({k['complaints_per_1k']:.2f} per 1,000). Highest rate: {top['City']} {top['Transport_Mode']} "
        f"at {top['complaints_per_1k']:.2f} per 1,000 passengers."
    )
    if len(worst):
        w0 = worst.iloc[0]
        msg += f" Highest-rate priority combination: {w0['City']} {w0['Transport_Mode']} ({w0['complaints_per_1k']:.2f})."
    zero_m = sorted(set(d.loc[d["Accessibility_Complaints"] == 0, "Transport_Mode"].astype(str)))
    st.caption(msg + f" Bubble area is proportional to passengers. {int((d['Accessibility_Complaints'] == 0).sum())} records report zero complaints"
               + (f" (modes: {', '.join(zero_m)})." if zero_m else "."))

with tabs[4]:
    left, right = st.columns([3, 2])
    with left:
        st.subheader("Cost recovery by city")
        ca = group_kpis(d, "City").set_index("City")["cost_recovery_pct"]
        mt = d[d["Transport_Mode"].astype(str).isin(MASS_TRANSIT)]
        cm = group_kpis(mt, "City").set_index("City")["cost_recovery_pct"] if len(mt) else pd.Series(dtype=float)
        order = ca.sort_values().index.tolist()
        fig = go.Figure()
        for city in order:
            if city in cm.index:
                fig.add_trace(go.Scatter(x=[ca[city], cm[city]], y=[city, city], mode="lines",
                                         line=dict(color="#BBBBBB", width=3), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(
            x=ca.reindex(order), y=order, mode="markers", name="All modes",
            marker=dict(size=13, color="#4477AA"),
            hovertemplate="%{y}, all modes: %{x:.1f}% recovery<extra></extra>"))
        fig.add_trace(go.Scatter(
            x=cm.reindex(order), y=order, mode="markers", name="Mass transit only",
            marker=dict(size=13, color="#EE6677", symbol="diamond"),
            hovertemplate="%{y}, Metro/Tram/Bus/Park and Ride: %{x:.1f}% recovery<extra></extra>"))
        fig.add_vline(x=100, line_dash="dash", line_color="#228833", annotation_text="Break-even (100%)",
                      annotation_position="top")
        fig.update_xaxes(title="Cost recovery (ticket revenue / operating cost, %)")
        fig.update_yaxes(title="City")
        show(layout(fig, 480))
        below = int((ca < 100).sum())
        msg = f"{below} of {len(ca)} cities recover less than 100% of operating cost across all modes; lowest is {ca.idxmin()} ({ca.min():.1f}%)."
        if len(cm):
            gapc = (cm - ca.reindex(cm.index)).dropna()
            if len(gapc):
                big = gapc.abs().idxmax()
                msg += f" Restricting to mass transit changes recovery most in {big} ({gapc[big]:+.1f} pp)."
        st.caption(msg)
    with right:
        st.subheader("Net result by transport mode")
        nm = group_kpis(d, "Transport_Mode").set_index("Transport_Mode")["net"].sort_values()
        fig = go.Figure(go.Bar(
            x=nm.values / 1e6, y=nm.index.astype(str), orientation="h",
            marker_color=[MODE_COLOURS[m] for m in nm.index],
            text=[f"{v / 1e6:+.2f}" for v in nm.values], textposition="outside",
            hovertemplate="%{y}: EUR %{x:+.2f} million (revenue minus operating cost)<extra></extra>"))
        pad = max(float(np.abs(nm.values / 1e6).max()) * 0.3, 0.2)
        fig.update_xaxes(title="Net result (EUR million)", range=[min(nm.min() / 1e6 - pad, -pad), max(nm.max() / 1e6 + pad, pad)])
        fig.update_yaxes(title="Transport mode")
        show(layout(fig, 480))
        st.caption(
            f"Net result for the selection is EUR {k['net'] / 1e6:+.2f} million. Largest surplus: {nm.index[-1]} "
            f"(EUR {nm.iloc[-1] / 1e6:+.2f} M); largest deficit: {nm.index[0]} (EUR {nm.iloc[0] / 1e6:+.2f} M)."
        )
