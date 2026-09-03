"""
Automated backend verification test
Tests endpoints and validates Scenarios A, B, and C against PRD expectations.
"""
import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Set working directory to project root
sys.path.insert(0, os.path.abspath("."))

from backend.app.database import init_db, get_connection
from backend.app.seed_data import seed_database_if_empty
from backend.app.risk_engine import calculate_risk

def run_tests():
    print("=== 1. Initializing Database and Seeding ===")
    init_db()
    seed_database_if_empty()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"Total seeded transactions in DB: {count}")
    assert count >= 45, f"Expected >= 45 transactions, got {count}"
    
    print("\n=== 2. Testing Scenario A (Legitimate) ===")
    # Scenario A:
    # Amount: 1,200, Avg: 2,000, Txn/10m: 1, New Device: No, New Location: No, Merchant: LOW
    scenario_a = {
        "cardId": "CARD001",
        "amount": 1200.0,
        "merchant": "Amazon Retail",
        "merchantRisk": "LOW",
        "transactionHour": 14,
        "transactionsLast10Minutes": 1,
        "averageTransactionAmount": 2000.0,
        "newDevice": False,
        "newLocation": False
    }
    res_a = calculate_risk(scenario_a)
    print(f"Scenario A -> Risk Score: {res_a['riskScore']}, Level: {res_a['riskLevel']}, Decision: {res_a['decision']}")
    assert res_a["decision"] == "APPROVE", f"Expected APPROVE, got {res_a['decision']}"
    assert res_a["riskLevel"] == "LOW", f"Expected LOW, got {res_a['riskLevel']}"
    print("Scenario A PASSED!")
    
    print("\n=== 3. Testing Scenario B (Suspicious) ===")
    # Scenario B:
    # Amount: 15,000, Avg: 3,000, Txn/10m: 4, New Device: Yes, New Location: No, Merchant: MEDIUM
    scenario_b = {
        "cardId": "CARD002",
        "amount": 15000.0,
        "merchant": "BestBuy Gadgets",
        "merchantRisk": "MEDIUM",
        "transactionHour": 15,
        "transactionsLast10Minutes": 4,
        "averageTransactionAmount": 3000.0,
        "newDevice": True,
        "newLocation": False
    }
    res_b = calculate_risk(scenario_b)
    print(f"Scenario B -> Risk Score: {res_b['riskScore']}, Level: {res_b['riskLevel']}, Decision: {res_b['decision']}")
    assert res_b["decision"] == "REVIEW", f"Expected REVIEW, got {res_b['decision']}"
    print("Scenario B PASSED!")
    
    print("\n=== 4. Testing Scenario C (Fraudulent) ===")
    # Scenario C:
    # Amount: 75,000, Avg: 2,500, Txn/10m: 8, New Device: Yes, New Location: Yes, Merchant: HIGH, Hour: 3 AM
    scenario_c = {
        "cardId": "CARD003",
        "amount": 75000.0,
        "merchant": "Crypto Gateway X",
        "merchantRisk": "HIGH",
        "transactionHour": 3,
        "transactionsLast10Minutes": 8,
        "averageTransactionAmount": 2500.0,
        "newDevice": True,
        "newLocation": True
    }
    res_c = calculate_risk(scenario_c)
    print(f"Scenario C -> Risk Score: {res_c['riskScore']}, Level: {res_c['riskLevel']}, Decision: {res_c['decision']}")
    print("Reasons:", res_c["reasons"])
    assert res_c["decision"] == "BLOCK", f"Expected BLOCK, got {res_c['decision']}"
    assert res_c["riskLevel"] == "CRITICAL", f"Expected CRITICAL, got {res_c['riskLevel']}"
    assert len(res_c["reasons"]) >= 3, f"Expected >= 3 reasons, got {len(res_c['reasons'])}"
    print("Scenario C PASSED!")
    
    print("\nALL BACKEND CORE LOGIC TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
