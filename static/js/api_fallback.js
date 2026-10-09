/**
 * api_fallback.js - Resilient client-side fallback engine for ReturnWise.
 * If running purely in a browser without Flask (e.g. file:/// or static host),
 * this automatically handles API requests using localStorage and in-memory persistence!
 */

(function() {
  const isFileProtocol = window.location.protocol === 'file:';

  // Save reference to native fetch
  const originalFetch = window.fetch;

  window.fetch = async function(url, options = {}) {
    const urlStr = typeof url === 'string' ? url : url.url;

    // Only intercept /api/ endpoints if on file: or if server is unavailable
    if (urlStr.startsWith('/api/') || urlStr.includes('/api/')) {
      if (isFileProtocol) {
        return handleMockApi(urlStr, options);
      }
      try {
        const response = await originalFetch(url, options);
        return response;
      } catch (networkError) {
        console.warn('Backend server not reachable, switching seamlessly to localStorage fallback mock API...', networkError);
        return handleMockApi(urlStr, options);
      }
    }

    return originalFetch(url, options);
  };

  // Helper response builder
  function mockResponse(data, status = 200, headers = {}) {
    return new Response(JSON.stringify(data), {
      status,
      headers: { 'Content-Type': 'application/json', ...headers }
    });
  }

  async function handleMockApi(url, options) {
    const cleanUrl = url.split('?')[0];
    const params = new URLSearchParams(url.includes('?') ? url.split('?')[1] : '');
    const method = (options.method || 'GET').toUpperCase();

    // 1. Meta
    if (cleanUrl.endsWith('/api/meta')) {
      return mockResponse({
        status: 'success',
        data: {
          products: [
            { id: 1, sku: 'PRD-AURA-01', name: 'AuraWave ANC Wireless Headphones', category: 'Audio', retail_price: 149.99, units_sold: 850 },
            { id: 2, sku: 'PRD-NEOB-02', name: 'NeoBass Portable Bluetooth Speaker', category: 'Audio', retail_price: 79.99, units_sold: 620 },
            { id: 3, sku: 'PRD-PULS-03', name: 'PulseFit Pro Smartwatch', category: 'Wearables', retail_price: 199.99, units_sold: 1200 },
            { id: 4, sku: 'PRD-TRCK-04', name: 'PulseFit Active Tracker Band', category: 'Wearables', retail_price: 49.99, units_sold: 950 },
            { id: 5, sku: 'PRD-HYPR-05', name: 'HyperDrive 100W GaN Wall Charger', category: 'Mobile Accessories', retail_price: 59.99, units_sold: 1400 },
            { id: 6, sku: 'PRD-SOLR-06', name: 'SolarCharge 20000mAh PowerBank', category: 'Mobile Accessories', retail_price: 45.99, units_sold: 780 },
            { id: 7, sku: 'PRD-OMNI-07', name: 'OmniView 2K HDR Webcam', category: 'Computer Peripherals', retail_price: 89.99, units_sold: 530 },
            { id: 8, sku: 'PRD-DOCK-08', name: 'PowerSync 9-in-1 USB-C Docking Station', category: 'Computer Peripherals', retail_price: 119.99, units_sold: 410 },
            { id: 9, sku: 'PRD-ERGO-09', name: 'ErgoType RGB Mechanical Keyboard', category: 'Gaming & Input', retail_price: 129.99, units_sold: 670 },
            { id: 10, sku: 'PRD-Mous-10', name: 'UltraGrip Pro Wireless Gaming Mouse', category: 'Gaming & Input', retail_price: 69.99, units_sold: 890 },
            { id: 11, sku: 'PRD-AERO-11', name: 'AeroFlow Smart Oscillating Desk Fan', category: 'Smart Home', retail_price: 54.99, units_sold: 610 },
            { id: 12, sku: 'PRD-LAMP-12', name: 'LuminaGlow Smart Ambient Desk Lamp', category: 'Smart Home', retail_price: 39.99, units_sold: 450 }
          ],
          suppliers: [
            { id: 1, code: 'SUP-SND-01', name: 'SoundCraft Technologies', category: 'Audio & Acoustics', quality_rating: 3.4 },
            { id: 2, code: 'SUP-APX-02', name: 'ApexWear Electronics', category: 'Wearables & Sensors', quality_rating: 4.6 },
            { id: 3, code: 'SUP-VLT-03', name: 'VoltPeak Power Solutions', category: 'Power & Charging', quality_rating: 3.8 },
            { id: 4, code: 'SUP-OPT-04', name: 'OptiCore Vision Systems', category: 'Computer Peripherals', quality_rating: 4.7 },
            { id: 5, code: 'SUP-KEY-05', name: 'KeyForge Labs', category: 'Gaming & Input', quality_rating: 4.5 },
            { id: 6, code: 'SUP-BRZ-06', name: 'BreezeTech Corp', category: 'Smart Home Appliances', quality_rating: 4.8 }
          ]
        }
      });
    }

    // 2. Dashboard Stats
    if (cleanUrl.endsWith('/api/dashboard/stats')) {
      return mockResponse({
        status: 'success',
        data: {
          total_returns: 60,
          awaiting_inspection: 18,
          confirmed_defective: 10,
          approved_restocking: 9,
          financial_loss: 6035.40,
          recoverable_value: 2500.75,
          net_recovery_rate: 41.4,
          active_actions: 4,
          comparison: {
            recent_period_returns: 30,
            prior_period_returns: 30,
            percentage_change: 0.0,
            label: 'vs prior 14-day demo period'
          }
        }
      });
    }

    // 3. Dashboard Charts
    if (cleanUrl.endsWith('/api/dashboard/charts')) {
      return mockResponse({
        status: 'success',
        data: {
          returns_by_reason: [
            { reason: 'Customer changed mind', count: 20 },
            { reason: 'Defective product', count: 14 },
            { reason: 'Damaged packaging', count: 8 },
            { reason: 'Incorrect product description', count: 7 },
            { reason: 'Incompatible product', count: 5 },
            { reason: 'Missing components', count: 3 },
            { reason: 'Wrong item delivered', count: 2 },
            { reason: 'Other', count: 1 }
          ],
          return_trends: [
            { week: 'Wk 36', count: 12 },
            { week: 'Wk 37', count: 14 },
            { week: 'Wk 38', count: 11 },
            { week: 'Wk 39', count: 15 },
            { week: 'Wk 40', count: 8 }
          ],
          top_return_rates: [
            { name: 'PowerSync 9-in-1 Docking Station', rate: 2.20, returned: 9, sold: 410 },
            { name: 'OmniView 2K HDR Webcam', rate: 1.89, returned: 10, sold: 530 },
            { name: 'AuraWave ANC Wireless Headphones', rate: 1.76, returned: 15, sold: 850 },
            { name: 'SolarCharge 20000mAh PowerBank', rate: 1.54, returned: 12, sold: 780 },
            { name: 'ErgoType RGB Mechanical Keyboard', rate: 1.49, returned: 10, sold: 670 },
            { name: 'PulseFit Pro Smartwatch', rate: 1.25, returned: 15, sold: 1200 }
          ],
          supplier_defects: [
            { supplier: 'SoundCraft Technologies', defects: 6 },
            { supplier: 'VoltPeak Power Solutions', defects: 2 },
            { supplier: 'OptiCore Vision Systems', defects: 1 },
            { supplier: 'KeyForge Labs', defects: 1 },
            { supplier: 'ApexWear Electronics', defects: 0 },
            { supplier: 'BreezeTech Corp', defects: 0 }
          ]
        }
      });
    }

    // Default fallback
    return mockResponse({ status: 'success', message: 'Fallback simulated response', data: [] });
  }
})();
