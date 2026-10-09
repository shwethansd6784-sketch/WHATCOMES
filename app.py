"""
app.py - Flask backend and REST API server for ReturnWise: Smart Returns & Root-Cause Advisor.
"""

import os
import io
import csv
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template, send_from_directory, Response

from database import get_db_connection, init_db
from recovery_engine import evaluate_recovery
from root_cause_engine import calculate_root_cause_insights
from seed_data import seed_database

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["JSON_SORT_KEYS"] = False


# ==========================================
# PAGE ROUTES
# ==========================================

@app.route("/")
def index():
    """Serves the primary single-page dashboard shell."""
    return render_template("index.html")


# ==========================================
# DASHBOARD API
# ==========================================

@app.route("/api/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """Returns high-level KPI cards and demo comparison metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total returns received
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(financial_value), 0) FROM returns")
    total_returns, total_financial_loss = cursor.fetchone()

    # Awaiting inspection
    cursor.execute("""
        SELECT COUNT(*) FROM returns r
        LEFT JOIN inspections i ON r.id = i.return_id
        WHERE i.id IS NULL
    """)
    awaiting_inspection = cursor.fetchone()[0]

    # Confirmed defective items
    cursor.execute("""
        SELECT COUNT(*) FROM inspections
        WHERE item_condition = 'Confirmed defective'
    """)
    confirmed_defective = cursor.fetchone()[0]

    # Approved for restocking
    cursor.execute("""
        SELECT COUNT(*) FROM recovery_recommendations
        WHERE recommended_action = 'Restock after inspection'
    """)
    approved_restocking = cursor.fetchone()[0]

    # Estimated recoverable value (net recovery sum)
    cursor.execute("""
        SELECT COALESCE(SUM(estimated_net_recovery), 0) FROM recovery_recommendations
    """)
    recoverable_value = cursor.fetchone()[0]

    # Priority / open actions
    cursor.execute("""
        SELECT COUNT(*) FROM corrective_actions
        WHERE status IN ('Open', 'In Progress')
    """)
    active_actions = cursor.fetchone()[0]

    # Calculate net recovery %
    net_recovery_rate = round((recoverable_value / total_financial_loss * 100), 1) if total_financial_loss > 0 else 0.0

    # Comparison metrics (last 14 days vs prior 14 days from demo anchor)
    anchor_date = datetime(2026, 10, 9)
    d14_ago = (anchor_date - timedelta(days=14)).strftime("%Y-%m-%d")
    d28_ago = (anchor_date - timedelta(days=28)).strftime("%Y-%m-%d")

    cursor.execute("SELECT COUNT(*) FROM returns WHERE return_date >= ?", (d14_ago,))
    recent_14 = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM returns WHERE return_date >= ? AND return_date < ?", (d28_ago, d14_ago))
    prior_14 = cursor.fetchone()[0]

    pct_change = round(((recent_14 - prior_14) / prior_14 * 100), 1) if prior_14 > 0 else 0.0

    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "total_returns": total_returns,
            "awaiting_inspection": awaiting_inspection,
            "confirmed_defective": confirmed_defective,
            "approved_restocking": approved_restocking,
            "financial_loss": round(total_financial_loss, 2),
            "recoverable_value": round(recoverable_value, 2),
            "net_recovery_rate": net_recovery_rate,
            "active_actions": active_actions,
            "comparison": {
                "recent_period_returns": recent_14,
                "prior_period_returns": prior_14,
                "percentage_change": pct_change,
                "label": "vs prior 14-day demo period"
            }
        }
    })


