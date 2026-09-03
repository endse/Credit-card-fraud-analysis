"""
Model Training & Evaluation Pipeline
Trains baseline Logistic Regression, Random Forest, and candidate XGBoost model.
Evaluates Accuracy, Precision, Recall, Specificity, F1, ROC-AUC, FPR/FNR, and Latency.
Serializes production model to fraud_model.pkl and metrics to model_metrics.json.
"""
import os
import time
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)
try:
    from xgboost import XGBClassifier
except ImportError:
    # Safe fallback for language servers running against unconfigured system interpreters
    try:
        from sklearn.ensemble import GradientBoostingClassifier as XGBClassifier
    except ImportError:
        XGBClassifier = None

try:
    from .generate_data import generate_dataset
except ImportError:
    from generate_data import generate_dataset

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

FEATURE_COLUMNS = [
    "amount",
    "average_transaction_amount",
    "amount_deviation",
    "transaction_hour",
    "transaction_day",
    "transactions_last_10_minutes",
    "transaction_frequency",
    "is_new_device",
    "is_new_location",
    "merchant_risk"
]

def evaluate_model(model, X_test, y_test, model_name: str) -> dict:
    start_time = time.perf_counter()
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    total_time = (time.perf_counter() - start_time) * 1000.0  # in ms
    latency_per_sample = total_time / max(1, len(X_test))
    
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_proba))
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    fpr = float(fp / (tn + fp)) if (tn + fp) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0
    
    metrics = {
        "model_name": model_name,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "specificity": round(specificity, 4),
        "f1": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "latency_ms_per_prediction": round(latency_per_sample, 4),
        "confusion_matrix": cm.tolist()
    }
    
    print(f"\n========================================================")
    print(f" {model_name} Evaluation")
    print(f"========================================================")
    print(f" Accuracy:       {metrics['accuracy'] * 100:.2f}%")
    print(f" Precision:      {metrics['precision'] * 100:.2f}%")
    print(f" Recall (TPR):   {metrics['recall'] * 100:.2f}% ({tp}/{tp + fn} frauds caught)")
    print(f" Specificity:    {metrics['specificity'] * 100:.2f}% ({tn}/{tn + fp} legit cleared)")
    print(f" F1 Score:       {metrics['f1'] * 100:.2f}%")
    print(f" ROC-AUC:        {metrics['roc_auc']:.4f}")
    print(f" False Pos Rate: {metrics['false_positive_rate'] * 100:.2f}% ({fp} false alarms)")
    print(f" False Neg Rate: {metrics['false_negative_rate'] * 100:.2f}% ({fn} missed frauds)")
    print(f" Latency/sample: {metrics['latency_ms_per_prediction']:.3f} ms")
    print(f" Confusion Matrix:\n   [TN: {tn}, FP: {fp}]\n   [FN: {fn}, TP: {tp}]")
    
    return metrics

def train_and_export():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    csv_path = os.path.join(DATA_DIR, "credit_card_transactions.csv")
    
    if not os.path.exists(csv_path):
        print("Generating dataset...")
        df = generate_dataset(num_records=20000, output_path=csv_path)
    else:
        print(f"Loading existing dataset from {csv_path}...")
        df = pd.read_csv(csv_path)
        
    X = df[FEATURE_COLUMNS]
    y = df["is_fraud"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    scale_pos_weight = (len(y_train) - sum(y_train)) / max(1, sum(y_train))
    
    print("\n--------------------------------------------------------")
    print(" 1. Training Baseline: Logistic Regression...")
    print("--------------------------------------------------------")
    baseline_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
    ])
    baseline_pipeline.fit(X_train, y_train)
    baseline_metrics = evaluate_model(baseline_pipeline, X_test, y_test, "Logistic Regression (Baseline)")
    
    print("\n--------------------------------------------------------")
    print(" 2. Training Multi-Model Ensemble: Random Forest...")
    print("--------------------------------------------------------")
    rf_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ])
    rf_pipeline.fit(X_train, y_train)
    rf_metrics = evaluate_model(rf_pipeline, X_test, y_test, "Random Forest Classifier")
    
    print("\n--------------------------------------------------------")
    print(" 3. Training Production Candidate: XGBoost Classifier...")
    print("--------------------------------------------------------")
    xgb_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.08,
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss",
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            n_jobs=-1
        ))
    ])
    xgb_pipeline.fit(X_train, y_train)
    candidate_metrics = evaluate_model(xgb_pipeline, X_test, y_test, "XGBoost (Candidate)")
    
    # Feature importances from XGBoost
    xgb_step = xgb_pipeline.named_steps["classifier"]
    xgb_importances = {
        col: round(float(imp), 4)
        for col, imp in sorted(
            zip(FEATURE_COLUMNS, xgb_step.feature_importances_),
            key=lambda item: item[1],
            reverse=True
        )
    }
    
    # Save candidate model pipeline (used in FastAPI backend)
    model_path = os.path.join(ARTIFACTS_DIR, "fraud_model.pkl")
    joblib.dump(xgb_pipeline, model_path)
    print(f"\n[OK] Saved candidate model pipeline to: {model_path}")
    
    # Save combined metrics (preserving backwards-compatibility)
    metrics_summary = {
        "dataset": {
            "total_records": len(df),
            "train_records": len(X_train),
            "test_records": len(X_test),
            "fraud_count": int(df["is_fraud"].sum()),
            "legit_count": int((df["is_fraud"] == 0).sum()),
            "fraud_prevalence_pct": round(float(df["is_fraud"].mean() * 100), 2)
        },
        "feature_columns": FEATURE_COLUMNS,
        "feature_importances": xgb_importances,
        "baseline": baseline_metrics,
        "random_forest": rf_metrics,
        "candidate": candidate_metrics,
        "models": {
            "logistic_regression": baseline_metrics,
            "random_forest": rf_metrics,
            "xgboost": candidate_metrics
        },
        "comparison": {
            "f1_improvement": round(candidate_metrics["f1"] - baseline_metrics["f1"], 4),
            "roc_auc_improvement": round(candidate_metrics["roc_auc"] - baseline_metrics["roc_auc"], 4),
            "recall_improvement": round(candidate_metrics["recall"] - baseline_metrics["recall"], 4),
            "false_positive_reduction_pct": round(
                ((baseline_metrics["confusion_matrix"][0][1] - candidate_metrics["confusion_matrix"][0][1]) /
                 max(1, baseline_metrics["confusion_matrix"][0][1])) * 100, 2
            )
        }
    }
    
    metrics_path = os.path.join(ARTIFACTS_DIR, "model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_summary, f, indent=2)
    print(f"[OK] Saved full metrics summary to: {metrics_path}")
    
    return metrics_summary

if __name__ == "__main__":
    train_and_export()
