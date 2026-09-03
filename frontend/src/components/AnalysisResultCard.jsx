import React from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  HelpCircle, 
  Layers, 
  CheckCircle2, 
  XCircle,
  Activity
} from 'lucide-react';

export default function AnalysisResultCard({ result, isLoading }) {
  if (isLoading) {
    return (
      <div className="glass-panel result-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '440px' }}>
        <div style={{ textAlign: 'center' }}>
          <Activity size={42} color="#38bdf8" className="spin-icon" style={{ margin: '0 auto 16px auto' }} />
          <h3 style={{ fontFamily: 'Outfit', fontSize: '1.25rem', marginBottom: '8px' }}>Evaluating Transaction...</h3>
          <p style={{ color: '#94a3b8', fontSize: '0.88rem' }}>
            Extracting behavioral features → Running XGBoost model → Evaluating hybrid rule engine
          </p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="glass-panel result-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '440px' }}>
        <div style={{ textAlign: 'center', maxWidth: '320px' }}>
          <div style={{ width: '56px', height: '56px', borderRadius: '50%', background: 'rgba(255, 255, 255, 0.04)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px auto' }}>
            <Layers size={28} color="#64748b" />
          </div>
          <h3 style={{ fontFamily: 'Outfit', fontSize: '1.15rem', color: '#cbd5e1', marginBottom: '8px' }}>Ready for Inference</h3>
          <p style={{ color: '#64748b', fontSize: '0.84rem' }}>
            Select a demo scenario or configure transaction attributes, then click <strong>Analyze Transaction</strong> to see real-time AI classification and explainability.
          </p>
        </div>
      </div>
    );
  }

  const {
    fraudProbability = 0,
    mlScore = 0,
    ruleScore = 0,
    riskScore = 0,
    riskLevel = 'LOW',
    decision = 'APPROVE',
    reasons = [],
    factorContributions = [],
    triggeredRules = []
  } = result;

  const decisionClass = decision.toLowerCase();
  const probPercent = Math.round(fraudProbability * 100);

  return (
    <div className={`glass-panel result-card ${decisionClass}`}>
      <div>
        {/* Header */}
        <div className="section-header" style={{ marginBottom: '16px' }}>
          <div className="section-title">
            <ShieldAlert size={20} color={decision === 'BLOCK' ? '#f43f5e' : decision === 'REVIEW' ? '#f59e0b' : '#10b981'} />
            <span>Fraud Risk Evaluation</span>
          </div>
          <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Real-Time Inference Result</span>
        </div>

        {/* Big Decision Banner */}
        <div className={`decision-banner ${decisionClass}`}>
          <div className="decision-text">
            <span className="decision-badge-title">AI Engine Decision</span>
            <div className="decision-value">
              {decision === 'APPROVE' && <CheckCircle2 size={28} />}
              {decision === 'REVIEW' && <AlertTriangle size={28} />}
              {decision === 'BLOCK' && <XCircle size={28} />}
              <span>{decision}</span>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600, color: '#94a3b8' }}>Risk Level</span>
            <div style={{ fontFamily: 'Outfit', fontSize: '1.3rem', fontWeight: 800 }}>{riskLevel}</div>
          </div>
        </div>

        {/* 3-Part Metric Breakdown (PRD Section 11, 14) */}
        <div className="score-cluster">
          <div className="score-box">
            <div className="score-box-label">Risk Score</div>
            <div className="score-box-val" style={{ 
              color: riskScore >= 70 ? '#f43f5e' : riskScore >= 30 ? '#f59e0b' : '#10b981' 
            }}>
              {riskScore}<span style={{ fontSize: '0.8rem', color: '#64748b' }}>/100</span>
            </div>
          </div>

          <div className="score-box">
            <div className="score-box-label">ML Prob (70%)</div>
            <div className="score-box-val" style={{ color: '#38bdf8' }}>
              {probPercent}%
            </div>
          </div>

          <div className="score-box">
            <div className="score-box-label">Rule Score (30%)</div>
            <div className="score-box-val" style={{ color: '#a855f7' }}>
              +{ruleScore.toFixed(0)}
            </div>
          </div>
        </div>

        {/* Why? Section (PRD Section 15 & 20) */}
        <div className="why-section">
          <div className="why-title">
            <HelpCircle size={16} />
            <span>Why? Decision Explainability</span>
          </div>
          <ul className="why-list">
            {reasons.map((reason, idx) => (
              <li key={idx} className="why-item">
                <span className="why-bullet" style={{
                  background: decision === 'BLOCK' ? '#f43f5e' : decision === 'REVIEW' ? '#f59e0b' : '#10b981'
                }}></span>
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Factor Breakdown Bars (From /grill-me User Alignment) */}
      <div className="factors-section">
        <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', fontWeight: 600, color: '#94a3b8', marginBottom: '2px' }}>
          Risk Factor Breakdown
        </div>
        {factorContributions.map((fc, idx) => {
          let barColor = '#10b981';
          if (fc.impact === 'CRITICAL' || fc.impact === 'HIGH') barColor = '#f43f5e';
          else if (fc.impact === 'MEDIUM') barColor = '#f59e0b';
          
          const fillWidth = Math.min(100, Math.max(5, (fc.scoreContribution / 35.0) * 100));

          return (
            <div key={idx} className="factor-row">
              <div className="factor-meta">
                <span className="factor-name">{fc.factor}</span>
                <span className="factor-desc" style={{ color: barColor }}>{fc.description}</span>
              </div>
              <div className="progress-bar-bg">
                <div 
                  className="progress-bar-fill" 
                  style={{ width: `${fillWidth}%`, backgroundColor: barColor }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
