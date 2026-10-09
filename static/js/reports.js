/**
 * reports.js - Executive report table rendering, financial yields, and CSV exports.
 */

async function loadReports() {
  await Promise.all([
    renderReportSupplierTable(),
    renderReportFinancialTable()
  ]);
}

async function renderReportSupplierTable() {
  const tbody = document.getElementById('reports-supplier-table');
  if (!tbody) return;

  try {
    const suppliers = await window.loadSuppliersScorecard();
    tbody.innerHTML = suppliers.map(s => {
      let statusBadge = '<span class="badge badge-restock">Normal Tolerance</span>';
      if (s.flag_level === 'danger') {
        statusBadge = '<span class="badge badge-defective">High Defect Risk</span>';
      } else if (s.flag_level === 'warning') {
        statusBadge = '<span class="badge badge-liquidate">Packaging Fragility</span>';
      } else if (s.status === 'Insufficient data') {
        statusBadge = '<span class="badge badge-insufficient">Insufficient data (N&lt;3)</span>';
      }

      return `
        <tr>
          <td>
            <strong>${escapeHtml(s.supplier_name)}</strong>
            <div style="font-size: 0.74rem; color: var(--text-muted);">${s.supplier_code} &bull; ${s.category}</div>
          </td>
          <td>${s.units_sold.toLocaleString()}</td>
          <td style="font-weight: 600;">${s.units_returned}</td>
          <td style="color: ${s.confirmed_defects > 0 ? 'var(--color-danger)' : 'inherit'}; font-weight: 700;">
            ${s.confirmed_defects}
          </td>
          <td>${s.return_rate_pct}%</td>
          <td>
            <span class="badge ${s.defect_share_pct > 35 ? 'badge-defective' : 'badge-restock'}">
              ${s.defect_share_pct}%
            </span>
          </td>
          <td style="font-weight: 700;">$${parseFloat(s.financial_impact).toFixed(2)}</td>
          <td>${statusBadge}</td>
          <td style="font-size: 0.78rem; color: var(--text-secondary); max-width: 240px;">
            ${escapeHtml(s.recommendation)}
          </td>
        </tr>
      `;
    }).join('');

  } catch (err) {
    console.error('Error rendering supplier report table:', err);
  }
}

async function renderReportFinancialTable() {
  const tbody = document.getElementById('reports-financial-table');
  if (!tbody) return;

  try {
    const res = await fetch('/api/reports/summary');
    const json = await res.json();
    if (json.status !== 'success') return;

    const data = json.data.recovery_financials;
    tbody.innerHTML = data.map(item => {
      const orig = parseFloat(item.original_value);
      const net = parseFloat(item.net_recovered_value);
      const yieldPct = orig > 0 ? ((net / orig) * 100).toFixed(1) : '0.0';

      return `
        <tr>
          <td><strong>${item.recommended_action}</strong></td>
          <td>${item.unit_count} units</td>
          <td>$${orig.toFixed(2)}</td>
          <td>$${parseFloat(item.gross_recovery).toFixed(2)}</td>
          <td style="color: var(--color-danger);">$${parseFloat(item.total_processing_cost).toFixed(2)}</td>
          <td style="font-weight: 700; color: var(--color-success);">$${net.toFixed(2)}</td>
          <td>
            <span class="badge ${parseFloat(yieldPct) > 70 ? 'badge-restock' : parseFloat(yieldPct) > 40 ? 'badge-repair' : 'badge-dispose'}">
              ${yieldPct}%
            </span>
          </td>
        </tr>
      `;
    }).join('');

  } catch (err) {
    console.error('Error rendering financial report table:', err);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const btnReturns = document.getElementById('btn-export-returns-csv');
  if (btnReturns) {
    btnReturns.addEventListener('click', () => {
      window.location.href = '/api/reports/export?type=returns';
    });
  }

  const btnSuppliers = document.getElementById('btn-export-suppliers-csv');
  if (btnSuppliers) {
    btnSuppliers.addEventListener('click', () => {
      window.location.href = '/api/reports/export?type=suppliers';
    });
  }

  const btnActions = document.getElementById('btn-export-actions-csv');
  if (btnActions) {
    btnActions.addEventListener('click', () => {
      window.location.href = '/api/reports/export?type=actions';
    });
  }
});

window.loadReports = loadReports;
