# Credit Card Fraud Detection — 1-Day Demo PRD

**Project:** Credit Card Fraud Detection System  
**Demo Duration:** 1 Day  
**Demo Type:** Functional AI/ML prototype  
**Primary Technologies:** Python, Java/Spring Boot, JavaScript/React  
**Primary Objective:** Demonstrate real-time transaction fraud detection using machine learning, explainable risk scoring, and a web dashboard.

---

# 1. Demo Objective

Build a working prototype that can accept a credit-card transaction, analyze it using an ML model, generate a fraud probability and risk score, and display the decision in a web interface.

The complete demo flow should be:

```text
User enters transaction
        ↓
Java Backend API
        ↓
Python ML Service
        ↓
Feature Engineering
        ↓
ML Fraud Prediction
        ↓
Risk Score
        ↓
Fraud Decision
        ↓
JavaScript Dashboard
        ↓
Approve / Review / Block
```

The demo must clearly show:

**"A transaction comes in → the system analyzes it → AI detects whether it looks fraudulent → the UI explains why."**

---

# 2. Demo Scope

## In Scope

The 1-day prototype will implement:

1. Transaction input form
2. REST API
3. ML fraud prediction
4. Basic transaction feature engineering
5. Fraud probability
6. Risk score
7. Rule-based secondary checks
8. Fraud explanation
9. Approve/Review/Block decision
10. Transaction history
11. Basic fraud dashboard
12. Preloaded sample transaction dataset

## Out of Scope

Do not attempt to implement:

- real banking integration
- actual payment processing
- Kafka
- Kubernetes
- distributed architecture
- automated model retraining
- model drift pipeline
- graph neural networks
- advanced customer authentication
- real card-network integration
- production-grade compliance infrastructure
- real PAN storage
- sophisticated device fingerprinting
- multi-bank fraud intelligence

These belong to later phases.

---

# 3. Demo Success Criteria

The demo is successful when the team can demonstrate:

```text
✓ Application starts successfully
✓ User can enter a transaction
✓ Transaction reaches Java backend
✓ Backend sends transaction/features to Python ML service
✓ ML model generates fraud probability
✓ Risk score is generated
✓ System produces APPROVE / REVIEW / BLOCK
✓ Explanation is displayed
✓ Transaction appears in dashboard/history
✓ Clearly fraudulent sample produces high risk
✓ Clearly legitimate sample produces low risk
```

---

# 4. Recommended Demo Architecture

Keep the architecture simple.

```text
                 React / JavaScript
                        │
                        │ HTTP
                        ▼
              ┌──────────────────┐
              │ Java Spring Boot │
              │   REST API       │
              └────────┬─────────┘
                       │
                       │ HTTP/JSON
                       ▼
              ┌──────────────────┐
              │ Python ML API    │
              │    FastAPI       │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ ML Model         │
              │ XGBoost / RF     │
              └──────────────────┘
                       │
                       ▼
                 Prediction
                       │
                       ▼
              Java Risk Engine
                       │
             ┌─────────┼──────────┐
             ▼         ▼          ▼
          APPROVE    REVIEW      BLOCK
                       │
                       ▼
                  Dashboard
```

For a one-day demo, PostgreSQL is optional. A local SQLite/database or in-memory transaction store is sufficient.

---

# 5. Technology Stack

## Frontend

```text
React
JavaScript / TypeScript
HTML
CSS
Chart.js
```

## Backend

```text
Java
Spring Boot
Maven
REST API
```

## ML

```text
Python
FastAPI
pandas
NumPy
scikit-learn
XGBoost
joblib
```

## Storage

Preferred:

```text
SQLite / PostgreSQL
```

For the demo:

```text
SQLite
```

is sufficient.

---

# 6. ML Model

The demo should use a simple supervised classifier.

## Recommended

**XGBoost**

Fallback:

**Random Forest**

Baseline:

**Logistic Regression**

For speed of implementation, the team may train one model and compare it informally against the baseline.

---

# 7. Dataset

Use a publicly available credit-card fraud dataset or an existing synthetic dataset.

Minimum requirement:

```text
transaction amount
time
merchant/category information
transaction frequency/history
fraud label
```

The dataset must contain:

```text
fraud = 0
fraud = 1
```

The demo does not need to build a sophisticated data ingestion pipeline.

---

# 8. ML Features

Keep the feature set small enough to implement in one day.

Recommended features:

```text
amount
transaction_hour
transaction_day
transaction_frequency
average_transaction_amount
amount_deviation
is_new_location
is_new_device
merchant_risk
transactions_last_10_minutes
```

Example:

```text
amount = 75000
average_transaction_amount = 2500
amount_deviation = 30
is_new_location = 1
is_new_device = 1
transactions_last_10_minutes = 8
```

