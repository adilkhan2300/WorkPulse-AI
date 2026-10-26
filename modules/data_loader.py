"""
Data Loader and SQLite Persistence Module for WorkPulse AI
Handles loading synthetic data, parsing CSV/Excel uploads, persisting to SQLite,
and generating consolidated analytical tables with dynamic filtering.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from modules.synthetic_data_generator import generate_all_datasets

DB_PATH = "data/workpulse.db"

def init_sqlite_db(datasets: Dict[str, pd.DataFrame], db_path: str = DB_PATH) -> None:
    """Store all datasets into SQLite database for persistent queries and audits."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    for table_name, df in datasets.items():
        if df is not None and not df.empty:
            df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

def load_data_from_db(db_path: str = DB_PATH) -> Optional[Dict[str, pd.DataFrame]]:
    """Loads all tables from SQLite database if present."""
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        datasets = {}
        for (tbl_name,) in tables:
            datasets[tbl_name] = pd.read_sql_query(f"SELECT * FROM {tbl_name}", conn)
        conn.close()
        return datasets if datasets else None
    except Exception:
        return None

def load_default_or_synthetic_data() -> Dict[str, pd.DataFrame]:
    """Loads synthetic CSVs from data/synthetic, or generates them if not present."""
    data_dir = "data/synthetic"
    files = {
        "employees": "employees.csv",
        "workload": "workload.csv",
        "task_performance": "task_performance.csv",
        "attendance": "attendance.csv",
        "engagement": "engagement.csv",
        "performance_reviews": "performance_reviews.csv",
        "process_metrics": "process_metrics.csv"
    }

    datasets = {}
    needs_generation = False
    for k, filename in files.items():
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            needs_generation = True
            break
        else:
            datasets[k] = pd.read_csv(path)

    if needs_generation:
        datasets = generate_all_datasets(data_dir)

    init_sqlite_db(datasets)
    return datasets

def parse_uploaded_file(uploaded_file) -> Optional[pd.DataFrame]:
    """Parse an uploaded CSV or Excel file safely."""
    try:
        filename = uploaded_file.name
        if filename.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        elif filename.endswith((".xls", ".xlsx")):
            return pd.read_excel(uploaded_file)
        else:
            return None
    except Exception as e:
        print(f"Error parsing file: {e}")
        return None

