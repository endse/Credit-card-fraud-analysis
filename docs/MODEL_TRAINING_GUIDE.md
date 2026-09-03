# FraudGuard AI — Machine Learning Model Training Guide

This guide provides an end-to-end, reproducible walkthrough of the machine learning training pipeline, feature engineering mechanics, multi-model evaluation benchmarks, and artifact export processes in FraudGuard AI.

---

## 1. Overview & Architecture

The machine learning subsystem implements a **multi-family benchmark** to select the optimal model for real-time transaction inference:
1. **Linear Baseline**: L2-regularized Logistic Regression with balanced class weighting.
2. **Bagged Ensemble**: Random Forest Classifier with 100 decision trees.
3. **Gradient Boosted Candidate**: Tuned XGBoost Classifier with asymmetric loss weighting (`scale_pos_weight = 24.0`).

```text
  Raw Synthetic Data (20,000 Records)
                  │
                  ▼
  Feature Extraction (10 Continuous & Ordinal Signals)
                  │
                  ▼
  Stratified 80/20 Train-Test Split
  ├── Train: 16,000 txns (640 Fraud, 15,360 Legit)
  └── Test:   4,000 txns (160 Fraud,  3,840 Legit)
                  │
                  ├───────────────────────┬───────────────────────┐
                  ▼                       ▼                       ▼
       Logistic Regression          Random Forest             XGBoost
        (Linear Baseline)        (Bagged Ensemble)     (Deployed Candidate)
                  │                       │                       │
                  └───────────────────────┼───────────────────────┘
                                          ▼
                         Cross-Model Evaluation & Scoring
                         • Accuracy, Precision, Recall, F1
                         • Specificity, ROC-AUC, FPR, FNR
                         • Confusion Matrix & Latency
                                          │
                                          ▼
                         Artifact Export & Serialization
                         • fraud_model.pkl (Scikit-Learn Pipeline)
                         • model_metrics.json (JSON Summary)
```

---

## 2. Environment Setup & Prerequisites

Ensure the Python virtual environment is activated and dependencies are installed:

```powershell
# 1. Initialize Python 3.11 virtual environment
uv venv .venv --python 3.11

# 2. Install machine learning and runtime dependencies
uv pip install -r backend/requirements.txt
```

### Core Libraries
- `scikit-learn` (v1.9+): Preprocessing, Pipeline, Baseline Models, Evaluation Metrics
- `xgboost` (v3.2+): Gradient-boosted decision tree algorithm
- `joblib` (v1.6+): Serialization of fitted pipelines
- `pandas` (v3.0+) & `numpy` (v2.4+): Vectorized feature manipulation

---

## 3. Step 1: Synthetic Dataset Generation

To train the models on realistic credit card fraud behavior without privacy constraints, run the data generator:

```powershell
.\.venv\Scripts\python.exe backend/ml/generate_data.py
```

### Distribution Parameters (`backend/ml/generate_data.py`):
- **Volume**: 20,000 transactions across 1,000 unique simulated cardholders (`CARD000` to `CARD999`).
- **Fraud Incidence**: Calibrated to **4.0%** (800 fraud cases, 19,200 legitimate transactions).
- **Legitimate Profile ($y = 0$)**:
  - Amount: Log-normal distribution centered around cardholder baseline ($\mu = \text{₹2,500}$, range ₹50 – ₹12,000).
  - Velocity: Low Poisson rate ($\lambda = 0.8$ transactions per 10 minutes).
  - Timing: Diurnal distribution peaking during daylight hours (10:00 AM – 9:00 PM).
  - Device/Location: Trusted known device (98% probability) and familiar IP/geo perimeter (97% probability).
- **Fraud Vectors ($y = 1$)**:
  - **Vector A (Large Amount Drain)**: Amount spikes to $5\times - 35\times$ customer historical average.
  - **Vector B (High-Velocity Bot Attack)**: $6 - 12$ transactions within a trailing 10-minute window.
  - **Vector C (Nocturnal Account Takeover)**: Transactions executing between 1:00 AM – 4:00 AM from unrecognized devices and foreign IPs at high-risk merchant categories (crypto, gaming, luxury retail).

Dataset artifact is stored at: `backend/ml/data/credit_card_transactions.csv`.

---

## 4. Step 2: Feature Matrix Engineering

The feature engineering layer transforms raw transaction attributes into an immutable 10-dimensional numerical feature vector:

