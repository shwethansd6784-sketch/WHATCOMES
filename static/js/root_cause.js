/**
 * root_cause.js - Root-cause intelligence, anomaly highlights, and statistical proof tables.
 */

async function loadRootCause() {
  try {
    const res = await fetch('/api/root-cause/summary');
    const json = await res.json();
    if (json.status !== 'success') return;

    const data = json.data;

    renderRootCauseHighlights(data.highlights);
    renderProductReliabilityTable(data.product_matrix);
    renderReasonRealityMatrix(data.reason_breakdown);

  } catch (err) {
    console.error('Error loading root-cause data:', err);
  }
}

// 1. Render Anomaly Highlight Cards
function renderRootCauseHighlights(highlights) {
  const container = document.getElementById('root-cause-highlights');
  if (!container) return;

  if (highlights.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted); padding: 16px;">No anomalous defect clusters detected at current sample thresholds.</p>';
    return;
  }

  container.innerHTML = highlights.map(h => {
    let borderClass = 'border-info';
    let badgeClass = 'badge-pending';
    if (h.badge_color === 'danger') {
      borderClass = 'highlight-card border-danger';
      badgeClass = 'badge-defective';
    } else if (h.badge_color === 'warning') {
      borderClass = 'highlight-card border-warning';
      badgeClass = 'badge-liquidate';
    } else {
      borderClass = 'highlight-card border-info';
      badgeClass = 'badge-repair';
    }

    return `
      <div class="${borderClass}">
        <div class="highlight-header">
          <span class="badge ${badgeClass}">${h.badge}</span>
          <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Sample: N=${h.sample_size} units</span>
        </div>
        <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 4px; color: var(--text-main);">${escapeHtml(h.title)}</h4>
        <div style="font-size: 0.76rem; color: var(--brand-primary); font-weight: 600; margin-bottom: 8px;">Target: ${escapeHtml(h.entity)}</div>
        <div class="highlight-body">
          <p style="margin-bottom: 8px;"><strong>Verified Evidence:</strong> ${escapeHtml(h.evidence)}</p>
          <p style="font-size: 0.8rem; color: #166534; background: #F0FDF4; padding: 6px 10px; border-radius: var(--radius-sm); border: 1px solid #BBF7D0;">
            <strong>Advisor Recommendation:</strong> ${escapeHtml(h.recommended_action)}
          </p>
        </div>
        <div class="highlight-footer">
          <span style="font-weight: 600; color: var(--text-secondary);">Impact: ${h.financial_impact}</span>
          <button class="btn btn-secondary btn-sm" onclick="quickJumpAction('${h.action_code}')">
            View ${h.action_code}
          </button>
        </div>
      </div>
    `;
  }).join('');
}

// 2. Render Product Reliability Matrix Table
function renderProductReliabilityTable(products) {
  const tbody = document.getElementById('root-cause-product-table');
  if (!tbody) return;

  tbody.innerHTML = products.map(p => {
    const isSampleLow = p.sample_size < 3;
    const sampleBadge = isSampleLow 
      ? '<span class="badge badge-insufficient">Insufficient data (N &lt; 3)</span>'
      : `<span style="font-weight: 600;">N=${p.sample_size}</span>`;

    const returnRateColor = p.return_rate_pct > 3.5 ? 'color: var(--color-danger); font-weight: 700;' : 'font-weight: 600;';

    return `
      <tr>
        <td>
          <div style="font-weight: 600; color: var(--text-main);">${escapeHtml(p.name)}</div>
          <div style="font-size: 0.74rem; color: var(--text-muted);">${p.sku} &bull; ${p.category}</div>
        </td>
        <td style="color: var(--text-secondary);">${escapeHtml(p.supplier)}</td>
        <td style="color: var(--text-secondary);">${p.units_sold.toLocaleString()}</td>
        <td style="font-weight: 600;">${p.units_returned}</td>
        <td style="${returnRateColor}">${p.return_rate_pct}%</td>
        <td style="font-weight: 700; color: ${p.confirmed_defects > 0 ? 'var(--color-danger)' : 'inherit'};">
          ${p.confirmed_defects}
        </td>
        <td>${p.defect_rate_sold_pct}%</td>
        <td>
          <span class="badge ${p.defect_rate_returns_pct > 40 ? 'badge-defective' : 'badge-restock'}">
            ${p.defect_rate_returns_pct}% of returns
          </span>
        </td>
        <td>${sampleBadge}</td>
      </tr>
    `;
  }).join('');
}

// 3. Render Reason Reality Matrix Table
function renderReasonRealityMatrix(reasons) {
  const tbody = document.getElementById('root-cause-reason-matrix');
  if (!tbody) return;

  tbody.innerHTML = reasons.map(r => `
    <tr>
      <td style="font-weight: 600; color: var(--text-main);">${r.customer_reason}</td>
      <td style="font-weight: 700;">${r.total_count}</td>
      <td style="color: var(--color-danger); font-weight: 600;">${r.confirmed_defects}</td>
      <td style="color: var(--brand-primary); font-weight: 600;">${r.opened_working}</td>
      <td style="color: var(--color-success); font-weight: 600;">${r.unopened}</td>
      <td style="color: var(--color-warning); font-weight: 600;">${r.damaged}</td>
      <td style="color: var(--text-muted);">${r.pending_inspection}</td>
    </tr>
  `).join('');
}

function quickJumpAction(actionCode) {
  switchTab('action-centre');
  setTimeout(() => {
    showToast(`Navigated to Corrective Action: ${actionCode}`, 'info');
  }, 200);
}

window.loadRootCause = loadRootCause;
window.quickJumpAction = quickJumpAction;
