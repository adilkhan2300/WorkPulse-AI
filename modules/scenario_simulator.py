"""
Productivity Scenario Simulator for WorkPulse AI
Simulates what-if workforce and operational policy scenarios:
- Adjusts Overtime, Headcount, Rework, Waiting Times, Task Switching, and Absenteeism
- Compares baseline reality against simulated hypothetical outcomes
- Calculates changes in capacity, throughput, backlog, on-time rates, costs, and utilization
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def run_what_if_simulation(
    kpis: Dict[str, Any],
    ot_reduction_pct: float = 20.0,
    headcount_change: int = 0,
    rework_reduction_pct: float = 25.0,
    process_wait_reduction_pct: float = 30.0,
    absenteeism_change_pct: float = -15.0,
    task_switching_reduction_pct: float = 20.0
) -> Dict[str, Any]:
    """
    Executes a structured operational simulation comparing baseline metrics with scenario projections.
    Explicitly labels all estimates as hypothetical models under specified parameters.
    """
    base_headcount = kpis.get("total_employees", 120)
    base_ot_hours = kpis.get("avg_overtime_hours", 6.5)
    base_working_hours = kpis.get("avg_working_hours", 46.5)
    base_completion_rate = kpis.get("task_completion_rate", 82.0)
    base_on_time_rate = kpis.get("on_time_completion_rate", 74.0)
    base_rework_pct = kpis.get("rework_rate_pct", 11.5)
    base_backlog = kpis.get("task_backlog_count", 320)
    base_ot_cost = kpis.get("estimated_overtime_expenditure", 145000.0)
    base_absenteeism = kpis.get("absenteeism_rate", 4.8)

    # 1. Projected Workforce & Overtime
    scen_headcount = max(1, base_headcount + headcount_change)
    scen_ot_hours = max(0.0, base_ot_hours * (1.0 - (ot_reduction_pct / 100.0)))
    scen_working_hours = round(40.0 + scen_ot_hours, 1)

    # 2. Overtime Cost
    # Proportional reduction based on hours and headcount
    headcount_factor = scen_headcount / base_headcount if base_headcount > 0 else 1.0
    ot_ratio = scen_ot_hours / base_ot_hours if base_ot_hours > 0 else 0.0
    scen_ot_cost = round(base_ot_cost * ot_ratio * headcount_factor, 2)
    saved_ot_cost = round(base_ot_cost - scen_ot_cost, 2)

    # 3. Available Net Capacity (Weekly Hours across organization)
    # 40 hrs base * headcount * (1 - absenteeism)
    scen_absenteeism = max(0.0, base_absenteeism * (1.0 + (absenteeism_change_pct / 100.0)))
    base_capacity = base_headcount * 40.0 * (1.0 - (base_absenteeism / 100.0)) * 0.85
    scen_capacity = scen_headcount * 40.0 * (1.0 - (scen_absenteeism / 100.0)) * 0.85

    # 4. Rework & Focus Recovery
    scen_rework_pct = max(1.0, base_rework_pct * (1.0 - (rework_reduction_pct / 100.0)))
    rework_hours_saved_pct = (base_rework_pct - scen_rework_pct)

    # Context switching reduction gives back cognitive capacity (~0.3 hrs per 10% reduction)
    focus_gain_factor = 1.0 + (task_switching_reduction_pct / 100.0 * 0.05) + (rework_hours_saved_pct * 0.008)

    # 5. On-Time Delivery Rate & Throughput
    # Shorter process waiting and less rework improves on-time delivery
    wait_benefit = (process_wait_reduction_pct / 100.0) * 8.0 # up to +8% on-time improvement
    rework_benefit = (rework_reduction_pct / 100.0) * 6.0 # up to +6% on-time improvement
    burnout_relief_benefit = min(5.0, (base_ot_hours - scen_ot_hours) * 0.8) # relief from fatigue
    
    scen_on_time_rate = min(98.0, round(base_on_time_rate + wait_benefit + rework_benefit + burnout_relief_benefit, 1))

    # Completion Rate & Backlog Clearance
    scen_completion_rate = min(96.0, round(base_completion_rate + (rework_reduction_pct / 100.0 * 4.0) + (headcount_change * 1.5), 1))
    
    # Backlog reduction
    backlog_clearance_factor = 1.0 - min(0.65, (rework_reduction_pct * 0.005 + process_wait_reduction_pct * 0.004 + max(0, headcount_change) * 0.05))
    scen_backlog = int(round(base_backlog * backlog_clearance_factor))

    # Utilization
    # Baseline utilization: (Base total hours) / (Contracted hours * 0.85)
    base_util = round((base_working_hours / 34.0) * 100, 1)
    scen_util = round((scen_working_hours / 34.0) * 100, 1)

    return {
        "parameters": {
            "ot_reduction_pct": ot_reduction_pct,
            "headcount_change": headcount_change,
            "rework_reduction_pct": rework_reduction_pct,
            "process_wait_reduction_pct": process_wait_reduction_pct,
            "absenteeism_change_pct": absenteeism_change_pct,
            "task_switching_reduction_pct": task_switching_reduction_pct
        },
        "baseline": {
            "headcount": base_headcount,
            "avg_working_hours": base_working_hours,
            "avg_overtime_hours": base_ot_hours,
            "on_time_rate": base_on_time_rate,
            "completion_rate": base_completion_rate,
            "rework_pct": base_rework_pct,
            "task_backlog": base_backlog,
            "overtime_expenditure": base_ot_cost,
            "capacity_utilization": base_util
        },
        "scenario": {
            "headcount": scen_headcount,
            "avg_working_hours": scen_working_hours,
            "avg_overtime_hours": round(scen_ot_hours, 1),
            "on_time_rate": scen_on_time_rate,
            "completion_rate": scen_completion_rate,
            "rework_pct": round(scen_rework_pct, 1),
            "task_backlog": scen_backlog,
            "overtime_expenditure": scen_ot_cost,
            "capacity_utilization": scen_util
        },
        "delta": {
            "on_time_rate_delta": round(scen_on_time_rate - base_on_time_rate, 1),
            "backlog_cleared": base_backlog - scen_backlog,
            "overtime_savings": saved_ot_cost,
            "rework_pct_reduction": round(base_rework_pct - scen_rework_pct, 1),
            "utilization_delta": round(scen_util - base_util, 1)
        }
    }
