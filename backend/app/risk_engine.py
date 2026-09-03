"""
Risk Engine Module
Combines ML fraud prediction with deterministic business rules
to calculate final risk score and decision as specified in PRD Sections 11, 12, 14.
"""
import sys
import os
from typing import Dict, Any, Tuple

# Ensure ML module is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml")))
from predict import predict_fraud_probability
from .rules import evaluate_rules
from .explainability import generate_explanations

def calculate_risk(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the full hybrid risk calculation:
      1. Evaluates ML model -> fraud_probability (0.00 - 1.00)
      2. Computes ML Score = fraud_probability * 70
      3. Evaluates Rule Engine -> rule_points out of max 70
      4. Computes Rule Score = (rule_points / 70) * 30
      5. Final Risk Score = ML Score + Rule Score (clamped to [0, 100])
      6. Maps to Risk Level (LOW, MEDIUM, HIGH, CRITICAL)
      7. Maps to Decision (APPROVE, REVIEW, BLOCK)
      8. Generates explainability reasons and factor breakdown
    """
    # 1. ML Probability
    ml_weight = float(os.getenv("ML_WEIGHT", "70.0"))
    rule_weight = float(os.getenv("RULE_WEIGHT", "30.0"))
    approve_threshold = int(os.getenv("APPROVE_THRESHOLD", "29"))
    review_threshold = int(os.getenv("REVIEW_THRESHOLD", "69"))

    fraud_prob = predict_fraud_probability(transaction_data)
    ml_score = round(fraud_prob * ml_weight, 2)
    
    # 2. Rule Points
    rule_pts, max_pts, triggered_rules = evaluate_rules(transaction_data)
    rule_score = round((rule_pts / max_pts) * rule_weight, 2) if max_pts > 0 else 0.0
    
    # 3. Final Risk Score (0-100)
    final_score = int(min(100, max(0, round(ml_score + rule_score))))
    
    # 4. Risk Level (PRD Section 11)
    if final_score <= approve_threshold:
        risk_level = "LOW"
    elif final_score <= 59:
        risk_level = "MEDIUM"
    elif final_score <= 79:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
        
    # 5. Decision (PRD Section 12)
    if final_score <= approve_threshold:
        decision = "APPROVE"
    elif final_score <= review_threshold:
        decision = "REVIEW"
    else:
        decision = "BLOCK"
        
    # 6. Explainability
    reasons, factor_contributions = generate_explanations(
        transaction_data, fraud_prob, final_score, triggered_rules
    )
    
    return {
        "fraudProbability": fraud_prob,
        "mlScore": ml_score,
        "ruleScore": rule_score,
        "riskScore": final_score,
        "riskLevel": risk_level,
        "decision": decision,
        "reasons": reasons,
        "factorContributions": factor_contributions,
        "triggeredRules": triggered_rules
    }
