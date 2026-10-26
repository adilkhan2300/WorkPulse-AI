"""
AI-Powered Operational Bottleneck Detection Engine for WorkPulse AI
Detects organizational and operational bottlenecks using configurable thresholds,
process queue analysis, task delays, rework rates, and workload imbalances.
Produces structured 10-attribute diagnostic cards.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any

DEFAULT_THRESHOLDS = {
    "excessive_ot_weekly_hours": 8.0,
    "high_rework_rate_pct": 12.0,
    "high_task_switches_weekly": 15.0,
    "long_process_waiting_hours": 16.0,
    "excessive_process_queue": 15.0,
    "high_blocked_tasks": 4.0,
    "high_unplanned_work_hours": 6.0,
    "deadline_miss_rate_pct": 20.0
}

def detect_operational_bottlenecks(
    datasets: Dict[str, pd.DataFrame],
    thresholds: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    Scans workload, task performance, and process metrics to diagnose operational bottlenecks.
    Outputs structured 10-attribute items.
    """
    cfg = DEFAULT_THRESHOLDS.copy()
    if thresholds:
        cfg.update(thresholds)

    emp_df = datasets.get("employees", pd.DataFrame())
    wl_df = datasets.get("workload", pd.DataFrame())
    task_df = datasets.get("task_performance", pd.DataFrame())
    proc_df = datasets.get("process_metrics", pd.DataFrame())
    att_df = datasets.get("attendance", pd.DataFrame())

    bottlenecks: List[Dict[str, Any]] = []

    # 1. Process-Level Bottlenecks (e.g. QA gates, Sign-off queues)
    if not proc_df.empty:
        proc_summary = proc_df.groupby(["process_id", "department", "process_name"]).agg(
            avg_queue=("queue_length", "mean"),
            avg_wait=("average_waiting_time_hours", "mean"),
            avg_blocked=("blocked_tasks", "mean"),
            avg_error=("error_rate", "mean")
        ).reset_index()

        for _, row in proc_summary.iterrows():
            is_wait_bn = row["avg_wait"] >= cfg["long_process_waiting_hours"]
            is_queue_bn = row["avg_queue"] >= cfg["excessive_process_queue"]
            is_blocked_bn = row["avg_blocked"] >= cfg["high_blocked_tasks"]

            if is_wait_bn or is_queue_bn or is_blocked_bn:
                prio = "Critical" if (row["avg_wait"] > 28 or row["avg_queue"] > 25) else "High"
                est_cost = round(row["avg_wait"] * row["avg_queue"] * 45.0 * 2.5, 0)
                
                bottlenecks.append({
                    "id": f"BN-PROC-{row['process_id']}",
                    "title": f"Process Stoppage: {row['process_name']}",
                    "description": f"Excessive staging queue and prolonged wait time detected in '{row['process_name']}' in {row['department']}.",
                    "affected_entity": f"{row['department']} / {row['process_name']}",
                    "supporting_metrics": {
                        "Average Waiting Time": f"{row['avg_wait']:.1f} hrs (Threshold: {cfg['long_process_waiting_hours']} hrs)",
                        "Average Queue Length": f"{row['avg_queue']:.1f} items (Threshold: {cfg['excessive_process_queue']})",
                        "Blocked Upstream Tasks": f"{row['avg_blocked']:.1f} tasks",
                        "Process Error Rate": f"{row['avg_error']*100:.1f}%"
                    },
                    "affected_count": f"~{int(row['avg_queue'] * 1.5)} downstream deliverables impacted",
                    "operational_explanation": "Approval serialization, centralized gatekeeping, or lack of automated verification creates an artificial choke point.",
                    "estimated_business_impact": f"${est_cost:,.0f} in accumulated latency and idle labor per quarter",
                    "recommended_intervention": "Implement automated pre-check pipelines, delegate sign-off authority, or establish SLA fast-tracks for non-critical changes.",
                    "priority_level": prio,
                    "kpi_to_monitor": "Average Waiting Time (Target < 12 hrs) & Queue Length (Target < 10)",
                    "confidence_limitations": "High confidence based on chronological process telemetry. Root cause depends on sign-off stakeholder availability."
                })

    # 2. Workload Imbalance & Senior Overload Bottleneck
    if not wl_df.empty and not emp_df.empty:
        merged_wl = wl_df.merge(emp_df[["employee_id", "department", "job_level", "job_role"]], on="employee_id", how="left")
        
        # Check by job level in departments
        level_stats = merged_wl.groupby(["department", "job_level"]).agg(
            avg_ot=("overtime_hours", "mean"),
            avg_switches=("task_switches", "mean"),
            avg_unplanned=("unplanned_work_hours", "mean"),
            emp_count=("employee_id", "nunique")
        ).reset_index()

        senior_strain = level_stats[
            (level_stats["job_level"].isin(["Senior", "Lead"])) &
            (level_stats["avg_ot"] > cfg["excessive_ot_weekly_hours"])
        ]

        for _, s_row in senior_strain.iterrows():
            dept = s_row["department"]
            # Look at junior level in the same dept
            junior_row = level_stats[(level_stats["department"] == dept) & (level_stats["job_level"].isin(["Junior", "Mid"]))]
            junior_ot = junior_row["avg_ot"].mean() if not junior_row.empty else 0.0

            bottlenecks.append({
                "id": f"BN-IMBAL-{dept}-{s_row['job_level']}",
                "title": f"Structural Workload Imbalance ({dept} {s_row['job_level']}s)",
                "description": f"Senior/Lead staff in {dept} are bearing disproportionate operational pressure while junior talent remains under-leveraged.",
                "affected_entity": f"{dept} ({s_row['job_level']} Cohort)",
                "supporting_metrics": {
                    "Senior Overtime": f"{s_row['avg_ot']:.1f} hrs/wk (Threshold: {cfg['excessive_ot_weekly_hours']} hrs)",
                    "Junior/Mid Overtime": f"{junior_ot:.1f} hrs/wk",
                    "Task Switches": f"{s_row['avg_switches']:.1f} context switches/wk",
                    "Unplanned Work": f"{s_row['avg_unplanned']:.1f} hrs/wk"
                },
                "affected_count": f"{s_row['emp_count']} key senior personnel",
                "operational_explanation": "Tasks are assigned by habit to experienced staff to minimize risk, creating a single-point-of-failure and chronic context-switching.",
                "estimated_business_impact": f"${s_row['avg_ot'] * s_row['emp_count'] * 120 * 12:,.0f} annual overtime expense and severe key-person attrition risk",
                "recommended_intervention": "Pair junior members on architectural tasks, mandate strict delegation guidelines, and shield seniors from ad-hoc operational fires.",
                "priority_level": "High",
                "kpi_to_monitor": "Workload Gini Coefficient & Senior Overtime Hours (< 5 hrs/wk)",
                "confidence_limitations": "High confidence from workload telemetry. Requires skill-matrix validation to confirm junior task-readiness."
            })

    # 3. High Task Switching & Firefighting Bottleneck
    if not wl_df.empty and not emp_df.empty:
        dept_wl = merged_wl.groupby("department").agg(
            avg_switches=("task_switches", "mean"),
            avg_unplanned=("unplanned_work_hours", "mean"),
            emp_count=("employee_id", "nunique")
        ).reset_index()

        firefighting_depts = dept_wl[
            (dept_wl["avg_switches"] >= cfg["high_task_switches_weekly"]) |
            (dept_wl["avg_unplanned"] >= cfg["high_unplanned_work_hours"])
        ]

        for _, f_row in firefighting_depts.iterrows():
            dept = f_row["department"]
            bottlenecks.append({
                "id": f"BN-SWITCH-{dept}",
                "title": f"Context Fragmentation & Firefighting: {dept}",
                "description": f"Excessive task switching ({f_row['avg_switches']:.1f}/wk) and ad-hoc unplanned work ({f_row['avg_unplanned']:.1f} hrs/wk) is destroying focus time.",
                "affected_entity": f"{dept} Department",
                "supporting_metrics": {
                    "Context Switches": f"{f_row['avg_switches']:.1f} switches/wk (Threshold: {cfg['high_task_switches_weekly']})",
                    "Unplanned Work": f"{f_row['avg_unplanned']:.1f} hrs/wk",
                    "Lost Focus Time": f"~{f_row['avg_switches'] * 0.4:.1f} hrs lost to re-orientation"
                },
                "affected_count": f"{f_row['emp_count']} employees across {dept}",
                "operational_explanation": "Unfiltered intake of urgent requests, shifting daily priorities, and multi-project fragmentation prevent deep work.",
                "estimated_business_impact": "20-30% reduction in cognitive productivity and higher error injection in critical tasks.",
                "recommended_intervention": "Institute daily protected focus blocks, funnel all ad-hoc requests through a dedicated rotating triage role, and cap concurrent projects to 2.",
                "priority_level": "High",
                "kpi_to_monitor": "Task Switches / Week (< 10) & Planned vs Unplanned Ratio (> 85% planned)",
                "confidence_limitations": "Moderate confidence. Self-reported task logs may slightly underestimate brief micro-interruptions."
            })

    # 4. Task Rework & Quality Degradation Bottleneck
    if not task_df.empty and not emp_df.empty:
        merged_tasks = task_df.merge(emp_df[["employee_id", "department"]], on="employee_id", how="left")
        rework_by_type = merged_tasks.groupby(["department", "task_type"]).agg(
            total_act_hours=("actual_hours", "sum"),
            total_rework_hours=("rework_hours", "sum"),
            task_count=("task_id", "count")
        ).reset_index()

        rework_by_type["rework_pct"] = rework_by_type["total_rework_hours"] / rework_by_type["total_act_hours"].replace(0, np.nan) * 100
        heavy_rework = rework_by_type[rework_by_type["rework_pct"] >= cfg["high_rework_rate_pct"]]

        for _, r_row in heavy_rework.iterrows():
            bottlenecks.append({
                "id": f"BN-REWORK-{r_row['department']}-{r_row['task_type'][:4]}",
                "title": f"Excessive Quality Rework: {r_row['task_type']} ({r_row['department']})",
                "description": f"Over {r_row['rework_pct']:.1f}% of effort spent on '{r_row['task_type']}' is consumed by rework and remediation.",
                "affected_entity": f"{r_row['department']} / {r_row['task_type']}",
                "supporting_metrics": {
                    "Rework Rate": f"{r_row['rework_pct']:.1f}% (Threshold: {cfg['high_rework_rate_pct']}%)",
                    "Total Rework Hours": f"{r_row['total_rework_hours']:.1f} hrs wasted",
                    "Tasks Affected": f"{r_row['task_count']} tasks"
                },
                "affected_count": f"{r_row['task_count']} task cycles",
                "operational_explanation": "Ambiguous specifications, hurried delivery under overtime pressure, or incomplete peer review guidelines.",
                "estimated_business_impact": f"${r_row['total_rework_hours'] * 65.0:,.0f} in direct wasted payroll hours",
                "recommended_intervention": "Implement explicit 'Definition of Ready' criteria and pre-implementation design reviews before execution begins.",
                "priority_level": "Medium",
                "kpi_to_monitor": "Rework Hours as % of Actual Hours (< 8%)",
                "confidence_limitations": "High confidence based on actual task closure logs."
            })

    # Sort bottlenecks by priority (Critical > High > Medium)
    prio_order = {"Critical": 0, "High": 1, "Medium": 2}
    bottlenecks.sort(key=lambda x: prio_order.get(x["priority_level"], 3))

    return bottlenecks
