"""
Workload Imbalance and Capacity Planning Engine for WorkPulse AI
Calculates net available capacity (accounting for contracted hours, leave, and cognitive buffer),
assesses resource utilization, and classifies employees and teams into:
- Underutilized (< 70%)
- Balanced (70% - 95%)
- High Workload (95% - 115%)
- Overallocated (> 115%)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

def calculate_capacity_utilization(
    datasets: Dict[str, pd.DataFrame],
    overhead_buffer_pct: float = 0.15,
    underutilized_threshold: float = 0.70,
    high_threshold: float = 0.95,
    overallocated_threshold: float = 1.15
) -> pd.DataFrame:
    """
    Computes capacity vs demand for each employee across reporting periods.
    Overhead buffer (e.g. 15%) accounts for non-task administrative overhead, syncs, breaks.
    """
    emp_df = datasets.get("employees", pd.DataFrame())
    wl_df = datasets.get("workload", pd.DataFrame())
    att_df = datasets.get("attendance", pd.DataFrame())

    if emp_df.empty or wl_df.empty:
        return pd.DataFrame()

    # Employee baseline weekly contracted hours
    emp_base = emp_df[["employee_id", "department", "job_role", "job_level", "contracted_weekly_hours", "work_arrangement"]].copy()

    # Absence deduction per employee (average weekly absent days)
    if not att_df.empty:
        avg_abs = att_df.groupby("employee_id")["days_absent"].mean().reset_index()
        avg_abs["absence_hours_deduction"] = avg_abs["days_absent"] * 8.0
    else:
        avg_abs = pd.DataFrame({"employee_id": emp_base["employee_id"], "absence_hours_deduction": 0.0})

    # Average weekly assigned demand (regular + overtime)
    avg_demand = wl_df.groupby("employee_id").agg(
        avg_assigned_tasks=("assigned_tasks", "mean"),
        avg_active_projects=("active_projects", "mean"),
        avg_reg_hours=("regular_working_hours", "mean"),
        avg_ot_hours=("overtime_hours", "mean"),
        avg_total_demand_hours=("regular_working_hours", lambda x: x.mean() + wl_df.loc[x.index, "overtime_hours"].mean()),
        avg_switches=("task_switches", "mean")
    ).reset_index()

    merged = emp_base.merge(avg_abs, on="employee_id", how="left").fillna(0.0)
    merged = merged.merge(avg_demand, on="employee_id", how="inner")

    # Net Available Capacity = (Contracted Hours - Absence Hours) * (1 - Overhead Buffer)
    merged["gross_capacity"] = np.maximum(0.0, merged["contracted_weekly_hours"] - merged["absence_hours_deduction"])
    merged["net_available_capacity"] = np.maximum(5.0, merged["gross_capacity"] * (1.0 - overhead_buffer_pct))
    
    # Capacity Utilization Ratio = Total Demand Hours / Net Available Capacity
    merged["capacity_utilization"] = merged["avg_total_demand_hours"] / merged["net_available_capacity"].replace(0, np.nan)
    merged["utilization_pct"] = round(merged["capacity_utilization"] * 100, 1)

    # Classification
    def classify_status(u):
        if pd.isna(u):
            return "Unknown"
        if u < underutilized_threshold:
            return "Underutilized"
        elif u <= high_threshold:
            return "Balanced"
        elif u <= overallocated_threshold:
            return "High Workload"
        else:
            return "Overallocated"

    merged["workload_status"] = merged["capacity_utilization"].apply(classify_status)

    return merged

def diagnose_team_capacity_constraints(capacity_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Diagnoses team-level causes:
    - Excess demand vs insufficient staffing
    - Uneven allocation within team
    - Healthy sustainable state
    """
    if capacity_df.empty or "department" not in capacity_df.columns:
        return []

    diagnostics = []
    for dept, grp in capacity_df.groupby("department"):
        total_team_capacity = grp["net_available_capacity"].sum()
        total_team_demand = grp["avg_total_demand_hours"].sum()
        team_util = (total_team_demand / total_team_capacity) if total_team_capacity > 0 else 1.0

        status_counts = grp["workload_status"].value_counts().to_dict()
        overallocated_cnt = status_counts.get("Overallocated", 0) + status_counts.get("High Workload", 0)
        underutilized_cnt = status_counts.get("Underutilized", 0)
        total_members = len(grp)

        # Workload disparity: standard deviation of demand
        demand_std = grp["avg_total_demand_hours"].std()

        if team_util > 1.15 and underutilized_cnt == 0:
            diagnosis_type = "Severe Capacity Shortage (Understaffed)"
            recommendation = "Demand exceeds aggregate team capacity. Requires head-count expansion or project deselecting."
        elif overallocated_cnt > 0 and underutilized_cnt > 0:
            diagnosis_type = "Internal Workload Mal-distribution"
            recommendation = f"{overallocated_cnt} members are overallocated while {underutilized_cnt} members have spare capacity. Re-allocate tasks internally."
        elif team_util < 0.75:
            diagnosis_type = "Underutilized Capacity"
            recommendation = "Team has surplus capacity available to absorb projects from constrained departments."
        else:
            diagnosis_type = "Sustainable & Balanced"
            recommendation = "Team capacity is well-calibrated to current intake."

        diagnostics.append({
            "department": dept,
            "headcount": total_members,
            "aggregate_net_capacity": round(total_team_capacity, 1),
            "aggregate_demand": round(total_team_demand, 1),
            "team_utilization_pct": round(team_util * 100, 1),
            "overallocated_count": overallocated_cnt,
            "underutilized_count": underutilized_cnt,
            "demand_std_dev": round(demand_std, 1) if not pd.isna(demand_std) else 0.0,
            "diagnosis": diagnosis_type,
            "recommendation": recommendation
        })

    return diagnostics

