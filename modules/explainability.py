"""
Explainable AI (XAI) Module for WorkPulse AI
Extracts feature importance using SHAP values where feasible,
with seamless fallback to Scikit-learn Permutation Importance.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.inspection import permutation_importance

def compute_model_explainability(model_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes global feature importances using SHAP or Permutation Importance.
    Returns structured DataFrame and explanation text.
    """
    if not model_result.get("success", False):
        return {"method": "None", "importance_df": pd.DataFrame(), "error": "Model was not trained successfully."}

    pipeline = model_result["pipeline"]
    X_test = model_result["X_test"]
    y_test = model_result["y_test"]
    feature_names = model_result["feature_names"]
    
    # Try SHAP first
    try:
        import shap
        preprocessor = pipeline.named_steps["preprocessor"]
        classifier = pipeline.named_steps["classifier"]
        
        # Transform X_test to numeric representation
        X_test_trans = preprocessor.transform(X_test)
        if hasattr(X_test_trans, "toarray"):
            X_test_trans = X_test_trans.toarray()

        # Choose explainer
        sample_subset = X_test_trans[:min(200, len(X_test_trans))]
        
        if hasattr(classifier, "estimators_") or "RandomForest" in type(classifier).__name__ or "Gradient" in type(classifier).__name__:
            explainer = shap.TreeExplainer(classifier)
            shap_values = explainer.shap_values(sample_subset)
            if isinstance(shap_values, list) and len(shap_values) == 2:
                # Class 1 (delay)
                mean_shap = np.abs(shap_values[1]).mean(axis=0)
            elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
                mean_shap = np.abs(shap_values[:, :, 1]).mean(axis=0)
            else:
                mean_shap = np.abs(shap_values).mean(axis=0)
        else:
            # Linear Explainer fallback
            explainer = shap.LinearExplainer(classifier, sample_subset)
            shap_values = explainer.shap_values(sample_subset)
            mean_shap = np.abs(shap_values).mean(axis=0)

        df_importance = pd.DataFrame({
            "Feature": feature_names[:len(mean_shap)],
            "Importance": mean_shap
        }).sort_values(by="Importance", ascending=False).reset_index(drop=True)

        return {
            "method": "SHAP (Shapley Additive Explanations)",
            "importance_df": df_importance,
            "top_features": df_importance.head(8)["Feature"].tolist()
        }

    except Exception as e:
        # Fallback to Permutation Importance
        try:
            r = permutation_importance(pipeline, X_test, y_test, n_repeats=5, random_state=42, scoring="roc_auc")
            # Feature names correspond to raw input columns for permutation_importance
            raw_cols = list(X_test.columns)
            importances = r.importances_mean

            df_importance = pd.DataFrame({
                "Feature": raw_cols,
                "Importance": importances
            }).sort_values(by="Importance", ascending=False).reset_index(drop=True)

            return {
                "method": "Scikit-Learn Permutation Importance (ROC-AUC drop)",
                "importance_df": df_importance,
                "top_features": df_importance.head(8)["Feature"].tolist()
            }
        except Exception as e2:
            return {
                "method": "Failed",
                "importance_df": pd.DataFrame(),
                "error": f"SHAP failed ({str(e)}); Permutation importance failed ({str(e2)})"
            }
