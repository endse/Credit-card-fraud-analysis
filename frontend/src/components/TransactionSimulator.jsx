import React, { useState } from 'react';
import { PlayCircle, Sparkles, Check, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function TransactionSimulator({ 
  onAnalyze, 
  isLoading, 
  currency 
}) {
  const currencySymbol = currency === 'INR' ? '₹' : '$';

  // Preset definitions according to PRD Section 22
  const presets = {
    A: {
      cardId: 'CARD001',
      amount: 1200,
      merchant: 'Amazon Retail',
      merchantRisk: 'LOW',
      transactionHour: 14,
      transactionsLast10Minutes: 1,
      averageTransactionAmount: 2000,
      newDevice: false,
      newLocation: false,
    },
    B: {
      cardId: 'CARD002',
      amount: 15000,
      merchant: 'BestBuy Electronics',
      merchantRisk: 'MEDIUM',
      transactionHour: 15,
      transactionsLast10Minutes: 4,
      averageTransactionAmount: 3000,
      newDevice: true,
      newLocation: false,
    },
    C: {
      cardId: 'CARD003',
      amount: 75000,
      merchant: 'Crypto Exchange X',
      merchantRisk: 'HIGH',
      transactionHour: 3,
      transactionsLast10Minutes: 8,
      averageTransactionAmount: 2500,
      newDevice: true,
      newLocation: true,
    }
  };

  const [activePreset, setActivePreset] = useState('C');
  const [formData, setFormData] = useState(presets.C);

  const selectPreset = (key) => {
    setActivePreset(key);
    setFormData(presets[key]);
  };

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setActivePreset(null);
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? (value === '' ? '' : Number(value)) : value
    }));
  };

  const handleToggle = (field, val) => {
    setActivePreset(null);
    setFormData((prev) => ({
      ...prev,
      [field]: val
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onAnalyze(formData);
  };

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div className="section-header">
        <div className="section-title">
          <Sparkles size={20} color="#38bdf8" />
          <span>Transaction Simulator</span>
        </div>
        <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>PRD Section 19</span>
      </div>

      {/* 1-Click Demo Scenarios */}
      <div className="presets-group">
        <div className="presets-label">1-Click Demo Scenarios (PRD Section 22)</div>
        <div className="presets-row">
          <button
            type="button"
            className={`preset-btn ${activePreset === 'A' ? 'active' : ''}`}
            onClick={() => selectPreset('A')}
          >
            <div className="preset-name" style={{ color: '#10b981' }}>
              <Check size={14} /> Scenario A
            </div>
            <div className="preset-desc">Legitimate (₹1,200) → APPROVE</div>
          </button>

          <button
            type="button"
            className={`preset-btn ${activePreset === 'B' ? 'active' : ''}`}
            onClick={() => selectPreset('B')}
          >
            <div className="preset-name" style={{ color: '#f59e0b' }}>
              <AlertTriangle size={14} /> Scenario B
            </div>
            <div className="preset-desc">Suspicious (₹15,000) → REVIEW</div>
          </button>

          <button
            type="button"
            className={`preset-btn ${activePreset === 'C' ? 'active' : ''}`}
            onClick={() => selectPreset('C')}
          >
            <div className="preset-name" style={{ color: '#f43f5e' }}>
              <ShieldAlert size={14} /> Scenario C
            </div>
            <div className="preset-desc">Fraudulent (₹75,000) → BLOCK</div>
          </button>
        </div>
      </div>

      {/* Simulator Form */}
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          {/* Card ID */}
          <div className="form-field">
            <label className="form-label">Card / Account ID</label>
            <input
              type="text"
              name="cardId"
              className="form-input"
              value={formData.cardId}
              onChange={handleChange}
              placeholder="e.g. CARD001"
              required
            />
          </div>

          {/* Amount */}
          <div className="form-field">
            <label className="form-label">
              <span>Transaction Amount ({currencySymbol})</span>
              {formData.averageTransactionAmount > 0 && (
                <span style={{ color: '#94a3b8', fontSize: '0.72rem' }}>
                  {(formData.amount / formData.averageTransactionAmount).toFixed(1)}x Avg
                </span>
              )}
            </label>
            <input
              type="number"
              name="amount"
              className="form-input"
              value={formData.amount}
              onChange={handleChange}
              min="1"
              required
            />
          </div>

          {/* Merchant */}
          <div className="form-field">
            <label className="form-label">Merchant Name</label>
            <input
              type="text"
              name="merchant"
              className="form-input"
              value={formData.merchant}
              onChange={handleChange}
              required
            />
          </div>

          {/* Merchant Risk */}
          <div className="form-field">
            <label className="form-label">Merchant Category Risk</label>
            <select
              name="merchantRisk"
              className="form-select"
              value={formData.merchantRisk}
              onChange={handleChange}
            >
              <option value="LOW">LOW (Trusted retail / groceries)</option>
              <option value="MEDIUM">MEDIUM (Travel / electronics)</option>
              <option value="HIGH">HIGH (Crypto / gaming / luxury)</option>
            </select>
          </div>

          {/* Average Transaction Amount */}
          <div className="form-field">
            <label className="form-label">Customer Average Spend ({currencySymbol})</label>
            <input
              type="number"
              name="averageTransactionAmount"
              className="form-input"
              value={formData.averageTransactionAmount}
              onChange={handleChange}
              min="100"
              required
            />
          </div>

          {/* Velocity */}
          <div className="form-field">
            <label className="form-label">Transactions in Last 10 Mins</label>
            <input
              type="number"
              name="transactionsLast10Minutes"
              className="form-input"
              value={formData.transactionsLast10Minutes}
              onChange={handleChange}
              min="0"
              max="50"
              required
            />
          </div>

          {/* Hour */}
          <div className="form-field full-width">
            <label className="form-label">
              <span>Transaction Hour (24-Hour Clock: {formData.transactionHour}:00)</span>
              {formData.transactionHour <= 4 && (
                <span style={{ color: '#fb923c', fontSize: '0.75rem', fontWeight: 600 }}>
                  ⚠️ Nocturnal Off-Hours
                </span>
              )}
            </label>
            <input
              type="range"
              name="transactionHour"
              min="0"
              max="23"
              value={formData.transactionHour}
              onChange={handleChange}
              style={{ accentColor: '#38bdf8', height: '6px', cursor: 'pointer' }}
            />
          </div>

          {/* New Device Toggle */}
          <div className="form-field">
            <label className="form-label">New Device Fingerprint?</label>
            <div className="toggle-group">
              <button
                type="button"
                className={`toggle-btn ${!formData.newDevice ? 'active' : ''}`}
                onClick={() => handleToggle('newDevice', false)}
              >
                No (Known)
              </button>
              <button
                type="button"
                className={`toggle-btn ${formData.newDevice ? 'active' : ''}`}
                onClick={() => handleToggle('newDevice', true)}
              >
                Yes (New)
              </button>
            </div>
          </div>

          {/* New Location Toggle */}
          <div className="form-field">
            <label className="form-label">New Geographic Location?</label>
            <div className="toggle-group">
              <button
                type="button"
                className={`toggle-btn ${!formData.newLocation ? 'active' : ''}`}
                onClick={() => handleToggle('newLocation', false)}
              >
                No (Familiar)
              </button>
              <button
                type="button"
                className={`toggle-btn ${formData.newLocation ? 'active' : ''}`}
                onClick={() => handleToggle('newLocation', true)}
              >
                Yes (Unusual)
              </button>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="btn btn-primary analyze-btn"
          id="analyze-transaction-btn"
        >
          <PlayCircle size={20} />
          <span>{isLoading ? 'ANALYZING TRANSACTION...' : 'ANALYZE TRANSACTION'}</span>
        </button>
      </form>
    </div>
  );
}
