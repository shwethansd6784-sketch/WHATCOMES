/**
 * app.js - Core application controller, navigation, modal management,
 * metadata loaders, toast notification system, and hackathon demo tour.
 */

window.AppState = {
  currentTab: 'overview',
  products: [],
  suppliers: [],
  metaLoaded: false
};

// ==========================================
// TOAST NOTIFICATIONS
// ==========================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span style="font-weight: 700; text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.05em;">${type}:</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ==========================================
// MODAL CONTROLLERS
// ==========================================
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
  }
}

// Global modal close handlers
document.addEventListener('click', (e) => {
  if (e.target.dataset && e.target.dataset.closeModal) {
    closeModal(e.target.dataset.closeModal);
  }
  if (e.target.classList && e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
  }
});

// ==========================================
// TAB NAVIGATION
// ==========================================
function switchTab(tabId) {
  // Update sidebar active state
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
    if (item.dataset.tab === tabId) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Update tab content panels
  document.querySelectorAll('.page-tab-content').forEach(content => {
    if (content.id === `tab-${tabId}`) {
      content.classList.add('active');
    } else {
      content.classList.remove('active');
    }
  });

  // Update Header title & subtitle
  const titleMap = {
    'overview': { title: 'Overview Dashboard', sub: 'Real-time returns processing, defect analysis, and recovery optimization' },
    'returns': { title: 'Returns Management', sub: 'Complete returns directory, tracking, and physical merchandise status' },
    'inspection': { title: 'Product Inspection Workflow', sub: 'Physical bench triage contrasting customer claims with verified hardware condition' },
    'root-cause': { title: 'Root-Cause Analysis', sub: 'Systemic pattern isolation, defect clustering, and statistical reliability insights' },
    'recommendations': { title: 'Smart Recovery Recommendations', sub: 'Explainable disposition decisions powered by transparent rule-based financial models' },
    'action-centre': { title: 'Action Centre & Corrective Tasks', sub: 'Prioritized operational containment tasks, vendor audits, and catalog updates' },
    'reports': { title: 'Reports & Executive Summary', sub: 'Auditable summaries of financial loss, recovery yields, and supplier risk matrices' },
    'settings': { title: 'Settings & Demo Controls', sub: 'System configuration, demo data reset, and architecture reference' }
  };

  const currentInfo = titleMap[tabId] || { title: 'ReturnWise', sub: 'Smart Returns Advisor' };
  document.getElementById('current-page-title').textContent = currentInfo.title;
  document.getElementById('current-page-subtitle').textContent = currentInfo.sub;

  window.AppState.currentTab = tabId;

  // Refresh tab data
  if (tabId === 'overview' && window.loadDashboard) window.loadDashboard();
  if (tabId === 'returns' && window.loadReturns) window.loadReturns();
  if (tabId === 'inspection' && window.loadInspectionData) window.loadInspectionData();
  if (tabId === 'root-cause' && window.loadRootCause) window.loadRootCause();
  if (tabId === 'recommendations' && window.loadRecommendations) window.loadRecommendations();
  if (tabId === 'action-centre' && window.loadActions) window.loadActions();
  if (tabId === 'reports' && window.loadReports) window.loadReports();

  // Close mobile sidebar if open
  document.getElementById('sidebar').classList.remove('mobile-open');
}

// ==========================================
// METADATA LOADER (Dropdowns)
// ==========================================
async function loadMetadata() {
  try {
    const res = await fetch('/api/meta');
    const data = await res.json();
    if (data.status === 'success') {
      window.AppState.products = data.data.products;
      window.AppState.suppliers = data.data.suppliers;
      window.AppState.metaLoaded = true;

      // Populate Returns Filter Product dropdown
      const filterProd = document.getElementById('filter-returns-product');
      if (filterProd) {
        filterProd.innerHTML = '<option value="">All Products</option>';
        data.data.products.forEach(p => {
          const opt = document.createElement('option');
          opt.value = p.id;
          opt.textContent = p.name;
          filterProd.appendChild(opt);
        });
      }

      // Populate Returns Filter Supplier dropdown
      const filterSupp = document.getElementById('filter-returns-supplier');
      if (filterSupp) {
        filterSupp.innerHTML = '<option value="">All Suppliers</option>';
        data.data.suppliers.forEach(s => {
          const opt = document.createElement('option');
          opt.value = s.id;
          opt.textContent = s.name;
          filterSupp.appendChild(opt);
        });
      }

      // Populate Add Return Modal Product select
      const modalProd = document.getElementById('modal-add-product');
      if (modalProd) {
        modalProd.innerHTML = '<option value="">-- Select Product --</option>';
        data.data.products.forEach(p => {
          const opt = document.createElement('option');
          opt.value = p.id;
          opt.textContent = `${p.name} ($${p.retail_price})`;
          modalProd.appendChild(opt);
        });
      }
    }
  } catch (err) {
    console.warn('Could not load metadata from backend API:', err);
  }
}

// ==========================================
// HACKATHON DEMO WALKTHROUGH STEPS
// ==========================================
function initDemoStepper() {
  document.querySelectorAll('.demo-step-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const step = parseInt(btn.dataset.step, 10);
      executeDemoStep(step);
    });
  });
}

