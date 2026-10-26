"""
Executive Overview View for WorkPulse AI
Renders the primary executive cockpit with 14 KPI cards,
period comparison deltas, management diagnostic summary, and trend charts.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any
from modules.productivity_metrics import calculate_executive_kpis, calculate_department_breakdown
from modules.statistical_analysis import compute_longitudinal_trends
from utils.styles import get_plotly_theme

def render_overview_view(datasets: Dict[str, pd.DataFrame]):
    st.markdown("## 📊 Executive Productivity & Workload Intelligence")
    st.caption("Strategic executive overview comparing working hours, overtime trajectory, output quality, and operational bottlenecks.")

    kpis = calculate_executive_kpis(datasets)
    dept_df = calculate_department_breakdown(datasets)

    # Management Summary Alert Box
    avg_ot = kpis.get("avg_overtime_hours", 0)
    on_time = kpis.get("on_time_completion_rate", 0)
    declining_depts = kpis.get("declining_depts_count", 0)

    if avg_ot > 5.0 and on_time < 80.0:
        alert_class = "alert-box-critical"
        status_heading = "⚠️ Critical Executive Notice: Working Hours Expanding While Output Stagnates"
        status_body = (
            f"Overtime has expanded to an average of <b>{avg_ot:.1f} hours/week</b> while on-time completion sits at <b>{on_time:.1f}%</b>. "
            f"<b>{declining_depts} departments</b> exhibit declining marginal returns on overtime. "
            "Telemetry indicates task fragmentation, staging gate wait-times, and uneven senior workload distribution are neutralizing overtime effort."
        )
    else:
        alert_class = "alert-box-info"
        status_heading = "ℹ️ Executive Status: Operations Stably Calibrated"
        status_body = (
            f"Average overtime is balanced at <b>{avg_ot:.1f} hrs/week</b> with an on-time completion rate of <b>{on_time:.1f}%</b>. "
            "Localized bottlenecks exist in specific process queues, but aggregate organizational capacity is sustainable."
        )

    st.markdown(f"""
    <div class="{alert_class}">
        <div style="font-weight: 700; font-size: 1rem; margin-bottom: 4px;">{status_heading}</div>
        <div>{status_body}</div>
        <div style="font-size: 0.78rem; margin-top: 6px; color: #475569;">
            *Notice: Measured Productivity reflects verified closed deliverables and on-time adherence. Modeled figures reflect baseline simulations.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 14 KPI Cards in a structured 5-column / 3-row layout
    st.markdown("### 🎯 Executive Performance Indicators")

    row1_c1, row1_c2, row1_c3, row1_c4, row1_c5 = st.columns(5)
    with row1_c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Employees</div>
            <div class="kpi-value">{kpis['total_employees']}</div>
            <div class="kpi-delta-neutral">Active Headcount</div>
        </div>
        """, unsafe_allow_html=True)
    with row1_c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Weekly Hours</div>
            <div class="kpi-value">{kpis['avg_working_hours']:.1f}</div>
            <div class="kpi-delta-negative">+{kpis['avg_overtime_hours']:.1f} hrs Overtime</div>
        </div>
        """, unsafe_allow_html=True)
    with row1_c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Overtime Hours</div>
            <div class="kpi-value">{kpis['avg_overtime_hours']:.1f}</div>
            <div class="kpi-delta-negative">hrs / week / emp</div>
        </div>
        """, unsafe_allow_html=True)
    with row1_c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Productivity Score</div>
            <div class="kpi-value">{kpis['productivity_score']:.1f}</div>
            <div class="kpi-delta-neutral">Scale 0 - 100 Index</div>
        </div>
        """, unsafe_allow_html=True)
    with row1_c5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Tasks Completed / Emp</div>
            <div class="kpi-value">{kpis['avg_tasks_completed_per_emp']:.1f}</div>
            <div class="kpi-delta-neutral">Verified Deliverables</div>
        </div>
        """, unsafe_allow_html=True)

    row2_c1, row2_c2, row2_c3, row2_c4, row2_c5 = st.columns(5)
    with row2_c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Task Completion Rate</div>
            <div class="kpi-value">{kpis['task_completion_rate']:.1f}%</div>
            <div class="kpi-delta-positive">Closed vs Assigned</div>
        </div>
        """, unsafe_allow_html=True)
    with row2_c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">On-Time Completion</div>
            <div class="kpi-value">{kpis['on_time_completion_rate']:.1f}%</div>
            <div class="kpi-delta-negative">Target: &gt; 85%</div>
        </div>
        """, unsafe_allow_html=True)
    with row2_c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Absenteeism Rate</div>
            <div class="kpi-value">{kpis['absenteeism_rate']:.1f}%</div>
            <div class="kpi-delta-neutral">Scheduled Workdays</div>
        </div>
        """, unsafe_allow_html=True)
    with row2_c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Engagement Score</div>
            <div class="kpi-value">{kpis['engagement_score']:.1f}</div>
            <div class="kpi-delta-neutral">Survey Rating (0-10)</div>
        </div>
        """, unsafe_allow_html=True)
    with row2_c5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Performance Rating</div>
            <div class="kpi-value">{kpis['performance_rating']:.1f}</div>
            <div class="kpi-delta-neutral">Annual Review (1-5)</div>
        </div>
        """, unsafe_allow_html=True)

    row3_c1, row3_c2, row3_c3, row3_c4 = st.columns(4)
    with row3_c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Excessive Workload Staff</div>
            <div class="kpi-value">{kpis['pct_excessive_workload']:.1f}%</div>
            <div class="kpi-delta-negative">&gt;8 hrs OT / week</div>
        </div>
        """, unsafe_allow_html=True)
    with row3_c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Declining Depts</div>
            <div class="kpi-value">{kpis['declining_depts_count']}</div>
            <div class="kpi-delta-negative">Negative Productivity Trend</div>
        </div>
        """, unsafe_allow_html=True)
    with row3_c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Potential Bottlenecks</div>
            <div class="kpi-value">{kpis['potential_bottlenecks_count']}</div>
            <div class="kpi-delta-negative">Process & Resource Chokes</div>
        </div>
        """, unsafe_allow_html=True)
    with row3_c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Overtime Expenditure</div>
            <div class="kpi-value">${kpis['estimated_overtime_expenditure']:,.0f}</div>
            <div class="kpi-delta-neutral">Period Payroll Impact</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Interactive Trend Visualizations
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("#### 📈 Longitudinal Hours & Overtime Surge by Department")
        trend_df = compute_longitudinal_trends(datasets)
        if not trend_df.empty:
            fig_trend = px.line(
                trend_df,
                x="reporting_date",
                y="avg_overtime",
                color="department",
                title="Average Weekly Overtime Trajectory (26 Weeks)",
                labels={"reporting_date": "Reporting Date", "avg_overtime": "Avg Overtime (hrs/wk)", "department": "Department"}
            )
            fig_trend.update_layout(**get_plotly_theme()["layout"])
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No longitudinal trend data available.")

    with col_right:
        st.markdown("#### 🏢 Departmental Productivity Index Ranking")
        if not dept_df.empty:
            fig_dept = px.bar(
                dept_df,
                x="Productivity Index",
                y="Department",
                orientation="h",
                color="Productivity Index",
                color_continuous_scale="Blues",
                title="Departmental Composite Productivity (0-100)"
            )
            dept_layout = get_plotly_theme()["layout"].copy()
            dept_layout["yaxis"] = dict(autorange="reversed", showgrid=True, gridcolor="#f1f5f9")
            fig_dept.update_layout(**dept_layout)
            st.plotly_chart(fig_dept, use_container_width=True)

    st.markdown("### 📋 Departmental Operational Summary Matrix")
    if not dept_df.empty:
        st.dataframe(dept_df, use_container_width=True, hide_index=True)
