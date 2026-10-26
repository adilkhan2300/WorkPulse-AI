"""
Machine Learning and Productivity Risk Prediction Module for WorkPulse AI
Predicts task delay risk without target leakage.
Supports Logistic Regression, Random Forest, and Gradient Boosting.
Provides chronological splitting and comprehensive classification diagnostics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, roc_curve, precision_recall_curve
)

def prepare_ml_task_dataset(datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Constructs a leakage-free feature matrix for predicting whether a task will be delayed.
    Only uses features that are known at or prior to task assignment.
    """
    task_df = datasets.get("task_performance", pd.DataFrame()).copy()
    emp_df = datasets.get("employees", pd.DataFrame()).copy()
    wl_df = datasets.get("workload", pd.DataFrame()).copy()

    if task_df.empty or emp_df.empty:
        return pd.DataFrame()

    # Only consider tasks that have reached completion or are past due date
    now = pd.Timestamp.now()
    task_df["due_dt"] = pd.to_datetime(task_df["task_due_date"], errors="coerce")
    task_df["comp_dt"] = pd.to_datetime(task_df["task_completion_date"], errors="coerce")
    task_df["start_dt"] = pd.to_datetime(task_df["task_start_date"], errors="coerce")

    # Define target: 1 if completed late OR (not completed and current time > due_dt)
    is_completed_late = (task_df["comp_dt"] > task_df["due_dt"])
    is_overdue_uncompleted = (task_df["task_status"] != "Completed") & (task_df["due_dt"] < now)
    task_df["is_delayed"] = (is_completed_late | is_overdue_uncompleted).astype(int)

    # Historical employee workload metrics (known baseline)
    if not wl_df.empty:
        emp_wl_baseline = wl_df.groupby("employee_id").agg(
            baseline_overtime=("overtime_hours", "mean"),
            baseline_task_switches=("task_switches", "mean"),
            baseline_unplanned_work=("unplanned_work_hours", "mean")
        ).reset_index()
    else:
        emp_wl_baseline = pd.DataFrame()

    # Merge task with employee features
    df_merged = task_df.merge(
        emp_df[["employee_id", "department", "job_role", "job_level", "work_arrangement"]],
        on="employee_id", how="left"
    )
    if not emp_wl_baseline.empty:
        df_merged = df_merged.merge(emp_wl_baseline, on="employee_id", how="left").fillna(0.0)

    # Feature selection: STRICTLY PRE-EXECUTION FEATURES (NO rework_hours, NO actual_hours, NO completion_date)
    feature_cols = [
        "task_type", "task_priority", "estimated_hours",
        "department", "job_level", "work_arrangement"
    ]
    if "baseline_overtime" in df_merged.columns:
        feature_cols.extend(["baseline_overtime", "baseline_task_switches", "baseline_unplanned_work"])

    valid_mask = df_merged["is_delayed"].notna() & df_merged["start_dt"].notna()
    final_df = df_merged[valid_mask].copy()

    # Sort chronologically for chronological split
    final_df = final_df.sort_values(by="start_dt").reset_index(drop=True)
    return final_df

def train_and_evaluate_model(
    df: pd.DataFrame,
    model_type: str = "Random Forest",
    split_strategy: str = "Chronological (80/20)",
    rf_trees: int = 100,
    lr_c: float = 1.0
) -> Dict[str, Any]:
    """
    Trains selected ML model and computes robust evaluation diagnostics.
    """
    if df.empty or len(df) < 50:
        return {"success": False, "error": "Insufficient dataset size (needs >= 50 observations)."}

    feature_cols = [
        c for c in ["task_type", "task_priority", "estimated_hours",
                    "department", "job_level", "work_arrangement",
                    "baseline_overtime", "baseline_task_switches", "baseline_unplanned_work"]
        if c in df.columns
    ]
    cat_cols = [c for c in ["task_type", "task_priority", "department", "job_level", "work_arrangement"] if c in feature_cols]
    num_cols = [c for c in ["estimated_hours", "baseline_overtime", "baseline_task_switches", "baseline_unplanned_work"] if c in feature_cols]

    X = df[feature_cols]
    y = df["is_delayed"].values

    if len(np.unique(y)) < 2:
        return {"success": False, "error": "Target contains only one class in the selected slice."}

    # Chronological vs Stratified Split
    if "Chronological" in split_strategy:
        split_idx = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols)
        ]
    )

    if model_type == "Logistic Regression":
        clf = LogisticRegression(C=lr_c, max_iter=1000, random_state=42)
    elif model_type == "Gradient Boosting":
        clf = GradientBoostingClassifier(n_estimators=rf_trees, max_depth=4, random_state=42)
    else: # Default Random Forest
        clf = RandomForestClassifier(n_estimators=rf_trees, max_depth=8, random_state=42)

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", clf)
    ])

    try:
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1] if hasattr(clf, "predict_proba") else y_pred

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred)

        try:
            roc_auc = roc_auc_score(y_test, y_prob)
            fpr, tpr, _ = roc_curve(y_test, y_prob)
        except Exception:
            roc_auc = 0.5
            fpr, tpr = [0, 1], [0, 1]

        try:
            pr_auc = average_precision_score(y_test, y_prob)
            prec_curve, rec_curve, _ = precision_recall_curve(y_test, y_prob)
        except Exception:
            pr_auc = float(np.mean(y_test))
            prec_curve, rec_curve = [0, 1], [1, 0]

        # Extract transformed feature names
        cat_encoder = pipeline.named_steps["preprocessor"].named_transformers_["cat"]
        encoded_cat_features = list(cat_encoder.get_feature_names_out(cat_cols))
        all_feature_names = num_cols + encoded_cat_features

        return {
            "success": True,
            "pipeline": pipeline,
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "y_prob": y_prob,
            "feature_names": all_feature_names,
            "num_cols": num_cols,
            "cat_cols": cat_cols,
            "metrics": {
                "accuracy": round(acc, 3),
                "precision": round(prec, 3),
                "recall": round(rec, 3),
                "f1": round(f1, 3),
                "roc_auc": round(roc_auc, 3),
                "pr_auc": round(pr_auc, 3),
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "delayed_test_actual": int(np.sum(y_test))
            },
            "confusion_matrix": cm.tolist(),
            "roc_curve": {"fpr": fpr.tolist(), "tpr": tpr.tolist()},
            "pr_curve": {"precision": prec_curve.tolist(), "recall": rec_curve.tolist()}
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
