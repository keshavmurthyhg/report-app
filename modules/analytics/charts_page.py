import streamlit as st
import pandas as pd

from modules.search.data_loader import load_data
from modules.search.search import apply_search
from modules.search.kpi import calculate_kpi


def render():

    st.title("📊 Ops Insights - Trends & Metrics")

    # ---------- LOAD ----------
    df, last_refresh = load_data()

    if df.empty:
        st.warning("No data available")
        return

    # ---------- SIDEBAR CONTROLS ----------
    st.sidebar.markdown("## 📊 Controls")

    chart_type = st.sidebar.radio(
        "Select Chart",
        [
            "Daily Trend",
            "Source Distribution",
            "Status Distribution",
            "Priority Distribution",
            "Monthly Heatmap"
        ]
    )

    # ---------- FILTERS (TOP) ----------
    st.subheader("Filters")

    col1, col2 = st.columns(2)

    with col1:
        sources = st.multiselect(
            "Source",
            ["AZURE", "SNOW", "PTC"],
            default=["AZURE", "SNOW", "PTC"]
        )

    with col2:
        search_value = st.text_input("🔎 Search")

    if not sources:
        st.warning("Select at least one source")
        return

    # ✅ CREATE FILTERED FIRST (IMPORTANT FIX)
    filtered = df[df["Source"].isin(sources)].copy()
    filtered = apply_search(filtered, search_value)

    # ---------- DATE FILTER (SIDEBAR) ----------
    with st.sidebar.expander("📅 Date Filter", True):

        date_column = st.selectbox(
            "Select Date Field",
            ["Created Date", "Resolved Date"]
        )

        mode = st.radio(
            "Filter Type",
            ["No Filter", "Date Range", "By Year", "Quick Select"]
        )

        # Convert safely
        filtered[date_column] = pd.to_datetime(
            filtered[date_column], errors="coerce"
        )

        temp_dates = filtered[date_column].dropna()

        if not temp_dates.empty:

            if mode == "Date Range":
                date_range = st.date_input(
                    "Select Date Range",
                    value=(temp_dates.min(), temp_dates.max())
                )

                if len(date_range) == 2:
                    start, end = date_range
                    filtered = filtered[
                        (filtered[date_column] >= pd.to_datetime(start)) &
                        (filtered[date_column] <= pd.to_datetime(end))
                    ]

            elif mode == "By Year":
                years = sorted(temp_dates.dt.year.unique())
                selected_year = st.selectbox("Select Year", years)

                filtered = filtered[
                    filtered[date_column].dt.year == selected_year
                ]

            elif mode == "Quick Select":

                quick_option = st.selectbox(
                    "Quick Options",
                    ["Last 7 Days", "Last 30 Days", "This Month"]
                )

                today = pd.Timestamp.today()

                if quick_option == "Last 7 Days":
                    start = today - pd.Timedelta(days=7)

                elif quick_option == "Last 30 Days":
                    start = today - pd.Timedelta(days=30)

                elif quick_option == "This Month":
                    start = today.replace(day=1)

                filtered = filtered[
                    filtered[date_column] >= start
                ]

    # ---------- KPI ----------
    kpi = calculate_kpi(filtered)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", kpi["total"])
    c2.metric("Open", kpi["open"])
    c3.metric("Closed", kpi["closed"])
    c4.metric("Cancelled", kpi["cancelled"])

    # ---------- DATE PREP ----------
    filtered["Created Date"] = pd.to_datetime(
        filtered["Created Date"], errors="coerce"
    )

    # =========================================================
    # 🎯 SHOW ONLY SELECTED CHART
    # =========================================================

    if chart_type == "Daily Trend":
        st.subheader("📈 Tickets Trend (Daily)")

        daily = (
            filtered
            .groupby(filtered["Created Date"].dt.date)
            .size()
            .reset_index(name="Count")
            .sort_values("Created Date")
        )

        st.line_chart(daily.set_index("Created Date"))

    elif chart_type == "Source Distribution":
        st.subheader("📊 Tickets by Source")
        st.bar_chart(filtered["Source"].value_counts())

    elif chart_type == "Status Distribution":
        st.subheader("📊 Tickets by Status")
        st.bar_chart(filtered["Status"].value_counts())

    elif chart_type == "Priority Distribution":
        st.subheader("📊 Tickets by Priority")
        st.bar_chart(filtered["Priority"].value_counts())

    elif chart_type == "Monthly Heatmap":
        st.subheader("🔥 Monthly Trend by Source")

        filtered["Month"] = filtered["Created Date"].dt.to_period("M").astype(str)

        heatmap = (
            filtered
            .groupby(["Month", "Source"])
            .size()
            .unstack(fill_value=0)
        )

        st.dataframe(heatmap, use_container_width=True)

    # ---------- FOOTER ----------
    st.caption(f"Last refreshed: {last_refresh}")
