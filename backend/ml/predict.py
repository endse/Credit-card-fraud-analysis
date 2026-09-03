"""
ML Inference Service Module
Loads the serialized fraud detection model and performs feature extraction and inference.
"""
import os
import joblib
import pandas as pd
from typing import Dict, Any

MODEL_PATH = os.path.join(os.path.dirname(__file__), "artifacts", "fraud_model.pkl")

_model = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Run train.py first.")
        _model = joblib.load(MODEL_PATH)
    return _model

def map_merchant_risk(risk_str: str) -> int:
    risk_upper = str(risk_str).strip().upper()
    if risk_upper == "HIGH":
        return 2
    elif risk_upper == "MEDIUM":
        return 1
    return 0

def predict_fraud_probability(features: Dict[str, Any]) -> float:
    """
    Accepts raw or structured transaction feature dictionary,
    extracts model inputs, and returns fraud probability between 0.0 and 1.0.
    """
    model = get_model()
    
    amount = float(features.get("amount", 0.0))
    avg_amt = float(features.get("averageTransactionAmount", features.get("average_transaction_amount", 2000.0)))
    if avg_amt <= 0:
        avg_amt = 2000.0
    amount_deviation = round(amount / avg_amt, 2)
    
    hour = int(features.get("transactionHour", features.get("transaction_hour", 12)))
    day = int(features.get("transactionDay", features.get("transaction_day", 15)))
    velocity_10m = int(features.get("transactionsLast10Minutes", features.get("transactions_last_10_minutes", 1)))
    frequency = int(features.get("transactionFrequency", features.get("transaction_frequency", 10)))
    
    new_device = 1 if features.get("newDevice", features.get("is_new_device", False)) else 0
    new_location = 1 if features.get("newLocation", features.get("is_new_location", False)) else 0
    
    m_risk = features.get("merchantRisk", features.get("merchant_risk", "LOW"))
    if isinstance(m_risk, str):
        merchant_risk_code = map_merchant_risk(m_risk)
    else:
        merchant_risk_code = int(m_risk)
        
    df_input = pd.DataFrame([{
        "amount": amount,
        "average_transaction_amount": avg_amt,
        "amount_deviation": amount_deviation,
        "transaction_hour": hour,
        "transaction_day": day,
        "transactions_last_10_minutes": velocity_10m,
        "transaction_frequency": frequency,
        "is_new_device": new_device,
        "is_new_location": new_location,
        "merchant_risk": merchant_risk_code
    }])
    
    proba = float(model.predict_proba(df_input)[0][1])
    return round(proba, 4)
