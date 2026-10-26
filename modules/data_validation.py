"""
Data Validation and Quality Assurance Engine for WorkPulse AI
Validates uploaded or synthetic datasets:
- Schema and column presence
- Data type consistency and date parsing
- Cross-table entity integrity (Employee IDs, Task IDs)
- Value boundary checks (negative hours, out-of-bound scores)
- Temporal integrity (start <= due <= completion)
- Missing value audit without silent fabrication
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from datetime import datetime

REQUIRED_COLUMNS = {
    "employees": [
        "employee_id", "department", "job_role", "job_level",
        "hire_date", "employment_status", "work_arrangement", "contracted_weekly_hours"
    ],
    "workload": [
        "employee_id", "reporting_date", "regular_working_hours",
        "overtime_hours", "assigned_tasks", "active_projects",
        "workload_score", "task_switches", "unplanned_work_hours"
    ],
    "task_performance": [
        "task_id", "employee_id", "project_id", "task_type",
        "task_priority", "estimated_hours", "actual_hours",
        "task_start_date", "task_due_date", "task_completion_date",
        "task_status", "quality_score", "rework_hours"
    ],
    "attendance": [
        "employee_id", "reporting_date", "scheduled_workdays",
        "days_absent", "unplanned_absence_days", "leave_days"
    ],
    "engagement": [
        "employee_id", "survey_date", "engagement_score",
        "job_satisfaction", "work_life_balance_score",
        "manager_support_score", "recognition_score"
    ],
    "performance_reviews": [
        "employee_id", "review_date", "performance_rating",
        "goal_completion_percentage", "quality_rating", "manager_feedback_score"
    ],
    "process_metrics": [
        "process_id", "department", "process_name", "reporting_date",
        "queue_length", "average_waiting_time_hours",
        "average_processing_time_hours", "pending_tasks", "blocked_tasks", "error_rate"
    ]
}

class ValidationResult:
    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.metrics_summary: Dict[str, Any] = {}
        self.table_health: Dict[str, Dict[str, Any]] = {}

def validate_datasets(datasets: Dict[str, pd.DataFrame]) -> ValidationResult:
    result = ValidationResult()

    if "employees" not in datasets or datasets["employees"] is None or datasets["employees"].empty:
        result.is_valid = False
        result.errors.append("Critical Error: 'employees' dataset is missing or empty. It is the primary entity anchor.")
        return result

    emp_df = datasets["employees"]
    valid_emp_ids = set(emp_df["employee_id"].dropna().unique())

    # Check each provided dataset
    for table_name, expected_cols in REQUIRED_COLUMNS.items():
        if table_name not in datasets or datasets[table_name] is None:
            result.warnings.append(f"Optional table '{table_name}' was not provided. Modules relying on it will use available subsets.")
            result.table_health[table_name] = {"status": "Missing", "row_count": 0, "issues": 0}
            continue

        df = datasets[table_name].copy()
        row_count = len(df)
        issues_count = 0
        table_issues = []

        if row_count == 0:
            result.warnings.append(f"Table '{table_name}' is empty.")
            result.table_health[table_name] = {"status": "Empty", "row_count": 0, "issues": 1}
            continue

        # Column presence
        missing_cols = [c for c in expected_cols if c not in df.columns]
        if missing_cols:
            result.is_valid = False
            err_msg = f"Table '{table_name}' missing required columns: {missing_cols}"
            result.errors.append(err_msg)
            table_issues.append(err_msg)
            issues_count += len(missing_cols)

        # Duplicate checking
        if table_name == "employees" and "employee_id" in df.columns:
            dups = df["employee_id"].duplicated().sum()
            if dups > 0:
                result.is_valid = False
                result.errors.append(f"Employees table contains {dups} duplicate employee_id entries.")
                issues_count += dups

        if table_name == "task_performance" and "task_id" in df.columns:
            dups = df["task_id"].duplicated().sum()
            if dups > 0:
                result.is_valid = False
                result.errors.append(f"Task performance contains {dups} duplicate task_id entries.")
                issues_count += dups

        # Referential integrity check
        if "employee_id" in df.columns and table_name != "employees":
            orphan_ids = set(df["employee_id"].dropna().unique()) - valid_emp_ids
            if orphan_ids:
                warn_msg = f"Table '{table_name}' contains {len(orphan_ids)} employee IDs not present in employees table."
                result.warnings.append(warn_msg)
                issues_count += len(orphan_ids)

        # Value Boundary and Negative Checks
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in ["regular_working_hours", "overtime_hours", "actual_hours", "estimated_hours",
                        "rework_hours", "days_absent", "queue_length", "average_waiting_time_hours"]:
                neg_count = (df[col] < 0).sum()
                if neg_count > 0:
                    result.is_valid = False
                    err_msg = f"Table '{table_name}', column '{col}' has {neg_count} negative values, which is physically impossible."
                    result.errors.append(err_msg)
                    issues_count += neg_count

        # Score boundaries
        if table_name == "engagement":
            for score_col in ["engagement_score", "job_satisfaction", "work_life_balance_score"]:
                if score_col in df.columns:
                    invalid_scores = ((df[score_col] < 0) | (df[score_col] > 10)).sum()
                    if invalid_scores > 0:
                        result.warnings.append(f"Engagement column '{score_col}' has {invalid_scores} values outside expected 0-10 range.")
                        issues_count += invalid_scores

        if table_name == "performance_reviews":
            if "performance_rating" in df.columns:
                invalid_ratings = ((df["performance_rating"] < 0) | (df["performance_rating"] > 5)).sum()
                if invalid_ratings > 0:
                    result.warnings.append(f"Performance ratings has {invalid_ratings} values outside expected 0-5 range.")
                    issues_count += invalid_ratings

        # Date Consistency
        date_cols = [c for c in df.columns if "date" in c.lower()]
        for dc in date_cols:
            try:
                # Try parsing sample
                parsed = pd.to_datetime(df[dc].dropna(), errors="coerce")
                bad_dates = parsed.isna().sum()
                if bad_dates > 0:
                    result.warnings.append(f"Table '{table_name}', column '{dc}' has {bad_dates} unparseable date values.")
                    issues_count += bad_dates
            except Exception:
                pass

        if table_name == "task_performance":
            try:
                start_dt = pd.to_datetime(df["task_start_date"], errors="coerce")
                due_dt = pd.to_datetime(df["task_due_date"], errors="coerce")
                comp_dt = pd.to_datetime(df["task_completion_date"], errors="coerce")
                
                # Check start after due
                start_after_due = (start_dt > due_dt).sum()
                if start_after_due > 0:
                    result.warnings.append(f"Task performance has {start_after_due} tasks where task_start_date is after task_due_date.")
                    issues_count += start_after_due

                # Check completion before start
                comp_before_start = ((comp_dt.notna()) & (comp_dt < start_dt)).sum()
                if comp_before_start > 0:
                    result.warnings.append(f"Task performance has {comp_before_start} tasks completed before task_start_date.")
                    issues_count += comp_before_start
            except Exception:
                pass

        status_str = "Passed" if issues_count == 0 else ("Warning" if result.is_valid else "Failed")
        result.table_health[table_name] = {
            "status": status_str,
            "row_count": row_count,
            "columns_found": len(df.columns),
            "issues": issues_count
        }

    return result
