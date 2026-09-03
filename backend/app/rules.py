"""
Rule Engine Module
Implements deterministic secondary rule checks as defined in PRD Section 13.
"""
from typing import Dict, Any, List, Tuple

def evaluate_rules(data: Dict[str, Any]) -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Evaluates business rules against incoming transaction.
    Returns:
      - total_rule_points (int)
      - max_rule_points (int = 70)
      - triggered_rules (List of dicts with rule id, name, points, and description)
    """
    amount = float(data.get("amount", 0.0))
    avg_amount = float(data.get("averageTransactionAmount", data.get("average_transaction_amount", 2500.0)))
    if avg_amount <= 0:
        avg_amount = 2500.0
        
    new_device = bool(data.get("newDevice", data.get("is_new_device", False)))
    new_location = bool(data.get("newLocation", data.get("is_new_location", False)))
    velocity_10m = int(data.get("transactionsLast10Minutes", data.get("transactions_last_10_minutes", 1)))
    merchant_risk = str(data.get("merchantRisk", data.get("merchant_risk", "LOW"))).strip().upper()
    
    triggered_rules = []
    points = 0
    max_possible = 70
    
    # Rule 1 — Large Transaction
    # IF amount > 5 × average_transaction_amount THEN risk + 15
    if amount > (5 * avg_amount):
        multiplier = round(amount / avg_amount, 1)
        triggered_rules.append({
            "id": "RULE_1_LARGE_AMOUNT",
            "name": "Large Transaction",
            "points": 15,
            "description": f"Transaction amount (₹{amount:,.0f}) is {multiplier}x the customer's average (₹{avg_amount:,.0f})."
        })
        points += 15
        
    # Rule 2 — New Device + High Amount
    # IF new_device = true AND amount > 50000 THEN risk + 15
    if new_device and amount > 50000:
        triggered_rules.append({
            "id": "RULE_2_NEW_DEVICE_HIGH_VALUE",
            "name": "High-Value Transaction on New Device",
            "points": 15,
            "description": f"Unrecognized device executing transaction exceeding ₹50,000 threshold."
        })
        points += 15
        
    # Rule 3 — Transaction Velocity
    # IF transactions_last_10_minutes > 5 THEN risk + 20
    if velocity_10m > 5:
        triggered_rules.append({
            "id": "RULE_3_HIGH_VELOCITY",
            "name": "Rapid Transaction Velocity",
            "points": 20,
            "description": f"{velocity_10m} transactions detected in the last 10 minutes (velocity threshold > 5)."
        })
        points += 20
        
    # Rule 4 — New Location
    # IF new_location = true THEN risk + 10
    if new_location:
        triggered_rules.append({
            "id": "RULE_4_NEW_LOCATION",
            "name": "Unusual Location",
            "points": 10,
            "description": "Transaction originated from a previously unseen geographic location or IP zone."
        })
        points += 10
        
    # Rule 5 — High-Risk Merchant
    # IF merchant_risk = HIGH THEN risk + 10
    if merchant_risk == "HIGH":
        triggered_rules.append({
            "id": "RULE_5_HIGH_RISK_MERCHANT",
            "name": "High-Risk Merchant Category",
            "points": 10,
            "description": "Merchant is classified in a high-risk sector (e.g., luxury goods, cryptocurrency, gaming)."
        })
        points += 10
        
    return points, max_possible, triggered_rules
