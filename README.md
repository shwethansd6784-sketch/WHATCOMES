# ReturnWise: Smart Returns & Root-Cause Advisor
**Demo Company:** GadgetBay | **Hackathon Problem Statement:** *“What Came Back”*

ReturnWise is an enterprise-grade returns intelligence platform built for **GadgetBay**, a modern consumer electronics e-commerce company. Rather than merely recording returns or showing static pie charts, ReturnWise connects **physical bench inspection triage** with **supplier root-cause analysis**, **rule-based recovery decision optimization**, and **closed-loop corrective-action tracking**.

---

## 🌟 Key Differentiating Features

1. **Physical Bench Triage vs. Unverified Customer Claims:**
   - Clearly separates customer intake claims (e.g. *"Incompatible"*, *"Defective"*) from bench-verified technician findings (*"Opened and working"*, *"Confirmed acoustic driver voice-coil failure"*).
   - Prevents premature accusations against suppliers by requiring bench proof.

2. **Smart Recovery Decision Engine (`recovery_engine.py`):**
   - Transparent, explainable rule-based decision architecture (ready for future ML drop-in).
   - Generates exact dispositions:
     - `Restock after inspection` (Fast-path Grade-A for factory-sealed units, 95%+ recovery)
     - `Repair` (Level-2 triage or supplier RMA warranty claim for high-value items)
     - `Refurbish` (Certified Open-Box packaging for operational units)
     - `Liquidate or sell through secondary channel` (B2B wholesale lot for cosmetic/transit damage)
     - `Hold for further inspection` (Thermal stress test or missing accessory replenishment)
     - `Dispose of according to applicable policy` (Uneconomic repair threshold; safe WEEE recycling)
   - Computes dynamic net recovery financials:  
     $$\text{Net Recovery Value} = \text{Expected Resale Value} - \text{Processing \& Triage Cost} - \text{Accessory Costs}$$

3. **Supplier Root-Cause & Defect Anomaly Detection (`root_cause_engine.py`):**
   - Correlates returns against verified units sold ($N \ge 3$ sample size safeguards to avoid premature claims).
   - Highlights repeated hardware defect clusters (e.g. *SoundCraft Technologies audio driver failure*).
   - Isolates packaging carton fragility (e.g. *VoltPeak Power crushed cartons*) from electrical defects.
   - Flags website catalog listing discrepancies (e.g. *SolarCharge PowerBank 10,000mAh vs 20,000mAh*).
   - Detects customer setup friction where zero hardware defects exist.

4. **Closed-Loop Action Centre:**
   - Tracks operational tasks (Priority, Assigned Lead, Root-Cause Evidence, Due Date, Financial Impact, Status: *Open* / *In Progress* / *Resolved*).
   - Real-time updates reflect across the executive dashboard.

5. **Auditable Executive Reports & One-Click CSV Exports:**
   - Supplier Quality Scorecard, Recovery Yield Economics, and download buttons for Returns, Supplier Scorecards, and Action items.
   - Built-in printable report layout optimized for executive presentations.

6. **Interactive Hackathon Walkthrough Bar:**
   - A dedicated 8-step guided stepper built into the top navigation bar to let hackathon judges effortlessly experience the entire flow in under 2 minutes.

---

## 🛠️ Technology Stack

- **Backend:** Python 3 with Flask (`app.py`), RESTful API architecture.
- **Database:** SQLite (`returnwise.db`) with relational integrity, foreign keys, and indexes.
- **Decision Engine:** Modular rule-based expert system (`recovery_engine.py`).
- **Analytics:** Statistical cross-tabulation engine (`root_cause_engine.py`).
- **Frontend:** Semantic HTML5, Modern SaaS CSS3 (`style.css`), Vanilla JavaScript (ES6+).
- **Visualizations:** Chart.js (Interactive Doughnut, Line, Horizontal Bar, Vertical Bar).
- **Offline / Standalone Fallback:** Resilient `static/js/api_fallback.js` that seamlessly falls back to client-side localStorage if run without Python!

---

## 🚀 How to Run the Project

### Option A: Flask Backend with SQLite (Recommended)

