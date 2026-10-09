/**
 * recommendations.js - Smart Recovery Recommendation directory and explainable decision cards.
 */

let allRecommendationsList = [];

async function loadRecommendations() {
  try {
    const res = await fetch('/api/returns');
    const json = await res.json();
    if (json.status !== 'success') return;

    // Filter to items that have generated recommendations
    allRecommendationsList = json.data.filter(r => r.recommendation_id);
    renderRecommendationsList();

  } catch (err) {
    console.error('Error loading recommendations:', err);
  }
}

function renderRecommendationsList() {
  const container = document.getElementById('recommendations-container');
  const actionFilter = document.getElementById('filter-rec-action')?.value || '';
  if (!container) return;

  const filtered = actionFilter
    ? allRecommendationsList.filter(r => r.recommended_action === actionFilter)
    : allRecommendationsList;

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px; background: #FFFFFF; border-radius: var(--radius-lg); border: 1px solid var(--border-light);">
        <p style="color: var(--text-muted); font-size: 0.9rem;">No recovery recommendations matching the selected action filter.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(r => {
    let bannerType = '';
    let badgeClass = 'badge-restock';
    if (r.recommended_action.includes('Dispose') || r.recommended_action.includes('Defective')) {
      bannerType = 'alert';
      badgeClass = 'badge-defective';
    } else if (r.recommended_action.includes('Hold') || r.recommended_action.includes('Liquidate')) {
      bannerType = 'caution';
      badgeClass = 'badge-liquidate';
    } else if (r.recommended_action.includes('Repair') || r.recommended_action.includes('Refurbish')) {
      badgeClass = 'badge-repair';
    }

    return `
      <div class="card" style="margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
          <div>
            <div style="display: flex; align-items: center; gap: 10px;">
              <span class="badge ${badgeClass}" style="font-size: 0.8rem; padding: 4px 10px;">
                ${r.recommended_action}
              </span>
              <span style="font-size: 0.76rem; color: var(--text-muted); font-weight: 600;">${r.return_code} &bull; Order ${r.order_id}</span>
            </div>
            <h4 style="font-size: 1.05rem; font-weight: 700; margin-top: 6px; color: var(--text-main);">
              ${escapeHtml(r.product_name)}
            </h4>
            <div style="font-size: 0.78rem; color: var(--text-secondary);">
              Supplier: ${escapeHtml(r.supplier_name)} &bull; Customer Intake: "${escapeHtml(r.customer_reason)}" &bull; Inspection: ${r.item_condition}
            </div>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="viewReturnModal(${r.id})">
            Full Audit Trail
          </button>
        </div>

        <div class="financial-math-breakdown">
          <div class="math-item">
            <span class="math-item-label">Original Retail Value</span>
            <span class="math-item-value">$${parseFloat(r.financial_value).toFixed(2)}</span>
          </div>
          <div class="math-item">
            <span class="math-item-label">Estimated Net Recovery</span>
            <span class="math-item-value net">$${parseFloat(r.estimated_net_recovery).toFixed(2)}</span>
          </div>
          <div class="math-item">
            <span class="math-item-label">Recovery Margin</span>
            <span class="math-item-value" style="color: var(--brand-primary);">
              ${((parseFloat(r.estimated_net_recovery) / parseFloat(r.financial_value)) * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

document.addEventListener('DOMContentLoaded', () => {
  const filter = document.getElementById('filter-rec-action');
  if (filter) {
    filter.addEventListener('change', () => renderRecommendationsList());
  }
});

window.loadRecommendations = loadRecommendations;
