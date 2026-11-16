 
import streamlit as st
import pandas as pd
 
# 1. Page Settings
st.set_page_config(
    page_title="EcoMove Mobility Dashboard",
    page_icon="🚍",
    layout="wide"
)
 
# 2. Load Dataset
df = pd.read_excel("assignquestion.xlsx")
 
# Convert Excel dates
df["Date"] = pd.to_datetime(
    df["Date"],
    unit="D",
    origin="1899-12-30"
)
 
# 3. Dashboard Heading
st.title("🚍 EcoMove Mobility Analytics Dashboard")
 
st.markdown(
    "An interactive analysis of passenger demand, "
    "transport performance, customer satisfaction "
    "and environmental sustainability."
)
 
st.divider()
 
# 4. Interactive Filters
st.header("Explore Transport Data")
 
col1, col2 = st.columns(2)
 
with col1:
    selected_city = st.selectbox(
        "Select City",
        ["All Cities"] + sorted(df["City"].unique().tolist()),
        key="city_filter"
    )
 
with col2:
    selected_mode = st.selectbox(
        "Select Transport Mode",
        ["All Modes"] + sorted(df["Transport_Mode"].unique().tolist()),
        key="mode_filter"
    )
 
col3, col4 = st.columns(2)
 
with col3:
    start_date = st.date_input(
        "Start Date",
        value=df["Date"].min().date()
    )
 
with col4:
    end_date = st.date_input(
        "End Date",
        value=df["Date"].max().date()
    )
 
# 5. Apply Filters
filtered_df = df.copy()
 
if selected_city != "All Cities":
    filtered_df = filtered_df[
        filtered_df["City"] == selected_city
    ]
 
if selected_mode != "All Modes":
    filtered_df = filtered_df[
        filtered_df["Transport_Mode"] == selected_mode
    ]
 
if start_date <= end_date:
    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date) &
        (filtered_df["Date"].dt.date <= end_date)
    ]
else:
    st.warning("Start date cannot be after end date.")
 
st.divider()
 
# 6. KPI Cards
st.header("Transport Performance Overview")
 
total_passengers = filtered_df["Passengers"].sum()
total_revenue = filtered_df["Ticket_Revenue_EUR"].sum()
average_delay = filtered_df["Average_Delay_Minutes"].mean()
total_co2 = filtered_df["CO2_Saved_KG"].sum()
 
col1, col2, col3, col4 = st.columns(4)
 
col1.metric("Total Passengers", f"{total_passengers:,.0f}")
col2.metric("Total Revenue", f"€{total_revenue:,.0f}")
col3.metric(
    "Average Delay",
    f"{average_delay:.2f} min" if pd.notna(average_delay) else "N/A"
)
col4.metric("CO₂ Saved", f"{total_co2:,.0f} kg")
 
st.divider()
 
# 7. Passenger Demand Chart
st.header("Passenger Demand Analysis")
 
st.subheader("Passenger Demand by Transport Mode")
 
passengers_by_mode = (
    filtered_df.groupby("Transport_Mode")["Passengers"]
    .sum()
    .sort_values(ascending=False)
)
 
st.bar_chart(passengers_by_mode)
 
# 8. Monthly Passenger Trend
st.subheader("Monthly Passenger Demand Trend")
 
monthly_passengers = (
    filtered_df.groupby(
        filtered_df["Date"].dt.to_period("M")
    )["Passengers"].sum()
)
 
monthly_passengers.index = monthly_passengers.index.astype(str)
 
st.line_chart(monthly_passengers)
 
st.divider()
 
# 9. Transport Service Quality
st.header("Transport Service Quality")
 
col1, col2 = st.columns(2)
 
with col1:
    st.subheader("Average Delay by Transport Mode")
 
    delay_by_mode = (
        filtered_df.groupby("Transport_Mode")[
            "Average_Delay_Minutes"
        ].mean().sort_values(ascending=False)
    )
 
    st.bar_chart(delay_by_mode)
 
with col2:
    st.subheader("Customer Satisfaction by Transport Mode")
 
    rating_by_mode = (
        filtered_df.groupby("Transport_Mode")[
            "Customer_Rating"
        ].mean().sort_values(ascending=False)
    )
 
    st.bar_chart(rating_by_mode)
 
st.divider()
 
# 10. Environmental Impact
st.header("Environmental Sustainability")
 
st.subheader("CO₂ Savings by Transport Mode")
 
co2_by_mode = (
    filtered_df.groupby("Transport_Mode")["CO2_Saved_KG"]
    .sum()
    .sort_values(ascending=False)
)
 
st.bar_chart(co2_by_mode)
 
st.caption(
    "This chart shows total recorded CO₂ savings "
    "for each transport mode under the selected filters."
)
 
st.divider()
 
# 11. Filtered Dataset
st.header("Explore Filtered Records")
 
st.write("Total matching records:", len(filtered_df))
 
st.dataframe(
    filtered_df.head(20),
    use_container_width=True
)
 
# 12. Download Filtered Data
st.subheader("Download Your Data")
 
csv = filtered_df.to_csv(index=False).encode("utf-8")
 
st.download_button(
    label="Download Filtered Dataset",
    data=csv,
    file_name="EcoMove_Filtered_Data.csv",
    mime="text/csv"
)
 
