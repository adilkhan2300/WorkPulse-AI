"""
Synthetic Data Generator for WorkPulse AI
Generates realistic, coherent HR and operations analytics datasets for 120+ employees across 26 weeks.
Simulates real-world organizational dynamics:
- Diminishing returns on overtime in specific teams (Engineering, Support)
- Process bottlenecks (QA Gate, Architecture Sign-off)
- Workload imbalance (Senior engineers overallocated, Junior engineers underutilized)
- High task-switching and unplanned work leading to high rework and delays
- Stable, sustainable benchmarks in balanced departments (Operations, Marketing)
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RANDOM_SEED = 42

def generate_all_datasets(output_dir: str = "data/synthetic") -> dict:
    os.makedirs(output_dir, exist_ok=True)
    templates_dir = "data/templates"
    os.makedirs(templates_dir, exist_ok=True)

    np.random.seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)

    # 1. Employees Dataset
    num_employees = 120
    departments = ["Engineering", "Customer Support", "Product", "Operations", "Marketing", "Sales"]
    dept_weights = [0.35, 0.25, 0.12, 0.12, 0.08, 0.08]

    job_roles = {
        "Engineering": ["Software Engineer", "Senior Software Engineer", "QA Engineer", "DevOps Engineer", "Lead Architect"],
        "Customer Support": ["Support Specialist", "Senior Support Specialist", "Support Team Lead", "Escalation Engineer"],
        "Product": ["Product Manager", "Product Owner", "UI/UX Designer", "Technical Writer"],
        "Operations": ["Operations Analyst", "Senior Process Coordinator", "Operations Manager"],
        "Marketing": ["Content Strategist", "Growth Marketer", "Marketing Specialist"],
        "Sales": ["Account Executive", "Sales Development Rep", "Sales Operations Lead"]
    }

    levels = ["Junior", "Mid", "Senior", "Lead", "Manager"]
    level_weights = [0.25, 0.35, 0.25, 0.10, 0.05]

    work_arrangements = ["Remote", "Hybrid", "On-site"]
    arrangement_weights = [0.45, 0.40, 0.15]

    start_date = datetime(2025, 8, 1)
    end_date = datetime(2026, 1, 31) # 26 weeks

    employees = []
    base_salaries = {
        "Junior": (30, 40),
        "Mid": (45, 60),
        "Senior": (65, 85),
        "Lead": (90, 115),
        "Manager": (100, 130)
    }

    for i in range(1, num_employees + 1):
        emp_id = f"EMP{i:03d}"
        dept = np.random.choice(departments, p=dept_weights)
        role = np.random.choice(job_roles[dept])
        level = np.random.choice(levels, p=level_weights)
        
        # Hire date within past 1 to 5 years
        days_ago = np.random.randint(180, 1800)
        hire_date = (end_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        status = np.random.choice(["Full-Time", "Contractor", "Part-Time"], p=[0.90, 0.07, 0.03])
        arrangement = np.random.choice(work_arrangements, p=arrangement_weights)
        contracted_hours = 20.0 if status == "Part-Time" else 40.0
        
        rate_range = base_salaries[level]
        hourly_rate = round(np.random.uniform(rate_range[0], rate_range[1]), 2)
        
        employees.append({
            "employee_id": emp_id,
            "department": dept,
            "job_role": role,
            "job_level": level,
            "hire_date": hire_date,
            "employment_status": status,
            "work_arrangement": arrangement,
            "contracted_weekly_hours": contracted_hours,
            "hourly_rate": hourly_rate
        })

    df_employees = pd.DataFrame(employees)
    df_employees.to_csv(os.path.join(output_dir, "employees.csv"), index=False)

    # 2. Workload Dataset (Weekly reports over 26 weeks)
    reporting_mondays = [start_date + timedelta(weeks=w) for w in range(26)]
    workload_records = []

    for emp in employees:
        emp_id = emp["employee_id"]
        dept = emp["department"]
        level = emp["job_level"]
        contracted = emp["contracted_weekly_hours"]

        # Department archetypes:
        # Engineering: Overtime surged in last 12 weeks, task switches high, unplanned work high
        # Customer Support: High overtime, high unplanned work, high burnout
        # Operations: Well-balanced, predictable
        # Product & Marketing: Moderate, stable
        for w_idx, rep_date in enumerate(reporting_mondays):
            date_str = rep_date.strftime("%Y-%m-%d")
            
            # Trend factor: week 14 onwards shows strain in Engineering & Support
            is_late_period = w_idx >= 13
            
            if dept == "Engineering":
                if level in ["Senior", "Lead"]:
                    # Overallocated senior engineers
                    base_ot = np.random.uniform(8, 16) if not is_late_period else np.random.uniform(14, 24)
                    assigned_tasks = int(np.random.uniform(8, 14) + (w_idx * 0.2))
                    active_projects = np.random.choice([3, 4, 5], p=[0.3, 0.5, 0.2])
                    task_switches = int(np.random.uniform(12, 22) + (w_idx * 0.3))
                    unplanned_hours = round(np.random.uniform(6, 14) + (w_idx * 0.25), 1)
                else:
                    # Junior/mid underutilized or waiting on seniors
                    base_ot = np.random.uniform(0, 4) if not is_late_period else np.random.uniform(1, 6)
                    assigned_tasks = int(np.random.uniform(3, 6))
                    active_projects = np.random.choice([1, 2], p=[0.7, 0.3])
                    task_switches = int(np.random.uniform(4, 8))
                    unplanned_hours = round(np.random.uniform(1, 4), 1)
                reg_hours = min(contracted, round(np.random.normal(39, 1), 1))
                ot_hours = round(base_ot, 1)

            elif dept == "Customer Support":
                # High ticket volume, overtime ramp-up
                base_ot = np.random.uniform(4, 10) if not is_late_period else np.random.uniform(10, 18)
                assigned_tasks = int(np.random.uniform(15, 30))
                active_projects = 1
                task_switches = int(np.random.uniform(15, 30))
                unplanned_hours = round(np.random.uniform(8, 16), 1)
                reg_hours = min(contracted, round(np.random.normal(40, 0.5), 1))
                ot_hours = round(base_ot, 1)

            elif dept == "Operations":
                # Healthy balance
                reg_hours = min(contracted, round(np.random.normal(38.5, 1.5), 1))
                ot_hours = round(np.random.uniform(0, 3.5), 1)
                assigned_tasks = int(np.random.uniform(5, 9))
                active_projects = np.random.choice([1, 2], p=[0.6, 0.4])
                task_switches = int(np.random.uniform(3, 7))
                unplanned_hours = round(np.random.uniform(1, 4), 1)

            else:
                # Other departments
                reg_hours = min(contracted, round(np.random.normal(39, 1), 1))
                ot_hours = round(np.random.uniform(1, 6), 1)
                assigned_tasks = int(np.random.uniform(4, 10))
                active_projects = np.random.choice([2, 3], p=[0.5, 0.5])
                task_switches = int(np.random.uniform(5, 10))
                unplanned_hours = round(np.random.uniform(2, 6), 1)

            # Workload score calculation: composite scale 1-100
            total_hours = reg_hours + ot_hours
            workload_score = min(100.0, round((total_hours / 40.0) * 50 + (assigned_tasks * 2.5) + (task_switches * 0.8), 1))

            workload_records.append({
                "employee_id": emp_id,
                "reporting_date": date_str,
                "regular_working_hours": reg_hours,
                "overtime_hours": ot_hours,
                "assigned_tasks": assigned_tasks,
                "active_projects": active_projects,
                "workload_score": workload_score,
                "task_switches": task_switches,
                "unplanned_work_hours": unplanned_hours
            })

    df_workload = pd.DataFrame(workload_records)
    df_workload.to_csv(os.path.join(output_dir, "workload.csv"), index=False)

    # 3. Task Performance Dataset (~4,500 tasks across the 6 months)
    task_types = {
        "Engineering": ["Feature Development", "Bug Fix", "Code Review", "Architecture Design", "Technical Debt"],
        "Customer Support": ["Customer Ticket - Tier 1", "Customer Ticket - Tier 2", "Incident Escalation", "Knowledge Base Update"],
        "Product": ["User Story Spec", "Roadmap Planning", "Wireframe Design", "Sprint Backlog Refinement"],
        "Operations": ["Process Optimization", "Vendor Review", "System Audit", "Compliance Check"],
        "Marketing": ["Campaign Launch", "Blog Post", "SEO Optimization", "Ad Copy Review"],
        "Sales": ["Client Proposal", "Lead Qualification", "Demo Delivery", "Contract Negotiation"]
    }

    priorities = ["Low", "Medium", "High", "Critical"]
    prio_weights = [0.20, 0.45, 0.25, 0.10]

    tasks = []
    task_counter = 1000

    for emp in employees:
        emp_id = emp["employee_id"]
        dept = emp["department"]
        level = emp["job_level"]
        
        # Number of tasks created for this employee across 26 weeks
        num_tasks = np.random.randint(25, 55) if dept != "Customer Support" else np.random.randint(60, 110)
        
        for _ in range(num_tasks):
            task_counter += 1
            task_id = f"TSK-{task_counter}"
            prj_id = f"PRJ-{np.random.randint(1, 13):02d}"
            t_type = np.random.choice(task_types[dept])
            prio = np.random.choice(priorities, p=prio_weights)
            
            # Start date scattered over the 26 weeks
            day_offset = np.random.randint(0, 175)
            t_start = start_date + timedelta(days=day_offset)
            
            # Estimated duration
            est_hours = round(np.random.choice([2, 4, 8, 16, 24, 40], p=[0.2, 0.3, 0.25, 0.15, 0.07, 0.03]), 1)
            
            # Due date typically est_hours/8 days later + 1 to 3 buffer days
            expected_days = max(1, int(np.ceil(est_hours / 8)) + np.random.randint(1, 5))
            t_due = t_start + timedelta(days=expected_days)
            
            # Actual behavior depends on department, level, and whether late in the timeline
            is_strained = (dept in ["Engineering", "Customer Support"]) and (day_offset > 80)
            
            # Completion probability: 82% completed, 10% in progress, 5% blocked, 3% backlog
            status_dice = np.random.rand()
            if status_dice < 0.82:
                status = "Completed"
                # If strained, actual hours blow out, rework increases, delay occurs
                if is_strained and (level in ["Senior", "Lead"] or prio in ["High", "Critical"]):
                    hour_multiplier = np.random.uniform(1.2, 2.1) # Scope creep / friction
                    delay_days = np.random.randint(2, 12)
                    rework = round(np.random.uniform(2.0, 8.5), 1)
                    quality = round(np.random.uniform(2.2, 3.8), 1)
                else:
                    hour_multiplier = np.random.uniform(0.85, 1.25)
                    delay_days = np.random.choice([-2, -1, 0, 1, 2], p=[0.1, 0.2, 0.45, 0.15, 0.10])
                    rework = round(np.random.uniform(0.0, 2.0), 1) if np.random.rand() < 0.25 else 0.0
                    quality = round(np.random.uniform(3.8, 5.0), 1)
                
                act_hours = round(est_hours * hour_multiplier + rework, 1)
                t_comp = t_due + timedelta(days=int(delay_days))
                if t_comp < t_start:
                    t_comp = t_start + timedelta(days=1)
                comp_date_str = t_comp.strftime("%Y-%m-%d")
            elif status_dice < 0.92:
                status = "In Progress"
                act_hours = round(est_hours * np.random.uniform(0.3, 0.9), 1)
                comp_date_str = None
                rework = round(np.random.uniform(0, 3), 1) if is_strained else 0.0
                quality = np.nan
            elif status_dice < 0.97:
                status = "Blocked"
                act_hours = round(est_hours * np.random.uniform(0.1, 0.5), 1)
                comp_date_str = None
                rework = round(np.random.uniform(1, 4), 1)
                quality = np.nan
            else:
                status = "Backlog"
                act_hours = 0.0
                comp_date_str = None
                rework = 0.0
                quality = np.nan

            tasks.append({
                "task_id": task_id,
                "employee_id": emp_id,
                "project_id": prj_id,
                "task_type": t_type,
                "task_priority": prio,
                "estimated_hours": est_hours,
                "actual_hours": act_hours,
                "task_start_date": t_start.strftime("%Y-%m-%d"),
                "task_due_date": t_due.strftime("%Y-%m-%d"),
                "task_completion_date": comp_date_str,
                "task_status": status,
                "quality_score": quality,
                "rework_hours": rework
            })

    df_tasks = pd.DataFrame(tasks)
    df_tasks.to_csv(os.path.join(output_dir, "task_performance.csv"), index=False)

    # 4. Attendance Dataset (Weekly attendance records for all employees)
    attendance_records = []
    for emp in employees:
        emp_id = emp["employee_id"]
        dept = emp["department"]

        for w_idx, rep_date in enumerate(reporting_mondays):
            date_str = rep_date.strftime("%Y-%m-%d")
            sched = 5 if emp["employment_status"] != "Part-Time" else 3
            
            # Strain in Engineering/Support leads to higher unplanned absence in late period
            is_strained = (dept in ["Engineering", "Customer Support"]) and (w_idx >= 13)
            
            if is_strained:
                p_unplanned = 0.22
                unplanned = np.random.choice([0, 1, 2], p=[0.78, 0.16, 0.06])
                leave = np.random.choice([0, 1, 2], p=[0.88, 0.09, 0.03])
            else:
                unplanned = np.random.choice([0, 1], p=[0.94, 0.06])
                leave = np.random.choice([0, 1, 2, 5], p=[0.88, 0.07, 0.04, 0.01])
            
            days_abs = min(sched, unplanned + leave)
            attendance_records.append({
                "employee_id": emp_id,
                "reporting_date": date_str,
                "scheduled_workdays": sched,
                "days_absent": days_abs,
                "unplanned_absence_days": unplanned,
                "leave_days": leave
            })

    df_attendance = pd.DataFrame(attendance_records)
    df_attendance.to_csv(os.path.join(output_dir, "attendance.csv"), index=False)

    # 5. Engagement Dataset (Monthly surveys: 6 surveys across the half-year)
    survey_dates = [datetime(2025, 8, 31), datetime(2025, 9, 30), datetime(2025, 10, 31),
                    datetime(2025, 11, 30), datetime(2025, 12, 31), datetime(2026, 1, 31)]
    engagement_records = []

    for emp in employees:
        emp_id = emp["employee_id"]
        dept = emp["department"]
        level = emp["job_level"]

        for s_idx, s_date in enumerate(survey_dates):
            date_str = s_date.strftime("%Y-%m-%d")
            
            # Degrading engagement in overtaxed teams
            if dept in ["Engineering", "Customer Support"] and s_idx >= 2:
                decay = (s_idx - 1) * 0.45
                eng_score = max(2.5, round(np.random.normal(7.8 - decay, 0.8), 1))
                job_sat = max(2.0, round(np.random.normal(7.6 - decay * 1.2, 0.9), 1))
                wlb_score = max(1.5, round(np.random.normal(7.5 - decay * 1.5, 0.8), 1))
                mgr_supp = max(3.0, round(np.random.normal(7.9 - decay * 0.5, 0.9), 1))
                rec_score = max(2.5, round(np.random.normal(7.2 - decay * 0.7, 0.9), 1))
            else:
                eng_score = min(10.0, max(4.0, round(np.random.normal(8.1, 0.6), 1)))
                job_sat = min(10.0, max(4.0, round(np.random.normal(8.0, 0.7), 1)))
                wlb_score = min(10.0, max(4.0, round(np.random.normal(8.2, 0.6), 1)))
                mgr_supp = min(10.0, max(4.0, round(np.random.normal(8.3, 0.6), 1)))
                rec_score = min(10.0, max(4.0, round(np.random.normal(7.9, 0.7), 1)))

            engagement_records.append({
                "employee_id": emp_id,
                "survey_date": date_str,
                "engagement_score": eng_score,
                "job_satisfaction": job_sat,
                "work_life_balance_score": wlb_score,
                "manager_support_score": mgr_supp,
                "recognition_score": rec_score
            })

    df_engagement = pd.DataFrame(engagement_records)
    df_engagement.to_csv(os.path.join(output_dir, "engagement.csv"), index=False)

    # 6. Performance Reviews Dataset (Quarterly: Q3 2025 and Q4 2025)
    review_dates = [datetime(2025, 9, 30), datetime(2025, 12, 31)]
    review_records = []

    for emp in employees:
        emp_id = emp["employee_id"]
        dept = emp["department"]

        for r_idx, r_date in enumerate(review_dates):
            date_str = r_date.strftime("%Y-%m-%d")
            # In Q4, overstretched departments see slight dip in quality and goal completion due to bottlenecks
            if dept in ["Engineering", "Customer Support"] and r_idx == 1:
                rating = round(np.random.choice([2.5, 3.0, 3.5, 4.0, 4.5], p=[0.10, 0.35, 0.35, 0.15, 0.05]), 1)
                goal_pct = round(np.random.uniform(68, 89), 1)
                qual_rat = round(np.random.uniform(2.8, 3.9), 1)
                mgr_fb = round(np.random.uniform(2.7, 4.0), 1)
            else:
                rating = round(np.random.choice([3.0, 3.5, 4.0, 4.5, 5.0], p=[0.05, 0.20, 0.45, 0.22, 0.08]), 1)
                goal_pct = round(np.random.uniform(85, 104), 1)
                qual_rat = round(np.random.uniform(3.8, 4.8), 1)
                mgr_fb = round(np.random.uniform(3.7, 4.8), 1)

            review_records.append({
                "employee_id": emp_id,
                "review_date": date_str,
                "performance_rating": rating,
                "goal_completion_percentage": goal_pct,
                "quality_rating": qual_rat,
                "manager_feedback_score": mgr_fb
            })

    df_reviews = pd.DataFrame(review_records)
    df_reviews.to_csv(os.path.join(output_dir, "performance_reviews.csv"), index=False)

    # 7. Process Metrics Dataset (Operational bottlenecks)
    processes = [
        {"id": "PRC-01", "dept": "Engineering", "name": "Code Deployment & QA Gate", "is_bottleneck": True},
        {"id": "PRC-02", "dept": "Engineering", "name": "Architecture Sign-off", "is_bottleneck": True},
        {"id": "PRC-03", "dept": "Customer Support", "name": "Tier 3 Escalation Triage", "is_bottleneck": True},
        {"id": "PRC-04", "dept": "Product", "name": "Design Spec Handoff", "is_bottleneck": False},
        {"id": "PRC-05", "dept": "Operations", "name": "Vendor Invoice Approval", "is_bottleneck": False},
        {"id": "PRC-06", "dept": "Marketing", "name": "Compliance & Brand Review", "is_bottleneck": False},
        {"id": "PRC-07", "dept": "Sales", "name": "Security Questionnaire Review", "is_bottleneck": True},
        {"id": "PRC-08", "dept": "Operations", "name": "Hardware Provisioning", "is_bottleneck": False}
    ]

    process_records = []
    # Bi-weekly reports for processes (13 reporting dates)
    proc_dates = [start_date + timedelta(weeks=w*2) for w in range(13)]

    for proc in processes:
        p_id = proc["id"]
        p_dept = proc["dept"]
        p_name = proc["name"]
        is_bn = proc["is_bottleneck"]

        for p_idx, p_date in enumerate(proc_dates):
            date_str = p_date.strftime("%Y-%m-%d")
            worsening = p_idx > 6 # second half worsens

            if is_bn:
                queue = int(np.random.uniform(18, 35) + (p_idx * 1.5 if worsening else 0))
                wait_hours = round(np.random.uniform(18.0, 36.0) + (p_idx * 2.2 if worsening else 0), 1)
                proc_hours = round(np.random.uniform(6.0, 14.0), 1)
                pending = int(queue * 1.3)
                blocked = int(np.random.uniform(4, 14) + (p_idx * 0.8 if worsening else 0))
                error_rate = round(np.random.uniform(0.12, 0.28) + (0.05 if worsening else 0), 3)
            else:
                queue = int(np.random.uniform(3, 9))
                wait_hours = round(np.random.uniform(1.5, 6.0), 1)
                proc_hours = round(np.random.uniform(2.0, 5.0), 1)
                pending = int(queue * 1.1)
                blocked = int(np.random.choice([0, 1, 2], p=[0.75, 0.20, 0.05]))
                error_rate = round(np.random.uniform(0.01, 0.05), 3)

            process_records.append({
                "process_id": p_id,
                "department": p_dept,
                "process_name": p_name,
                "reporting_date": date_str,
                "queue_length": queue,
                "average_waiting_time_hours": wait_hours,
                "average_processing_time_hours": proc_hours,
                "pending_tasks": pending,
                "blocked_tasks": blocked,
                "error_rate": error_rate
            })

    df_proc = pd.DataFrame(process_records)
    df_proc.to_csv(os.path.join(output_dir, "process_metrics.csv"), index=False)

    # 8. Generate Clean Downloadable Templates (Headers + 2 sample rows)
    template_dfs = {
        "employees_template.csv": df_employees.head(2),
        "workload_template.csv": df_workload.head(2),
        "task_performance_template.csv": df_tasks.head(2),
        "attendance_template.csv": df_attendance.head(2),
        "engagement_template.csv": df_engagement.head(2),
        "performance_reviews_template.csv": df_reviews.head(2),
        "process_metrics_template.csv": df_proc.head(2),
    }

    for name, sample_df in template_dfs.items():
        sample_df.to_csv(os.path.join(templates_dir, name), index=False)

    return {
        "employees": df_employees,
        "workload": df_workload,
        "task_performance": df_tasks,
        "attendance": df_attendance,
        "engagement": df_engagement,
        "performance_reviews": df_reviews,
        "process_metrics": df_proc
    }

if __name__ == "__main__":
    datasets = generate_all_datasets()
    print("Synthetic datasets successfully created in data/synthetic and data/templates.")
    for k, v in datasets.items():
        print(f" - {k}: {len(v)} rows")