@app.route("/api/dashboard/charts", methods=["GET"])
def get_dashboard_charts():
    """Returns aggregated data for interactive Chart.js visualizations."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Returns by Reason
    cursor.execute("""
        SELECT customer_reason, COUNT(*) AS count
        FROM returns
        GROUP BY customer_reason
        ORDER BY count DESC
    """)
    reasons_data = [{"reason": row["customer_reason"], "count": row["count"]} for row in cursor.fetchall()]

    # 2. Return Trends over Time (Weekly buckets)
    cursor.execute("""
        SELECT strftime('%Y-%W', return_date) AS week_num, MIN(return_date) AS week_start, COUNT(*) AS count
        FROM returns
        GROUP BY week_num
        ORDER BY week_num ASC
    """)
    trend_rows = cursor.fetchall()
    trends_data = [
        {"week": f"Wk {row['week_start'][5:]}", "date": row["week_start"], "count": row["count"]}
        for row in trend_rows
    ]

    # 3. Products with Highest Return Rates (% returned / sold)
    cursor.execute("""
        SELECT p.name, p.units_sold, COUNT(r.id) AS returns_count,
               ROUND((CAST(COUNT(r.id) AS REAL) / p.units_sold) * 100, 2) AS return_rate
        FROM products p
        LEFT JOIN returns r ON p.id = r.product_id
        GROUP BY p.id
        ORDER BY return_rate DESC
        LIMIT 6
    """)
    product_rates = [
        {"name": row["name"], "rate": row["return_rate"], "returned": row["returns_count"], "sold": row["units_sold"]}
        for row in cursor.fetchall()
    ]

    # 4. Supplier-Related Confirmed Defects
    cursor.execute("""
        SELECT s.name AS supplier, COUNT(i.id) AS defect_count
        FROM suppliers s
        JOIN products p ON s.id = p.supplier_id
        JOIN returns r ON p.id = r.product_id
        JOIN inspections i ON r.id = i.return_id
        WHERE i.item_condition = 'Confirmed defective'
        GROUP BY s.id
        ORDER BY defect_count DESC
    """)
    supplier_defects = [
        {"supplier": row["supplier"], "defects": row["defect_count"]}
        for row in cursor.fetchall()
    ]

    # 5. Recovery Outcomes by Product Condition
    cursor.execute("""
        SELECT i.item_condition, rec.recommended_action, COUNT(*) as count
        FROM inspections i
        JOIN recovery_recommendations rec ON i.return_id = rec.return_id
        GROUP BY i.item_condition, rec.recommended_action
    """)
    outcomes_rows = cursor.fetchall()
    outcomes_data = [
        {"condition": r["item_condition"], "action": r["recommended_action"], "count": r["count"]}
        for r in outcomes_rows
    ]

    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "returns_by_reason": reasons_data,
            "return_trends": trends_data,
            "top_return_rates": product_rates,
            "supplier_defects": supplier_defects,
            "outcomes_by_condition": outcomes_data
        }
    })


# ==========================================
# RETURNS MANAGEMENT API
# ==========================================

@app.route("/api/returns", methods=["GET"])
def get_returns():
    """Lists returns with live search and multi-faceted filters."""
    search = request.args.get("search", "").strip()
    product_id = request.args.get("product_id")
    supplier_id = request.args.get("supplier_id")
    reason = request.args.get("reason")
    status = request.args.get("status")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    query = """
        SELECT 
            r.id,
            r.return_code,
            r.order_id,
            r.product_id,
            p.name AS product_name,
            p.sku AS product_sku,
            p.category AS product_category,
            s.id AS supplier_id,
            s.name AS supplier_name,
            r.customer_name,
            r.customer_reason,
            r.customer_comment,
            r.return_date,
            r.status,
            r.financial_value,
            i.id AS inspection_id,
            i.item_condition,
            rec.id AS recommendation_id,
            rec.recommended_action,
            rec.estimated_net_recovery
        FROM returns r
        JOIN products p ON r.product_id = p.id
        JOIN suppliers s ON p.supplier_id = s.id
        LEFT JOIN inspections i ON r.id = i.return_id
        LEFT JOIN recovery_recommendations rec ON r.id = rec.return_id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (r.return_code LIKE ? OR r.order_id LIKE ? OR p.name LIKE ? OR r.customer_name LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])

    if product_id:
        query += " AND r.product_id = ?"
        params.append(product_id)

    if supplier_id:
        query += " AND s.id = ?"
        params.append(supplier_id)

    if reason:
        query += " AND r.customer_reason = ?"
        params.append(reason)

    if status:
        if status == "Pending Inspection":
            query += " AND i.id IS NULL"
        else:
            query += " AND r.status = ?"
            params.append(status)

    if date_from:
        query += " AND r.return_date >= ?"
        params.append(date_from)

    if date_to:
        query += " AND r.return_date <= ?"
        params.append(date_to)

    query += " ORDER BY r.return_date DESC, r.id DESC"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"status": "success", "count": len(rows), "data": rows})


