/**
 * actions.js - Action Centre task management, status updates, and creation modal.
 */

let allActionsList = [];

async function loadActions() {
  const status = document.getElementById('filter-action-status')?.value || '';
  const priority = document.getElementById('filter-action-priority')?.value || '';

  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (priority) params.append('priority', priority);

  try {
    const res = await fetch(`/api/actions?${params.toString()}`);
    const json = await res.json();
    if (json.status !== 'success') return;

    allActionsList = json.data;
    renderActionsTable(allActionsList);

  } catch (err) {
    console.error('Error loading actions:', err);
  }
}

function renderActionsTable(actions) {
  const tbody = document.getElementById('actions-table-body');
  if (!tbody) return;

  if (actions.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align: center; padding: 36px; color: var(--text-muted);">
          No corrective actions found matching the filters.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = actions.map(act => {
    let statusClass = 'badge-pending';
    if (act.status === 'Resolved') statusClass = 'badge-restock';
    if (act.status === 'In Progress') statusClass = 'badge-repair';

    return `
      <tr>
        <td><strong>${act.action_code}</strong></td>
        <td>
          <span class="action-priority-tag ${act.priority}">${act.priority}</span>
        </td>
        <td>
          <div style="font-weight: 600; color: var(--text-main);">${escapeHtml(act.title)}</div>
          <div style="font-size: 0.74rem; color: var(--text-secondary); max-width: 280px; margin-top: 2px;">
            ${escapeHtml(act.evidence.substring(0, 95))}...
          </div>
        </td>
        <td>
          <span class="badge" style="background: #F1F5F9; color: var(--text-main);">${act.related_type}</span>
          <div style="font-size: 0.8rem; font-weight: 500; margin-top: 2px;">${escapeHtml(act.related_id)}</div>
        </td>
        <td style="color: var(--text-secondary); font-size: 0.82rem;">${escapeHtml(act.assigned_to)}</td>
        <td style="color: var(--text-secondary); white-space: nowrap; font-size: 0.82rem;">${act.due_date}</td>
        <td>
          <select class="form-control" style="height: 30px; font-size: 0.78rem; width: 120px; padding: 2px 6px;" onchange="updateActionStatus(${act.id}, this.value)">
            <option value="Open" ${act.status === 'Open' ? 'selected' : ''}>Open</option>
            <option value="In Progress" ${act.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
            <option value="Resolved" ${act.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
          </select>
        </td>
        <td style="font-size: 0.8rem; color: #166534; font-weight: 500;">
          ${escapeHtml(act.estimated_impact || 'Containment')}
        </td>
        <td style="text-align: right;">
          <button class="btn btn-secondary btn-sm" onclick="showActionNotesModal(${act.id})">Notes</button>
        </td>
      </tr>
    `;
  }).join('');
}

async function updateActionStatus(actionId, newStatus) {
  try {
    const res = await fetch(`/api/actions/${actionId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(`Action status updated to "${newStatus}"`, 'success');
      loadActions();
      if (window.loadDashboard) window.loadDashboard();
    }
  } catch (err) {
    showToast('Failed to update action status.', 'error');
  }
}

function showActionNotesModal(actionId) {
  const act = allActionsList.find(a => a.id === actionId);
  if (!act) return;

  const notes = prompt(`Add internal notes / progress log for ${act.action_code}:`, act.notes || '');
  if (notes !== null && notes !== act.notes) {
    fetch(`/api/actions/${actionId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes })
    }).then(() => {
      showToast('Notes saved successfully.', 'success');
      loadActions();
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  ['filter-action-status', 'filter-action-priority'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', () => loadActions());
  });

  const openAddBtn = document.getElementById('btn-open-add-action');
  if (openAddBtn) {
    openAddBtn.addEventListener('click', () => {
      openModal('modal-add-action');
    });
  }

  const form = document.getElementById('form-add-action');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('modal-act-title').value.trim();
      const related_type = document.getElementById('modal-act-type').value;
      const related_id = document.getElementById('modal-act-entity').value.trim();
      const priority = document.getElementById('modal-act-priority').value;
      const assigned_to = document.getElementById('modal-act-assignee').value.trim();
      const evidence = document.getElementById('modal-act-evidence').value.trim();
      const estimated_impact = document.getElementById('modal-act-impact').value.trim();

      if (!title || !related_id || !evidence) {
        showToast('Please complete all required fields.', 'error');
        return;
      }

      try {
        const res = await fetch('/api/actions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title,
            related_type,
            related_id,
            priority,
            assigned_to,
            evidence,
            estimated_impact
          })
        });

        const data = await res.json();
        if (data.status === 'success') {
          closeModal('modal-add-action');
          form.reset();
          showToast(data.message || 'Action created successfully!', 'success');
          loadActions();
          if (window.loadDashboard) window.loadDashboard();
        } else {
          showToast(data.message || 'Error creating action.', 'error');
        }
      } catch (err) {
        showToast('Network error creating corrective action.', 'error');
      }
    });
  }
});

window.loadActions = loadActions;
window.updateActionStatus = updateActionStatus;
window.showActionNotesModal = showActionNotesModal;
