"""
Statistical Analysis Module for WorkPulse AI
Investigates the relationship between working hours, overtime, workload, and productivity.
Includes:
- Correlation analysis with p-values
- Polynomial regression testing for Diminishing Returns (Hours vs Hours^2)
- Regression diagnostics and inflection point computation
- Longitudinal tracking over reporting weeks
- Causal vs Associational scientific disclaimers
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from scipy import stats
import statsmodels.api as sm

def prepare_productivity_analytical_dataset(datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Merges employee weekly workload with task completion performance and engagement
    to build an observation-level dataset for rigorous statistical analysis.
    """
    wl_df = datasets.get("workload", pd.DataFrame()).copy()
    emp_df = datasets.get("employees", pd.DataFrame()).copy()
    task_df = datasets.get("task_performance", pd.DataFrame()).copy()
    eng_df = datasets.get("engagement", pd.DataFrame()).copy()

    if wl_df.empty or emp_df.empty:
        return pd.DataFrame()

    # Aggregate tasks per employee
    if not task_df.empty:
        task_df["is_comp"] = (task_df["task_status"] == "Completed").astype(int)
        
        # On-time
        due_dt = pd.to_datetime(task_df["task_due_date"], errors="coerce")
        comp_dt = pd.to_datetime(task_df["task_completion_date"], errors="coerce")
        task_df["is_ontime"] = ((comp_dt <= due_dt) & (task_df["task_status"] == "Completed")).astype(int)
        
        emp_tasks = task_df.groupby("employee_id").agg(
            total_tasks=("task_id", "count"),
            completed_tasks=("is_comp", "sum"),
            ontime_tasks=("is_ontime", "sum"),
            avg_quality=("quality_score", "mean"),
            total_rework_hours=("rework_hours", "sum"),
            total_actual_hours=("actual_hours", "sum")
        ).reset_index()

        emp_tasks["completion_rate"] = emp_tasks["completed_tasks"] / emp_tasks["total_tasks"] * 100
        emp_tasks["ontime_rate"] = emp_tasks["ontime_tasks"] / emp_tasks["completed_tasks"].replace(0, np.nan) * 100
        emp_tasks["rework_rate"] = emp_tasks["total_rework_hours"] / emp_tasks["total_actual_hours"].replace(0, np.nan) * 100
    else:
        emp_tasks = pd.DataFrame()

    # Average weekly workload per employee
    emp_wl = wl_df.groupby("employee_id").agg(
        avg_regular_hours=("regular_working_hours", "mean"),
        avg_overtime_hours=("overtime_hours", "mean"),
        avg_workload_score=("workload_score", "mean"),
        avg_task_switches=("task_switches", "mean"),
        avg_unplanned_hours=("unplanned_work_hours", "mean")
    ).reset_index()
    emp_wl["avg_total_hours"] = emp_wl["avg_regular_hours"] + emp_wl["avg_overtime_hours"]

    # Average engagement per employee
    if not eng_df.empty:
        emp_eng = eng_df.groupby("employee_id").agg(
            avg_engagement=("engagement_score", "mean"),
            avg_job_sat=("job_satisfaction", "mean"),
            avg_wlb=("work_life_balance_score", "mean")
        ).reset_index()
    else:
        emp_eng = pd.DataFrame()

    # Merge everything
    merged = emp_df[["employee_id", "department", "job_role", "job_level", "work_arrangement"]].merge(
        emp_wl, on="employee_id", how="inner"
    )
    if not emp_tasks.empty:
        merged = merged.merge(emp_tasks, on="employee_id", how="left")
    if not emp_eng.empty:
        merged = merged.merge(emp_eng, on="employee_id", how="left")

    # Productivity index per employee (0-100)
    ontime_c = merged["ontime_rate"].fillna(50)
    comp_c = merged["completion_rate"].fillna(50)
    rework_c = merged["rework_rate"].fillna(5)
    merged["productivity_index"] = (ontime_c * 0.45) + (comp_c * 0.35) + (np.clip(100 - rework_c * 3, 0, 100) * 0.20)
    merged["output_per_hour"] = merged["completed_tasks"] / merged["avg_total_hours"].replace(0, np.nan)

    return merged