def apply_global_filters(
    datasets: Dict[str, pd.DataFrame],
    date_range: Optional[Tuple[datetime.date, datetime.date]] = None,
    departments: Optional[List[str]] = None,
    job_roles: Optional[List[str]] = None,
    work_arrangements: Optional[List[str]] = None,
    projects: Optional[List[str]] = None,
    task_types: Optional[List[str]] = None,
    min_tenure_months: Optional[int] = None
) -> Dict[str, pd.DataFrame]:
    """
    Applies consistent multi-dimensional filters across all interconnected datasets.
    Preserves referential integrity across filtered views.
    """
    filtered = {}
    
    # 1. Filter Employees first
    emp_df = datasets.get("employees", pd.DataFrame()).copy()
    if not emp_df.empty:
        if departments:
            emp_df = emp_df[emp_df["department"].isin(departments)]
        if job_roles:
            emp_df = emp_df[emp_df["job_role"].isin(job_roles)]
        if work_arrangements:
            emp_df = emp_df[emp_df["work_arrangement"].isin(work_arrangements)]
        if min_tenure_months is not None and "hire_date" in emp_df.columns:
            emp_df["hire_dt"] = pd.to_datetime(emp_df["hire_date"], errors="coerce")
            now = pd.Timestamp.now()
            emp_df["tenure_m"] = (now - emp_df["hire_dt"]).dt.days / 30.4
            emp_df = emp_df[emp_df["tenure_m"] >= min_tenure_months]
            emp_df = emp_df.drop(columns=["hire_dt", "tenure_m"], errors="ignore")
    
    filtered["employees"] = emp_df
    allowed_emp_ids = set(emp_df["employee_id"].unique()) if not emp_df.empty else set()

    # 2. Filter Workload
    wl_df = datasets.get("workload", pd.DataFrame()).copy()
    if not wl_df.empty and allowed_emp_ids:
        wl_df = wl_df[wl_df["employee_id"].isin(allowed_emp_ids)]
        if date_range and "reporting_date" in wl_df.columns:
            wl_df["rep_dt"] = pd.to_datetime(wl_df["reporting_date"], errors="coerce")
            wl_df = wl_df[(wl_df["rep_dt"].dt.date >= date_range[0]) & (wl_df["rep_dt"].dt.date <= date_range[1])]
            wl_df = wl_df.drop(columns=["rep_dt"], errors="ignore")
    filtered["workload"] = wl_df

    # 3. Filter Task Performance
    task_df = datasets.get("task_performance", pd.DataFrame()).copy()
    if not task_df.empty:
        if allowed_emp_ids:
            task_df = task_df[task_df["employee_id"].isin(allowed_emp_ids)]
        if projects:
            task_df = task_df[task_df["project_id"].isin(projects)]
        if task_types:
            task_df = task_df[task_df["task_type"].isin(task_types)]
        if date_range and "task_start_date" in task_df.columns:
            task_df["s_dt"] = pd.to_datetime(task_df["task_start_date"], errors="coerce")
            task_df = task_df[(task_df["s_dt"].dt.date >= date_range[0]) & (task_df["s_dt"].dt.date <= date_range[1])]
            task_df = task_df.drop(columns=["s_dt"], errors="ignore")
    filtered["task_performance"] = task_df

    # 4. Filter Attendance
    att_df = datasets.get("attendance", pd.DataFrame()).copy()
    if not att_df.empty and allowed_emp_ids:
        att_df = att_df[att_df["employee_id"].isin(allowed_emp_ids)]
        if date_range and "reporting_date" in att_df.columns:
            att_df["rep_dt"] = pd.to_datetime(att_df["reporting_date"], errors="coerce")
            att_df = att_df[(att_df["rep_dt"].dt.date >= date_range[0]) & (att_df["rep_dt"].dt.date <= date_range[1])]
            att_df = att_df.drop(columns=["rep_dt"], errors="ignore")
    filtered["attendance"] = att_df

    # 5. Filter Engagement
    eng_df = datasets.get("engagement", pd.DataFrame()).copy()
    if not eng_df.empty and allowed_emp_ids:
        eng_df = eng_df[eng_df["employee_id"].isin(allowed_emp_ids)]
        if date_range and "survey_date" in eng_df.columns:
            eng_df["srv_dt"] = pd.to_datetime(eng_df["survey_date"], errors="coerce")
            eng_df = eng_df[(eng_df["srv_dt"].dt.date >= date_range[0]) & (eng_df["srv_dt"].dt.date <= date_range[1])]
            eng_df = eng_df.drop(columns=["srv_dt"], errors="ignore")
    filtered["engagement"] = eng_df

    # 6. Filter Performance Reviews
    rev_df = datasets.get("performance_reviews", pd.DataFrame()).copy()
    if not rev_df.empty and allowed_emp_ids:
        rev_df = rev_df[rev_df["employee_id"].isin(allowed_emp_ids)]
        if date_range and "review_date" in rev_df.columns:
            rev_df["rev_dt"] = pd.to_datetime(rev_df["review_date"], errors="coerce")
            rev_df = rev_df[(rev_df["rev_dt"].dt.date >= date_range[0]) & (rev_df["rev_dt"].dt.date <= date_range[1])]
            rev_df = rev_df.drop(columns=["rev_dt"], errors="ignore")
    filtered["performance_reviews"] = rev_df

    # 7. Filter Process Metrics
    proc_df = datasets.get("process_metrics", pd.DataFrame()).copy()
    if not proc_df.empty:
        if departments:
            proc_df = proc_df[proc_df["department"].isin(departments)]
        if date_range and "reporting_date" in proc_df.columns:
            proc_df["rep_dt"] = pd.to_datetime(proc_df["reporting_date"], errors="coerce")
            proc_df = proc_df[(proc_df["rep_dt"].dt.date >= date_range[0]) & (proc_df["rep_dt"].dt.date <= date_range[1])]
            proc_df = proc_df.drop(columns=["rep_dt"], errors="ignore")
    filtered["process_metrics"] = proc_df

    return filtered
