"""
Synthetic Transaction Dataset Generator
Generates high-fidelity credit card transaction dataset with realistic statistical
distributions and fraud patterns as specified in PRD Section 7, 8, 22, and 23.
"""
import os
import random
import numpy as np
import pandas as pd

np.random.seed(42)
random.seed(42)

def generate_dataset(num_records: int = 20000, output_path: str = "backend/ml/data/credit_card_transactions.csv") -> pd.DataFrame:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fraud_ratio = 0.04  # 4% fraud rate for realistic class imbalance
    num_fraud = int(num_records * fraud_ratio)
    num_legit = num_records - num_fraud
    
    records = []
    
    # 1. Generate Legitimate Transactions (96%)
    for _ in range(num_legit):
        avg_amt = float(np.random.choice([1500, 2000, 2500, 3000, 4500, 6000, 8000, 12000]))
        # Borderline / suspicious transaction profile (mixed legit and fraud)
        # E.g., customer traveling, buying new gadget on a new phone with moderate velocity
        is_suspicious_profile = (random.random() < 0.12)
        if is_suspicious_profile:
            amount = avg_amt * random.uniform(3.5, 6.0)
            velocity_10m = random.choice([3, 4, 5])
            new_device = int(np.random.choice([0, 1], p=[0.3, 0.7]))
            new_location = int(np.random.choice([0, 1], p=[0.6, 0.4]))
            merchant_risk = int(np.random.choice([0, 1, 2], p=[0.2, 0.6, 0.2]))
        else:
            amount = max(50.0, float(np.random.lognormal(mean=np.log(avg_amt), sigma=0.40)))
            if amount > 2.5 * avg_amt:
                amount = avg_amt * random.uniform(0.6, 1.8)
            velocity_10m = int(np.random.choice([0, 1, 2], p=[0.85, 0.13, 0.02]))
            new_device = int(np.random.choice([0, 1], p=[0.97, 0.03]))
            new_location = int(np.random.choice([0, 1], p=[0.98, 0.02]))
            merchant_risk = int(np.random.choice([0, 1, 2], p=[0.85, 0.13, 0.02]))
            
        amount_deviation = round(amount / avg_amt, 2)
        hour_probs = np.array([
            0.01, 0.005, 0.005, 0.005, 0.005, 0.01, 0.02, 0.04, 0.06, 0.07,
            0.08, 0.08, 0.08, 0.07, 0.07, 0.07, 0.07, 0.08, 0.08, 0.07,
            0.04, 0.03, 0.02, 0.01
        ])
        hour_probs = hour_probs / hour_probs.sum()
        hour = int(np.random.choice(range(24), p=hour_probs))
        day = random.randint(1, 28)
        frequency_monthly = random.randint(5, 50)
        
        records.append({
            "amount": round(amount, 2),
            "average_transaction_amount": round(avg_amt, 2),
            "amount_deviation": amount_deviation,
            "transaction_hour": hour,
            "transaction_day": day,
            "transactions_last_10_minutes": velocity_10m,
            "transaction_frequency": frequency_monthly,
            "is_new_device": new_device,
            "is_new_location": new_location,
            "merchant_risk": merchant_risk,
            "is_fraud": 0
        })
        
    # 2. Generate Fraudulent Transactions (4%)
    fraud_patterns = ["velocity_attack", "night_drain", "device_takeover", "high_amount_surge", "moderate_anomaly"]
    for _ in range(num_fraud):
        pattern = random.choice(fraud_patterns)
        avg_amt = float(np.random.choice([1500, 2000, 2500, 3000, 4000]))
        
        if pattern == "moderate_anomaly":
            # Suspicious borderline fraud
            amount = avg_amt * random.uniform(4.0, 6.0)
            velocity_10m = random.choice([3, 4, 5])
            hour = random.randint(8, 22)
            new_device = 1
            new_location = int(np.random.choice([0, 1], p=[0.7, 0.3]))
            merchant_risk = int(np.random.choice([1, 2], p=[0.7, 0.3]))
        elif pattern == "velocity_attack":
            # Rapid-fire card testing or drain
            amount = avg_amt * random.uniform(2.5, 8.0)
            velocity_10m = random.randint(5, 12)
            hour = random.randint(0, 23)
            new_device = int(np.random.choice([0, 1], p=[0.3, 0.7]))
            new_location = int(np.random.choice([0, 1], p=[0.4, 0.6]))
            merchant_risk = int(np.random.choice([1, 2], p=[0.4, 0.6]))
            
        elif pattern == "night_drain":
            # Late night (1 AM - 4 AM) large amount transaction
            amount = avg_amt * random.uniform(8.0, 35.0)
            velocity_10m = random.randint(3, 8)
            hour = random.choice([1, 2, 3, 4])
            new_device = 1
            new_location = 1
            merchant_risk = 2
            
        elif pattern == "device_takeover":
            # Account takeover from new device & new location
            amount = avg_amt * random.uniform(6.0, 25.0)
            velocity_10m = random.randint(4, 9)
            hour = random.choice([0, 1, 2, 3, 22, 23])
            new_device = 1
            new_location = 1
            merchant_risk = int(np.random.choice([1, 2], p=[0.3, 0.7]))
            
        else: # "high_amount_surge"
            amount = avg_amt * random.uniform(10.0, 40.0)
            velocity_10m = random.randint(2, 6)
            hour = random.randint(0, 23)
            new_device = int(np.random.choice([0, 1], p=[0.2, 0.8]))
            new_location = int(np.random.choice([0, 1], p=[0.3, 0.7]))
            merchant_risk = int(np.random.choice([0, 1, 2], p=[0.1, 0.4, 0.5]))
            
        amount_deviation = round(amount / avg_amt, 2)
        records.append({
            "amount": round(amount, 2),
            "average_transaction_amount": round(avg_amt, 2),
            "amount_deviation": amount_deviation,
            "transaction_hour": hour,
            "transaction_day": random.randint(1, 28),
            "transactions_last_10_minutes": velocity_10m,
            "transaction_frequency": random.randint(5, 50),
            "is_new_device": new_device,
            "is_new_location": new_location,
            "merchant_risk": merchant_risk,
            "is_fraud": 1
        })
        
    df = pd.DataFrame(records)
    # Shuffle the dataset thoroughly
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} transactions ({df['is_fraud'].sum()} fraudulent, {(df['is_fraud']==0).sum()} legitimate)")
    print(f"Saved to: {output_path}")
    return df

if __name__ == "__main__":
    generate_dataset()