These features create a convincing demonstration of behavioral fraud detection.

---

# 9. Feature Engineering

The Python service should perform:

```text
Raw Transaction
      ↓
Validation
      ↓
Feature Extraction
      ↓
Feature Scaling/Encoding where required
      ↓
Model Input
```

Example:

```python
features = {
    "amount": 75000,
    "transaction_hour": 3,
    "transactions_last_10_minutes": 8,
    "average_transaction_amount": 2500,
    "amount_deviation": 30,
    "is_new_location": 1,
    "is_new_device": 1
}
```

---

# 10. Fraud Prediction

The ML model returns:

```text
fraud_probability
```

Example:

```text
0.94
```

This means the model estimates a high likelihood of fraud for the modeled target definition; it should not be presented as proof that the transaction is fraudulent.

---

# 11. Risk Score

Convert the model output into a demo risk score:

```text
risk_score = fraud_probability × 100
```

Example:

```text
0.94 → 94
```

Risk levels:

```text
0–29   LOW
30–59  MEDIUM
60–79  HIGH
80–100 CRITICAL
```

---

# 12. Decision Engine

Use simple thresholds.

```text
0–29
→ APPROVE

30–69
→ REVIEW

70–100
→ BLOCK
```

For the demo, these thresholds can be manually configured in the backend.

The UI should clearly display the decision.

---

# 13. Rule Engine

Add 4–5 deterministic rules to make the demo visibly hybrid.

### Rule 1 — Large Transaction

```text
IF amount > 5 × average_transaction_amount
THEN risk + 15
```

### Rule 2 — New Device

```text
IF new_device = true
AND amount > 50000
THEN risk + 15
```

### Rule 3 — Transaction Velocity

```text
IF transactions_last_10_minutes > 5
THEN risk + 20
```

### Rule 4 — New Location

```text
IF new_location = true
THEN risk + 10
```

### Rule 5 — High-Risk Merchant

```text
IF merchant_risk = HIGH
THEN risk + 10
```

Maximum score:

```text
100
```

The final risk score can combine the ML score and rule contribution, but the exact formula should remain simple enough to explain during the demo.

---

# 14. Hybrid Risk Calculation

Recommended demo formula:

```text
ML Score = fraud_probability × 70
Rule Score = rule_points × 30 / max_rule_points

Final Risk Score =
ML Score + Rule Score
```

Example:

```text
ML probability = 0.90

ML contribution:
0.90 × 70 = 63

Rules:
25 / 50 × 30 = 15

Final Risk Score:
63 + 15 = 78
```

Decision:

```text
78 → BLOCK
```

This demonstrates that the system does not rely solely on the ML prediction.

---

# 15. Explainability

For every suspicious transaction, return the top reasons.

Example:

```text
Fraud Risk: 92

Why?

• Transaction amount is 12× the customer's average.
• New device detected.
• Unusual transaction location.
• 7 transactions occurred in the last 10 minutes.
```

The first demo can use feature/rule-based explanations rather than implementing a full SHAP pipeline.

SHAP can be added later.

---

# 16. Java API

Primary endpoint:

```text
POST /api/transactions/analyze
```

Request:

```json
{
  "cardId": "CARD001",
  "amount": 75000,
  "merchant": "Online Electronics",
  "merchantRisk": "HIGH",
  "transactionHour": 3,
  "transactionsLast10Minutes": 8,
  "averageTransactionAmount": 2500,
  "newDevice": true,
  "newLocation": true
}
```

Response:

```json
{
  "fraudProbability": 0.94,
  "riskScore": 92,
  "riskLevel": "CRITICAL",
  "decision": "BLOCK",
  "reasons": [
    "Transaction amount significantly exceeds customer average",
    "New device detected",
    "Unusual location",
    "High transaction velocity"
  ]
}
```

---

# 17. Python ML API

Endpoint:

```text
POST /predict
```

Request:

```json
{
  "features": {
    "amount": 75000,
    "transactionHour": 3,
    "transactionsLast10Minutes": 8,
    "averageTransactionAmount": 2500,
    "newDevice": true,
    "newLocation": true
  }
}
```

Response:

```json
{
  "fraudProbability": 0.94
}
```

The Python service should do only ML-related work.

The Java service should remain responsible for the business decision.

---

# 18. Frontend

The demo needs only 3 main screens.

## Screen 1 — Dashboard

Display:

```text
Total Transactions
Fraud Detected
Blocked
Under Review
Approved
```

Example:

```text
┌────────────────────────────────────┐
│ Credit Card Fraud Detection        │
├──────────┬──────────┬──────────────┤
│ 1,250    │ 48       │ 31           │
│ TXNs     │ Fraud    │ Blocked      │
├──────────┴──────────┴──────────────┤
│ Fraud Detection Trend               │
│        █                             │
│     █  █      █                      │
│  █  █  █   █  █                     │
└────────────────────────────────────┘
```

