/**
 * inspection.js - Physical product bench triage workflow and instant recovery advisor reveal.
 */

let allReturnsList = [];

async function loadInspectionData() {
  const dateInput = document.getElementById('insp-date');
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().split('T')[0];
  }

  try {
    const res = await fetch('/api/returns');
    const json = await res.json();
    if (json.status !== 'success') return;

    allReturnsList = json.data;
    populateInspectionDropdown(allReturnsList);

  } catch (err) {
    console.error('Error loading inspection candidates:', err);
  }
}

function populateInspectionDropdown(returns) {
  const select = document.getElementById('insp-return-select');
  if (!select) return;

  const currentVal = select.value;
  select.innerHTML = '<option value="">-- Choose Return ID to triage --</option>';

  const pendingGroup = document.createElement('optgroup');
  pendingGroup.label = 'Pending Bench Triage (Action Required)';

  const inspectedGroup = document.createElement('optgroup');
  inspectedGroup.label = 'Already Inspected (Review / Re-test)';

  returns.forEach(r => {
    const opt = document.createElement('option');
    opt.value = r.id;
    opt.textContent = `${r.return_code} — ${r.product_name} (${r.customer_reason}) [${r.status}]`;

    if (!r.inspection_id) {
      pendingGroup.appendChild(opt);
    } else {
      inspectedGroup.appendChild(opt);
    }
  });

  select.appendChild(pendingGroup);
  select.appendChild(inspectedGroup);

  if (currentVal) select.value = currentVal;
}

// When user selects a return, load its item profile and previous inspection if any
async function handleReturnSelection(returnId) {
  const card = document.getElementById('insp-selected-card');
  const liveRec = document.getElementById('insp-live-recommendation-box');
  if (!returnId) {
    if (card) card.style.display = 'none';
    if (liveRec) liveRec.style.display = 'none';
    return;
  }

  try {
    const res = await fetch(`/api/returns/${returnId}`);
    const json = await res.json();
    if (json.status !== 'success') return;

    const r = json.data;

    // Show selected product details
    document.getElementById('insp-disp-product-name').textContent = `${r.product_name} (${r.product_sku})`;
    document.getElementById('insp-disp-meta').textContent = `Order: ${r.order_id} • Supplier: ${r.supplier_name} • Category: ${r.product_category}`;
    document.getElementById('insp-disp-price').textContent = `$${parseFloat(r.retail_price).toFixed(2)}`;
    document.getElementById('insp-disp-reason-text').textContent = `Customer stated: "${r.customer_reason}" — ${r.customer_comment || 'No additional comments provided.'}`;

    if (card) card.style.display = 'block';

    // If item was already inspected, populate the form
    if (r.inspection_id) {
      document.getElementById('insp-condition').value = r.item_condition;
      document.getElementById('insp-functionality').value = r.functionality_status;
      document.getElementById('insp-packaging').value = r.packaging_condition;
      document.getElementById('insp-missing').value = r.missing_components || 'None';
      document.getElementById('insp-inspector').value = r.inspector_name;
      document.getElementById('insp-date').value = r.inspection_date;
      document.getElementById('insp-notes').value = r.inspection_notes || '';

      if (r.recommendation_id) {
        revealLiveRecommendation({
          recommended_action: r.recommended_action,
          reason: r.rec_reason,
          rule_triggered: r.rule_triggered,
          estimated_recovery_value: r.estimated_recovery_value,
          estimated_processing_cost: r.estimated_processing_cost,
          estimated_net_recovery: r.estimated_net_recovery,
          confidence_score: r.confidence_score,
          confidence_pct: r.confidence_pct
        });
      }
    } else {
      // Clear form for fresh inspection
      document.getElementById('insp-condition').value = '';
      document.getElementById('insp-functionality').value = 'Fully Functional';
      document.getElementById('insp-packaging').value = 'Opened Intact';
      document.getElementById('insp-missing').value = 'None';
      document.getElementById('insp-notes').value = '';
      if (liveRec) liveRec.style.display = 'none';
    }

  } catch (err) {
    console.error('Error fetching return for inspection:', err);
  }
}

function revealLiveRecommendation(rec) {
  const box = document.getElementById('insp-live-recommendation-box');
  const banner = document.getElementById('insp-rec-banner');
  if (!box || !banner) return;

  document.getElementById('insp-rec-action').textContent = rec.recommended_action;
  document.getElementById('insp-rec-confidence').textContent = `${rec.confidence_score} Confidence (${rec.confidence_pct}%)`;
  document.getElementById('insp-rec-reason').textContent = rec.reason;
  document.getElementById('insp-rec-rule').textContent = `Triggered Rule: ${rec.rule_triggered}`;

  document.getElementById('insp-rec-resale').textContent = `$${parseFloat(rec.estimated_recovery_value).toFixed(2)}`;
  document.getElementById('insp-rec-cost').textContent = `$${parseFloat(rec.estimated_processing_cost).toFixed(2)}`;
  document.getElementById('insp-rec-net').textContent = `$${parseFloat(rec.estimated_net_recovery).toFixed(2)}`;

  // Styling banner based on outcome
  banner.className = 'recommendation-banner';
  if (rec.recommended_action.includes('Dispose') || rec.recommended_action.includes('Defective')) {
    banner.classList.add('alert');
  } else if (rec.recommended_action.includes('Hold') || rec.recommended_action.includes('Liquidate')) {
    banner.classList.add('caution');
  }

  box.style.display = 'block';
  box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ==========================================
// SUBMIT INSPECTION
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  const select = document.getElementById('insp-return-select');
  if (select) {
    select.addEventListener('change', (e) => {
      handleReturnSelection(e.target.value);
    });
  }

  const clearBtn = document.getElementById('btn-clear-insp');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      const selectEl = document.getElementById('insp-return-select');
      if (selectEl) selectEl.value = '';
      handleReturnSelection('');
    });
  }

  const form = document.getElementById('inspection-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const return_id = document.getElementById('insp-return-select').value;
      if (!return_id) {
        showToast('Please select a return item to triage.', 'error');
        return;
      }

      const item_condition = document.getElementById('insp-condition').value;
      const functionality_status = document.getElementById('insp-functionality').value;
      const packaging_condition = document.getElementById('insp-packaging').value;
      const missing_components = document.getElementById('insp-missing').value.trim() || 'None';
      const inspector_name = document.getElementById('insp-inspector').value.trim();
      const inspection_date = document.getElementById('insp-date').value;
      const inspection_notes = document.getElementById('insp-notes').value.trim();

      const saveBtn = document.getElementById('btn-save-insp');
      saveBtn.disabled = true;
      saveBtn.textContent = 'Analyzing & Saving...';

      try {
        const res = await fetch('/api/inspections', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            return_id: parseInt(return_id, 10),
            item_condition,
            functionality_status,
            packaging_condition,
            missing_components,
            inspector_name,
            inspection_date,
            inspection_notes
          })
        });

        const data = await res.json();
        if (data.status === 'success') {
          showToast(data.message, 'success');
          revealLiveRecommendation(data.data.recommendation);
          // Refresh dropdown list
          loadInspectionData();
          // Refresh background stats
          if (window.loadDashboard) window.loadDashboard();
        } else {
          showToast(data.message || 'Error recording inspection.', 'error');
        }
      } catch (err) {
        showToast('Network error while saving inspection.', 'error');
      } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
          Save Inspection & Generate Recommendation
        `;
      }
    });
  }
});

window.loadInspectionData = loadInspectionData;