@app.route("/api/returns/<int:return_id>", methods=["GET"])
def get_return_detail(return_id):
    """Fetches complete profile of a single return including inspection & recommendation."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            r.*,
            p.name AS product_name,
            p.sku AS product_sku,
            p.category AS product_category,
            p.retail_price,
            p.resale_eligible,
            s.id AS supplier_id,
            s.name AS supplier_name,
            s.code AS supplier_code,
            i.id AS inspection_id,
            i.inspection_date,
            i.inspector_name,
            i.item_condition,
            i.functionality_status,
            i.packaging_condition,
            i.missing_components,
            i.inspection_notes,
            rec.id AS recommendation_id,
            rec.recommended_action,
            rec.reason AS rec_reason,
            rec.rule_triggered,
            rec.evidence_summary,
            rec.estimated_recovery_value,
            rec.estimated_processing_cost,
            rec.estimated_net_recovery,
            rec.confidence_score,
            rec.confidence_pct,
            rec.alternative_actions
        FROM returns r
        JOIN products p ON r.product_id = p.id
        JOIN suppliers s ON p.supplier_id = s.id
        LEFT JOIN inspections i ON r.id = i.return_id
        LEFT JOIN recovery_recommendations rec ON r.id = rec.return_id
        WHERE r.id = ?
    """, (return_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"status": "error", "message": "Return record not found"}), 404

    data = dict(row)
    if data.get("alternative_actions"):
        try:
            data["alternative_actions"] = json.loads(data["alternative_actions"])
        except Exception:
            pass

    return jsonify({"status": "success", "data": data})


@app.route("/api/returns", methods=["POST"])
def create_return():
    """Validates and creates a new return record."""
    body = request.get_json() or {}
    product_id = body.get("product_id")
    order_id = body.get("order_id", "").strip()
    customer_name = body.get("customer_name", "").strip()
    customer_reason = body.get("customer_reason", "").strip()
    customer_comment = body.get("customer_comment", "").strip()
    return_date = body.get("return_date") or datetime.now().strftime("%Y-%m-%d")

    if not product_id or not order_id or not customer_name or not customer_reason:
        return jsonify({"status": "error", "message": "Missing required fields (product, order ID, customer name, reason)"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get product retail price
    cursor.execute("SELECT retail_price FROM products WHERE id = ?", (product_id,))
    prod = cursor.fetchone()
    if not prod:
        conn.close()
        return jsonify({"status": "error", "message": "Invalid product ID selected"}), 400

    financial_value = float(body.get("financial_value") or prod["retail_price"])

    # Generate next return code
    cursor.execute("SELECT MAX(id) FROM returns")
    max_id = cursor.fetchone()[0] or 1000
    return_code = f"RET-{max_id + 1}"

    cursor.execute("""
        INSERT INTO returns (return_code, order_id, product_id, customer_name, customer_reason, customer_comment, return_date, status, financial_value)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending Inspection', ?)
    """, (return_code, order_id, product_id, customer_name, customer_reason, customer_comment, return_date, financial_value))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "status": "success",
        "message": f"Return {return_code} successfully registered",
        "data": {"id": new_id, "return_code": return_code}
    }), 201