| Index | Feature | Calculation | Rationale |
| :---: | :--- | :--- | :--- |
| 1 | `amount` | Raw monetary spend value | Absolute loss liability indicator |
| 2 | `average_transaction_amount` | Cardholder historical rolling mean | Customer behavioral anchor |
| 3 | `amount_deviation` | $\frac{\text{amount}}{\max(1.0, \text{average\_amount})}$ | Normalized relative spending surge |
| 4 | `transaction_hour` | $t_{\text{hour}} \in [0, 23]$ | Detects off-hours nocturnal activity |
| 5 | `transaction_day` | Day of month $[1, 28]$ | Captures cyclical billing cycles |
| 6 | `transactions_last_10_minutes` | 10-minute transaction counter | Identifies rapid card-testing bots |
| 7 | `transaction_frequency` | 30-day cumulative volume | Calibrates baseline user velocity |
| 8 | `is_new_device` | Binary flag (0 = Known, 1 = New) | Account takeover / credential stuffing |
| 9 | `is_new_location` | Binary flag (0 = Familiar, 1 = Foreign) | Geographic anomaly / card cloning |
| 10 | `merchant_risk` | Ordinal: 0 (LOW), 1 (MED), 2 (HIGH) | Terminal category risk exposure |

---

## 5. Step 3: Executing Model Training

Run the master training pipeline:

```powershell
.\.venv\Scripts\python.exe backend/ml/train.py
```

### Execution Log Output:
```text
Loading existing dataset from backend/ml/data/credit_card_transactions.csv...

--------------------------------------------------------
 1. Training Baseline: Logistic Regression...
--------------------------------------------------------
========================================================
 Logistic Regression (Baseline) Evaluation
========================================================
 Accuracy:       95.60%
 Precision:      47.59%
 Recall (TPR):   98.75% (158/160 frauds caught)
 Specificity:    95.47% (3666/3840 legit cleared)
 F1 Score:       64.23%
 ROC-AUC:        0.9966
 False Pos Rate: 4.53% (174 false alarms)
 False Neg Rate: 1.25% (2 missed frauds)
 Latency/sample: 0.001 ms
 Confusion Matrix:
   [TN: 3666, FP: 174]
   [FN: 2, TP: 158]

--------------------------------------------------------
 2. Training Multi-Model Ensemble: Random Forest...
--------------------------------------------------------
========================================================
 Random Forest Classifier Evaluation
========================================================
 Accuracy:       97.60%
 Precision:      62.50%
 Recall (TPR):   100.00% (160/160 frauds caught)
 Specificity:    97.50% (3744/3840 legit cleared)
 F1 Score:       76.92%
 ROC-AUC:        0.9982
 False Pos Rate: 2.50% (96 false alarms)
 False Neg Rate: 0.00% (0 missed frauds)
 Latency/sample: 0.015 ms
 Confusion Matrix:
   [TN: 3744, FP: 96]
   [FN: 0, TP: 160]

--------------------------------------------------------
 3. Training Production Candidate: XGBoost Classifier...
--------------------------------------------------------
========================================================
 XGBoost (Candidate) Evaluation
========================================================
 Accuracy:       98.50%
 Precision:      73.58%
 Recall (TPR):   97.50% (156/160 frauds caught)
 Specificity:    98.54% (3784/3840 legit cleared)
 F1 Score:       83.87%
 ROC-AUC:        0.9987
 False Pos Rate: 1.46% (56 false alarms)
 False Neg Rate: 2.50% (4 missed frauds)
 Latency/sample: 0.002 ms
 Confusion Matrix:
   [TN: 3784, FP: 56]
   [FN: 4, TP: 156]

[OK] Saved candidate model pipeline to: backend/ml/artifacts/fraud_model.pkl
[OK] Saved full metrics summary to: backend/ml/artifacts/model_metrics.json
```

---

## 6. Step 4: Comparative Evaluation & Benchmarks

Performance measured on **4,000 unseen test transactions** (Stratified 20% holdout split):

| Metric | Logistic Regression (Baseline) | Random Forest (Ensemble) | XGBoost (Candidate) | Winner / Impact |
| :--- | :---: | :---: | :---: | :--- |
| **Accuracy** | 95.60% | 97.60% | **98.50%** | **XGBoost (+2.90% over baseline)** |
| **Precision** | 47.59% | 62.50% | **73.58%** | **XGBoost (+25.99% over baseline)** |
| **Recall (Sensitivity)** | 98.75% | **100.00%** | 97.50% | Random Forest caught all 160 |
| **Specificity** | 95.47% | 97.50% | **98.54%** | **XGBoost (Highest legit clearance)** |
| **F1-Score** | 64.23% | 76.92% | **83.87%** | **XGBoost (+19.64% over baseline)** |
| **ROC-AUC** | 0.9966 | 0.9982 | **0.9987** | **XGBoost (Superior separation)** |
| **False Positive Rate** | 4.53% (174 alarms) | 2.50% (96 alarms) | **1.46% (56 alarms)** | **XGBoost (67.82% fewer false alarms)** |
| **False Negative Rate** | 1.25% (2 misses) | **0.00% (0 misses)** | 2.50% (4 misses) | Random Forest (0 leakage) |
| **P95 Latency / sample** | **0.001 ms** | 0.015 ms | **0.002 ms** | XGBoost 7.5× faster than RF |

