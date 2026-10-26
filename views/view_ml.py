"""
Machine Learning and Productivity Risk Prediction View for WorkPulse AI
Trains predictive classifiers for task delivery delays without data leakage,
evaluates performance metrics, renders ROC/PR curves, and computes XAI feature importance.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any
from modules.prediction_models import prepare_ml_task_dataset, train_and_evaluate_model
from modules.explainability import compute_model_explainability
from utils.styles import get_plotly_theme

def render_ml_view(datasets: Dict[str, pd.DataFrame]):
    st.markdown("## 🤖 Machine Learning & Delivery Risk Prediction")
    st.caption("Predicting probability of task delivery delays prior to work execution. Designed to trigger proactive support, not punitive surveillance.")

    ml_df = prepare_ml_task_dataset(datasets)

    if ml_df.empty or len(ml_df) < 50:
        st.warning("Insufficient task records with historical start and due dates to train predictive models.")
        return

    # User Model Controls
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
        model_choice = st.selectbox("Predictive Algorithm", ["Random Forest", "Gradient Boosting", "Logistic Regression"], index=0)
    with col_ctrl2:
        split_choice = st.selectbox("Validation Splitting", ["Chronological (80/20)", "Stratified Random (80/20)"], index=0)
    with col_ctrl3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        retrain_clicked = st.button("🚀 Train Model", use_container_width=True)

    # Train model (cached or on demand)
    cache_key = f"ml_result_{model_choice}_{split_choice}"
    if retrain_clicked or cache_key not in st.session_state:
        with st.spinner(f"Training {model_choice} with {split_choice} split..."):
            res = train_and_evaluate_model(ml_df, model_type=model_choice, split_strategy=split_choice)
            st.session_state[cache_key] = res
    else:
        res = st.session_state[cache_key]

    if not res.get("success", False):
        st.error(f"Model training error: {res.get('error', 'Unknown error')}")
        return

    metrics = res["metrics"]

    # Model Metric Cards
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("ROC-AUC", f"{metrics['roc_auc']:.3f}", delta="Discriminative Power")
    m2.metric("PR-AUC", f"{metrics['pr_auc']:.3f}", delta="Precision vs Recall")
    m3.metric("F1-Score", f"{metrics['f1']:.3f}")
    m4.metric("Precision", f"{metrics['precision']:.3f}")
    m5.metric("Recall", f"{metrics['recall']:.3f}")
    m6.metric("Accuracy", f"{metrics['accuracy']:.3f}")

    st.markdown("---")

    # Section 1: ROC and Precision-Recall Curves
    c_roc, c_pr, c_cm = st.columns([2, 2, 1.5])

    with c_roc:
        roc_data = res["roc_curve"]
        fig_roc = go.Figure()
        fig_roc.add_trace(go.Scatter(x=roc_data["fpr"], y=roc_data["tpr"], mode="lines", name=f"{model_choice} (AUC={metrics['roc_auc']:.2f})", line=dict(color="#2563eb", width=2.5)))
        fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random Baseline", line=dict(dash="dash", color="gray")))
        fig_roc.update_layout(title="ROC Curve", xaxis_title="False Positive Rate", yaxis_title="True Positive Rate", **get_plotly_theme()["layout"])
        st.plotly_chart(fig_roc, use_container_width=True)

    with c_pr:
        pr_data = res["pr_curve"]
        fig_pr = go.Figure()
        fig_pr.add_trace(go.Scatter(x=pr_data["recall"], y=pr_data["precision"], mode="lines", name=f"PR Curve (AUC={metrics['pr_auc']:.2f})", line=dict(color="#10b981", width=2.5)))
        fig_pr.update_layout(title="Precision-Recall Curve", xaxis_title="Recall", yaxis_title="Precision", **get_plotly_theme()["layout"])
        st.plotly_chart(fig_pr, use_container_width=True)

    with c_cm:
        cm = np.array(res["confusion_matrix"])
        fig_cm = px.imshow(
            cm,
            text_auto=True,
            color_continuous_scale="Blues",
            labels=dict(x="Predicted Class", y="Actual Class"),
            x=["On-Time (0)", "Delayed (1)"],
            y=["On-Time (0)", "Delayed (1)"],
            title="Confusion Matrix"
        )
        fig_cm.update_layout(**get_plotly_theme()["layout"])
        st.plotly_chart(fig_cm, use_container_width=True)

    # Section 2: Explainable AI (XAI)
    st.markdown("---")
    st.markdown("### 🧠 Explainable AI: Feature Importance")
    st.caption("Identifying the operational signals most strongly predictive of schedule slippage (SHAP with Permutation Importance fallback).")

    with st.spinner("Computing feature importances..."):
        xai_res = compute_model_explainability(res)

    if xai_res.get("method") != "Failed" and not xai_res["importance_df"].empty:
        col_x1, col_x2 = st.columns([3, 2])
        imp_df = xai_res["importance_df"].head(10)

        with col_x1:
            fig_imp = px.bar(
                imp_df.sort_values(by="Importance", ascending=True),
                x="Importance",
                y="Feature",
                orientation="h",
                color="Importance",
                color_continuous_scale="Purples",
                title=f"Top Predictive Drivers ({xai_res['method']})"
            )
            fig_imp.update_layout(**get_plotly_theme()["layout"])
            st.plotly_chart(fig_imp, use_container_width=True)

        with col_x2:
            st.markdown("#### 🔑 Model Insights & Drivers")
            st.markdown(f"**Methodology:** `{xai_res['method']}`")
            top_feats = xai_res.get("top_features", [])
            st.markdown("**Dominant Predictors:**")
            for f in top_feats[:5]:
                st.markdown(f"- 🔸 `{f}`")
            st.markdown("""
            **Executive Interpretation:** Tasks assigned to employees already carrying elevated baseline overtime, or requiring high estimated hours in constrained departments, exhibit a significantly higher probability of deadline slippage.
            """)
    else:
        st.info("Feature importance explanation unavailable for this configuration.")

    st.markdown("---")
    st.markdown("""
    <div class="alert-box-info">
        <b>⚖️ Ethical Machine Learning Governance:</b><br/>
        This predictive pipeline is engineered strictly to flag operational friction, forecast delivery risks, and allocate supportive resources early. 
        It MUST NOT be utilized for individual punitive appraisal or automated performance ratings.
    </div>
    """, unsafe_allow_html=True)
