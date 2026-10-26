"""
Intervention Planner View for WorkPulse AI
Presents strategic workforce and process interventions across 5 core management pillars:
A: Workload Redistribution, B: Process Optimization, C: Capacity & Staffing,
D: Sustainable Work Practices, E: Employee Development.
Includes interactive adoption tracker.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from modules.productivity_metrics import calculate_executive_kpis
from modules.bottleneck_detection import detect_operational_bottlenecks
from modules.capacity_planning import calculate_capacity_utilization
from modules.intervention_engine import generate_evidence_based_interventions

def render_interventions_view(datasets: Dict[str, pd.DataFrame]):
    st.markdown("## 📋 Strategic Workload Intervention Planner")
    st.caption("Actionable management interventions structured across 5 core operational pillars. Formulated as testable hypotheses.")

    kpis = calculate_executive_kpis(datasets)
    bottlenecks = detect_operational_bottlenecks(datasets)
    capacity_df = calculate_capacity_utilization(datasets)

    interventions = generate_evidence_based_interventions(datasets, kpis, bottlenecks, capacity_df)

    if not interventions:
        st.info("No active interventions generated under current workload metrics.")
        return

    # Filter by Category
    categories = ["All Pillars"] + sorted(list(set(itv["category"] for itv in interventions)))
    selected_cat = st.selectbox("Filter by Strategic Pillar", categories)

    filtered_itvs = interventions if selected_cat == "All Pillars" else [i for i in interventions if i["category"] == selected_cat]

    st.markdown(f"### 🎯 Strategic Interventions ({len(filtered_itvs)} Active Proposals)")

    for idx, itv in enumerate(filtered_itvs, 1):
        prio = itv.get("priority", "Medium")
        badge_class = "badge-critical" if prio == "Critical" else ("badge-high" if prio == "High" else "badge-medium")

        with st.container():
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px; margin-bottom: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a;">
                        {idx}. {itv.get('title')}
                    </div>
                    <div>
                        <span class="badge-pill {badge_class}">{prio.upper()} PRIORITY</span>
                        <span class="badge-pill badge-blue" style="margin-left: 6px;">{itv.get('category')}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([3, 2])

            with col1:
                st.markdown(f"**Proposed Operational Action:**")
                st.markdown(f"""
                <div style="background-color: #f8fafc; padding: 10px 14px; border-radius: 6px; border-left: 3px solid #3b82f6; font-size: 0.92rem; color: #1e293b; margin-bottom: 8px;">
                    {itv.get('proposed_action')}
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"**Empirical Evidence:** {itv.get('supporting_evidence')}")
                st.markdown(f"**Target Department:** `{itv.get('department')}` &nbsp;|&nbsp; **Review Cycle:** `{itv.get('suggested_review_period')}`")

            with col2:
                st.markdown(f"**Estimated Implementation Cost/Effort:** `{itv.get('estimated_effort_cost')}`")
                st.markdown(f"**Hypothesized Impact Direction:** *{itv.get('expected_impact')}*")
                st.markdown(f"**Target Evaluation KPI:** 🎯 `{itv.get('kpi_for_evaluation')}`")

                # Action status selector for management tracking
                status_key = f"itv_status_{idx}_{itv.get('title')[:10]}"
                st.selectbox(
                    "Implementation Status",
                    ["Not Started", "In Scoping", "Pilot Underway", "Adopted", "Rejected"],
                    index=0,
                    key=status_key
                )

            st.markdown("<hr style='border: 0.5px solid #f1f5f9; margin-top: 10px; margin-bottom: 16px;' />", unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-box-info">
        <b>💡 Management Principle:</b> No intervention guarantees instant output acceleration. 
        Each initiative should be run as an operational experiment, monitoring the designated KPI over the suggested review period before permanent codification.
    </div>
    """, unsafe_allow_html=True)
