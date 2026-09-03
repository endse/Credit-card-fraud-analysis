import React from 'react';
import { ShieldAlert, BarChart3, RefreshCw, Cpu } from 'lucide-react';

export default function Navbar({ 
  currency, 
  onToggleCurrency, 
  onOpenMetrics, 
  onRefresh, 
  isRefreshing 
}) {
  return (
    <header className="navbar glass-panel">
      <div className="brand-group">
        <div className="logo-badge">
          <ShieldAlert size={26} color="#ffffff" />
        </div>
        <div className="brand-text">
          <h1>FraudGuard AI</h1>
          <p>Real-Time Fraud Detection &amp; Risk Engine</p>
        </div>
      </div>

      <div className="nav-actions">
        <div className="btn btn-secondary btn-pill" title="Backend ML Model Status">
          <span className="live-indicator"></span>
          <Cpu size={14} color="#38bdf8" />
          <span style={{ fontSize: '0.78rem', color: '#e2e8f0' }}>XGBoost + Rules Active</span>
        </div>

        <button 
          className="btn btn-secondary btn-pill" 
          onClick={onToggleCurrency}
          title="Toggle Currency Display"
        >
          <strong>{currency === 'INR' ? '₹ INR' : '$ USD'}</strong>
        </button>

        <button 
          className="btn btn-secondary" 
          onClick={onOpenMetrics}
          title="View Model Precision, Recall, and ROC-AUC"
        >
          <BarChart3 size={16} />
          <span>Model Metrics</span>
        </button>

        <button 
          className="btn btn-secondary" 
          onClick={onRefresh}
          disabled={isRefreshing}
          title="Refresh Dashboard & History"
        >
          <RefreshCw size={16} className={isRefreshing ? 'spin-icon' : ''} />
          <span>Refresh</span>
        </button>
      </div>
    </header>
  );
}
