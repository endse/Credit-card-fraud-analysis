import React, { useState } from 'react';
import { History, Search, ChevronRight, CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';

export default function TransactionHistory({ 
  transactions = [], 
  currency = 'INR', 
  onSelectTransaction 
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDecision, setFilterDecision] = useState('ALL');
  const [selectedTxn, setSelectedTxn] = useState(null);

  const currencySymbol = currency === 'INR' ? '₹' : '$';

  const filtered = transactions.filter((t) => {
    const matchesSearch = 
      (t.cardId || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (t.merchant || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (t.amount || '').toString().includes(searchTerm);

    const matchesFilter = 
      filterDecision === 'ALL' || t.decision === filterDecision;

    return matchesSearch && matchesFilter;
  });

  const handleRowClick = (txn) => {
    setSelectedTxn(selectedTxn?.id === txn.id ? null : txn);
    if (onSelectTransaction) {
      onSelectTransaction(txn);
    }
  };

  return (
    <div className="glass-panel history-section" style={{ padding: '24px' }}>
      <div className="section-header">
        <div className="section-title">
          <History size={20} color="#38bdf8" />
          <span>Transaction Audit History</span>
        </div>
        <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
          {filtered.length} of {transactions.length} transactions shown • Newest first
        </span>
      </div>

      {/* Search & Filter Bar */}
      <div className="table-controls">
        <div className="search-box">
          <Search size={16} color="#64748b" />
          <input
            type="text"
            placeholder="Search by Card ID, merchant, or amount..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-tabs">
          {['ALL', 'BLOCK', 'REVIEW', 'APPROVE'].map((status) => (
            <button
              key={status}
              className={`filter-tab ${filterDecision === status ? 'active' : ''}`}
              onClick={() => setFilterDecision(status)}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="data-table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Card ID</th>
              <th>Merchant</th>
              <th>Amount</th>
              <th>Risk Score</th>
              <th>Decision</th>
              <th>Quick Reason</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '32px', color: '#64748b' }}>
                  No transactions found matching your search criteria.
                </td>
              </tr>
            ) : (
              filtered.map((t) => {
                const timeStr = t.timestamp ? t.timestamp.split(' ')[1] || t.timestamp : '--';
                const firstReason = t.reasons && t.reasons.length > 0 ? t.reasons[0] : 'Normal pattern';

                return (
                  <React.Fragment key={t.id}>
                    <tr onClick={() => handleRowClick(t)}>
                      <td style={{ fontFamily: 'JetBrains Mono', color: '#94a3b8' }}>{timeStr}</td>
                      <td style={{ fontFamily: 'JetBrains Mono', fontWeight: 600, color: '#f8fafc' }}>{t.cardId}</td>
                      <td>
                        <span style={{ color: '#e2e8f0' }}>{t.merchant}</span>
                        <span style={{ 
                          fontSize: '0.68rem', 
                          marginLeft: '6px',
                          color: t.merchantRisk === 'HIGH' ? '#f43f5e' : t.merchantRisk === 'MEDIUM' ? '#f59e0b' : '#64748b' 
                        }}>
                          [{t.merchantRisk}]
                        </span>
                      </td>
                      <td style={{ fontFamily: 'JetBrains Mono', fontWeight: 600, color: '#f8fafc' }}>
                        {currencySymbol}{Number(t.amount).toLocaleString()}
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ 
                            fontFamily: 'Outfit', 
                            fontWeight: 700, 
                            color: t.riskScore >= 70 ? '#f43f5e' : t.riskScore >= 30 ? '#f59e0b' : '#10b981' 
                          }}>
                            {t.riskScore}
                          </span>
                          <span style={{ fontSize: '0.72rem', color: '#64748b' }}>({Math.round(t.fraudProbability * 100)}% ML)</span>
                        </div>
                      </td>
                      <td>
                        <span className={`badge badge-${t.decision.toLowerCase()}`}>
                          {t.decision === 'APPROVE' && <CheckCircle2 size={12} />}
                          {t.decision === 'REVIEW' && <AlertTriangle size={12} />}
                          {t.decision === 'BLOCK' && <XCircle size={12} />}
                          {t.decision}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.78rem', color: '#94a3b8', maxWidth: '280px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {firstReason}
                      </td>
                    </tr>

                    {/* Expandable Details Drawer */}
                    {selectedTxn?.id === t.id && (
                      <tr style={{ background: 'rgba(2, 6, 23, 0.7)' }}>
                        <td colSpan="7" style={{ padding: '16px 20px', borderBottom: '1px solid rgba(56, 189, 248, 0.2)' }}>
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '12px' }}>
                            <div>
                              <span style={{ fontSize: '0.72rem', color: '#64748b', textTransform: 'uppercase' }}>Avg Amount:</span>
                              <div style={{ fontSize: '0.88rem', fontWeight: 600 }}>{currencySymbol}{t.averageTransactionAmount?.toLocaleString()}</div>
                            </div>
                            <div>
                              <span style={{ fontSize: '0.72rem', color: '#64748b', textTransform: 'uppercase' }}>Velocity (10m):</span>
                              <div style={{ fontSize: '0.88rem', fontWeight: 600 }}>{t.transactionsLast10Minutes} transactions</div>
                            </div>
                            <div>
                              <span style={{ fontSize: '0.72rem', color: '#64748b', textTransform: 'uppercase' }}>New Device:</span>
                              <div style={{ fontSize: '0.88rem', fontWeight: 600, color: t.newDevice ? '#fb923c' : '#10b981' }}>
                                {t.newDevice ? 'Yes (Unrecognized)' : 'No (Known)'}
                              </div>
                            </div>
                            <div>
                              <span style={{ fontSize: '0.72rem', color: '#64748b', textTransform: 'uppercase' }}>New Location:</span>
                              <div style={{ fontSize: '0.88rem', fontWeight: 600, color: t.newLocation ? '#fb923c' : '#10b981' }}>
                                {t.newLocation ? 'Yes (Unusual)' : 'No (Familiar)'}
                              </div>
                            </div>
                          </div>

                          <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '12px', borderRadius: '8px' }}>
                            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8', marginBottom: '6px' }}>
                              Comprehensive Explanations:
                            </div>
                            <ul style={{ listStyle: 'disc', paddingLeft: '20px', fontSize: '0.82rem', color: '#cbd5e1' }}>
                              {(t.reasons || []).map((r, i) => (
                                <li key={i}>{r}</li>
                              ))}
                            </ul>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
