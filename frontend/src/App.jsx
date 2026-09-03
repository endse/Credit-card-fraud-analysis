import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import MetricCards from './components/MetricCards';
import FraudTrendChart from './components/FraudTrendChart';
import TransactionSimulator from './components/TransactionSimulator';
import AnalysisResultCard from './components/AnalysisResultCard';
import TransactionHistory from './components/TransactionHistory';
import ModelMetricsModal from './components/ModelMetricsModal';
import { 
  analyzeTransaction, 
  getTransactions, 
  getDashboardStats, 
  getModelMetrics 
} from './services/api';

export default function App() {
  const [currency, setCurrency] = useState('INR');
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState(null);
  const [latestResult, setLatestResult] = useState(null);
  const [modelMetrics, setModelMetrics] = useState(null);
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isMetricsOpen, setIsMetricsOpen] = useState(false);
  const [apiError, setApiError] = useState(null);

  const loadInitialData = async () => {
    setIsRefreshing(true);
    setApiError(null);
    try {
      const [txnsData, statsData, metricsData] = await Promise.all([
        getTransactions(100),
        getDashboardStats(),
        getModelMetrics()
      ]);
      setTransactions(txnsData);
      setStats(statsData);
      setModelMetrics(metricsData);
    } catch (err) {
      console.error("Data fetch error:", err);
      setApiError("Unable to connect to backend service. Ensure backend is running on port 8000.");
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const handleAnalyze = async (formData) => {
    setIsAnalyzing(true);
    setApiError(null);
    try {
      const analysisResult = await analyzeTransaction(formData);
      setLatestResult(analysisResult);
      
      // Prepend to history table immediately
      setTransactions((prev) => [analysisResult, ...prev]);

      // Refresh stats
      const updatedStats = await getDashboardStats();
      setStats(updatedStats);
    } catch (err) {
      console.error("Analysis error:", err);
      setApiError("Transaction analysis failed: " + err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleToggleCurrency = () => {
    setCurrency((prev) => (prev === 'INR' ? 'USD' : 'INR'));
  };

  return (
    <div className="app-container">
      {/* Navbar */}
      <Navbar
        currency={currency}
        onToggleCurrency={handleToggleCurrency}
        onOpenMetrics={() => setIsMetricsOpen(true)}
        onRefresh={loadInitialData}
        isRefreshing={isRefreshing}
      />

      {/* Error Alert if backend unreachable */}
      {apiError && (
        <div style={{
          background: 'rgba(244, 63, 94, 0.15)',
          border: '1px solid rgba(244, 63, 94, 0.4)',
          borderRadius: '12px',
          padding: '14px 20px',
          color: '#f87171',
          marginBottom: '24px',
          fontSize: '0.88rem'
        }}>
          ⚠️ {apiError}
        </div>
      )}

      {/* Metric Cards */}
      <MetricCards stats={stats} />

      {/* Fraud Trend Chart */}
      <FraudTrendChart transactions={transactions} />

      {/* Demo Workspace: Simulator + Result Card */}
      <div className="demo-layout">
        <TransactionSimulator
          onAnalyze={handleAnalyze}
          isLoading={isAnalyzing}
          currency={currency}
        />
        <AnalysisResultCard
          result={latestResult}
          isLoading={isAnalyzing}
        />
      </div>

      {/* Transaction History Table */}
      <TransactionHistory
        transactions={transactions}
        currency={currency}
        onSelectTransaction={(txn) => setLatestResult(txn)}
      />

      {/* Model Evaluation Modal */}
      <ModelMetricsModal
        isOpen={isMetricsOpen}
        onClose={() => setIsMetricsOpen(false)}
        metrics={modelMetrics}
      />
    </div>
  );
}
