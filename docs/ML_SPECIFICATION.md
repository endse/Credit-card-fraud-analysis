# FraudGuard AI — Machine Learning Algorithm Specification

## 1. Problem Formulation & Objective

Credit card fraud detection is formulated as a supervised binary classification task:

$$y \in \{0, 1\}$$

where:
- $y = 0$: Legitimate transaction
- $y = 1$: Fraudulent transaction (unauthorized card use, account takeover, card-cloning, or velocity attack)

Given an input feature vector $\mathbf{x} \in \mathbb{R}^{10}$, the model estimates the conditional posterior probability:

$$\hat{p} = P(y = 1 \mid \mathbf{x}) \in [0.0, 1.0]$$

---

## 2. Severe Class Imbalance Mitigation

Real-world financial transaction datasets typically exhibit extreme imbalance (fraud incidence $< 0.1\%$). In our benchmark dataset (20,000 transactions), fraud prevalence is calibrated to **4.0%** (800 fraud positives vs. 19,200 legitimate instances).

To prevent the algorithm from collapsing into a trivial majority-class classifier, we apply an asymmetric loss penalty via the **positive class weight** parameter:

$$\text{scale\_pos\_weight} = \frac{N_{\text{negative}}}{N_{\text{positive}}} = \frac{19200 \times 0.8}{800 \times 0.8} = 24.0$$

The XGBoost objective function is thus defined as weighted log-loss:

$$\mathcal{L}(\theta) = -\sum_{i=1}^{N} \left[ w \cdot y_i \log(\hat{p}_i) + (1 - y_i) \log(1 - \hat{p}_i) \right] + \sum_{k} \Omega(f_k)$$

where $w = 24.0$ when $y_i = 1$, and $w = 1.0$ when $y_i = 0$. $\Omega(f_k) = \gamma T + \frac{1}{2}\lambda \sum_{j=1}^{T} w_j^2$ is the tree complexity regularization term.

---

## 3. Mathematical Feature Engineering

The feature engineering layer (`backend/ml/generate_data.py` and `backend/ml/predict.py`) maps raw transaction inputs to a 10-dimensional continuous/ordinal feature vector:

| # | Feature Symbol | Formulation | Distribution / Range |
| :---: | :--- | :--- | :---: |
| 1 | $x_{\text{amt}}$ | $\text{Raw monetary value}$ | $[50.0, 150000.0]$ |
| 2 | $x_{\text{avg}}$ | $\text{Customer historical mean}$ | $[1200.0, 12000.0]$ |
| 3 | $x_{\text{dev}}$ | $\frac{x_{\text{amt}}}{\max(1.0, x_{\text{avg}})}$ | $[0.1, 40.0]$ |
| 4 | $x_{\text{hour}}$ | $\text{Hour of event } t \pmod{24}$ | $\{0, 1, \dots, 23\}$ |
| 5 | $x_{\text{day}}$ | $\text{Day of month}$ | $\{1, 2, \dots, 28\}$ |
| 6 | $x_{\text{vel}}$ | $\sum \mathbb{I}(t_{\text{prev}} \ge t - 10\text{m})$ | $\{0, 1, \dots, 15\}$ |
| 7 | $x_{\text{freq}}$ | $\text{Trailing 30-day transaction count}$ | $\{5, 6, \dots, 50\}$ |
| 8 | $x_{\text{dev\_flag}}$ | $\mathbb{I}(\text{Hardware fingerprint unrecognized})$ | $\{0, 1\}$ |
| 9 | $x_{\text{loc\_flag}}$ | $\mathbb{I}(\text{Geo-IP distance outside 3}\sigma \text{ perimeter})$ | $\{0, 1\}$ |
| 10| $x_{\text{merch\_risk}}$| $\text{Ordinal risk category (LOW=0, MED=1, HIGH=2)}$ | $\{0, 1, 2\}$ |

---

## 4. Hyperparameter Architecture

### 4.1 Candidate Model: XGBoost Classifier

```python
XGBClassifier(
    n_estimators=150,          # Number of gradient boosted decision trees
    max_depth=5,               # Prevents deep overfitting on spurious noise
    learning_rate=0.08,        # Shrinkage factor stabilizing gradient steps
    scale_pos_weight=24.0,     # Class imbalance weighting
    eval_metric="logloss",     # Standard cross-entropy optimization
    subsample=0.85,            # Row subsampling for bagging effect
    colsample_bytree=0.85,     # Column subsampling per tree
    random_state=42,           # Deterministic reproducibility
    n_jobs=-1                  # Multi-threaded parallel inference
)
```

### 4.2 Baseline Model: L2-Regularized Logistic Regression

```python
LogisticRegression(
    class_weight="balanced",   # Inversely proportional class weighting
    max_iter=1000,
    C=1.0,                     # Moderate L2 penalty
    random_state=42
)
```

---

## 5. Benchmark Performance Comparison

Evaluated on 4,000 holdout test transactions (stratified 20% split, 160 true fraud cases):

### Confusion Matrices

#### Baseline: Logistic Regression
```text
                  Predicted Legit (0)    Predicted Fraud (1)
Actual Legit (0)         3,666                   174
Actual Fraud (1)             2                   158
```
- **False Positives**: 174
- **False Negatives**: 2
- **Precision**: $158 / (158 + 174) = 47.59\%$
- **Recall**: $158 / (158 + 2) = 98.75\%$
- **F1 Score**: $64.23\%$

#### Candidate: XGBoost Classifier
```text
                  Predicted Legit (0)    Predicted Fraud (1)
Actual Legit (0)         3,769                    71
Actual Fraud (1)             2                   158
```
- **False Positives**: 71 (**59.2% reduction in false positive declines**)
- **False Negatives**: 2
- **Precision**: $158 / (158 + 71) = 69.00\%$ (**+21.4% gain**)
- **Recall**: $158 / (158 + 2) = 98.75\%$
- **F1 Score**: $81.23\%$ (**+17.0% gain**)
- **ROC-AUC**: $0.9987$

---

## 6. Drift Monitoring & Retraining Protocol

In production deployments, consumer spending habits and fraud vectors evolve:
1. **Population Stability Index (PSI)**: Monitored weekly on all continuous features ($x_{\text{amt}}, x_{\text{dev}}, x_{\text{vel}}$). If $\text{PSI} > 0.25$, trigger retraining workflow.
2. **Concept Drift Detection**: Track daily false positive rate against verified chargeback reports from issuing networks (Visa/Mastercard TC40 data).
3. **Automated Shadow Deployment**: New models must run in shadow mode for 7 days, achieving superior or equal F1 score before taking live traffic.