@app.route("/api/returns/<int:return_id>", methods=["PUT"])
def update_return(return_id):
    """Updates editable return fields."""
    body = request.get_json() or {}
    customer_reason = body.get("customer_reason")
    customer_comment = body.get("customer_comment")
    status = body.get("status")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE returns
        SET customer_reason = COALESCE(?, customer_reason),
            customer_comment = COALESCE(?, customer_comment),
            status = COALESCE(?, status)
        WHERE id = ?
    """, (customer_reason, customer_comment, status, return_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Return record updated successfully"})


# ==========================================
# PRODUCT INSPECTION & RECOMMENDATION API
# ==========================================

@app.route("/api/inspections", methods=["GET"])
def get_inspections():
    """Returns inspection audit trail."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            i.*,
            r.return_code,
            r.order_id,
            r.customer_reason,
            p.name AS product_name,
            rec.recommended_action,
            rec.estimated_net_recovery
        FROM inspections i
        JOIN returns r ON i.return_id = r.id
        JOIN products p ON r.product_id = p.id
        LEFT JOIN recovery_recommendations rec ON r.id = rec.return_id
        ORDER BY i.inspection_date DESC, i.id DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"status": "success", "data": rows})


@app.route("/api/inspections", methods=["POST"])
def record_inspection():
    """
    Submits physical inspection for a return, automatically executes
    the Smart Recovery Recommendation Engine, and updates persistent database.
    """
    body = request.get_json() or {}
    return_id = body.get("return_id")
    inspection_date = body.get("inspection_date") or datetime.now().strftime("%Y-%m-%d")
    inspector_name = body.get("inspector_name", "").strip() or "Senior QA Bench Technician"
    item_condition = body.get("item_condition", "").strip()
    functionality_status = body.get("functionality_status", "").strip()
    packaging_condition = body.get("packaging_condition", "").strip()
    missing_components = body.get("missing_components", "None").strip()
    inspection_notes = body.get("inspection_notes", "").strip()

    valid_conditions = [
        "Unopened", "Opened and working", "Damaged",
        "Confirmed defective", "Missing components", "Requires further inspection"
    ]
    if item_condition not in valid_conditions:
        return jsonify({"status": "error", "message": f"Invalid item condition. Must be one of: {', '.join(valid_conditions)}"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch return and product details
    cursor.execute("""
        SELECT 
            r.*,
            p.name AS product_name,
            p.category AS product_category,
            p.retail_price,
            p.resale_eligible,
            p.processing_cost_base,
            s.name AS supplier_name
        FROM returns r
        JOIN products p ON r.product_id = p.id
        JOIN suppliers s ON p.supplier_id = s.id
        WHERE r.id = ?
    """, (return_id,))
    ret_row = cursor.fetchone()

    if not ret_row:
        conn.close()
        return jsonify({"status": "error", "message": "Return record not found"}), 404

    # Upsert inspection record
    cursor.execute("SELECT id FROM inspections WHERE return_id = ?", (return_id,))
    existing_insp = cursor.fetchone()
    if existing_insp:
        cursor.execute("""
            UPDATE inspections
            SET inspection_date = ?, inspector_name = ?, item_condition = ?,
                functionality_status = ?, packaging_condition = ?, missing_components = ?, inspection_notes = ?
            WHERE return_id = ?
        """, (inspection_date, inspector_name, item_condition, functionality_status, packaging_condition, missing_components, inspection_notes, return_id))
    else:
        cursor.execute("""
            INSERT INTO inspections (return_id, inspection_date, inspector_name, item_condition, functionality_status, packaging_condition, missing_components, inspection_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (return_id, inspection_date, inspector_name, item_condition, functionality_status, packaging_condition, missing_components, inspection_notes))

    # Evaluate recommendation through transparent rule engine
    rec = evaluate_recovery(
        item_condition=item_condition,
        functionality_status=functionality_status,
        packaging_condition=packaging_condition,
        missing_components=missing_components,
        retail_price=ret_row["retail_price"],
        resale_eligible=bool(ret_row["resale_eligible"]),
        processing_cost_base=ret_row["processing_cost_base"],
        customer_reason=ret_row["customer_reason"],
        supplier_name=ret_row["supplier_name"],
        category=ret_row["product_category"]
    )

    # Upsert recommendation
    cursor.execute("SELECT id FROM recovery_recommendations WHERE return_id = ?", (return_id,))
    existing_rec = cursor.fetchone()
    if existing_rec:
        cursor.execute("""
            UPDATE recovery_recommendations
            SET recommended_action = ?, reason = ?, rule_triggered = ?, evidence_summary = ?,
                estimated_recovery_value = ?, estimated_processing_cost = ?, estimated_net_recovery = ?,
                confidence_score = ?, confidence_pct = ?, alternative_actions = ?, status = 'Generated'
            WHERE return_id = ?
        """, (
            rec["recommended_action"], rec["reason"], rec["rule_triggered"], rec["evidence_summary"],
            rec["estimated_recovery_value"], rec["estimated_processing_cost"], rec["estimated_net_recovery"],
            rec["confidence_score"], rec["confidence_pct"], rec["alternative_actions"], return_id
        ))
    else:
        cursor.execute("""
            INSERT INTO recovery_recommendations (
                return_id, recommended_action, reason, rule_triggered, evidence_summary,
                estimated_recovery_value, estimated_processing_cost, estimated_net_recovery,
                confidence_score, confidence_pct, alternative_actions, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            return_id, rec["recommended_action"], rec["reason"], rec["rule_triggered"], rec["evidence_summary"],
            rec["estimated_recovery_value"], rec["estimated_processing_cost"], rec["estimated_net_recovery"],
            rec["confidence_score"], rec["confidence_pct"], rec["alternative_actions"], "Generated"
        ))

    # Update return status to 'Inspected'
    cursor.execute("UPDATE returns SET status = 'Inspected' WHERE id = ?", (return_id,))

    conn.commit()
    conn.close()

    # Decode alternative actions for JSON output
    rec_output = dict(rec)
    try:
        rec_output["alternative_actions"] = json.loads(rec["alternative_actions"])
    except Exception:
        pass

    return jsonify({
        "status": "success",
        "message": f"Inspection recorded and recommendation generated: {rec['recommended_action']}",
        "data": {
            "return_id": return_id,
            "return_code": ret_row["return_code"],
            "product_name": ret_row["product_name"],
            "inspection": {
                "condition": item_condition,
                "functionality": functionality_status,
                "inspector": inspector_name
            },
            "recommendation": rec_output
        }
    })


# ==========================================
# ROOT-CAUSE & SUPPLIER INTELLIGENCE API
# ==========================================

@app.route("/api/root-cause/summary", methods=["GET"])
def get_root_cause_summary():
    """Returns dynamic root-cause intelligence, anomaly clusters, and statistical proofs."""
    insights = calculate_root_cause_insights()
    return jsonify({"status": "success", "data": insights})


@app.route("/api/suppliers/scorecard", methods=["GET"])
def get_supplier_scorecard():
    """Returns supplier performance matrix with verified defect ratios and follow-ups."""
    insights = calculate_root_cause_insights()
    return jsonify({"status": "success", "data": insights["supplier_matrix"]})


# ==========================================
# ACTION CENTRE API
# ==========================================

@app.route("/api/actions", methods=["GET"])
def get_actions():
    """Returns prioritized corrective action tasks."""
    status_filter = request.args.get("status")
    priority_filter = request.args.get("priority")

    query = "SELECT * FROM corrective_actions WHERE 1=1"
    params = []

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    if priority_filter:
        query += " AND priority = ?"
        params.append(priority_filter)

    query += " ORDER BY CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END, due_date ASC"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"status": "success", "count": len(rows), "data": rows})


