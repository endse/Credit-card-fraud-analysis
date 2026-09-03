import React from 'react';
import { CreditCard, AlertTriangle, ShieldX, Eye, CheckCircle2, Gauge } from 'lucide-react';

export default function MetricCards({ stats }) {
  const {
    totalTransactions = 0,
    fraudDetected = 0,
    blocked = 0,
    underReview = 0,
    approved = 0,
    fraudRatePercentage = 0,
    averageRiskScore = 0
  } = stats || {};

  return (
    <div className="kpi-grid">
      {/* Total Transactions */}
      <div className="glass-panel kpi-card kpi-total">
        <div className="kpi-header">
          <span className="kpi-title">Total Analyzed</span>
          <div className="kpi-icon">
            <CreditCard size={18} color="#38bdf8" />
          </div>
        </div>
        <div className="kpi-value">{totalTransactions.toLocaleString()}</div>
        <div className="kpi-sub">Transactions processed</div>
      </div>

      {/* Fraud Detected */}
      <div className="glass-panel kpi-card kpi-fraud">
        <div className="kpi-header">
          <span className="kpi-title">Fraud Detected</span>
          <div className="kpi-icon">
            <AlertTriangle size={18} color="#fb923c" />
          </div>
        </div>
        <div className="kpi-value" style={{ color: '#fb923c' }}>{fraudDetected.toLocaleString()}</div>
        <div className="kpi-sub">{fraudRatePercentage}% suspicious rate</div>
      </div>

      {/* Blocked */}
      <div className="glass-panel kpi-card kpi-blocked">
        <div className="kpi-header">
          <span className="kpi-title">Blocked (Critical)</span>
          <div className="kpi-icon">
            <ShieldX size={18} color="#f43f5e" />
          </div>
        </div>
        <div className="kpi-value" style={{ color: '#f43f5e' }}>{blocked.toLocaleString()}</div>
        <div className="kpi-sub">Score ≥ 70 (Immediate drop)</div>
      </div>

      {/* Under Review */}
      <div className="glass-panel kpi-card kpi-review">
        <div className="kpi-header">
          <span className="kpi-title">Under Review</span>
          <div className="kpi-icon">
            <Eye size={18} color="#f59e0b" />
          </div>
        </div>
        <div className="kpi-value" style={{ color: '#f59e0b' }}>{underReview.toLocaleString()}</div>
        <div className="kpi-sub">Score 30–69 (Step-up auth)</div>
      </div>

      {/* Approved */}
      <div className="glass-panel kpi-card kpi-approved">
        <div className="kpi-header">
          <span className="kpi-title">Approved (Safe)</span>
          <div className="kpi-icon">
            <CheckCircle2 size={18} color="#10b981" />
          </div>
        </div>
        <div className="kpi-value" style={{ color: '#10b981' }}>{approved.toLocaleString()}</div>
        <div className="kpi-sub">Score 0–29 (Instant pass)</div>
      </div>

      {/* Average Risk Score */}
      <div className="glass-panel kpi-card">
        <div className="kpi-header">
          <span className="kpi-title">Avg Risk Score</span>
          <div className="kpi-icon">
            <Gauge size={18} color="#a855f7" />
          </div>
        </div>
        <div className="kpi-value">{averageRiskScore} <span style={{ fontSize: '1rem', color: '#64748b' }}>/100</span></div>
        <div className="kpi-sub">Portfolio risk baseline</div>
      </div>
    </div>
  );
}
