/**
 * returns.js - Returns directory table, live filtering, Add Return modal, and View details.
 */

let returnsData = [];

async function loadReturns() {
  const search = document.getElementById('filter-returns-search')?.value || '';
  const product_id = document.getElementById('filter-returns-product')?.value || '';
  const supplier_id = document.getElementById('filter-returns-supplier')?.value || '';
  const reason = document.getElementById('filter-returns-reason')?.value || '';
  const status = document.getElementById('filter-returns-status')?.value || '';

  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (product_id) params.append('product_id', product_id);
  if (supplier_id) params.append('supplier_id', supplier_id);
  if (reason) params.append('reason', reason);
  if (status) params.append('status', status);

  try {
    const res = await fetch(`/api/returns?${params.toString()}`);
    const json = await res.json();
    if (json.status !== 'success') return;

    returnsData = json.data;
    renderReturnsTable(returnsData);

  } catch (err) {
    console.error('Error loading returns:', err);
  }
}

function renderReturnsTable(items) {
  const tbody = document.getElementById('returns-table-body');
  if (!tbody) return;

  if (items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="10" style="text-align: center; padding: 36px; color: var(--text-muted);">
          No return records found matching the active filter criteria.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = items.map(r => {
    // Determine status badge
    let statusBadge = '<span class="badge badge-pending">Pending Inspection</span>';
    if (r.inspection_id) {
      if (r.item_condition === 'Confirmed defective') {
        statusBadge = '<span class="badge badge-defective">Defective</span>';
      } else if (r.item_condition === 'Unopened') {
        statusBadge = '<span class="badge badge-restock">Unopened</span>';
      } else if (r.item_condition === 'Opened and working') {
        statusBadge = '<span class="badge badge-repair">Functional</span>';
      } else {
        statusBadge = '<span class="badge badge-inspected">Inspected</span>';
      }
    }

    // Determine recovery badge
    let recBadge = '<span style="color: var(--text-muted); font-size: 0.76rem;">—</span>';
    if (r.recommended_action) {
      if (r.recommended_action.includes('Restock')) {
        recBadge = `<span class="badge badge-restock">Restock ($${r.estimated_net_recovery})</span>`;
      } else if (r.recommended_action.includes('Repair')) {
        recBadge = `<span class="badge badge-repair">Repair ($${r.estimated_net_recovery})</span>`;
      } else if (r.recommended_action.includes('Refurbish')) {
        recBadge = `<span class="badge badge-repair">Refurbish ($${r.estimated_net_recovery})</span>`;
      } else if (r.recommended_action.includes('Liquidate')) {
        recBadge = `<span class="badge badge-liquidate">Liquidate ($${r.estimated_net_recovery})</span>`;
      } else if (r.recommended_action.includes('Dispose')) {
        recBadge = `<span class="badge badge-dispose">Dispose</span>`;
      } else {
        recBadge = `<span class="badge badge-pending">Hold for QA</span>`;
      }
    }

    return `
      <tr>
        <td><strong>${r.return_code}</strong></td>
        <td style="color: var(--text-secondary);">${r.order_id}</td>
        <td>
          <div style="font-weight: 600; color: var(--text-main);">${escapeHtml(r.product_name)}</div>
          <div style="font-size: 0.74rem; color: var(--text-muted);">${r.product_sku} &bull; ${r.product_category}</div>
        </td>
        <td style="color: var(--text-secondary);">${escapeHtml(r.supplier_name)}</td>
        <td>
          <span style="font-size: 0.8rem; font-weight: 500;">${r.customer_reason}</span>
          ${r.customer_comment ? `<div style="font-size: 0.72rem; color: var(--text-muted); max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${escapeHtml(r.customer_comment)}">"${escapeHtml(r.customer_comment)}"</div>` : ''}
        </td>
        <td style="white-space: nowrap; color: var(--text-secondary);">${r.return_date}</td>
        <td>${statusBadge}</td>
        <td style="font-weight: 700;">$${parseFloat(r.financial_value).toFixed(2)}</td>
        <td>${recBadge}</td>
        <td style="text-align: right; white-space: nowrap;">
          <button class="btn btn-secondary btn-sm" onclick="viewReturnModal(${r.id})">Details</button>
          ${!r.inspection_id ? `<button class="btn btn-primary btn-sm" onclick="jumpToInspection(${r.id})">Inspect</button>` : ''}
        </td>
      </tr>
    `;
  }).join('');
}

// ==========================================
// VIEW RETURN MODAL
// ==========================================
async function viewReturnModal(returnId) {
  try {
    const res = await fetch(`/api/returns/${returnId}`);
    const json = await res.json();
    if (json.status !== 'success') return;

    const r = json.data;
    document.getElementById('view-modal-title').textContent = `${r.return_code} — Return Details`;

    let inspectionHtml = `
      <div style="background: #FFFBEB; border: 1px solid #FDE68A; padding: 12px; border-radius: var(--radius-md); font-size: 0.85rem; color: #92400E;">
        <strong>Pending Physical Bench Inspection:</strong> This returned product has not yet been checked by a triage technician.
      </div>
    `;

    if (r.inspection_id) {
      inspectionHtml = `
        <div style="background: #F8FAFC; border: 1px solid var(--border-light); padding: 14px; border-radius: var(--radius-md);">
          <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <strong style="color: var(--text-main);">Physical Inspection Findings (Bench Verified)</strong>
            <span style="font-size: 0.75rem; color: var(--text-muted);">${r.inspection_date} &bull; ${r.inspector_name}</span>
          </div>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; font-size: 0.82rem; margin-bottom: 10px;">
            <div><strong>Item Condition:</strong> <span class="badge ${r.item_condition === 'Confirmed defective' ? 'badge-defective' : 'badge-restock'}">${r.item_condition}</span></div>
            <div><strong>Functionality:</strong> ${r.functionality_status}</div>
            <div><strong>Packaging:</strong> ${r.packaging_condition}</div>
            <div><strong>Missing Parts:</strong> ${r.missing_components || 'None'}</div>
          </div>
          <div style="font-size: 0.82rem; color: var(--text-secondary); background: #FFFFFF; padding: 8px 12px; border-radius: var(--radius-sm); border: 1px solid var(--border-light);">
            <strong>Bench Diagnostic Notes:</strong> ${escapeHtml(r.inspection_notes || 'No technical notes recorded.')}
          </div>
        </div>
      `;
    }

    let recHtml = '';
    if (r.recommendation_id) {
      recHtml = `
        <div style="margin-top: 16px; background: #F0FDF4; border: 1px solid #BBF7D0; padding: 14px; border-radius: var(--radius-md);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <strong style="color: #166534; font-size: 0.95rem;">Smart Recovery Recommendation: ${r.recommended_action}</strong>
            <span class="badge badge-restock">${r.confidence_score} Confidence (${r.confidence_pct}%)</span>
          </div>
          <p style="font-size: 0.82rem; color: #166534; margin-bottom: 8px;">${r.rec_reason}</p>
          <div style="font-size: 0.75rem; color: #15803D;"><strong>Triggered Business Rule:</strong> ${r.rule_triggered}</div>
          <div class="financial-math-breakdown" style="margin-top: 10px;">
            <div class="math-item">
              <span class="math-item-label">Resale Recovery</span>
              <span class="math-item-value">$${parseFloat(r.estimated_recovery_value).toFixed(2)}</span>
            </div>
            <div class="math-item">
              <span class="math-item-label">Processing / Triage</span>
              <span class="math-item-value">$${parseFloat(r.estimated_processing_cost).toFixed(2)}</span>
            </div>
            <div class="math-item">
              <span class="math-item-label">Net Recovered Value</span>
              <span class="math-item-value net">$${parseFloat(r.estimated_net_recovery).toFixed(2)}</span>
            </div>
          </div>
        </div>
      `;
    }

    const content = document.getElementById('view-modal-content');
    content.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-bottom: 16px; font-size: 0.85rem;">
        <div><strong>Order ID:</strong> ${r.order_id}</div>
        <div><strong>Customer Name:</strong> ${escapeHtml(r.customer_name)}</div>
        <div><strong>Product:</strong> ${escapeHtml(r.product_name)} (${r.product_sku})</div>
        <div><strong>Manufacturer:</strong> ${escapeHtml(r.supplier_name)}</div>
        <div><strong>Return Date:</strong> ${r.return_date}</div>
        <div><strong>Original Retail Price:</strong> $${parseFloat(r.retail_price).toFixed(2)}</div>
      </div>

      <div style="background: #FFFFFF; border: 1px solid var(--border-light); padding: 12px; border-radius: var(--radius-md); margin-bottom: 16px;">
        <span style="font-size: 0.75rem; font-weight: 700; color: #B45309; text-transform: uppercase;">Customer Intake Claim</span>
        <div style="font-weight: 600; margin-top: 2px;">${r.customer_reason}</div>
        <p style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 4px;">"${escapeHtml(r.customer_comment || 'No comment provided by customer.')}"</p>
      </div>

      ${inspectionHtml}
      ${recHtml}
    `;

    // Setup "Inspect This Item" button
    const inspectBtn = document.getElementById('btn-modal-go-inspect');
    if (inspectBtn) {
      if (r.inspection_id) {
        inspectBtn.textContent = 'Re-Inspect Item';
      } else {
        inspectBtn.textContent = 'Inspect This Item';
      }
      inspectBtn.onclick = () => {
        closeModal('modal-view-return');
        jumpToInspection(r.id);
      };
    }

    openModal('modal-view-return');

  } catch (err) {
    console.error('Error viewing return detail:', err);
  }
}

function jumpToInspection(returnId) {
  switchTab('inspection');
  setTimeout(() => {
    const select = document.getElementById('insp-return-select');
    if (select) {
      select.value = returnId;
      select.dispatchEvent(new Event('change'));
    }
  }, 200);
}

// ==========================================
// ADD RETURN FORM SUBMISSION
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  // Filter triggers
  ['filter-returns-search', 'filter-returns-product', 'filter-returns-supplier', 'filter-returns-reason', 'filter-returns-status'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', () => loadReturns());
      el.addEventListener('change', () => loadReturns());
    }
  });

  const resetBtn = document.getElementById('btn-reset-returns-filter');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      document.getElementById('filter-returns-search').value = '';
      document.getElementById('filter-returns-product').value = '';
      document.getElementById('filter-returns-supplier').value = '';
      document.getElementById('filter-returns-reason').value = '';
      document.getElementById('filter-returns-status').value = '';
      loadReturns();
    });
  }

  const openAddBtn = document.getElementById('btn-open-add-return');
  if (openAddBtn) {
    openAddBtn.addEventListener('click', () => {
      openModal('modal-add-return');
      document.getElementById('modal-add-date').value = new Date().toISOString().split('T')[0];
    });
  }

  const form = document.getElementById('form-add-return');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const product_id = document.getElementById('modal-add-product').value;
      const order_id = document.getElementById('modal-add-order').value.trim();
      const customer_name = document.getElementById('modal-add-customer').value.trim();
      const return_date = document.getElementById('modal-add-date').value;
      const customer_reason = document.getElementById('modal-add-reason').value;
      const customer_comment = document.getElementById('modal-add-comment').value.trim();

      if (!product_id || !order_id || !customer_name || !customer_reason) {
        showToast('Please fill all required fields.', 'error');
        return;
      }

      try {
        const res = await fetch('/api/returns', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_id: parseInt(product_id, 10),
            order_id,
            customer_name,
            return_date,
            customer_reason,
            customer_comment
          })
        });

        const data = await res.json();
        if (data.status === 'success') {
          closeModal('modal-add-return');
          form.reset();
          showToast(data.message || 'Return registered successfully!', 'success');
          loadReturns();
          if (window.loadDashboard) window.loadDashboard();
        } else {
          showToast(data.message || 'Error creating return.', 'error');
        }
      } catch (err) {
        showToast('Network error saving return record.', 'error');
      }
    });
  }
});

window.loadReturns = loadReturns;
window.viewReturnModal = viewReturnModal;
window.jumpToInspection = jumpToInspection;