@app.route("/api/actions", methods=["POST"])
def create_action():
    """Creates a new corrective action item."""
    body = request.get_json() or {}
    title = body.get("title", "").strip()
    related_type = body.get("related_type", "Supplier")
    related_id = body.get("related_id", "").strip()
    priority = body.get("priority", "Medium")
    evidence = body.get("evidence", "").strip()
    estimated_impact = body.get("estimated_impact", "").strip()
    assigned_to = body.get("assigned_to", "QA Team").strip()
    due_date = body.get("due_date") or (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    notes = body.get("notes", "").strip()

    if not title or not related_id:
        return jsonify({"status": "error", "message": "Action title and related entity are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM corrective_actions")
    max_id = cursor.fetchone()[0] or 100
    action_code = f"ACT-{max_id + 1}"

    cursor.execute("""
        INSERT INTO corrective_actions (action_code, title, related_type, related_id, priority, evidence, estimated_impact, assigned_to, due_date, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open', ?)
    """, (action_code, title, related_type, related_id, priority, evidence, estimated_impact, assigned_to, due_date, notes))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "status": "success",
        "message": f"Corrective action {action_code} created successfully",
        "data": {"id": new_id, "action_code": action_code}
    }), 201


@app.route("/api/actions/<int:action_id>", methods=["PUT"])
def update_action(action_id):
    """Updates status, assignment, or notes of a corrective action."""
    body = request.get_json() or {}
    status = body.get("status")
    assigned_to = body.get("assigned_to")
    notes = body.get("notes")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE corrective_actions
        SET status = COALESCE(?, status),
            assigned_to = COALESCE(?, assigned_to),
            notes = COALESCE(?, notes)
        WHERE id = ?
    """, (status, assigned_to, notes, action_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Action updated successfully"})


# ==========================================
# REPORTS & EXPORT API
# ==========================================

@app.route("/api/reports/summary", methods=["GET"])
def get_reports_summary():
    """Generates complete aggregated executive return summary."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Financial breakdown by recovery recommendation
    cursor.execute("""
        SELECT 
            rec.recommended_action,
            COUNT(*) AS unit_count,
            COALESCE(SUM(r.financial_value), 0) AS original_value,
            COALESCE(SUM(rec.estimated_recovery_value), 0) AS gross_recovery,
            COALESCE(SUM(rec.estimated_processing_cost), 0) AS total_processing_cost,
            COALESCE(SUM(rec.estimated_net_recovery), 0) AS net_recovered_value
        FROM recovery_recommendations rec
        JOIN returns r ON rec.return_id = r.id
        GROUP BY rec.recommended_action
        ORDER BY net_recovered_value DESC
    """)
    recovery_financials = [dict(row) for row in cursor.fetchall()]

    # Actions resolution metric
    cursor.execute("""
        SELECT status, COUNT(*) AS count
        FROM corrective_actions
        GROUP BY status
    """)
    action_stats = {row["status"]: row["count"] for row in cursor.fetchall()}

    conn.close()
    return jsonify({
        "status": "success",
        "data": {
            "recovery_financials": recovery_financials,
            "action_stats": action_stats
        }
    })


