/**
 * suppliers.js - Supplier root-cause scorecards and vendor risk analytics.
 */

async function loadSuppliersScorecard() {
  try {
    const res = await fetch('/api/suppliers/scorecard');
    const json = await res.json();
    if (json.status !== 'success') return [];
    return json.data;
  } catch (err) {
    console.error('Error loading suppliers scorecard:', err);
    return [];
  }
}

window.loadSuppliersScorecard = loadSuppliersScorecard;
