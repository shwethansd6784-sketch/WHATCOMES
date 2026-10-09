/**
 * dashboard.js - Overview dashboard metrics, Chart.js instances, and priority actions.
 */

window.ChartInstances = {
  reasons: null,
  trends: null,
  productRates: null,
  supplierDefects: null
};

async function loadDashboard() {
  await Promise.all([
    fetchDashboardStats(),
    fetchDashboardCharts()
  ]);
}

// ==========================================
// FETCH & RENDER KPI STATS
// ==========================================
async function fetchDashboardStats() {
  try {
    const res = await fetch('/api/dashboard/stats');
    const json = await res.json();
    if (json.status !== 'success') return;

    const data = json.data;

    // KPI Values
    document.getElementById('kpi-total-returns').textContent = data.total_returns.toLocaleString();
    document.getElementById('kpi-awaiting-inspection').textContent = data.awaiting_inspection.toLocaleString();
    document.getElementById('kpi-confirmed-defective').textContent = data.confirmed_defective.toLocaleString();
    document.getElementById('kpi-approved-restocking').textContent = data.approved_restocking.toLocaleString();
    document.getElementById('kpi-financial-loss').textContent = `$${data.financial_loss.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById('kpi-recoverable-value').textContent = `$${data.recoverable_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

    // Subtext & Badge
    document.getElementById('kpi-recovery-rate-sub').textContent = `${data.net_recovery_rate}% net recovery yield`;

    const changeLabel = document.getElementById('kpi-change-label');
    if (data.comparison) {
      const pct = data.comparison.percentage_change;
      const sign = pct > 0 ? '+' : '';
      changeLabel.textContent = `${sign}${pct}% ${data.comparison.label}`;
      changeLabel.className = pct > 0 ? 'kpi-badge up' : pct < 0 ? 'kpi-badge down' : 'kpi-badge neutral';
    }

    // Update sidebar counters
    const navReturns = document.getElementById('nav-returns-count');
    if (navReturns) navReturns.textContent = data.total_returns;

    const navPending = document.getElementById('nav-pending-count');
    if (navPending) navPending.textContent = data.awaiting_inspection;

    const navActions = document.getElementById('nav-actions-count');
    if (navActions) navActions.textContent = data.active_actions;

  } catch (err) {
    console.error('Error fetching dashboard stats:', err);
  }
}

// ==========================================
// FETCH & RENDER CHARTS
// ==========================================
async function fetchDashboardCharts() {
  try {
    const res = await fetch('/api/dashboard/charts');
    const json = await res.json();
    if (json.status !== 'success') return;

    const data = json.data;

    renderReasonsChart(data.returns_by_reason);
    renderTrendsChart(data.return_trends);
    renderProductRatesChart(data.top_return_rates);
    renderSupplierDefectsChart(data.supplier_defects);

    // Also fetch priority actions for the overview list
    fetchOverviewPriorityActions();

  } catch (err) {
    console.error('Error fetching dashboard charts:', err);
  }
}

// 1. Returns by Reason (Doughnut)
function renderReasonsChart(reasonsData) {
  const ctx = document.getElementById('chart-reasons');
  if (!ctx) return;

  if (window.ChartInstances.reasons) {
    window.ChartInstances.reasons.destroy();
  }

  const labels = reasonsData.map(r => r.reason);
  const counts = reasonsData.map(r => r.count);

  const colors = [
    '#0284C7', // Blue
    '#0D9488', // Teal
    '#DC2626', // Red
    '#F59E0B', // Amber
    '#6366F1', // Indigo
    '#8B5CF6', // Purple
    '#EC4899', // Pink
    '#64748B'  // Slate
  ];

  window.ChartInstances.reasons = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: counts,
        backgroundColor: colors.slice(0, labels.length),
        borderWidth: 2,
        borderColor: '#FFFFFF'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            boxWidth: 12,
            font: { size: 11, family: 'inherit' },
            color: '#334155'
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const val = context.raw;
              const pct = ((val / total) * 100).toFixed(1);
              return ` ${context.label}: ${val} units (${pct}%)`;
            }
          }
        }
      },
      cutout: '68%'
    }
  });
}