@app.route("/api/reports/export", methods=["GET"])
def export_csv():
    """Exports data tables to downloadable CSV."""
    report_type = request.args.get("type", "returns")
    conn = get_db_connection()
    cursor = conn.cursor()
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == "returns":
        cursor.execute("""
            SELECT 
                r.return_code, r.order_id, p.name AS product_name, p.category, s.name AS supplier,
                r.customer_reason, r.return_date, r.status, r.financial_value,
                COALESCE(i.item_condition, 'Not Inspected') AS inspection_condition,
                COALESCE(rec.recommended_action, 'Pending') AS recommended_action,
                COALESCE(rec.estimated_net_recovery, 0) AS net_recovery
            FROM returns r
            JOIN products p ON r.product_id = p.id
            JOIN suppliers s ON p.supplier_id = s.id
            LEFT JOIN inspections i ON r.id = i.return_id
            LEFT JOIN recovery_recommendations rec ON r.id = rec.return_id
            ORDER BY r.id ASC
        """)
        rows = cursor.fetchall()
        writer.writerow([
            "Return ID", "Order ID", "Product Name", "Category", "Supplier",
            "Customer Reason", "Return Date", "Status", "Original Value ($)",
            "Inspection Condition", "Recommended Action", "Net Recovery ($)"
        ])
        for r in rows:
            writer.writerow(list(r))
        filename = "ReturnWise_Returns_Report.csv"

    elif report_type == "suppliers":
        insights = calculate_root_cause_insights()
        writer.writerow([
            "Supplier Code", "Supplier Name", "Category", "Units Sold", "Units Returned",
            "Confirmed Defects", "Return Rate (%)", "Defect Rate (%)", "Financial Impact ($)", "Status", "Recommendation"
        ])
        for s in insights["supplier_matrix"]:
            writer.writerow([
                s["supplier_code"], s["supplier_name"], s["category"], s["units_sold"],
                s["units_returned"], s["confirmed_defects"], f"{s['return_rate_pct']}%",
                f"{s['defect_share_pct']}%", f"${s['financial_impact']:.2f}", s["status"], s["recommendation"]
            ])
        filename = "ReturnWise_Supplier_Quality_Report.csv"

    elif report_type == "actions":
        cursor.execute("SELECT action_code, title, related_type, related_id, priority, assigned_to, due_date, status, evidence, estimated_impact FROM corrective_actions ORDER BY id ASC")
        rows = cursor.fetchall()
        writer.writerow([
            "Action ID", "Title", "Related Type", "Related Entity", "Priority",
            "Assigned To", "Due Date", "Status", "Evidence", "Estimated Impact"
        ])
        for r in rows:
            writer.writerow(list(r))
        filename = "ReturnWise_Corrective_Actions.csv"

    else:
        conn.close()
        return jsonify({"status": "error", "message": "Invalid report type"}), 400

    conn.close()
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