### Why XGBoost is Deployed for Production:
1. **Massive False-Positive Reduction**: Slashes false alarms by **67.82%** (from 174 down to 56), preventing unnecessary cardholder blocks and support costs.
2. **Superior Precision (73.58%) & F1-Score (83.87%)**: Meets and exceeds PRD MVP targets ($\ge 70\%$).
3. **Ultra-Fast Inference (< 3 microseconds per sample)**: Ensures the system operates well within the 100ms real-time payment gateway latency budget.

---

## 7. Step 5: Confusion Matrix Visualizations

### XGBoost Classifier (Deployed Model)
```text
                          Predicted Legitimate        Predicted Fraud
Actual Legitimate (3,840)       3,784 (TN)                56 (FP)
Actual Fraud (160)                  4 (FN)               156 (TP)
```

### Random Forest Classifier
```text
                          Predicted Legitimate        Predicted Fraud
Actual Legitimate (3,840)       3,744 (TN)                96 (FP)
Actual Fraud (160)                  0 (FN)               160 (TP)
```

### Logistic Regression Baseline
```text
                          Predicted Legitimate        Predicted Fraud
Actual Legitimate (3,840)       3,666 (TN)               174 (FP)
Actual Fraud (160)                  2 (FN)               158 (TP)
```

---

## 8. Step 6: Feature Importance Breakdown

Feature importances extracted directly from the deployed XGBoost tree model:

| Rank | Feature Name | Split Contribution | Operational Insight |
| :---: | :--- | :---: | :--- |
| **1** | `amount_deviation` | **49.79%** | Primary risk driver: sudden spikes above customer spending average |
| **2** | `average_transaction_amount` | **13.97%** | Account baseline scale anchor |
| **3** | `transactions_last_10_minutes`| **12.04%** | Critical indicator for automated card-testing scripts |
| **4** | `is_new_device` | **10.73%** | Key signal for credential stuffing and account takeover |
| **5** | `merchant_risk` | **6.91%** | Exposure to high-chargeback merchant terminals |
| **6** | `amount` | **2.62%** | Absolute transaction volume |
| **7** | `transaction_hour` | **1.00%** | Nocturnal off-hours activity |
| **8** | `transaction_frequency` | **1.00%** | Normalizes individual velocity bounds |
| **9** | `is_new_location` | **1.00%** | Geographic anomaly jump |
| **10**| `transaction_day` | **0.93%** | Calendar billing cycles |

---

## 9. Step 7: Model Artifact Export & Verification

The training script automatically produces two critical serialized artifacts in `backend/ml/artifacts/`:

### 1. `fraud_model.pkl` (Scikit-Learn Pipeline)
Contains the encapsulated `StandardScaler` transformer followed by the fitted `XGBClassifier`. Can be loaded and executed in any Python environment using:

```python
import joblib
pipeline = joblib.load("backend/ml/artifacts/fraud_model.pkl")

# Predict probability of fraud for a feature matrix
prob = pipeline.predict_proba(features)[:, 1]
```

### 2. `model_metrics.json`
Machine-readable evaluation file read dynamically by the FastAPI `/api/model/metrics` endpoint and rendered in the React dashboard modal.

---

## 10. Step 8: Automated Verification Tests

Verify the newly trained model works with all operational business rules and API endpoints:

```powershell
.\.venv\Scripts\python.exe backend/test_backend.py
```

### Expected Output:
```text
=== 1. Initializing Database and Seeding ===
Total seeded transactions in DB: 54

=== 2. Testing Scenario A (Legitimate) ===
Scenario A -> Risk Score: 0, Level: LOW, Decision: APPROVE
Scenario A PASSED!

=== 3. Testing Scenario B (Suspicious) ===
Scenario B -> Risk Score: 36, Level: MEDIUM, Decision: REVIEW
Scenario B PASSED!

=== 4. Testing Scenario C (Fraudulent) ===
Scenario C -> Risk Score: 100, Level: CRITICAL, Decision: BLOCK
Scenario C PASSED!

ALL BACKEND CORE LOGIC TESTS PASSED SUCCESSFULLY!
```
