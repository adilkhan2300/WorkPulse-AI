"""
Cost and Business Impact Analysis View for WorkPulse AI
Quantifies the financial toll of overtime, rework, delays, and queue bottlenecks.
Compares intervention costs with projected operational savings and computes ROI.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any
from modules.productivity_metrics import calculate_executive_kpis
from modules.bottleneck_detection import detect_operational_bottlenecks
from modules.capacity_planning import calculate_capacity_utilization
from modules.intervention_engine import generate_evidence_based_interventions
from modules.cost_analysis import compute_operational_cost_breakdown, compute_intervention_roi, DEFAULT_COST_ASSUMPTIONS
from utils.styles import get_plotly_theme

def render_costs_view(datasets: Dict[str, pd.DataFrame]):
    st.markdown("## 💰 Cost & Business Impact Analysis")
    st.caption("Quantifying operational inefficiencies, overtime burdens, rework expenses, and computing intervention ROI.")

    # Assumptions Configuration Box
    with st.expander("⚙️ Adjust Financial & Cost Modeling Assumptions", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        base_rate = c1.number_input("Default Hourly Rate ($/hr)", 25.0, 150.0, float(DEFAULT_COST_ASSUMPTIONS["default_hourly_rate"]), 5.0)
        ot_mult = c2.number_input("Overtime Multiplier", 1.0, 2.5, float(DEFAULT_COST_ASSUMPTIONS["overtime_premium_multiplier"]), 0.25)
        delay_pen = c3.number_input("Daily Delay Penalty ($/day)", 50.0, 500.0, float(DEFAULT_COST_ASSUMPTIONS["daily_delay_penalty"]), 25.0)
        loaded_fac = c4.number_input("Overhead Loaded Factor", 1.0, 2.0, float(DEFAULT_COST_ASSUMPTIONS["overhead_loaded_factor"]), 0.05)

        active_assumptions = {
            "default_hourly_rate": base_rate,
            "overtime_premium_multiplier": ot_mult,
            "daily_delay_penalty": delay_pen,
            "overhead_loaded_factor": loaded_fac
        }

    kpis = calculate_executive_kpis(datasets)
    costs = compute_operational_cost_breakdown(datasets, kpis, active_assumptions)

    # 4 Main Financial Impact Metrics
    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    c_m1.metric("Recorded Overtime Cost", f"${costs['recorded_overtime_expenditure']:,.0f}", f"{costs['total_overtime_hours']:,.0f} Hours Logged")
    c_m2.metric("Rework Waste Payroll", f"${costs['rework_waste_cost']:,.0f}", f"{costs['total_rework_hours']:,.0f} Wasted Hours")
    c_m3.metric("Estimated Delay Penalty", f"${costs['delay_penalty_cost']:,.0f}", f"{costs['delayed_tasks_count']} Delayed Tasks")
    c_m4.metric("Process Idle Waiting Loss", f"${costs['process_idle_cost']:,.0f}", f"{costs['total_wait_hours']:,.0f} Blocked Hours")

    st.markdown(f"""
    <div class="alert-box-critical" style="margin-top: 14px;">
        <span style="font-size: 1.1rem; font-weight: 800;">
            Total Estimated Operational Inefficiency Burden: ${costs['total_operational_burden']:,.2f}
        </span><br/>
        <span>This represents capital consumed by chronic overtime premiums, rework corrections, schedule penalties, and idle waiting.</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Visual Breakdown of Cost Components
    col_chart1, col_chart2 = st.columns([3, 2])

    with col_chart1:
        cost_breakdown_df = pd.DataFrame({
            "Cost Category": ["Overtime Premium", "Rework Payroll Waste", "Delivery Delay Penalty", "Process Waiting Loss"],
            "Amount": [
                costs["recorded_overtime_expenditure"],
                costs["rework_waste_cost"],
                costs["delay_penalty_cost"],
                costs["process_idle_cost"]
            ],
            "Type": ["Actual Incurred", "Loaded Labor Loss", "Estimated Penalty", "Latency Opportunity Loss"]
        })

        fig_cost_bar = px.bar(
            cost_breakdown_df,
            x="Cost Category",
            y="Amount",
            color="Cost Category",
            text_auto="$,.0f",
            title="Operational Financial Burden by Inefficiency Source"
        )
        fig_cost_bar.update_layout(**get_plotly_theme()["layout"], showlegend=False)
        st.plotly_chart(fig_cost_bar, use_container_width=True)

    with col_chart2:
        fig_cost_pie = px.pie(
            cost_breakdown_df,
            names="Cost Category",
            values="Amount",
            hole=0.45,
            title="Share of Financial Inefficiency"
        )
        fig_cost_pie.update_layout(**get_plotly_theme()["layout"])
        st.plotly_chart(fig_cost_pie, use_container_width=True)

    # Section 2: Intervention ROI & Cost-Benefit Analysis
    st.markdown("---")
    st.markdown("### 📈 Cost-Benefit & Intervention ROI Comparison")
    st.caption("Evaluating capital investment vs projected operational cost recovery across proposed interventions.")

    bottlenecks = detect_operational_bottlenecks(datasets)
    capacity_df = calculate_capacity_utilization(datasets)
    interventions = generate_evidence_based_interventions(datasets, kpis, bottlenecks, capacity_df)
    roi_df = compute_intervention_roi(costs, interventions)

    if not roi_df.empty:
        st.dataframe(roi_df, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="alert-box-info">
        <b>📘 Accounting Disclosure:</b> Financial figures separate verified recorded payroll expenses (overtime) from 
        model-based scenario projections (rework and delay penalties). All ROI multiples reflect theoretical potential savings and should be audited quarterly.
    </div>
    """, unsafe_allow_html=True)
