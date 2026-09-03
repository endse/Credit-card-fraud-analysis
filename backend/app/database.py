"""
SQLite Database Layer
Stores transaction analyses and provides query helpers for history and dashboard metrics.
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "transactions.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        card_id TEXT NOT NULL,
        amount REAL NOT NULL,
        merchant TEXT NOT NULL,
        merchant_risk TEXT NOT NULL,
        transaction_hour INTEGER NOT NULL,
        transactions_last_10_minutes INTEGER NOT NULL,
        average_transaction_amount REAL NOT NULL,
        new_device INTEGER NOT NULL,
        new_location INTEGER NOT NULL,
        fraud_probability REAL NOT NULL,
        ml_score REAL NOT NULL,
        rule_score REAL NOT NULL,
        risk_score INTEGER NOT NULL,
        risk_level TEXT NOT NULL,
        decision TEXT NOT NULL,
        reasons TEXT NOT NULL,
        factor_contributions TEXT NOT NULL,
        triggered_rules TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def save_transaction(data: Dict[str, Any], analysis: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
    INSERT INTO transactions (
        timestamp, card_id, amount, merchant, merchant_risk,
        transaction_hour, transactions_last_10_minutes, average_transaction_amount,
        new_device, new_location, fraud_probability, ml_score, rule_score,
        risk_score, risk_level, decision, reasons, factor_contributions, triggered_rules
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ts,
        data.get("cardId", "CARD001"),
        float(data.get("amount", 0.0)),
        data.get("merchant", "Online Store"),
        str(data.get("merchantRisk", "LOW")).upper(),
        int(data.get("transactionHour", 12)),
        int(data.get("transactionsLast10Minutes", 1)),
        float(data.get("averageTransactionAmount", 2500.0)),
        1 if data.get("newDevice", False) else 0,
        1 if data.get("newLocation", False) else 0,
        float(analysis.get("fraudProbability", 0.0)),
        float(analysis.get("mlScore", 0.0)),
        float(analysis.get("ruleScore", 0.0)),
        int(analysis.get("riskScore", 0)),
        analysis.get("riskLevel", "LOW"),
        analysis.get("decision", "APPROVE"),
        json.dumps(analysis.get("reasons", [])),
        json.dumps(analysis.get("factorContributions", [])),
        json.dumps(analysis.get("triggeredRules", []))
    ))
    
    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inserted_id

def get_transactions(limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM transactions
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "cardId": r["card_id"],
            "amount": r["amount"],
            "merchant": r["merchant"],
            "merchantRisk": r["merchant_risk"],
            "transactionHour": r["transaction_hour"],
            "transactionsLast10Minutes": r["transactions_last_10_minutes"],
            "averageTransactionAmount": r["average_transaction_amount"],
            "newDevice": bool(r["new_device"]),
            "newLocation": bool(r["new_location"]),
            "fraudProbability": r["fraud_probability"],
            "mlScore": r["ml_score"],
            "ruleScore": r["rule_score"],
            "riskScore": r["risk_score"],
            "riskLevel": r["risk_level"],
            "decision": r["decision"],
            "reasons": json.loads(r["reasons"]) if r["reasons"] else [],
            "factorContributions": json.loads(r["factor_contributions"]) if r["factor_contributions"] else [],
            "triggeredRules": json.loads(r["triggered_rules"]) if r["triggered_rules"] else []
        })
    return results

def get_dashboard_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM transactions")
    total = cursor.fetchone()[0]
    
    if total == 0:
        conn.close()
        return {
            "totalTransactions": 0,
            "fraudDetected": 0,
            "blocked": 0,
            "underReview": 0,
            "approved": 0,
            "fraudRatePercentage": 0.0,
            "averageRiskScore": 0.0
        }
        
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE decision = 'BLOCK'")
    blocked = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE decision = 'REVIEW'")
    review = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE decision = 'APPROVE'")
    approved = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(risk_score) FROM transactions")
    avg_risk = cursor.fetchone()[0] or 0.0
    
    conn.close()
    
    fraud_detected = blocked + review
    fraud_rate = round((fraud_detected / total) * 100.0, 1)
    
    return {
        "totalTransactions": total,
        "fraudDetected": fraud_detected,
        "blocked": blocked,
        "underReview": review,
        "approved": approved,
        "fraudRatePercentage": fraud_rate,
        "averageRiskScore": round(avg_risk, 1)
    }
