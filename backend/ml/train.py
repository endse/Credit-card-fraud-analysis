"""
Model Training & Evaluation Pipeline
Trains baseline Logistic Regression and candidate XGBoost model.
Evaluates Precision, Recall, F1, ROC-AUC, and Confusion Matrix.
Serializes model to fraud_model.pkl and metrics to model_metrics.json.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)
from xgboost import XGBClassifier

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
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_proba))
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    metrics = {
        "model_name": model_name,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "confusion_matrix": cm
    }
    
    print(f"\n--- {model_name} Results ---")
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1 Score:  {metrics['f1']:.4f}")
    print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
    print(f"Confusion Matrix: {cm}")
    
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
    
    # 1. Baseline Model: Logistic Regression
    print("\nTraining Baseline: Logistic Regression...")
    baseline_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
    ])
    baseline_pipeline.fit(X_train, y_train)
    baseline_metrics = evaluate_model(baseline_pipeline, X_test, y_test, "Logistic Regression (Baseline)")
    
    # 2. Candidate Production Model: XGBoost
    print("\nTraining Candidate: XGBoost Classifier...")
    xgb_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.08,
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1
        ))
    ])
    xgb_pipeline.fit(X_train, y_train)
    candidate_metrics = evaluate_model(xgb_pipeline, X_test, y_test, "XGBoost (Candidate)")
    
    # Save candidate model pipeline
    model_path = os.path.join(ARTIFACTS_DIR, "fraud_model.pkl")
    joblib.dump(xgb_pipeline, model_path)
    print(f"\nSaved trained model pipeline to: {model_path}")
    
    # Save combined metrics
    metrics_summary = {
        "dataset": {
            "total_records": len(df),
            "train_records": len(X_train),
            "test_records": len(X_test),
            "fraud_count": int(df["is_fraud"].sum()),
            "legit_count": int((df["is_fraud"] == 0).sum())
        },
        "feature_columns": FEATURE_COLUMNS,
        "baseline": baseline_metrics,
        "candidate": candidate_metrics,
        "comparison": {
            "f1_improvement": round(candidate_metrics["f1"] - baseline_metrics["f1"], 4),
            "roc_auc_improvement": round(candidate_metrics["roc_auc"] - baseline_metrics["roc_auc"], 4),
            "recall_improvement": round(candidate_metrics["recall"] - baseline_metrics["recall"], 4)
        }
    }
    
    metrics_path = os.path.join(ARTIFACTS_DIR, "model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_summary, f, indent=2)
    print(f"Saved metrics summary to: {metrics_path}")
    
    return metrics_summary

if __name__ == "__main__":
    train_and_export()