function executeDemoStep(step) {
  // Highlight active step button
  document.querySelectorAll('.demo-step-btn').forEach(btn => {
    btn.classList.toggle('highlight', parseInt(btn.dataset.step, 10) === step);
  });

  switch (step) {
    case 1:
      // Step 1: Open dashboard and show overall returns situation
      switchTab('overview');
      showToast('Step 1: Inspecting overall returns volume, financial loss, and recoverable value.', 'info');
      break;

    case 2:
      // Step 2: Open returned headphone record (RET-1002) with customer complaint about audio failure
      switchTab('returns');
      const searchInput = document.getElementById('filter-returns-search');
      if (searchInput) {
        searchInput.value = 'RET-1002';
        window.loadReturns();
      }
      showToast('Step 2: Found return RET-1002 (AuraWave Headphones - Audio cutout complaint).', 'info');
      break;

    case 3:
      // Step 3: Open inspection page pre-filled with RET-1002
      switchTab('inspection');
      setTimeout(() => {
        const select = document.getElementById('insp-return-select');
        if (select) {
          // Find option for RET-1002
          for (let opt of select.options) {
            if (opt.text.includes('RET-1002')) {
              select.value = opt.value;
              select.dispatchEvent(new Event('change'));
              break;
            }
          }
        }
        // Pre-fill bench defect findings
        document.getElementById('insp-condition').value = 'Confirmed defective';
        document.getElementById('insp-functionality').value = 'Complete Failure / Dead';
        document.getElementById('insp-packaging').value = 'Opened Intact';
        document.getElementById('insp-notes').value = 'Acoustic driver coil open-circuit confirmed on audio bench analyzer. Left driver completely unresponsive.';
        showToast('Step 3: Bench inspection details set confirming audio defect. Ready to save!', 'info');
      }, 250);
      break;

    case 4:
      // Step 4: Show Recovery Recommendations
      switchTab('recommendations');
      showToast('Step 4: Smart Recovery Advisor recommends holding for OEM repair / supplier claim with $75.49 net recovery.', 'info');
      break;

    case 5:
      // Step 5: Root-cause analysis identifying repeated confirmed defect pattern for SoundCraft Technologies
      switchTab('root-cause');
      showToast('Step 5: Root-cause engine identified Acoustic Driver Failure pattern on AuraWave Headphones (Supplier: SoundCraft Technologies).', 'info');
      break;

    case 6:
      // Step 6: Create or view corrective action ACT-101 for supplier quality team
      switchTab('action-centre');
      showToast('Step 6: Corrective Action ACT-101 assigned to QA Lead for formal 8D supplier quality investigation.', 'info');
      break;

    case 7:
      // Step 7: Open unopened product (RET-1014) to demonstrate instant restock recommendation
      switchTab('inspection');
      setTimeout(() => {
        const select = document.getElementById('insp-return-select');
        if (select) {
          for (let opt of select.options) {
            if (opt.text.includes('RET-1014')) {
              select.value = opt.value;
              select.dispatchEvent(new Event('change'));
              break;
            }
          }
        }
        document.getElementById('insp-condition').value = 'Unopened';
        document.getElementById('insp-functionality').value = 'Untested';
        document.getElementById('insp-packaging').value = 'Original Sealed';
        document.getElementById('insp-notes').value = 'Factory seal pristine and untouched. Eligible for immediate Grade-A restock.';
        showToast('Step 7: Pre-filled unopened return RET-1014 (PulseFit Pro Smartwatch) for 100% restock recovery.', 'info');
      }, 250);
      break;

    case 8:
      // Step 8: View live reports & financial recovery audit
      switchTab('reports');
      showToast('Step 8: Auditing complete financial recovery yield breakdown and supplier defect scoreboard.', 'info');
      break;
  }
}

// ==========================================
// SYSTEM RESET DEMO DATA
// ==========================================
function initResetDemo() {
  const triggerBtn = document.getElementById('btn-trigger-reset-demo');
  if (triggerBtn) {
    triggerBtn.addEventListener('click', () => {
      openModal('modal-confirm-reset');
    });
  }

  const confirmBtn = document.getElementById('btn-confirm-reset-execute');
  if (confirmBtn) {
    confirmBtn.addEventListener('click', async () => {
      confirmBtn.disabled = true;
      confirmBtn.textContent = 'Resetting...';
      try {
        const res = await fetch('/api/system/reset-demo', { method: 'POST' });
        const data = await res.json();
        closeModal('modal-confirm-reset');
        showToast(data.message || 'Demo data successfully reset!', 'success');
        // Refresh all views
        loadMetadata();
        switchTab('overview');
      } catch (err) {
        showToast('Failed to reset demo data: ' + err.message, 'error');
      } finally {
        confirmBtn.disabled = false;
        confirmBtn.textContent = 'Reset Database';
      }
    });
  }
}

// ==========================================
// INITIALIZATION ON DOM LOAD
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  // Sidebar navigation listeners
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const tabId = item.dataset.tab;
      if (tabId) switchTab(tabId);
    });
  });

  // Mobile sidebar toggle
  const toggleBtn = document.getElementById('sidebar-toggle');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      document.getElementById('sidebar').classList.toggle('mobile-open');
    });
  }

  // Quick action header buttons
  const quickNewReturnBtn = document.getElementById('btn-quick-new-return');
  if (quickNewReturnBtn) {
    quickNewReturnBtn.addEventListener('click', () => {
      openModal('modal-add-return');
      document.getElementById('modal-add-date').value = new Date().toISOString().split('T')[0];
    });
  }

  const quickInspectBtn = document.getElementById('btn-quick-inspect');
  if (quickInspectBtn) {
    quickInspectBtn.addEventListener('click', () => {
      switchTab('inspection');
    });
  }

  const viewAllActionsBtn = document.getElementById('btn-view-all-actions');
  if (viewAllActionsBtn) {
    viewAllActionsBtn.addEventListener('click', () => {
      switchTab('action-centre');
    });
  }

  // Initialize modules
  loadMetadata();
  initDemoStepper();
  initResetDemo();

  // Default to overview tab
  switchTab('overview');
});
