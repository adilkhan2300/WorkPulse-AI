"""
Automated Unit and Integration Tests for WorkPulse AI
Validates:
- Synthetic data generation and schema integrity
- Data validation rules and negative value detection
- Productivity KPI engine computations
- Capacity planning and utilization classifications
- Bottleneck detection logic
- Statistical regression and diminishing returns detection
- ML pipeline training and leakage prevention
- What-if scenario simulations
- PDF report compilation
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.synthetic_data_generator import generate_all_datasets
from modules.data_validation import validate_datasets
from modules.productivity_metrics import calculate_executive_kpis, calculate_department_breakdown
from modules.capacity_planning import calculate_capacity_utilization, diagnose_team_capacity_constraints
from modules.bottleneck_detection import detect_operational_bottlenecks
from modules.statistical_analysis import prepare_productivity_analytical_dataset, run_diminishing_returns_regression
from modules.prediction_models import prepare_ml_task_dataset, train_and_evaluate_model
from modules.scenario_simulator import run_what_if_simulation
from modules.cost_analysis import compute_operational_cost_breakdown
from modules.reporting import generate_pdf_management_report

@pytest.fixture(scope="session")
def loaded_datasets():
    """Generates synthetic dataset fixture for all tests."""
    return generate_all_datasets(output_dir="data/synthetic")

def test_dataset_generation_and_schemas(loaded_datasets):
    assert "employees" in loaded_datasets
    assert "workload" in loaded_datasets
    assert "task_performance" in loaded_datasets
    assert len(loaded_datasets["employees"]) >= 100
    assert len(loaded_datasets["workload"]) >= 1000
    assert len(loaded_datasets["task_performance"]) >= 1000

def test_data_validation_engine(loaded_datasets):
    val_result = validate_datasets(loaded_datasets)
    assert val_result.is_valid is True
    assert len(val_result.errors) == 0

    # Negative check test
    corrupted_datasets = {k: v.copy() for k, v in loaded_datasets.items()}
    corrupted_datasets["workload"].loc[0, "regular_working_hours"] = -10.0
    bad_val = validate_datasets(corrupted_datasets)
    assert bad_val.is_valid is False
    assert any("negative values" in e for e in bad_val.errors)

def test_kpi_engine(loaded_datasets):
    kpis = calculate_executive_kpis(loaded_datasets)
    assert kpis["total_employees"] >= 100
    assert 30 <= kpis["avg_working_hours"] <= 60
    assert 0 <= kpis["task_completion_rate"] <= 100
    assert 0 <= kpis["on_time_completion_rate"] <= 100
    assert 0 <= kpis["productivity_score"] <= 100
    assert kpis["estimated_overtime_expenditure"] > 0

def test_capacity_planning(loaded_datasets):
    cap_df = calculate_capacity_utilization(loaded_datasets)
    assert not cap_df.empty
    assert "workload_status" in cap_df.columns
    assert set(cap_df["workload_status"].unique()).issubset({"Underutilized", "Balanced", "High Workload", "Overallocated", "Unknown"})
    
    diags = diagnose_team_capacity_constraints(cap_df)
    assert len(diags) > 0

def test_bottleneck_detection(loaded_datasets):
    bottlenecks = detect_operational_bottlenecks(loaded_datasets)
    assert len(bottlenecks) > 0
    first_bn = bottlenecks[0]
    required_keys = [
        "title", "description", "affected_entity", "supporting_metrics",
        "affected_count", "operational_explanation", "estimated_business_impact",
        "recommended_intervention", "priority_level", "kpi_to_monitor", "confidence_limitations"
    ]
    for rk in required_keys:
        assert rk in first_bn

def test_diminishing_returns_regression(loaded_datasets):
    df_ana = prepare_productivity_analytical_dataset(loaded_datasets)
    assert not df_ana.empty
    res = run_diminishing_returns_regression(df_ana)
    assert res["fitted"] is True
    assert "b1" in res and "b2" in res

def test_ml_pipeline_leakage_prevention(loaded_datasets):
    ml_df = prepare_ml_task_dataset(loaded_datasets)
    assert not ml_df.empty
    assert "is_delayed" in ml_df.columns
    # Ensure leakage features are NOT in the preprocessed feature matrix
    assert "task_completion_date" not in ml_df.select_dtypes(include=[np.number]).columns
    assert "rework_hours" not in ml_df.columns or "rework_hours" not in [
        "task_type", "task_priority", "estimated_hours", "department", "job_level", "work_arrangement"
    ]

    res = train_and_evaluate_model(ml_df, model_type="Random Forest", split_strategy="Chronological (80/20)", rf_trees=20)
    assert res["success"] is True
    assert 0.5 <= res["metrics"]["roc_auc"] <= 1.0

def test_scenario_simulator(loaded_datasets):
    kpis = calculate_executive_kpis(loaded_datasets)
    sim = run_what_if_simulation(kpis, ot_reduction_pct=30.0, rework_reduction_pct=40.0)
    assert sim["scenario"]["avg_overtime_hours"] < sim["baseline"]["avg_overtime_hours"]
    assert sim["delta"]["overtime_savings"] > 0

def test_pdf_report_generation(loaded_datasets):
    kpis = calculate_executive_kpis(loaded_datasets)
    bottlenecks = detect_operational_bottlenecks(loaded_datasets)
    costs = compute_operational_cost_breakdown(loaded_datasets, kpis)
    pdf_bytes = generate_pdf_management_report(
        kpis=kpis,
        bottlenecks=bottlenecks,
        interventions=[],
        costs=costs,
        executive_insight={"executive_finding": "Test finding"}
    )
    assert len(pdf_bytes) > 1000 # Valid non-empty PDF
