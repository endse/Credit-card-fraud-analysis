"""
Pydantic Schemas for Request & Response validation
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    features: Dict[str, Any]

class PredictResponse(BaseModel):
    fraudProbability: float

class TransactionAnalyzeRequest(BaseModel):
    cardId: str = Field(default="CARD001", description="Card or Account identifier")
    amount: float = Field(..., gt=0, description="Transaction amount")
    merchant: str = Field(default="Online Merchant", description="Merchant name")
    merchantRisk: str = Field(default="LOW", description="LOW, MEDIUM, or HIGH")
    transactionHour: int = Field(default=12, ge=0, le=23, description="Hour of day (0-23)")
    transactionsLast10Minutes: int = Field(default=1, ge=0, description="Recent transaction velocity")
    averageTransactionAmount: float = Field(default=2500.0, gt=0, description="Customer average transaction amount")
    newDevice: bool = Field(default=False, description="Whether transaction came from new device")
    newLocation: bool = Field(default=False, description="Whether transaction originated from new location")

class RiskFactorContribution(BaseModel):
    factor: str
    impact: str  # e.g., "HIGH", "MEDIUM", "LOW", "NEUTRAL"
    scoreContribution: float
    description: str

class TransactionAnalyzeResponse(BaseModel):
    id: Optional[int] = None
    timestamp: str
    cardId: str
    amount: float
    merchant: str
    merchantRisk: str
    fraudProbability: float
    mlScore: float
    ruleScore: float
    riskScore: int
    riskLevel: str  # LOW, MEDIUM, HIGH, CRITICAL
    decision: str   # APPROVE, REVIEW, BLOCK
    reasons: List[str]
    factorContributions: List[RiskFactorContribution]
    triggeredRules: List[Dict[str, Any]]

class TransactionRecord(BaseModel):
    id: int
    timestamp: str
    cardId: str
    amount: float
    merchant: str
    merchantRisk: str
    fraudProbability: float
    riskScore: int
    riskLevel: str
    decision: str
    reasons: List[str]
    newDevice: bool
    newLocation: bool
    transactionsLast10Minutes: int
    averageTransactionAmount: float

class DashboardStats(BaseModel):
    totalTransactions: int
    fraudDetected: int
    blocked: int
    underReview: int
    approved: int
    fraudRatePercentage: float
    averageRiskScore: float
