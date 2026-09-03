/**
 * API Service for FraudGuard AI
 * Connects frontend to Python FastAPI backend endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function analyzeTransaction(transactionData) {
  const response = await fetch(`${API_BASE_URL}/api/transactions/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(transactionData),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error (${response.status}): ${errorText}`);
  }

  return await response.json();
}

export async function getTransactions(limit = 100) {
  const response = await fetch(`${API_BASE_URL}/api/transactions?limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch transactions: ${response.statusText}`);
  }
  return await response.json();
}

export async function getDashboardStats() {
  const response = await fetch(`${API_BASE_URL}/api/stats`);
  if (!response.ok) {
    throw new Error(`Failed to fetch dashboard stats: ${response.statusText}`);
  }
  return await response.json();
}

export async function getModelMetrics() {
  const response = await fetch(`${API_BASE_URL}/api/model/metrics`);
  if (!response.ok) {
    throw new Error(`Failed to fetch model metrics: ${response.statusText}`);
  }
  return await response.json();
}

export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    return response.ok;
  } catch {
    return false;
  }
}