1. **Activate the Virtual Environment & Install Dependencies:**
   ```powershell
   # If using PowerShell on Windows:
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **(Optional) Seed or Reset the Demo Database:**
   ```powershell
   python seed_data.py
   ```
   *(Initializes `returnwise.db` with 60 realistic returns, 12 products across 6 suppliers, pre-seeded inspections, and corrective actions).*

3. **Start the Flask Application:**
   ```powershell
   python app.py
   ```

4. **Open in your Web Browser:**
   ```text
   http://127.0.0.1:5000
   ```

---

### Option B: Zero-Install Standalone Browser Fallback

If you are on an environment without Python installed:
1. Double-click or open the root file:
   ```text
   index.html
   ```
2. The application detects the file protocol and automatically loads the mock demo state through `static/js/api_fallback.js`.

---

## 🧪 Automated Test Verification

You can verify all end-to-end hackathon requirements with the automated verification script:
```powershell
python test_demo_flow.py
```
This tests:
- Initial dashboard KPI calculations
- Locating `RET-1002` (AuraWave Headphones audio cutout)
- Recording bench inspection confirming audio coil defect
- Triggering rule `RULE_BENCH_REPAIR_SUPPLIER_CLAIM_05` and verifying net financial recovery
- Identifying SoundCraft Technologies defect cluster ($N=10$)
- Creating corrective action for vendor quality audit
- Inspecting `RET-1014` (Unopened PulseFit Pro Smartwatch) for 100% restock
- Verifying live dashboard stat updates

---

## 🎬 Hackathon Live Demo Script (Step-by-Step)

| Step | Action | What to Point Out to Judges |
|---|---|---|
| **Step 1** | Click **"1. Overview"** on the top bar | Point out the 6 dynamic KPI cards (**Total Returns: 60**, **Awaiting Inspection: 18**, **Confirmed Defective: 10**, **Approved Restocking: 9**, **Loss: $6,035.40**, **Net Recoverable: $2,500.75**). Show interactive Chart.js charts and the Priority Actions panel. |
| **Step 2** | Click **"2. Find RET-1002"** | The app navigates to Returns Management and filters for `RET-1002` (*AuraWave ANC Wireless Headphones*). Notice customer complaint: *"Left earbud cuts out completely after 2 minutes"*. Status is **Pending Inspection**. Click **"Details"** to view audit trail. |
| **Step 3** | Click **"3. Bench Inspection"** | Navigates to Product Inspection with `RET-1002` selected. Condition is set to **"Confirmed defective"**, Functionality: **"Complete Failure / Dead"**. Click **"Save Inspection & Generate Recommendation"**. |
| **Step 4** | Click **"4. Recovery Decision"** | The green decision banner appears immediately. Notice: **Action:** `Repair`, **Reason:** Verified hardware failure justifies OEM warranty return, **Net Recovery:** `$69.49` ($97.49 resale - $28.00 repair cost), **Rule:** `RULE_BENCH_REPAIR_SUPPLIER_CLAIM_05`. |
| **Step 5** | Click **"5. Supplier Root-Cause"** | Shows Root-Cause Analysis. A prominent card flags **Repeated Acoustic Driver Failure on AuraWave ANC Headphones** (*Supplier: SoundCraft Technologies, N=10*). Highlight how the system contrasts customer claims with verified technician data and safeguards against low sample sizes (*"Insufficient data"* badge). |
| **Step 6** | Click **"6. Corrective Action (ACT-101)"** | Shows Action Centre task `ACT-101` assigned to Sarah Chen (QA Lead). Demonstrates closed-loop governance: change the status dropdown from *In Progress* to *Resolved*, or add progress notes. |
| **Step 7** | Click **"7. Test RET-1014 (Restock)"** | Selects unopened return `RET-1014` (*PulseFit Pro Smartwatch*). Inspect as **"Unopened"**, packaging **"Original Sealed"**. Save inspection to show instant **Restock after inspection** recommendation with **$189.99 net recovery (95% yield)**! |
| **Step 8** | Click **"8. Financial Audit"** | Navigates to Reports. Show the **Supplier Quality Scorecard** and the **Recovery Yield Breakdown**. Click **"Export Returns (CSV)"** to demonstrate real CSV data export. |

---

## 🏛️ System Architecture & Logic Flow

```
+-------------------------------------------------------------+
|                 Customer Inbound Return                     |
|           (Customer Reason, Order ID, Product)              |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                  Physical Bench Triage                      |
|       (Condition, Functionality, Packaging, Notes)          |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|             Smart Recovery Engine (Rule-Based)              |
|        - Evaluates Resale Eligibility & Condition           |
|        - Calculates Net Recovery ($Resale - Processing$)    |
|        - Outputs Transparent Rule & Actionable Pathway      |
+------------------------------+------------------------------+
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
+-----------------------------+   +---------------------------+
|  Supplier Root-Cause Engine |   |   Action Centre & Audit   |
|   - Defect Rate vs Sold %   |   |   - Vendor 8D Audits      |
|   - Defect Share in Returns |   |   - Spec Corrections      |
|   - Anomaly Pattern Badging |   |   - Status Lifecycle      |
+-----------------------------+   +---------------------------+
```

---

## 🗄️ Database Schema Summary

1. `suppliers`: `id`, `code`, `name`, `contact_email`, `category`, `quality_rating`, `lead_time_days`
2. `products`: `id`, `sku`, `name`, `category`, `supplier_id`, `retail_price`, `cost_price`, `units_sold`, `resale_eligible`, `processing_cost_base`
3. `returns`: `id`, `return_code`, `order_id`, `product_id`, `customer_name`, `customer_reason`, `customer_comment`, `return_date`, `status`, `financial_value`
4. `inspections`: `id`, `return_id`, `inspection_date`, `inspector_name`, `item_condition`, `functionality_status`, `packaging_condition`, `missing_components`, `inspection_notes`
5. `recovery_recommendations`: `id`, `return_id`, `recommended_action`, `reason`, `rule_triggered`, `evidence_summary`, `estimated_recovery_value`, `estimated_processing_cost`, `estimated_net_recovery`, `confidence_score`, `confidence_pct`, `alternative_actions`, `status`
6. `corrective_actions`: `id`, `action_code`, `title`, `related_type`, `related_id`, `priority`, `evidence`, `estimated_impact`, `assigned_to`, `due_date`, `status`, `notes`

---

## 📝 Demo Reset Notice

At any point during testing or after a demonstration, you can reset the entire database to the clean benchmark state by going to **Settings > Reset Demo Database**, or by running:
```powershell
python seed_data.py
```
*(All records, statistics, and charts will immediately refresh).*
