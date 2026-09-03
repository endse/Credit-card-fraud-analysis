# FraudGuard AI — Live Demo Presentation Script (5–10 Minutes)

This script provides an exact, step-by-step walkthrough for demonstrating the FraudGuard AI platform live to stakeholders, engineering leadership, and clients. It directly aligns with **PRD Section 29 (Demo Presentation Flow)**.

---

## Presentation Checklist & Pre-Flight

1. **Verify Services Are Running**:
   - Backend API: `http://localhost:8000/api/health` -> `{"status":"ok"}`
   - Frontend Web Console: `http://localhost:5173`
2. **Open the Dashboard**: Navigate to `http://localhost:5173` in full screen (`F11`).
3. **Target Duration**: 6–8 minutes (leaving 2–4 minutes for Q&A).

---

## Step 1: The Problem Statement (~1 Minute)

> **Speaker Script:**
> *"Good morning/afternoon everyone. Traditional payment fraud detection relies heavily on static if-else rule engines. While rules are easy to audit, they suffer from two major fatal flaws:
> 1. They produce an unacceptable volume of false positives, declining legitimate customers and causing friction.
> 2. Fraudsters quickly reverse-engineer simple thresholds (like spending ₹49,999 instead of ₹50,000) to evade detection.
>
> Pure black-box deep learning models, on the other hand, cannot explain their decisions to fraud investigators or banking regulators.
>
> Today, I'm presenting **FraudGuard AI** — a high-speed, production-ready hybrid fraud prevention platform that unifies supervised gradient-boosted machine learning with deterministic financial compliance rules and real-time Explainable AI (XAI)."*

---

## Step 2: Architecture & Latency Profile (~1 Minute)

> **Action:** Point to the top status badge and the architecture summary in the dashboard.
>
> **Speaker Script:**
> *"Behind this dashboard is an ultra-low-latency pipeline engineered for high-throughput card networks:
> - **REST Gateway**: Powered by FastAPI, ingesting transactions in under 2 milliseconds.
> - **ML Inference Tier**: An optimized XGBoost pipeline executing 10 continuous behavioral features in less than 3 microseconds per sample.
> - **Deterministic Rule Engine**: 5 secondary compliance checks that enforce legal guardrails.
> - **Hybrid Synthesis Engine**: Weighs ML probability at 70% and rule penalties at 30% to compute an actionable risk score from 0 to 100 with sub-50ms end-to-end latency."*

---

## Step 3: Scenario A — Normal Everyday Transaction (~1.5 Minutes)

> **Action:** Under **Transaction Simulator**, click the preset button **"Scenario A: Legitimate (Approve)"**.
>
> **Speaker Script:**
> *"Let's test our first scenario: a routine, legitimate purchase.
> Notice the parameters:
> - The cardholder is spending ₹1,200 at Amazon Retail.
> - Their historical baseline average is ₹2,000 (meaning they are spending well within their 0.6× norm).
> - This is their only transaction in the last 10 minutes, originating from a verified device and familiar location.
>
> Let's click **Analyze Transaction**."*
>
> **Action:** Click **ANALYZE TRANSACTION**.
>
> **Observation:**
> - Risk Score: `0 / 100` (`LOW`)
> - Decision Badge: `✅ APPROVE`
> - ML Probability: `0.01%`
> - Explainability: All risk factor bars are green. The transaction is instantly approved with zero cardholder friction.

---

## Step 4: Scenario B — Suspicious Transaction (~1.5 Minutes)

> **Action:** Under **Transaction Simulator**, click the preset button **"Scenario B: Suspicious (Review)"**.
>
> **Speaker Script:**
> *"Now let's examine an elevated transaction that exhibits multiple borderline anomalies:
> - Spending ₹15,000 on Electronics against a ₹3,000 historical baseline (a 5.0× deviation).
> - 4 transactions have occurred within the last 10 minutes.
> - The transaction originated from an unrecognized hardware device.
>
> Let's analyze this."*
>
> **Action:** Click **ANALYZE TRANSACTION**.
>
> **Observation:**
> - Risk Score: `36 / 100` (`MEDIUM`)
> - Decision Badge: `⚠️ REVIEW`
> - ML Probability: `51.4%`
> - Explainability: The UI displays amber warning flags for amount deviation and device novelty. The engine routes this for Step-Up Authentication (3D-Secure SMS/OTP) rather than immediately declining the customer.

---

## Step 5: Scenario C — Critical Fraud Drain (~1.5 Minutes)

> **Action:** Under **Transaction Simulator**, click the preset button **"Scenario C: Fraudulent (Block)"**.
>
> **Speaker Script:**
> *"Finally, let's simulate a sophisticated, high-impact account takeover attack:
> - The fraudster attempts an ₹75,000 transaction at a high-risk cryptocurrency exchange.
> - This is 30.0× the customer's typical ₹2,500 average.
> - An aggressive velocity spike of 8 transactions in 10 minutes.
> - Originating at 3:00 AM from a brand-new device and an international IP address.
>
> Let's submit this."*
>
> **Action:** Click **ANALYZE TRANSACTION**.
>
> **Observation:**
> - Risk Score: `100 / 100` (`CRITICAL`)
> - Decision Badge: `🚫 BLOCK`
> - ML Probability: `100.0%`
> - Rule Score: `30 / 30` (All 5 rules breached)
> - Action: The transaction is immediately terminated, and an urgent SMS/app push alert is dispatched to the cardholder.

---

## Step 6: Explainability & Compliance Audit (~1 Minute)

> **Action:** Scroll to the **Why was this decision made?** section of the Result Card.
>
> **Speaker Script:**
> *"Notice the Explainable AI output. Instead of presenting a black-box probability, FraudGuard AI delivers transparent, plain-English reasons:
> - 'Transaction amount (₹75,000) is 30.0× the customer's historical average.'
> - 'High velocity anomaly: 8 transactions attempted within the last 10 minutes.'
> - 'New/unrecognized device fingerprint detected.'
> - 'Unusual geographic location outside regular perimeter.'
> - 'Nocturnal off-hours activity at 3:00 AM.'
>
> Furthermore, the factor contribution bars quantify exactly how much each feature contributed to the final score. This directly satisfies banking regulatory requirements (e.g. Fair Credit Reporting Act, GDPR Article 22)."*

---

## Step 7: Live Audit Trail & Model Benchmarks (~1.5 Minutes)

> **Action:** 
> 1. Scroll down to the **Real-Time Fraud Risk Velocity Timeline** and show how the latest 100-risk transaction is plotted as a crimson node.
> 2. Point out the **Transaction Audit History** table where all analyzed transactions are prepended live with search and category filters (`BLOCK`, `REVIEW`, `APPROVE`).
> 3. Click **Model Benchmarks** in the top navigation bar.
>
> **Speaker Script:**
> *"To conclude, let's inspect the offline model benchmarks:
> - Evaluated on a 4,000-transaction holdout set, our candidate XGBoost model achieved **98.50% overall accuracy**, **73.58% precision**, and **97.50% recall**, completely exceeding the PRD MVP targets.
> - Most importantly, XGBoost achieved a **67.82% reduction in false alarms** compared to the baseline, directly protecting customer satisfaction while stopping fraud in real time.
>
> Thank you! I'm happy to answer any questions or test custom transaction parameters."*
