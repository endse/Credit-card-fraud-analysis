"""
Explainability Engine Module
Generates plain-English explanatory reasons and risk factor contribution metrics.
"""
from typing import Dict, Any, List, Tuple

def generate_explanations(
    data: Dict[str, Any],
    fraud_prob: float,
    risk_score: int,
    triggered_rules: List[Dict[str, Any]]
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Produces:
      1. Human-readable bullet points explaining the decision.
      2. Factor breakdown with impact levels and relative contribution for visual progress bars.
    """
    amount = float(data.get("amount", 0.0))
    avg_amt = float(data.get("averageTransactionAmount", data.get("average_transaction_amount", 2500.0)))
    if avg_amt <= 0:
        avg_amt = 2500.0
    amount_deviation = round(amount / avg_amt, 1)
    
    velocity = int(data.get("transactionsLast10Minutes", data.get("transactions_last_10_minutes", 1)))
    new_device = bool(data.get("newDevice", data.get("is_new_device", False)))
    new_location = bool(data.get("newLocation", data.get("is_new_location", False)))
    merchant_risk = str(data.get("merchantRisk", data.get("merchant_risk", "LOW"))).strip().upper()
    hour = int(data.get("transactionHour", data.get("transaction_hour", 12)))
    
    reasons: List[str] = []
    factor_contributions: List[Dict[str, Any]] = []
    
    # 1. Amount Factor
    if amount_deviation >= 5.0:
        reasons.append(f"Transaction amount (₹{amount:,.0f}) is {amount_deviation}× the customer's historical average (₹{avg_amt:,.0f}).")
        amt_impact = "CRITICAL" if amount_deviation >= 10.0 else "HIGH"
        amt_score = min(35.0, amount_deviation * 2.5)
    elif amount_deviation >= 2.5:
        reasons.append(f"Transaction amount is {amount_deviation}× higher than typical spending baseline.")
        amt_impact = "MEDIUM"
        amt_score = 15.0
    else:
        amt_impact = "LOW"
        amt_score = 2.0
    factor_contributions.append({
        "factor": "Amount Deviation",
        "impact": amt_impact,
        "scoreContribution": round(amt_score, 1),
        "description": f"{amount_deviation}× customer average"
    })
    
    # 2. Velocity Factor
    if velocity > 5:
        reasons.append(f"High velocity anomaly: {velocity} transactions attempted within the last 10 minutes.")
        vel_impact = "HIGH"
        vel_score = min(25.0, velocity * 3.0)
    elif velocity >= 3:
        reasons.append(f"Elevated transaction frequency: {velocity} transactions in the last 10 minutes.")
        vel_impact = "MEDIUM"
        vel_score = 12.0
    else:
        vel_impact = "LOW"
        vel_score = 1.0
    factor_contributions.append({
        "factor": "Velocity (10m)",
        "impact": vel_impact,
        "scoreContribution": round(vel_score, 1),
        "description": f"{velocity} txns in 10 mins"
    })
    
    # 3. Device Factor
    if new_device:
        reasons.append("New/unrecognized device fingerprint detected for this cardholder.")
        dev_impact = "HIGH" if (amount > 50000 or velocity > 3) else "MEDIUM"
        dev_score = 20.0
    else:
        dev_impact = "LOW"
        dev_score = 0.0
    factor_contributions.append({
        "factor": "Device Novelty",
        "impact": dev_impact,
        "scoreContribution": round(dev_score, 1),
        "description": "Unrecognized device" if new_device else "Known trusted device"
    })
    
    # 4. Location Factor
    if new_location:
        reasons.append("Unusual transaction geographic location outside regular cardholder perimeter.")
        loc_impact = "MEDIUM"
        loc_score = 15.0
    else:
        loc_impact = "LOW"
        loc_score = 0.0
    factor_contributions.append({
        "factor": "Location Novelty",
        "impact": loc_impact,
        "scoreContribution": round(loc_score, 1),
        "description": "Unfamiliar location" if new_location else "Familiar location"
    })
    
    # 5. Merchant Risk Factor
    if merchant_risk == "HIGH":
        reasons.append("High-risk merchant terminal category (frequent target for fraudulent chargebacks).")
        merch_impact = "HIGH"
        merch_score = 15.0
    elif merchant_risk == "MEDIUM":
        reasons.append("Merchant operates in a moderately sensitive commercial sector.")
        merch_impact = "MEDIUM"
        merch_score = 8.0
    else:
        merch_impact = "LOW"
        merch_score = 0.0
    factor_contributions.append({
        "factor": "Merchant Risk",
        "impact": merch_impact,
        "scoreContribution": round(merch_score, 1),
        "description": f"{merchant_risk} risk category"
    })
    
    # 6. Time of Day (Off-hours / night drain)
    if hour in [1, 2, 3, 4] and (amount_deviation > 3.0 or new_device):
        reasons.append(f"Off-hours nocturnal activity ({hour}:00 AM) combined with elevated amount.")
        factor_contributions.append({
            "factor": "Time Anomaly",
            "impact": "MEDIUM",
            "scoreContribution": 10.0,
            "description": f"Nocturnal hour ({hour}:00 AM)"
        })
        
    # If no reasons were triggered (legitimate transaction)
    if not reasons:
        reasons.append("Transaction conforms to cardholder historical spending patterns and trusted credentials.")
        reasons.append("Device and geographic location are recognized and consistent.")
        reasons.append("Transaction velocity is within normal baseline parameters.")
        
    return reasons, factor_contributions
