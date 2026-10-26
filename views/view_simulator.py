"""
Productivity Scenario Simulator View for WorkPulse AI
Interactive What-If policy testing laboratory:
Manipulate overtime ceilings, staffing levels, rework rates, and process waiting times,
simulating baseline vs scenario impacts across capacity, throughput, backlog, and costs.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any
from modules.productivity_metrics import calculate_executive_kpis
from modules.scenario_simulator import run_what_if_simulation
from utils.styles import get_plotly_theme

def render_simulator_view(datasets: Dict[str, pd.DataFrame]):
    st.markdown("## 🧪 What-If Productivity Scenario Simulator")
    st.caption("Simulate the organizational and economic impact of targeted operational interventions prior to policy implementation.")

    kpis = calculate_executive_kpis(datasets)

    # Simulation Controls in 3 columns
    st.markdown("### 🎛️ Simulation Levers & Policy Adjustments")
    s_col1, s_col2, s_col3 = st.columns(3)

    with s_col1:
        st.markdown("**1. Capacity & Overtime**")
        ot_reduce = st.slider("Overtime Reduction Target (%)", 0, 80, 25, 5, help="Cap mandatory overtime hours")
        headcount_add = st.slider("Staffing Adjustment (Headcount)", -10, 20, 2, 1, help="Add or reallocate staff")

    with s_col2:
        st.markdown("**2. Quality & Execution**")
        rework_reduce = st.slider("Rework Reduction Target (%)", 0, 75, 30, 5, help="Achieved via Definition-of-Ready checklists")
        switch_reduce = st.slider("Task Switching Reduction (%)", 0, 60, 25, 5, help="Achieved via protected deep-work blocks")

    with s_col3:
        st.markdown("**3. Process & Well-being**")
        wait_reduce = st.slider("Process Wait Time Reduction (%)", 0, 70, 35, 5, help="Achieved via automated QA & distributed approvals")
        abs_change = st.slider("Absenteeism Reduction (%)", -50, 20, -15, 5, help="Healthier workload reduces stress absences")

    # Run Simulation
    sim = run_what_if_simulation(
        kpis=kpis,
        ot_reduction_pct=float(ot_reduce),
        headcount_change=int(headcount_add),
        rework_reduction_pct=float(rework_reduce),
        process_wait_reduction_pct=float(wait_reduce),
        absenteeism_change_pct=float(abs_change),
        task_switching_reduction_pct=float(switch_reduce)
    )

    base = sim["baseline"]
    scen = sim["scenario"]
    delta = sim["delta"]

    st.markdown("---")

    # Section 1: Side-by-Side Comparison KPI Cards
    st.markdown("### 📊 Baseline Reality vs. Simulated Scenario")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "On-Time Completion Rate",
            f"{scen['on_time_rate']:.1f}%",
            delta=f"{delta['on_time_rate_delta']:+.1f}% vs Baseline"
        )
    with c2:
        st.metric(
            "Estimated Backlog Tasks",
            f"{scen['task_backlog']} Tasks",
            delta=f"-{delta['backlog_cleared']} Cleared",
            delta_color="normal"
        )
    with c3:
        st.metric(
            "Overtime Expenditure",
            f"${scen['overtime_expenditure']:,.0f}",
            delta=f"-${delta['overtime_savings']:,.0f} Saved",
            delta_color="normal"
        )
    with c4:
        st.metric(
            "Capacity Utilization",
            f"{scen['capacity_utilization']:.1f}%",
            delta=f"{delta['utilization_delta']:+.1f}% vs Baseline",
            delta_color="inverse" if scen['capacity_utilization'] > 105 else "normal"
        )

    st.markdown("---")

    # Section 2: Visual Comparison Radar / Grouped Bar
    col_v1, col_v2 = st.columns([3, 2])

    with col_v1:
        categories = ["On-Time Rate (%)", "Completion Rate (%)", "Backlog (Tasks / 5)", "Overtime Cost ($k)", "Utilization (%)"]
        base_vals = [
            base["on_time_rate"],
            base["completion_rate"],
            base["task_backlog"] / 5.0,
            base["overtime_expenditure"] / 1000.0,
            base["capacity_utilization"]
        ]
        scen_vals = [
            scen["on_time_rate"],
            scen["completion_rate"],
            scen["task_backlog"] / 5.0,
            scen["overtime_expenditure"] / 1000.0,
            scen["capacity_utilization"]
        ]

        fig_bar = go.Figure(data=[
            go.Bar(name="Baseline Reality", x=categories, y=base_vals, marker_color="#94a3b8"),
            go.Bar(name="Simulated Scenario", x=categories, y=scen_vals, marker_color="#2563eb")
        ])
        fig_bar.update_layout(barmode="group", title="Operational Metric Shift: Baseline vs Scenario", **get_plotly_theme()["layout"])
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_v2:
        st.markdown("#### 📝 Simulation Synthesis")
        st.markdown(f"""
        - **Overtime Savings:** Simulated policy shifts yield **${delta['overtime_savings']:,.2f}** in direct overtime reduction.
        - **Throughput Recovery:** Resolving rework ({rework_reduce}%) and process chokepoints ({wait_reduce}%) elevates on-time completion by **{delta['on_time_rate_delta']:+.1f}%**.
        - **Workload Rebalancing:** Net capacity utilization shifts from **{base['capacity_utilization']:.1f}%** to **{scen['capacity_utilization']:.1f}%**, stabilizing team cognitive bandwidth.
        """)

    # Detailed Comparison Table
    st.markdown("### 📋 Parameter & Metric Comparison Table")
    comp_table = pd.DataFrame([
        {"Metric": "Workforce Headcount", "Baseline": f"{base['headcount']}", "Scenario": f"{scen['headcount']}", "Net Change": f"{scen['headcount'] - base['headcount']:+d}"},
        {"Metric": "Average Weekly Working Hours", "Baseline": f"{base['avg_working_hours']:.1f} hrs", "Scenario": f"{scen['avg_working_hours']:.1f} hrs", "Net Change": f"{scen['avg_working_hours'] - base['avg_working_hours']:+.1f} hrs"},
        {"Metric": "Average Overtime Hours", "Baseline": f"{base['avg_overtime_hours']:.1f} hrs", "Scenario": f"{scen['avg_overtime_hours']:.1f} hrs", "Net Change": f"{scen['avg_overtime_hours'] - base['avg_overtime_hours']:+.1f} hrs"},
        {"Metric": "On-Time Completion Rate", "Baseline": f"{base['on_time_rate']:.1f}%", "Scenario": f"{scen['on_time_rate']:.1f}%", "Net Change": f"{delta['on_time_rate_delta']:+.1f}%"},
        {"Metric": "Task Backlog", "Baseline": f"{base['task_backlog']} items", "Scenario": f"{scen['task_backlog']} items", "Net Change": f"-{delta['backlog_cleared']} items"},
        {"Metric": "Overtime Expenditure", "Baseline": f"${base['overtime_expenditure']:,.2f}", "Scenario": f"${scen['overtime_expenditure']:,.2f}", "Net Change": f"-${delta['overtime_savings']:,.2f}"},
    ])
    st.dataframe(comp_table, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="alert-box-info">
        <b>🔬 Modeling Disclaimer:</b> Simulated projections are mathematically derived from historical capacity elasticity curves and sensitivity assumptions. 
        They model directional impact rather than deterministic guarantees.
    </div>
    """, unsafe_allow_html=True)