def compute_project_resource_contention(datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Identifies which projects are drawing from the same strained resources."""
    task_df = datasets.get("task_performance", pd.DataFrame())
    emp_df = datasets.get("employees", pd.DataFrame())
    wl_df = datasets.get("workload", pd.DataFrame())

    if task_df.empty:
        return pd.DataFrame()

    # Employees that have high overtime (>8 hrs)
    if not wl_df.empty:
        strained_emp_ids = set(wl_df.groupby("employee_id")["overtime_hours"].mean().loc[lambda x: x > 8.0].index)
    else:
        strained_emp_ids = set()

    proj_summary = []
    for prj, p_tasks in task_df.groupby("project_id"):
        assigned_emps = set(p_tasks["employee_id"].dropna().unique())
        strained_on_project = assigned_emps.intersection(strained_emp_ids)
        total_hours = p_tasks["actual_hours"].sum()
        rework_hrs = p_tasks["rework_hours"].sum()
        delayed_tasks = 0
        if "task_due_date" in p_tasks.columns and "task_completion_date" in p_tasks.columns:
            due_dt = pd.to_datetime(p_tasks["task_due_date"], errors="coerce")
            comp_dt = pd.to_datetime(p_tasks["task_completion_date"], errors="coerce")
            delayed_tasks = int(((comp_dt > due_dt) | (comp_dt.isna() & (pd.Timestamp.now() > due_dt))).sum())

        proj_summary.append({
            "project_id": prj,
            "total_tasks": len(p_tasks),
            "active_personnel": len(assigned_emps),
            "overallocated_personnel": len(strained_on_project),
            "contention_risk": "Critical" if len(strained_on_project) >= 3 else ("Moderate" if len(strained_on_project) >= 1 else "Low"),
            "total_logged_hours": round(total_hours, 1),
            "rework_hours": round(rework_hrs, 1),
            "delayed_tasks_count": delayed_tasks
        })

    return pd.DataFrame(proj_summary).sort_values(by="overallocated_personnel", ascending=False)
