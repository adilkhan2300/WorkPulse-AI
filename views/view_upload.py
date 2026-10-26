"""
Data Upload and Validation View for WorkPulse AI
Allows independent file uploads for all 7 organizational datasets,
runs the validation engine, displays health audits, and offers downloadable templates.
"""

import os
import streamlit as st
import pandas as pd
from typing import Dict, Any
from modules.data_validation import validate_datasets
from modules.data_loader import parse_uploaded_file, load_default_or_synthetic_data, init_sqlite_db

TABLE_DESCRIPTIONS = {
    "employees": "Core personnel master: IDs, department, role, job level, tenure, contract hours, pay rate.",
    "workload": "Weekly workload logs: regular hours, overtime, assigned tasks, project count, context switches.",
    "task_performance": "Granular task lifecycle: priority, estimated vs actual hours, start, due, completion, quality, rework.",
    "attendance": "Weekly attendance tracking: scheduled workdays, unplanned absences, approved leave.",
    "engagement": "Pulse survey ratings: engagement, satisfaction, work-life balance, manager support.",
    "performance_reviews": "Quarterly / annual reviews: ratings, goal completion percentage, feedback.",
    "process_metrics": "Staged process telemetry: queue lengths, average wait times, blocked tasks, error rates."
}

def render_upload_view(datasets: Dict[str, pd.DataFrame]):
    st.markdown("## 📥 Data Upload & Schema Validation Center")
    st.caption("Upload company datasets independently or use the pre-loaded synthetic organizational cohort. Never silently invents missing metrics.")

    # Top Action Bar
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.info("💡 **Integrity Assurance:** The validation engine audits data types, referential consistency, boundary constraints (negative hours/impossible dates), and generates a comprehensive quality report.")
    with top_col2:
        if st.button("🔄 Reload Synthetic Demo Cohort", use_container_width=True):
            st.session_state["raw_datasets"] = load_default_or_synthetic_data()
            st.success("Synthetic dataset reloaded successfully!")
            st.rerun()

    # Upload Section (Tabs for modularity)
    st.markdown("### 📂 Upload Datasets (CSV or Excel)")
    upload_tabs = st.tabs([
        "1. Employees", "2. Workload", "3. Tasks",
        "4. Attendance", "5. Engagement", "6. Reviews", "7. Processes"
    ])

    tab_table_keys = [
        "employees", "workload", "task_performance",
        "attendance", "engagement", "performance_reviews", "process_metrics"
    ]

    for tab, key in zip(upload_tabs, tab_table_keys):
        with tab:
            st.markdown(f"**Target Dataset:** `{key}`")
            st.caption(TABLE_DESCRIPTIONS[key])
            
            uploaded_file = st.file_uploader(f"Upload {key} (.csv, .xlsx)", key=f"uploader_{key}")
            if uploaded_file is not None:
                parsed_df = parse_uploaded_file(uploaded_file)
                if parsed_df is not None:
                    st.session_state["raw_datasets"][key] = parsed_df
                    init_sqlite_db(st.session_state["raw_datasets"])
                    st.success(f"Successfully updated '{key}' with {len(parsed_df)} records.")
                else:
                    st.error("Failed to parse file. Please verify CSV or Excel structure.")

            current_df = datasets.get(key)
            if current_df is not None and not current_df.empty:
                st.markdown(f"**Current Active Records:** {len(current_df):,} rows | {len(current_df.columns)} columns")
                st.dataframe(current_df.head(5), use_container_width=True)
            else:
                st.warning(f"No records currently loaded for '{key}'.")

    st.markdown("---")

    # Data Quality & Validation Audit Report
    st.markdown("### 🛡️ Data Quality & Integrity Audit Report")
    val_result = validate_datasets(datasets)

    if val_result.is_valid and not val_result.errors:
        st.markdown("""
        <div class="alert-box-success">
            <b>✅ Validation Status: PASSED</b> — All primary entities and critical relational links verified.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-box-critical">
            <b>❌ Validation Status: ISSUES DETECTED</b> — Review error log below before conducting statistical inference.
        </div>
        """, unsafe_allow_html=True)

    # Health Table
    health_rows = []
    for tbl_name, info in val_result.table_health.items():
        health_rows.append({
            "Dataset Table": tbl_name,
            "Status": info["status"],
            "Row Count": f"{info['row_count']:,}",
            "Columns Present": info.get("columns_found", 0),
            "Detected Issues": info["issues"]
        })
    df_health = pd.DataFrame(health_rows)
    st.dataframe(df_health, use_container_width=True, hide_index=True)

    # Errors & Warnings Callout
    if val_result.errors:
        with st.expander("🚨 Critical Errors Requiring Remediation", expanded=True):
            for err in val_result.errors:
                st.markdown(f"- 🔴 {err}")

    if val_result.warnings:
        with st.expander("⚠️ Data Quality Warnings & Observations", expanded=False):
            for warn in val_result.warnings:
                st.markdown(f"- 🟡 {warn}")

    st.markdown("---")

    # Downloadable CSV Templates Section
    st.markdown("### 📥 Download Standard Schema Templates")
    st.caption("Download clean CSV templates populated with headers and example rows.")
    
    template_cols = st.columns(4)
    templates = [
        ("employees_template.csv", "Employees Template"),
        ("workload_template.csv", "Workload Template"),
        ("task_performance_template.csv", "Task Performance Template"),
        ("attendance_template.csv", "Attendance Template"),
        ("engagement_template.csv", "Engagement Template"),
        ("performance_reviews_template.csv", "Performance Reviews Template"),
        ("process_metrics_template.csv", "Process Metrics Template")
    ]

    for idx, (filename, label) in enumerate(templates):
        col = template_cols[idx % 4]
        path = os.path.join("data/templates", filename)
        if os.path.exists(path):
            with open(path, "rb") as f:
                col.download_button(
                    label=f"📄 {label}",
                    data=f.read(),
                    file_name=filename,
                    mime="text/csv",
                    key=f"dl_{filename}"
                )
