"""
FastAPI Main Application
Unified REST API providing transaction analysis, ML prediction, stats, and history.
"""
import os
import json
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    TransactionAnalyzeRequest, TransactionAnalyzeResponse,
    PredictRequest, PredictResponse,
    TransactionRecord, DashboardStats
)
from .database import init_db, save_transaction, get_transactions, get_dashboard_stats
from .seed_data import seed_database_if_empty
from .risk_engine import calculate_risk
from ..ml.predict import predict_fraud_probability

METRICS_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "artifacts", "model_metrics.json")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing Database...")
    init_db()
    seed_database_if_empty()
    yield
    # Shutdown
    print("Shutting down API...")

app = FastAPI(
    title="Credit Card Fraud Detection API",
    description="Real-time transaction fraud analysis with hybrid ML and rule scoring.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "fraud-detection-api"}

@app.post("/predict", response_model=PredictResponse)
def predict_endpoint(req: PredictRequest):
    """
    Pure ML inference endpoint as defined in PRD Section 17.
    """
    try:
        prob = predict_fraud_probability(req.features)
        return {"fraudProbability": prob}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transactions/analyze", response_model=TransactionAnalyzeResponse)
def analyze_transaction(req: TransactionAnalyzeRequest):
    """
    Primary transaction analysis endpoint as defined in PRD Section 16.
    Evaluates ML fraud probability, business rules, hybrid risk score,
    explainability reasons, and persists record to SQLite.
    """
    try:
        data = req.model_dump()
        analysis = calculate_risk(data)
        
        # Save to database
        saved_id = save_transaction(data, analysis)
        
        from datetime import datetime
        return {
            "id": saved_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cardId": req.cardId,
            "amount": req.amount,
            "merchant": req.merchant,
            "merchantRisk": req.merchantRisk,
            "fraudProbability": analysis["fraudProbability"],
            "mlScore": analysis["mlScore"],
            "ruleScore": analysis["ruleScore"],
            "riskScore": analysis["riskScore"],
            "riskLevel": analysis["riskLevel"],
            "decision": analysis["decision"],
            "reasons": analysis["reasons"],
            "factorContributions": analysis["factorContributions"],
            "triggeredRules": analysis["triggeredRules"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/transactions")
def list_transactions(limit: int = Query(default=100, ge=1, le=500)):
    """
    Retrieves recent transaction history sorted newest first.
    """
    return get_transactions(limit=limit)

@app.get("/api/stats", response_model=DashboardStats)
def get_stats():
    """
    Retrieves aggregated dashboard metrics.
    """
    return get_dashboard_stats()

@app.get("/api/model/metrics")
def get_model_metrics():
    """
    Returns candidate vs baseline ML evaluation metrics.
    """
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r") as f:
            return json.load(f)
    return {"error": "Model metrics not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
