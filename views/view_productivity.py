"""
Productivity Analytics View for WorkPulse AI
Granular investigation of Task Productivity, Workload Indices,
Quality-Adjusted Output, Estimation Accuracy, and Backlog Dynamics.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any
from modules.productivity_metrics import calculate_executive_kpis
from utils.styles import get_plotly_theme

def render_productivity_view(datasets: Dict[str, pd.DataFrame]):
    st.markdown("## ⚡ Multi-Dimensional Productivity Engine")
    st.caption("Comprehensive analysis of output volume, quality-adjusted output, estimation fidelity, and cycle times.")

    task_df = datasets.get("task_performance", pd.DataFrame())
    wl_df = datasets.get("workload", pd.DataFrame())
    emp_df = datasets.get("employees", pd.DataFrame())

    if task_df.empty:
        st.warning("Task performance dataset is required for productivity analytics.")
        return

    kpis = calculate_executive_kpis(datasets)

    # Top summary metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Task Completion Rate", f"{kpis['task_completion_rate']:.1f}%")
    c2.metric("On-Time Rate", f"{kpis['on_time_completion_rate']:.1f}%")
    c3.metric("Rework Rate", f"{kpis['rework_rate_pct']:.1f}%", delta=f"{kpis['rework_rate_pct'] - 5:.1f}% vs Target", delta_color="inverse")
    c4.metric("Avg Task Cycle Time", f"{kpis['avg_cycle_time_days']:.1f} Days")

    st.markdown("---")

    # Section 1: Estimation Accuracy & Actual vs Estimated Hours
    st.markdown("### ⏱️ Estimation Accuracy & Hours Deviation")
    st.caption("Analyzing scope blowout: Tasks where Actual Hours heavily exceed Estimated Hours indicate hidden friction or scope creep.")

    comp_tasks = task_df[task_df["task_status"] == "Completed"].copy()
    if not comp_tasks.empty and "estimated_hours" in comp_tasks.columns and "actual_hours" in comp_tasks.columns:
        comp_tasks["hour_ratio"] = comp_tasks["actual_hours"] / comp_tasks["estimated_hours"].replace(0, np.nan)
        comp_tasks["hour_diff"] = comp_tasks["actual_hours"] - comp_tasks["estimated_hours"]

        col_est1, col_est2 = st.columns([3, 2])
        with col_est1:
            fig_scatter = px.scatter(
                comp_tasks,
                x="estimated_hours",
                y="actual_hours",
                color="task_priority",
                hover_data=["task_id", "task_type", "rework_hours", "quality_score"],
                title="Actual vs Estimated Hours (Diagonal Line = Perfect Estimate)",
                labels={"estimated_hours": "Estimated Hours", "actual_hours": "Actual Hours Logged"}
            )
            # Add 1:1 diagonal line
            max_val = max(comp_tasks["estimated_hours"].max(), comp_tasks["actual_hours"].max())
            fig_scatter.add_shape(
                type="line", line=dict(dash="dash", color="gray", width=1.5),
                x0=0, y0=0, x1=max_val, y1=max_val
            )
            fig_scatter.update_layout(**get_plotly_theme()["layout"])
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col_est2:
            fig_box = px.box(
                comp_tasks,
                x="task_type",
                y="hour_ratio",
                color="task_type",
                title="Estimation Variance Ratio (Actual / Est)",
                labels={"hour_ratio": "Ratio (Actual / Estimated)"}
            )
            fig_box.update_layout(**get_plotly_theme()["layout"], showlegend=False)
            fig_box.add_hline(y=1.0, line_dash="dot", line_color="green", annotation_text="Accurate 1.0x")
            st.plotly_chart(fig_box, use_container_width=True)

    # Section 2: Quality-Adjusted Output vs Rework
    st.markdown("---")
    st.markdown("### 💎 Quality-Adjusted Output & Rework Sinks")
    st.caption("Raw task counts fail to measure real productivity when tasks require substantial rework or result in poor quality.")

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if not comp_tasks.empty and "rework_hours" in comp_tasks.columns:
            rework_by_type = comp_tasks.groupby("task_type").agg(
                total_rework=("rework_hours", "sum"),
                avg_quality=("quality_score", "mean"),
                task_count=("task_id", "count")
            ).reset_index()

            fig_rework = px.bar(
                rework_by_type.sort_values(by="total_rework", ascending=False),
                x="task_type",
                y="total_rework",
                color="avg_quality",
                color_continuous_scale="Viridis",
                title="Cumulative Rework Hours Consumed by Task Type",
                labels={"total_rework": "Total Rework Hours", "avg_quality": "Avg Quality Rating"}
            )
            fig_rework.update_layout(**get_plotly_theme()["layout"])
            st.plotly_chart(fig_rework, use_container_width=True)

    with col_q2:
        if "task_status" in task_df.columns:
            status_counts = task_df["task_status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Task Count"]

            fig_donut = px.pie(
                status_counts,
                names="Status",
                values="Task Count",
                hole=0.45,
                color="Status",
                color_discrete_map={
                    "Completed": "#10b981",
                    "In Progress": "#3b82f6",
                    "Blocked": "#ef4444",
                    "Backlog": "#f59e0b"
                },
                title="Total Task Inventory Status Distribution"
            )
            fig_donut.update_layout(**get_plotly_theme()["layout"])
            st.plotly_chart(fig_donut, use_container_width=True)

    # Section 3: Task Cycle Time Distribution
    st.markdown("---")
    st.markdown("### ⏳ Task Cycle Time & Delivery Delay Breakdown")
    if not comp_tasks.empty and "task_due_date" in comp_tasks.columns and "task_completion_date" in comp_tasks.columns:
        due_dt = pd.to_datetime(comp_tasks["task_due_date"], errors="coerce")
        comp_dt = pd.to_datetime(comp_tasks["task_completion_date"], errors="coerce")
        start_dt = pd.to_datetime(comp_tasks["task_start_date"], errors="coerce")
        
        comp_tasks["cycle_time_days"] = (comp_dt - start_dt).dt.days
        comp_tasks["delay_days"] = (comp_dt - due_dt).dt.days
        delayed_only = comp_tasks[comp_tasks["delay_days"] > 0]

        c_hist1, c_hist2 = st.columns(2)
        with c_hist1:
            fig_hist = px.histogram(
                comp_tasks,
                x="cycle_time_days",
                nbins=25,
                color="task_priority",
                title="Cycle Time Distribution (Days from Start to Done)",
                labels={"cycle_time_days": "Cycle Time (Days)"}
            )
            fig_hist.update_layout(**get_plotly_theme()["layout"])
            st.plotly_chart(fig_hist, use_container_width=True)

        with c_hist2:
            fig_delay = px.box(
                delayed_only,
                x="task_type",
                y="delay_days",
                color="task_type",
                title="Slippage Severity on Delayed Deliverables",
                labels={"delay_days": "Days Past Due Date"}
            )
            fig_delay.update_layout(**get_plotly_theme()["layout"], showlegend=False)
            st.plotly_chart(fig_delay, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div class="alert-box-info">
        <b>📘 Methodological Limitations & Complexities Notice:</b><br/>
        Comparing raw task throughput without controlling for task type, complexity, or quality creates perverse incentives. 
        WorkPulse AI computes <i>Quality-Adjusted Output</i>: <code>∑ (Completed Tasks × (Quality Score / 5.0)) - (Rework Hours / 8.0)</code>.
    </div>
    """, unsafe_allow_html=True)
