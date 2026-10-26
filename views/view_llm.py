"""
LLM Productivity Insights View for WorkPulse AI
Translates complex workforce telemetry into structured executive narratives.
Provides interactive question answering using OpenAI API with automatic rule-based fallback.
"""

import os
import streamlit as st
import pandas as pd
from typing import Dict, Any
from modules.productivity_metrics import calculate_executive_kpis
from modules.bottleneck_detection import detect_operational_bottlenecks
from modules.statistical_analysis import prepare_productivity_analytical_dataset, run_diminishing_returns_regression
from modules.llm_insights import generate_management_llm_insight

def render_llm_view(datasets: Dict[str, pd.DataFrame]):
    st.markdown("## 🧠 LLM-Powered Executive Productivity Advisor")
    st.caption("AI-synthesized strategic management guidance translating empirical signals into actionable policy interventions.")

    kpis = calculate_executive_kpis(datasets)
    bottlenecks = detect_operational_bottlenecks(datasets)
    analysis_df = prepare_productivity_analytical_dataset(datasets)
    reg_res = run_diminishing_returns_regression(analysis_df)

    # API Configuration Expander
    with st.expander("🔑 Configure External LLM API (Optional)", expanded=False):
        col_k1, col_k2 = st.columns([3, 1])
        api_input = col_k1.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""), placeholder="sk-proj-...")
        col_k2.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        save_btn = col_k2.button("Apply Key")
        if save_btn and api_input:
            st.session_state["user_api_key"] = api_input
            st.success("API key stored for session.")
        st.caption("ℹ️ If no API key is provided, the platform automatically utilizes its built-in rule-based expert intelligence engine.")

    active_key = st.session_state.get("user_api_key", os.getenv("OPENAI_API_KEY", ""))

    # Interactive Query Box
    st.markdown("### 💬 Ask WorkPulse AI Executive Advisor")
    preset_questions = [
        "Executive Assessment: Why are increasing hours failing to improve output?",
        "How can we rebalance Senior Engineer workload without dropping deliverables?",
        "What operational changes will eliminate the QA gate bottleneck?",
        "Assess the financial impact of our current task rework rates."
    ]

    selected_preset = st.selectbox("Select a standard strategic query or enter your own:", ["-- Custom Query --"] + preset_questions)
    if selected_preset != "-- Custom Query --":
        user_query = st.text_input("Strategic Prompt", value=selected_preset)
    else:
        user_query = st.text_input("Strategic Prompt", placeholder="e.g. Provide a tactical plan to stabilize Engineering overtime")

    generate_btn = st.button("✨ Generate Executive Assessment", type="primary")

    # Generate or load cached insight
    if generate_btn or "cached_llm_insight" not in st.session_state:
        with st.spinner("Synthesizing organizational telemetry and statistical regressions..."):
            insight = generate_management_llm_insight(
                kpis=kpis,
                bottlenecks=bottlenecks,
                regression_results=reg_res,
                openai_api_key=active_key,
                user_query=user_query
            )
            st.session_state["cached_llm_insight"] = insight
    else:
        insight = st.session_state["cached_llm_insight"]

    # Display Engine Source Pill
    source_tag = insight.get("source", "Rule-Based Insight Engine")
    st.markdown(f"<span class='badge-pill badge-blue'>Engine Source: {source_tag}</span>", unsafe_allow_html=True)
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Render Structured Response Card
    st.markdown(f"""
    <div style="background: white; border: 1px solid #cbd5e1; border-radius: 12px; padding: 22px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-bottom: 12px;">
            📋 Executive Finding & Diagnosis
        </div>
        <div style="font-size: 1.05rem; line-height: 1.6; color: #1e293b; background-color: #f8fafc; padding: 14px 18px; border-radius: 8px; border-left: 4px solid #2563eb; margin-bottom: 18px;">
            {insight.get('executive_finding')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    col_l1, col_l2 = st.columns(2)

    with col_l1:
        st.markdown("#### 🔍 Empirical Evidence from Active Data")
        evidence_list = insight.get("evidence_from_data", [])
        if isinstance(evidence_list, list):
            for ev in evidence_list:
                st.markdown(f"- 📊 {ev}")
        else:
            st.markdown(f"- 📊 {evidence_list}")

        st.markdown("#### ⚙️ Key Contributing Factors")
        factors = insight.get("contributing_factors", [])
        if isinstance(factors, list):
            for f in factors:
                st.markdown(f"- ⚠️ {f}")
        else:
            st.markdown(f"- ⚠️ {factors}")

        st.markdown("#### 🏢 Impacted Teams & Processes")
        st.markdown(f"**Target:** `{insight.get('affected_team_or_process')}`")

    with col_l2:
        st.markdown("#### 💡 Recommended Strategic Intervention")
        st.markdown(f"""
        <div class="alert-box-info" style="font-size: 0.95rem;">
            {insight.get('recommended_intervention')}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🔬 Suggested Further Investigation")
        st.markdown(f"*{insight.get('suggested_investigation')}*")

        st.markdown("#### 🎯 Target KPI to Monitor")
        st.markdown(f"`{insight.get('kpi_to_monitor')}`")

        st.markdown("#### 📈 Expected Direction of Impact")
        st.markdown(f"*{insight.get('expected_direction_of_impact')}*")

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size: 0.8rem; color: #64748b;">
        <b>Data Integrity & Governance Guarantee:</b> {insight.get('limitations_and_confidence')}
    </div>
    """, unsafe_allow_html=True)
