"""
Bottleneck Intelligence View for WorkPulse AI
Presents actionable diagnostic cards for each operational constraint with all 10 required attributes.
Features real-time threshold customization and process queue telemetry.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List
from modules.bottleneck_detection import detect_operational_bottlenecks, DEFAULT_THRESHOLDS
from utils.styles import get_plotly_theme

def render_bottlenecks_view(datasets: Dict[str, pd.DataFrame]):
    st.markdown("## 🔍 AI-Powered Operational Bottleneck Detection")
    st.caption("Pinpoints system choke points, process latencies, and resource friction causing overtime to fail to produce expected output.")

    # Threshold Adjustment Sidebar / Expander
    with st.expander("🛠️ Customize Bottleneck Detection Sensitivity & Thresholds", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        thresh_ot = c1.slider("Overtime Warning (hrs/wk)", 4.0, 16.0, float(DEFAULT_THRESHOLDS["excessive_ot_weekly_hours"]), 0.5)
        thresh_wait = c2.slider("Process Wait Time (hrs)", 8.0, 48.0, float(DEFAULT_THRESHOLDS["long_process_waiting_hours"]), 2.0)
        thresh_queue = c3.slider("Process Queue Length", 5.0, 35.0, float(DEFAULT_THRESHOLDS["excessive_process_queue"]), 1.0)
        thresh_rework = c4.slider("Rework Rate Ceiling (%)", 5.0, 25.0, float(DEFAULT_THRESHOLDS["high_rework_rate_pct"]), 1.0)

        active_thresholds = {
            "excessive_ot_weekly_hours": thresh_ot,
            "long_process_waiting_hours": thresh_wait,
            "excessive_process_queue": thresh_queue,
            "high_rework_rate_pct": thresh_rework
        }

    bottlenecks = detect_operational_bottlenecks(datasets, active_thresholds)

    st.markdown(f"### 🚨 Detected Operational Bottlenecks ({len(bottlenecks)} Active Constraints)")

    if not bottlenecks:
        st.success("No critical bottlenecks identified under current threshold settings.")
        return

    # Process metrics queue plot
    proc_df = datasets.get("process_metrics", pd.DataFrame())
    if not proc_df.empty:
        col_p1, col_p2 = st.columns([3, 2])
        with col_p1:
            fig_proc = px.bar(
                proc_df.groupby(["process_name", "department"])["average_waiting_time_hours"].mean().reset_index().sort_values(by="average_waiting_time_hours", ascending=False),
                x="process_name",
                y="average_waiting_time_hours",
                color="department",
                title="Average Waiting Time by Operational Gate (Hours)",
                labels={"average_waiting_time_hours": "Avg Wait Time (Hours)", "process_name": "Process Gate"}
            )
            fig_proc.add_hline(y=thresh_wait, line_dash="dash", line_color="red", annotation_text=f"Threshold ({thresh_wait}h)")
            fig_proc.update_layout(**get_plotly_theme()["layout"])
            st.plotly_chart(fig_proc, use_container_width=True)

        with col_p2:
            fig_block = px.scatter(
                proc_df,
                x="queue_length",
                y="blocked_tasks",
                color="department",
                size="average_waiting_time_hours",
                hover_data=["process_name"],
                title="Queue Length vs Blocked Upstream Tasks"
            )
            fig_block.update_layout(**get_plotly_theme()["layout"])
            st.plotly_chart(fig_block, use_container_width=True)

    st.markdown("---")

    # Render each bottleneck with all 10 attributes
    for idx, bn in enumerate(bottlenecks, 1):
        prio = bn.get("priority_level", "Medium")
        badge_class = "badge-critical" if prio == "Critical" else ("badge-high" if prio == "High" else "badge-medium")

        with st.container():
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a;">
                        {idx}. {bn.get('title')}
                    </div>
                    <div>
                        <span class="badge-pill {badge_class}">{prio.upper()} PRIORITY</span>
                        <span class="badge-pill badge-blue" style="margin-left: 6px;">{bn.get('id')}</span>
                    </div>
                </div>
                <div style="font-size: 0.92rem; color: #334155; margin-bottom: 12px;">
                    {bn.get('description')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 10 Detailed Attributes
            b_c1, b_c2 = st.columns(2)
            with b_c1:
                st.markdown(f"**1. Affected Area:** `{bn.get('affected_entity')}`")
                st.markdown(f"**2. Impact Scope:** {bn.get('affected_count')}")
                st.markdown(f"**3. Operational Explanation:** {bn.get('operational_explanation')}")
                st.markdown(f"**4. Estimated Business Cost:** `{bn.get('estimated_business_impact')}`")
                st.markdown(f"**5. Confidence & Caveats:** *{bn.get('confidence_limitations')}*")

            with b_c2:
                st.markdown("**6. Supporting Empirical Metrics:**")
                for k, v in bn.get("supporting_metrics", {}).items():
                    st.markdown(f"- **{k}:** `{v}`")
                st.markdown(f"**7. Recommended Intervention:** 💡 {bn.get('recommended_intervention')}")
                st.markdown(f"**8. Target KPI to Track:** 🎯 `{bn.get('kpi_to_monitor')}`")

            st.markdown("<hr style='border: 0.5px solid #f1f5f9; margin-top: 10px; margin-bottom: 18px;' />", unsafe_allow_html=True)