---

# 19. Transaction Simulator

This is the most important demo screen.

Input fields:

```text
Card ID
Amount
Merchant
Merchant Risk
Transaction Hour
Transactions in Last 10 Minutes
Average Transaction Amount
New Device
New Location
```

Button:

```text
[ ANALYZE TRANSACTION ]
```

---

# 20. Result Display

After clicking Analyze:

```text
┌────────────────────────────────────┐
│ FRAUD ANALYSIS                     │
├────────────────────────────────────┤
│ Fraud Probability      94%         │
│ Risk Score             92/100      │
│ Risk Level             CRITICAL    │
│                                    │
│ Decision                            │
│             🚫 BLOCK               │
│                                    │
│ Why?                               │
│ • Large transaction               │
│ • New device                      │
│ • New location                    │
│ • High transaction velocity       │
└────────────────────────────────────┘
```

The result should update immediately without refreshing the page.

---

# 21. Transaction History

Display recently analyzed transactions:

| Time | Amount | Risk | Decision |
|---|---:|---:|---|
| 12:01 | ₹750 | 12 | APPROVE |
| 12:05 | ₹1,200 | 19 | APPROVE |
| 12:17 | ₹72,000 | 92 | BLOCK |
| 12:20 | ₹8,000 | 55 | REVIEW |

Sort by newest first.

---

# 22. Demo Scenarios

The team must prepare three transactions.

## Scenario A — Legitimate

```text
Amount: ₹1,200
Average: ₹2,000
Transactions/10min: 1
New Device: No
New Location: No
Merchant Risk: LOW
```

Expected:

```text
LOW
APPROVE
```

---

## Scenario B — Suspicious

```text
Amount: ₹15,000
Average: ₹3,000
Transactions/10min: 4
New Device: Yes
New Location: No
Merchant Risk: MEDIUM
```

Expected:

```text
MEDIUM/HIGH
REVIEW
```

---

## Scenario C — Fraudulent

```text
Amount: ₹75,000
Average: ₹2,500
Transactions/10min: 8
New Device: Yes
New Location: Yes
Merchant Risk: HIGH
Transaction Hour: 3 AM
```

Expected:

```text
CRITICAL
BLOCK
```

The exact outputs must be validated against the trained model and configured rules before the presentation; the team should not hardcode the expected ML probability.

---

# 23. Demo Dataset Preparation

Prepare approximately:

```text
5,000–50,000 transactions
```

depending on available compute and dataset size.

For a one-day prototype, the dataset should already be cleaned.

Pipeline:

```text
Dataset
   ↓
Clean
   ↓
Select Features
   ↓
Train/Test Split
   ↓
Train Model
   ↓
Evaluate
   ↓
Save Model
```

Save:

```text
fraud_model.pkl
```

or the appropriate serialized model format.

---

# 24. ML Evaluation

The demo should show basic model metrics:

```text
Precision
Recall
F1
ROC-AUC
Confusion Matrix
```

Do not optimize for accuracy alone because fraud datasets are usually highly imbalanced.

The demo should display something like:

```text
Model Performance

Precision:  0.84
Recall:     0.76
F1 Score:   0.80
ROC-AUC:    0.91
```

These values are illustrative; use the actual results from the selected dataset/model.

---

# 25. One-Day Development Plan

## Hour 1 — Project Setup

Frontend:

```text
React application
```

Backend:

```text
Spring Boot application
```

ML:

```text
Python environment
```

Create repository structure.

---

# Hour 2 — Dataset + ML

Tasks:

```text
Load dataset
Clean data
Select features
Train Logistic Regression
Train XGBoost/Random Forest
Evaluate
Select candidate
Save model
```

Deliverable:

```text
fraud_model
```

---

# Hour 3 — Python API

Implement:

```text
FastAPI
POST /predict
```

Connect saved ML model.

Test:

```text
JSON → Prediction
```

---

# Hour 4 — Java Backend

Implement:

```text
POST /api/transactions/analyze
```

Flow:

```text
Request
 ↓
Validation
 ↓
Call Python ML API
 ↓
Calculate rules
 ↓
Calculate risk score
 ↓
Decision
 ↓
Response
```

---

# Hour 5 — Frontend

Build:

```text
Dashboard
Transaction Simulator
Result Card
Transaction History
```

Focus on usability rather than extensive UI components.

---

# Hour 6 — Integration

Connect:

```text
React
 ↓
Java
 ↓
Python
 ↓
ML Model
```

Test end-to-end.

---

# Hour 7 — Demo Scenarios + Polish

Prepare:

```text
Legitimate scenario
Suspicious scenario
Fraud scenario
```

Improve:

- loading state
- error handling
- risk visualization
- charts
- explanation text

---

# Hour 8 — Testing + Presentation

Verify:

```text
✓ Backend starts
✓ ML service starts
✓ Frontend starts
✓ APIs work
✓ Legit transaction works
✓ Fraud transaction works
✓ Dashboard updates
✓ No console errors
```

Create a short presentation explaining:

```text
Problem
 ↓
Solution
 ↓
ML Algorithm
 ↓
Architecture
 ↓
Live Demo
 ↓
Results
 ↓
Future Scope
```

---

# 26. Repository Structure

Use a minimal structure:

```text
credit-card-fraud-demo/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
│
├── backend/
│   ├── src/main/java/
│   │   ├── controller/
│   │   ├── service/
│   │   ├── model/
│   │   └── config/
│   └── pom.xml
│
├── ml/
│   ├── data/
│   ├── train.py
│   ├── predict.py
│   ├── model/
│   └── requirements.txt
│
├── README.md
└── docker-compose.yml
```

---

# 27. MVP Acceptance Thresholds for the Demo

Because this is a one-day demonstration rather than a production system, acceptance thresholds should be realistic.

## Functional

```text
Transaction analysis success rate: ≥ 95%
Fraud API response success: ≥ 95%
All 3 demo scenarios working: 100%
```

## ML

```text
Recall: ≥ 70%
Precision: ≥ 70%
F1: ≥ 70%
ROC-AUC: ≥ 0.80
```

These are demo thresholds, not production-bank acceptance criteria.

## Performance

```text
Median end-to-end response: ≤ 1 second
P95 response: ≤ 2 seconds
```

## UI

```text
All core screens functional: 100%
No blocking frontend errors
No blocking backend errors
```

## Explainability

```text
HIGH/CRITICAL transactions:
≥ 3 meaningful reasons where applicable
```

---

# 28. Definition of Done

The 1-day demo is complete when the following sequence works on a fresh run:

```text
START SYSTEM
     ↓
Open Browser
     ↓
Enter Transaction
     ↓
Click Analyze
     ↓
Java API Receives Transaction
     ↓
Python ML Model Evaluates Transaction
     ↓
Risk Score Generated
     ↓
Rules Evaluated
     ↓
APPROVE / REVIEW / BLOCK
     ↓
Explanation Displayed
     ↓
Transaction Saved
     ↓
Dashboard Updated
```

---

# 29. Demo Presentation Flow

The live presentation should take approximately 5–10 minutes.

### Step 1 — Problem

Explain that static fraud rules can struggle with changing behavioral patterns and false positives.

### Step 2 — Architecture

Show:

```text
React
 ↓
Java
 ↓
Python ML
 ↓
Risk Engine
 ↓
Decision
```

### Step 3 — Normal Transaction

Enter a normal transaction.

Expected:

```text
Risk: LOW
Decision: APPROVE
```

### Step 4 — Suspicious Transaction

Change:

```text
amount ↑
new device = true
```

Expected:

```text
Risk ↑
Decision: REVIEW
```

### Step 5 — Fraud Transaction

Set:

```text
large amount
new device
new location
high transaction velocity
3 AM
```

Expected:

```text
Risk: HIGH/CRITICAL
Decision: BLOCK
```

### Step 6 — Explain Why

Show:

```text
Large amount
+
Behavior deviation
+
New device
+
New location
+
High velocity
```

### Step 7 — Dashboard

Show the transaction appearing in the history and fraud statistics.

---

# 30. Future Scope

After the demo, the architecture can evolve into:

```text
MVP
 ↓
Real-time Kafka pipeline
 ↓
Redis behavioral profiles
 ↓
SHAP explanations
 ↓
Isolation Forest
 ↓
Model registry
 ↓
Model drift monitoring
 ↓
Automated retraining
 ↓
Graph fraud detection
 ↓
Deep learning
 ↓
Production deployment
```

---

# 31. One-Day Priority Rule

The team should prioritize the following in order:

```text
1. END-TO-END FUNCTIONALITY
2. ML PREDICTION
3. FRAUD RISK SCORE
4. APPROVE/REVIEW/BLOCK
5. EXPLANATION
6. DASHBOARD
7. UI POLISH
8. ADVANCED ML
```

Do **not** spend the demo day implementing infrastructure such as Kubernetes, Kafka, sophisticated MLOps, or distributed services.

The strongest one-day demo is a **small but complete vertical slice**:

```text
Transaction
   ↓
ML
   ↓
Risk
   ↓
Decision
   ↓
Explanation
   ↓
Dashboard
```

That gives the team something that can actually be demonstrated live rather than a large partially implemented architecture.