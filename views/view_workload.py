"""
Workload and Capacity Planning View for WorkPulse AI
Evaluates available capacity against demand, displays heatmaps,
identifies overallocated key resources, and models project resource contention.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any
from modules.capacity_planning import (
    calculate_capacity_utilization,
    diagnose_team_capacity_constraints,
    compute_project_resource_contention
)
from utils.styles import get_plotly_theme

def render_workload_view(datasets: Dict[str, pd.DataFrame]):
    st.markdown("## ⚖️ Workload Imbalance & Capacity Planning")
    st.caption("Aligning demand with net available capacity while accounting for cognitive buffers, administrative overhead, and leave.")

    # Capacity parameters in sidebar or top bar
    with st.expander("⚙️ Adjust Capacity Planning Assumptions", expanded=False):
        c_p1, c_p2, c_p3 = st.columns(3)
        overhead_buf = c_p1.slider("Administrative / Focus Buffer (%)", 5, 30, 15, help="Time reserved for team syncs, breaks, and operational overhead") / 100.0
        high_thresh = c_p2.slider("High Workload Threshold (%)", 85, 110, 95) / 100.0
        over_thresh = c_p3.slider("Overallocated Threshold (%)", 105, 135, 115) / 100.0

    capacity_df = calculate_capacity_utilization(
        datasets,
        overhead_buffer_pct=overhead_buf,
        high_threshold=high_thresh,
        overallocated_threshold=over_thresh
    )

    if capacity_df.empty:
        st.warning("Insufficient data to compute workload capacity.")
        return

    # Utilization status metrics
    status_counts = capacity_df["workload_status"].value_counts().to_dict()
    overallocated_cnt = status_counts.get("Overallocated", 0)
    high_cnt = status_counts.get("High Workload", 0)
    balanced_cnt = status_counts.get("Balanced", 0)
    under_cnt = status_counts.get("Underutilized", 0)

    u1, u2, u3, u4 = st.columns(4)
    u1.metric("🔴 Overallocated (>115%)", f"{overallocated_cnt} Employees", delta="Severe Burnout Risk", delta_color="inverse")
    u2.metric("🟠 High Workload (95-115%)", f"{high_cnt} Employees", delta="Capacity Ceiling")
    u3.metric("🟢 Balanced (70-95%)", f"{balanced_cnt} Employees", delta="Optimal Zone")
    u4.metric("🔵 Underutilized (<70%)", f"{under_cnt} Employees", delta="Surplus Availability")

    st.markdown("---")

    # Team Capacity vs Demand Bar Chart
    st.markdown("### 📊 Team Demand vs Available Net Capacity")
    col_t1, col_t2 = st.columns([3, 2])

    with col_t1:
        team_agg = capacity_df.groupby("department").agg(
            total_net_capacity=("net_available_capacity", "sum"),
            total_demand=("avg_total_demand_hours", "sum")
        ).reset_index()

        fig_cap = go.Figure(data=[
            go.Bar(name="Available Net Capacity (hrs/wk)", x=team_agg["department"], y=team_agg["total_net_capacity"], marker_color="#94a3b8"),
            go.Bar(name="Actual Demand (hrs/wk)", x=team_agg["department"], y=team_agg["total_demand"], marker_color="#2563eb")
        ])
        fig_cap.update_layout(barmode="group", title="Weekly Departmental Capacity vs Demand Hours", **get_plotly_theme()["layout"])
        st.plotly_chart(fig_cap, use_container_width=True)

    with col_t2:
        # Donut of workload status
        df_status_pie = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])
        fig_pie = px.pie(
            df_status_pie,
            names="Status",
            values="Count",
            hole=0.45,
            color="Status",
            color_discrete_map={
                "Overallocated": "#ef4444",
                "High Workload": "#f97316",
                "Balanced": "#10b981",
                "Underutilized": "#3b82f6"
            },
            title="Workforce Workload Status Distribution"
        )
        fig_pie.update_layout(**get_plotly_theme()["layout"])
        st.plotly_chart(fig_pie, use_container_width=True)

    # Section 2: Team Capacity Diagnostics
    st.markdown("---")
    st.markdown("### 🩺 Diagnostic Constraint Evaluation by Department")
    team_diagnostics = diagnose_team_capacity_constraints(capacity_df)
    
    if team_diagnostics:
        diag_df = pd.DataFrame(team_diagnostics)
        st.dataframe(diag_df[[
            "department", "headcount", "aggregate_net_capacity", "aggregate_demand",
            "team_utilization_pct", "overallocated_count", "underutilized_count", "diagnosis", "recommendation"
        ]], use_container_width=True, hide_index=True)

    # Section 3: Workload Heatmap across Job Levels
    st.markdown("---")
    st.markdown("### 🗺️ Workload Imbalance Heatmap (Department × Job Level)")
    st.caption("Notice how Senior & Lead cadres in Engineering and Support carry intense utilization while Junior cadres remain below baseline.")

    pivot_wl = capacity_df.pivot_table(
        index="job_level",
        columns="department",
        values="utilization_pct",
        aggfunc="mean"
    ).round(1)

    fig_heat = px.imshow(
        pivot_wl,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="RdYlGn_r",
        title="Average Capacity Utilization % (Department × Job Level)"
    )
    fig_heat.update_layout(**get_plotly_theme()["layout"])
    st.plotly_chart(fig_heat, use_container_width=True)

    # Section 4: Project Resource Contention
    st.markdown("---")
    st.markdown("### ⚔️ Project Resource Contention Matrix")
    st.caption("Identifies which critical projects are competing for the exact same strained and overallocated individuals.")

    proj_df = compute_project_resource_contention(datasets)
    if not proj_df.empty:
        st.dataframe(proj_df, use_container_width=True, hide_index=True)

    # List of Overallocated Personnel
    with st.expander("🚨 View Individual Overallocated Personnel (>115% Utilization)", expanded=False):
        over_emps = capacity_df[capacity_df["workload_status"] == "Overallocated"][
            ["employee_id", "department", "job_role", "job_level", "avg_total_demand_hours", "net_available_capacity", "utilization_pct", "avg_ot_hours"]
        ].sort_values(by="utilization_pct", ascending=False)
        st.dataframe(over_emps, use_container_width=True, hide_index=True)