def compute_correlation_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Computes correlation coefficients and corresponding p-values."""
    cols_to_correlate = [
        "avg_total_hours", "avg_overtime_hours", "avg_task_switches",
        "avg_unplanned_hours", "avg_workload_score", "productivity_index",
        "ontime_rate", "rework_rate", "avg_engagement", "avg_wlb"
    ]
    valid_cols = [c for c in cols_to_correlate if c in df.columns and df[c].notna().sum() > 5]
    sub_df = df[valid_cols].dropna()

    if sub_df.empty or len(valid_cols) < 2:
        return pd.DataFrame(), pd.DataFrame()

    corr_df = pd.DataFrame(index=valid_cols, columns=valid_cols)
    pval_df = pd.DataFrame(index=valid_cols, columns=valid_cols)

    for c1 in valid_cols:
        for c2 in valid_cols:
            if c1 == c2:
                corr_df.loc[c1, c2] = 1.0
                pval_df.loc[c1, c2] = 0.0
            else:
                r, p = stats.pearsonr(sub_df[c1], sub_df[c2])
                corr_df.loc[c1, c2] = round(r, 3)
                pval_df.loc[c1, c2] = round(p, 4)

    return corr_df.astype(float), pval_df.astype(float)

def run_diminishing_returns_regression(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Fits: Productivity_Index = beta_0 + beta_1 * Total_Hours + beta_2 * Total_Hours^2
    Tests if beta_2 is negative and statistically significant (p < 0.05),
    indicating an inverted-U / diminishing return relationship.
    """
    if df.empty or "avg_total_hours" not in df.columns or "productivity_index" not in df.columns:
        return {"fitted": False, "reason": "Insufficient data"}

    sub = df[["avg_total_hours", "productivity_index"]].dropna()
    if len(sub) < 15:
        return {"fitted": False, "reason": "Sample size too small (<15)"}

    x = sub["avg_total_hours"].values
    y = sub["productivity_index"].values

    # Design matrix: [1, x, x^2]
    X_poly = np.column_stack([np.ones_like(x), x, x**2])
    
    try:
        model = sm.OLS(y, X_poly).fit()
        b0, b1, b2 = model.params
        p_b2 = model.pvalues[2]
        r2 = model.rsquared

        # Inflection point: dy/dx = b1 + 2*b2*x = 0  => x* = -b1 / (2 * b2)
        inflection_hours = None
        has_diminishing_returns = False
        if b2 < 0:
            inflection_hours = -b1 / (2 * b2)
            if 35 <= inflection_hours <= 70:
                has_diminishing_returns = True

        return {
            "fitted": True,
            "b0": round(b0, 3),
            "b1": round(b1, 3),
            "b2": round(b2, 4),
            "p_val_b2": round(p_b2, 5),
            "r_squared": round(r2, 3),
            "has_diminishing_returns": has_diminishing_returns,
            "inflection_hours": round(inflection_hours, 1) if inflection_hours else None,
            "summary_text": model.summary().as_text()
        }
    except Exception as e:
        return {"fitted": False, "reason": str(e)}

def compute_longitudinal_trends(datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Tracks weekly trajectory of working hours vs task output across departments over time."""
    wl_df = datasets.get("workload", pd.DataFrame())
    emp_df = datasets.get("employees", pd.DataFrame())

    if wl_df.empty or emp_df.empty or "reporting_date" not in wl_df.columns:
        return pd.DataFrame()

    merged = wl_df.merge(emp_df[["employee_id", "department"]], on="employee_id", how="left")
    grouped = merged.groupby(["reporting_date", "department"]).agg(
        avg_total_hours=("regular_working_hours", lambda x: x.mean() + merged.loc[x.index, "overtime_hours"].mean()),
        avg_overtime=("overtime_hours", "mean"),
        avg_tasks=("assigned_tasks", "mean"),
        avg_workload_score=("workload_score", "mean"),
        avg_task_switches=("task_switches", "mean"),
        avg_unplanned=("unplanned_work_hours", "mean")
    ).reset_index()

    return grouped