# ==========================================
# SYSTEM / DEMO UTILITIES
# ==========================================

@app.route("/api/system/reset-demo", methods=["POST"])
def reset_demo():
    """Resets SQLite database back to original clean demo state."""
    seed_database()
    return jsonify({
        "status": "success",
        "message": "Demo database successfully restored to pristine state with 60 realistic returns."
    })


@app.route("/api/meta", methods=["GET"])
def get_metadata():
    """Returns dropdown metadata for products, suppliers, reasons, and condition types."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, sku, name, category, retail_price, units_sold FROM products ORDER BY name ASC")
    products = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT id, code, name, category, quality_rating FROM suppliers ORDER BY name ASC")
    suppliers = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "products": products,
            "suppliers": suppliers,
            "return_reasons": [
                "Defective product",
                "Damaged packaging",
                "Wrong item delivered",
                "Incorrect product description",
                "Incompatible product",
                "Customer changed mind",
                "Missing components",
                "Other"
            ],
            "condition_categories": [
                "Unopened",
                "Opened and working",
                "Damaged",
                "Confirmed defective",
                "Missing components",
                "Requires further inspection"
            ],
            "functionality_options": [
                "Fully Functional",
                "Intermittent Fault",
                "Complete Failure / Dead",
                "Cosmetic Damage Only",
                "Untested"
            ],
            "packaging_options": [
                "Original Sealed",
                "Opened Intact",
                "Torn / Distressed",
                "Missing Packaging"
            ]
        }
    })


if __name__ == "__main__":
    # If database doesn't exist yet, seed it automatically
    from database import DB_FILE
    if not os.path.exists(DB_FILE):
        seed_database()

    print("=================================================================")
    print("ReturnWise: Smart Returns & Root-Cause Advisor (GadgetBay Demo)")
    print("Starting Flask web server on http://127.0.0.1:5000 ...")
    print("=================================================================")
    app.run(host="127.0.0.1", port=5000, debug=False)