// 2. Return Trends over Time (Line)
function renderTrendsChart(trendsData) {
  const ctx = document.getElementById('chart-trends');
  if (!ctx) return;

  if (window.ChartInstances.trends) {
    window.ChartInstances.trends.destroy();
  }

  const labels = trendsData.map(t => t.week);
  const counts = trendsData.map(t => t.count);

  window.ChartInstances.trends = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Inbound Returns',
        data: counts,
        borderColor: '#0284C7',
        backgroundColor: 'rgba(2, 132, 199, 0.08)',
        fill: true,
        tension: 0.35,
        borderWidth: 3,
        pointBackgroundColor: '#0284C7',
        pointBorderColor: '#FFFFFF',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: { precision: 0, font: { size: 10, family: 'inherit' }, color: '#64748B' },
          grid: { color: '#F1F5F9' }
        },
        x: {
          ticks: { font: { size: 10, family: 'inherit' }, color: '#64748B' },
          grid: { display: false }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` Returns received: ${ctx.raw} units`
          }
        }
      }
    }
  });
}

// 3. Products with Highest Return Rates (Horizontal Bar)
function renderProductRatesChart(productRates) {
  const ctx = document.getElementById('chart-product-rates');
  if (!ctx) return;

  if (window.ChartInstances.productRates) {
    window.ChartInstances.productRates.destroy();
  }

  const labels = productRates.map(p => p.name.length > 22 ? p.name.substring(0, 20) + '...' : p.name);
  const rates = productRates.map(p => p.rate);

  window.ChartInstances.productRates = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Return Rate (%)',
        data: rates,
        backgroundColor: rates.map(r => r > 4.0 ? 'rgba(220, 38, 38, 0.85)' : 'rgba(2, 132, 199, 0.85)'),
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          beginAtZero: true,
          ticks: { callback: v => `${v}%`, font: { size: 10, family: 'inherit' }, color: '#64748B' },
          grid: { color: '#F1F5F9' }
        },
        y: {
          ticks: { font: { size: 10, family: 'inherit' }, color: '#334155' },
          grid: { display: false }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (c) => ` Return rate: ${c.raw}% (Benchmark: <3.0%)`
          }
        }
      }
    }
  });
}

// 4. Supplier-Related Confirmed Defects (Bar)
function renderSupplierDefectsChart(supplierDefects) {
  const ctx = document.getElementById('chart-supplier-defects');
  if (!ctx) return;

  if (window.ChartInstances.supplierDefects) {
    window.ChartInstances.supplierDefects.destroy();
  }

  const labels = supplierDefects.map(s => s.supplier.split(' ')[0]);
  const defects = supplierDefects.map(s => s.defects);

  window.ChartInstances.supplierDefects = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Confirmed Defects',
        data: defects,
        backgroundColor: '#0D9488',
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: { precision: 0, font: { size: 10, family: 'inherit' }, color: '#64748B' },
          grid: { color: '#F1F5F9' }
        },
        x: {
          ticks: { font: { size: 10, family: 'inherit' }, color: '#334155' },
          grid: { display: false }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (c) => ` Confirmed defective units: ${c.raw}`
          }
        }
      }
    }
  });
}

// 5. Overview Priority Actions List
async function fetchOverviewPriorityActions() {
  const container = document.getElementById('overview-priority-actions');
  if (!container) return;

  try {
    const res = await fetch('/api/actions');
    const json = await res.json();
    if (json.status !== 'success' || !json.data) return;

    const actions = json.data.slice(0, 3); // Top 3 priority actions
    if (actions.length === 0) {
      container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem; padding: 12px;">No active priority actions.</p>';
      return;
    }

    container.innerHTML = actions.map(act => `
      <div class="priority-action-row">
        <div class="action-info-box">
          <span class="action-priority-tag ${act.priority}">${act.priority}</span>
          <div class="action-text">
            <h4>${act.action_code}: ${escapeHtml(act.title)}</h4>
            <p>${escapeHtml(act.evidence.substring(0, 110))}...</p>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
          <span class="badge ${act.status === 'Resolved' ? 'badge-restock' : act.status === 'In Progress' ? 'badge-repair' : 'badge-pending'}">${act.status}</span>
          <button class="btn btn-secondary btn-sm" onclick="viewActionDetail('${act.action_code}')">View</button>
        </div>
      </div>
    `).join('');

  } catch (err) {
    console.error('Error fetching overview priority actions:', err);
  }
}

function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/[&<>"']/g, function(m) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
  });
}

window.loadDashboard = loadDashboard;
