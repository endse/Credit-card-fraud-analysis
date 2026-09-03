"""
Seed Data Generator
Pre-populates the database with 45 realistic historical transactions
so that dashboard charts and tables are immediately engaging on startup.
"""
import random
from datetime import datetime, timedelta
from .database import get_connection, save_transaction
from .risk_engine import calculate_risk

MERCHANTS = [
    ("Amazon Retail", "LOW"),
    ("Uber Mobility", "LOW"),
    ("Starbucks Coffee", "LOW"),
    ("Netflix Subscription", "LOW"),
    ("Apple App Store", "LOW"),
    ("Target Superstore", "LOW"),
    ("Flipkart Electronics", "MEDIUM"),
    ("BestBuy Gadgets", "MEDIUM"),
    ("Steam Video Games", "MEDIUM"),
    ("Airbnb Booking", "MEDIUM"),
    ("Luxury Watch Boutique", "HIGH"),
    ("Crypto Gateway X", "HIGH"),
    ("Overseas Diamond Emporium", "HIGH"),
    ("Fast Cash Advance", "HIGH")
]

CARDS = [f"CARD{str(i).zfill(3)}" for i in range(1, 16)]

def seed_database_if_empty():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count > 0:
        return
        
    print("Seeding initial 45 transactions...")
    now = datetime.now()
    
    # 45 historical transactions over the past 24 hours
    for i in range(45, 0, -1):
        ts = now - timedelta(minutes=i * 28 + random.randint(1, 10))
        card = random.choice(CARDS)
        
        # 75% legitimate, 15% suspicious, 10% fraudulent
        roll = random.random()
        if roll < 0.75:
            # Legitimate
            avg_amt = random.choice([1200, 1800, 2400, 3200, 4500])
            amt = round(avg_amt * random.uniform(0.3, 1.8), 2)
            merchant, risk = random.choice(MERCHANTS[:8])
            data = {
                "cardId": card,
                "amount": amt,
                "merchant": merchant,
                "merchantRisk": risk,
                "transactionHour": ts.hour,
                "transactionsLast10Minutes": random.choice([0, 1, 1, 2]),
                "averageTransactionAmount": avg_amt,
                "newDevice": False,
                "newLocation": False
            }
        elif roll < 0.90:
            # Suspicious
            avg_amt = random.choice([2000, 3000, 4000])
            amt = round(avg_amt * random.uniform(3.5, 5.5), 2)
            merchant, risk = random.choice(MERCHANTS[6:10])
            data = {
                "cardId": card,
                "amount": amt,
                "merchant": merchant,
                "merchantRisk": risk,
                "transactionHour": ts.hour,
                "transactionsLast10Minutes": random.choice([3, 4]),
                "averageTransactionAmount": avg_amt,
                "newDevice": True,
                "newLocation": False
            }
        else:
            # Fraudulent
            avg_amt = random.choice([1500, 2500])
            amt = round(avg_amt * random.uniform(12.0, 35.0), 2)
            merchant, risk = random.choice(MERCHANTS[10:])
            data = {
                "cardId": card,
                "amount": amt,
                "merchant": merchant,
                "merchantRisk": risk,
                "transactionHour": random.choice([1, 2, 3, 4, 23]),
                "transactionsLast10Minutes": random.randint(5, 9),
                "averageTransactionAmount": avg_amt,
                "newDevice": True,
                "newLocation": True
            }
            
        analysis = calculate_risk(data)
        
        # Override timestamp to preserve chronological timeline
        conn = get_connection()
        cursor = conn.cursor()
        import json
        cursor.execute("""
        INSERT INTO transactions (
            timestamp, card_id, amount, merchant, merchant_risk,
            transaction_hour, transactions_last_10_minutes, average_transaction_amount,
            new_device, new_location, fraud_probability, ml_score, rule_score,
            risk_score, risk_level, decision, reasons, factor_contributions, triggered_rules
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ts.strftime("%Y-%m-%d %H:%M:%S"),
            data["cardId"],
            data["amount"],
            data["merchant"],
            data["merchantRisk"],
            data["transactionHour"],
            data["transactionsLast10Minutes"],
            data["averageTransactionAmount"],
            1 if data["newDevice"] else 0,
            1 if data["newLocation"] else 0,
            analysis["fraudProbability"],
            analysis["mlScore"],
            analysis["ruleScore"],
            analysis["riskScore"],
            analysis["riskLevel"],
            analysis["decision"],
            json.dumps(analysis["reasons"]),
            json.dumps(analysis["factorContributions"]),
            json.dumps(analysis["triggeredRules"])
        ))
        conn.commit()
        conn.close()
        
    print("Seeding completed successfully.")
