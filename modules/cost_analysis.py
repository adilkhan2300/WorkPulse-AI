"""
Cost and Business Impact Analysis Module for WorkPulse AI
Quantifies operational financial costs associated with productivity bottlenecks:
- Overtime expenditure (recorded and projected)
- Rework waste cost (rework hours * loaded labor rate)
- Delayed delivery penalty estimates
- Stalled capacity loss in process queues
- Cost-benefit analysis of interventions vs baseline losses
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

DEFAULT_COST_ASSUMPTIONS = {
    "default_hourly_rate": 55.0,
    "overtime_premium_multiplier": 1.5,
    "daily_delay_penalty": 150.0,
    "overhead_loaded_factor": 1.25 # benefits, facilities, tools
}

def compute_operational_cost_breakdown(
    datasets: Dict[str, pd.DataFrame],
    kpis: Dict[str, Any],
    assumptions: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Computes rigorous financial impact estimates, explicitly separating recorded expenditure
    from model-based assumptions.
    """
    cfg = DEFAULT_COST_ASSUMPTIONS.copy()
    if assumptions:
        cfg.update(assumptions)

    emp_df = datasets.get("employees", pd.DataFrame())
    wl_df = datasets.get("workload", pd.DataFrame())
    task_df = datasets.get("task_performance", pd.DataFrame())
    proc_df = datasets.get("process_metrics", pd.DataFrame())

    # 1. Overtime Expenditure (Actual Recorded / Derived)
    if not wl_df.empty and not emp_df.empty and "hourly_rate" in emp_df.columns:
        merged_ot = wl_df.merge(emp_df[["employee_id", "hourly_rate"]], on="employee_id", how="left")
        merged_ot["rate"] = merged_ot["hourly_rate"].fillna(cfg["default_hourly_rate"])
        ot_expenditure = float((merged_ot["overtime_hours"] * merged_ot["rate"] * cfg["overtime_premium_multiplier"]).sum())
        total_ot_hours = float(merged_ot["overtime_hours"].sum())
    else:
        total_ot_hours = float(wl_df["overtime_hours"].sum()) if not wl_df.empty else 0.0
        ot_expenditure = total_ot_hours * cfg["default_hourly_rate"] * cfg["overtime_premium_multiplier"]

    # 2. Rework Cost (Wasted hours * loaded hourly rate)
    if not task_df.empty:
        total_rework_hours = float(task_df["rework_hours"].sum()) if "rework_hours" in task_df.columns else 0.0
    else:
        total_rework_hours = 0.0
    loaded_hourly_cost = cfg["default_hourly_rate"] * cfg["overhead_loaded_factor"]
    rework_cost = round(total_rework_hours * loaded_hourly_cost, 2)

    # 3. Delivery Delay Financial Impact
    # Number of delayed tasks * average delay days * daily delay penalty
    if not task_df.empty and "task_due_date" in task_df.columns and "task_completion_date" in task_df.columns:
        due_dt = pd.to_datetime(task_df["task_due_date"], errors="coerce")
        comp_dt = pd.to_datetime(task_df["task_completion_date"], errors="coerce")
        delays = (comp_dt - due_dt).dt.days
        pos_delays = delays[delays > 0]
        total_delayed_days = float(pos_delays.sum()) if not pos_delays.empty else 0.0
        delayed_tasks_count = len(pos_delays)
    else:
        total_delayed_days, delayed_tasks_count = 0.0, 0
    estimated_delay_cost = round(total_delayed_days * cfg["daily_delay_penalty"], 2)

    # 4. Process Queue Waiting Idle Loss
    if not proc_df.empty:
        total_wait_hours = float((proc_df["average_waiting_time_hours"] * proc_df["blocked_tasks"]).sum())
        process_idle_cost = round(total_wait_hours * (cfg["default_hourly_rate"] * 0.5), 2) # 50% idle opportunity cost
    else:
        total_wait_hours = 0.0
        process_idle_cost = 0.0

    # Total Operational Inefficiency Burden
    total_cost_burden = round(ot_expenditure + rework_cost + estimated_delay_cost + process_idle_cost, 2)

    return {
        "recorded_overtime_expenditure": round(ot_expenditure, 2),
        "total_overtime_hours": round(total_ot_hours, 1),
        "rework_waste_cost": rework_cost,
        "total_rework_hours": round(total_rework_hours, 1),
        "delay_penalty_cost": estimated_delay_cost,
        "delayed_tasks_count": delayed_tasks_count,
        "total_delayed_days": round(total_delayed_days, 1),
        "process_idle_cost": process_idle_cost,
        "total_wait_hours": round(total_wait_hours, 1),
        "total_operational_burden": total_cost_burden,
        "assumptions_used": cfg
    }

def compute_intervention_roi(
    operational_costs: Dict[str, Any],
    proposed_interventions: list
) -> pd.DataFrame:
    """Estimates payback and net operational cost recovery for each proposed intervention."""
    roi_rows = []
    total_burden = operational_costs.get("total_operational_burden", 250000.0)

    for item in proposed_interventions:
        title = item.get("title", "Intervention")
        dept = item.get("department", "All")
        category = item.get("category", "")
        
        # Estimate implementation cost and potential annual savings
        if "Redistribution" in category:
            impl_cost = 3500.0
            savings_pct = 0.18
        elif "Process Optimization" in category:
            impl_cost = 8000.0
            savings_pct = 0.22
        elif "Staffing" in category:
            impl_cost = 28000.0
            savings_pct = 0.25
        elif "Sustainable" in category:
            impl_cost = 1500.0
            savings_pct = 0.14
        else: # Development
            impl_cost = 4500.0
            savings_pct = 0.12

        estimated_annual_savings = round(total_burden * savings_pct, 2)
        net_annual_benefit = round(estimated_annual_savings - impl_cost, 2)
        roi_multiple = round(estimated_annual_savings / impl_cost, 1) if impl_cost > 0 else 10.0
        payback_months = round((impl_cost / (estimated_annual_savings / 12.0)), 1) if estimated_annual_savings > 0 else 12.0

        roi_rows.append({
            "Intervention": title,
            "Target Department": dept,
            "Implementation Cost ($)": impl_cost,
            "Projected Savings ($)": estimated_annual_savings,
            "Net Benefit ($)": net_annual_benefit,
            "ROI Multiple": f"{roi_multiple}x",
            "Payback Period": f"{payback_months} Months"
        })

    return pd.DataFrame(roi_rows)
