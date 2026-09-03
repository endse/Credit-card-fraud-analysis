import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { TrendingUp, PieChart } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function FraudTrendChart({ transactions }) {
  // Take last 20 transactions reversed so chronological order left to right
  const chronological = [...(transactions || [])].reverse().slice(-20);

  const labels = chronological.map((t) => {
    const parts = (t.timestamp || '').split(' ');
    return parts.length > 1 ? parts[1].substring(0, 5) : t.id;
  });

  const riskScores = chronological.map((t) => t.riskScore);
  const mlProbabilities = chronological.map((t) => Math.round(t.fraudProbability * 100));

  const chartData = {
    labels: labels.length > 0 ? labels : ['10:00', '10:15', '10:30', '10:45', '11:00'],
    datasets: [
      {
        type: 'line',
        label: 'Hybrid Risk Score',
        data: riskScores.length > 0 ? riskScores : [12, 18, 92, 45, 10],
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.1)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: chronological.map((t) => {
          if (t.decision === 'BLOCK') return '#f43f5e';
          if (t.decision === 'REVIEW') return '#f59e0b';
          return '#10b981';
        }),
        pointBorderColor: '#0e1526',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7,
      },
      {
        type: 'line',
        label: 'ML Probability %',
        data: mlProbabilities.length > 0 ? mlProbabilities : [10, 15, 95, 40, 8],
        borderColor: '#a855f7',
        borderDash: [5, 5],
        borderWidth: 1.8,
        pointRadius: 0,
        fill: false,
        tension: 0.3,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        align: 'end',
        labels: {
          color: '#94a3b8',
          font: { family: 'Plus Jakarta Sans', size: 12, weight: 600 },
          boxWidth: 12,
          usePointStyle: true,
        }
      },
      tooltip: {
        backgroundColor: '#090e1a',
        titleColor: '#f8fafc',
        bodyColor: '#cbd5e1',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 12,
        titleFont: { family: 'Outfit', size: 13, weight: 700 },
        bodyFont: { family: 'Plus Jakarta Sans', size: 12 },
        callbacks: {
          afterLabel: function(context) {
            const index = context.dataIndex;
            const t = chronological[index];
            if (t) {
              return `Card: ${t.cardId} | Decision: ${t.decision}`;
            }
            return '';
          }
        }
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.04)' },
        ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 11 } }
      },
      y: {
        min: 0,
        max: 100,
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: {
          color: '#64748b',
          font: { family: 'JetBrains Mono', size: 11 },
          stepSize: 25,
          callback: (value) => `${value}`
        }
      }
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '22px', marginBottom: '28px' }}>
      <div className="section-header" style={{ marginBottom: '14px' }}>
        <div className="section-title">
          <TrendingUp size={20} color="#38bdf8" />
          <span>Real-Time Fraud Risk Velocity Timeline</span>
        </div>
        <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
          <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
            Showing last 20 transactions • Dot color indicates decision
          </span>
        </div>
      </div>
      <div style={{ height: '240px', width: '100%' }}>
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
}
