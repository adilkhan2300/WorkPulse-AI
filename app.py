"""
WorkPulse AI — Employee Productivity, Workload & Operational Bottleneck Intelligence
Main Application Launcher & Navigation Controller
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. Page Configuration
st.set_page_config(
    page_title="WorkPulse AI — Workforce Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Imports
from utils.styles import apply_custom_css
from modules.data_loader import load_default_or_synthetic_data, apply_global_filters

# Import all 13 modular views
from views.view_overview import render_overview_view
from views.view_upload import render_upload_view
from views.view_productivity import render_productivity_view
from views.view_working_hours import render_working_hours_view
from views.view_workload import render_workload_view
from views.view_bottlenecks import render_bottlenecks_view
from views.view_ml import render_ml_view
from views.view_llm import render_llm_view
from views.view_interventions import render_interventions_view
from views.view_costs import render_costs_view
from views.view_simulator import render_simulator_view
from views.view_reports import render_reports_view
from views.view_methodology import render_methodology_view

# Apply modern styling
apply_custom_css()

# 3. State Initialization
if "raw_datasets" not in st.session_state:
    with st.spinner("Initializing WorkPulse AI organizational database..."):
        st.session_state["raw_datasets"] = load_default_or_synthetic_data()

raw_data = st.session_state["raw_datasets"]

# 4. Sidebar: Branding & Navigation
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 8px;">
        <span style="font-size: 1.8rem; margin-right: 8px;">💼</span>
        <div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a; line-height: 1.1;">WorkPulse AI</div>
            <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">Workforce & Bottleneck Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    PAGES = [
        "1. Executive Overview",
        "2. Data Upload and Validation",
        "3. Productivity Analytics",
        "4. Working Hours vs. Productivity",
        "5. Workload and Capacity",
        "6. Bottleneck Intelligence",
        "7. Machine Learning Insights",
        "8. LLM Recommendations",
        "9. Intervention Planner",
        "10. Cost Analysis",
        "11. Scenario Simulator",
        "12. Reports and Exports",
        "13. Methodology"
    ]

    selected_page = st.radio("Navigation", PAGES, index=0, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 🔍 Multi-Dimensional Filters")

    # Global Filter Controls
    emp_df = raw_data.get("employees", pd.DataFrame())
    wl_df = raw_data.get("workload", pd.DataFrame())
    task_df = raw_data.get("task_performance", pd.DataFrame())

    # Date Range Filter
    if not wl_df.empty and "reporting_date" in wl_df.columns:
        parsed_dates = pd.to_datetime(wl_df["reporting_date"], errors="coerce").dropna()
        min_date = parsed_dates.min().date() if not parsed_dates.empty else date(2025, 8, 1)
        max_date = parsed_dates.max().date() if not parsed_dates.empty else date(2026, 1, 31)
    else:
        min_date, max_date = date(2025, 8, 1), date(2026, 1, 31)

    date_filter = st.date_input(
        "Reporting Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Departments Filter
    all_depts = sorted(list(emp_df["department"].dropna().unique())) if not emp_df.empty else []
    dept_filter = st.multiselect("Department", all_depts, default=[])

    # Job Roles Filter
    if dept_filter:
        available_roles = sorted(list(emp_df[emp_df["department"].isin(dept_filter)]["job_role"].dropna().unique()))
    else:
        available_roles = sorted(list(emp_df["job_role"].dropna().unique())) if not emp_df.empty else []
    role_filter = st.multiselect("Job Role", available_roles, default=[])

    # Work Arrangement Filter
    arrangements = sorted(list(emp_df["work_arrangement"].dropna().unique())) if not emp_df.empty else []
    arr_filter = st.multiselect("Work Arrangement", arrangements, default=[])

    # Project Filter
    all_projects = sorted(list(task_df["project_id"].dropna().unique())) if not task_df.empty else []
    project_filter = st.multiselect("Project ID", all_projects, default=[])

    # Task Type Filter
    all_task_types = sorted(list(task_df["task_type"].dropna().unique())) if not task_df.empty else []
    task_type_filter = st.multiselect("Task Type", all_task_types, default=[])

    # Tenure Filter
    tenure_filter = st.slider("Min Employee Tenure (Months)", 0, 48, 0)

    # Filter reset button
    if st.button("Reset All Filters", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.caption("MBA & General Management Intelligence System | v2.4 (Antigravity)")

# 5. Apply Global Filters
active_date_range = date_filter if isinstance(date_filter, tuple) and len(date_filter) == 2 else (min_date, max_date)

filtered_datasets = apply_global_filters(
    datasets=raw_data,
    date_range=active_date_range,
    departments=dept_filter if dept_filter else None,
    job_roles=role_filter if role_filter else None,
    work_arrangements=arr_filter if arr_filter else None,
    projects=project_filter if project_filter else None,
    task_types=task_type_filter if task_type_filter else None,
    min_tenure_months=tenure_filter if tenure_filter > 0 else None
)

# 6. Route to Selected Page
if selected_page.startswith("1."):
    render_overview_view(filtered_datasets)
elif selected_page.startswith("2."):
    render_upload_view(filtered_datasets)
elif selected_page.startswith("3."):
    render_productivity_view(filtered_datasets)
elif selected_page.startswith("4."):
    render_working_hours_view(filtered_datasets)
elif selected_page.startswith("5."):
    render_workload_view(filtered_datasets)
elif selected_page.startswith("6."):
    render_bottlenecks_view(filtered_datasets)
elif selected_page.startswith("7."):
    render_ml_view(filtered_datasets)
elif selected_page.startswith("8."):
    render_llm_view(filtered_datasets)
elif selected_page.startswith("9."):
    render_interventions_view(filtered_datasets)
elif selected_page.startswith("10."):
    render_costs_view(filtered_datasets)
elif selected_page.startswith("11."):
    render_simulator_view(filtered_datasets)
elif selected_page.startswith("12."):
    render_reports_view(filtered_datasets)
elif selected_page.startswith("13."):
    render_methodology_view()
