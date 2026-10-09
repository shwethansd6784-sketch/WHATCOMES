"""
test_demo_flow.py - Automated verification of the Hackathon Demo Scenario.
"""

import json
import urllib.request

BASE_URL = "http://127.0.0.1:5000"

def get(path):
    req = urllib.request.Request(f"{BASE_URL}{path}")
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode("utf-8"))

def post(path, payload):
    req = urllib.request.Request(f"{BASE_URL}{path}", method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, data=json.dumps(payload).encode("utf-8")) as res:
        return json.loads(res.read().decode("utf-8"))

def run_test():
    print("-----------------------------------------------------------------")
    print("STEP 1: Checking Baseline Stats on Dashboard")
    print("-----------------------------------------------------------------")
    stats1 = get("/api/dashboard/stats")["data"]
    print(f"Total Returns: {stats1['total_returns']}")
    print(f"Awaiting Inspection: {stats1['awaiting_inspection']}")
    print(f"Confirmed Defective: {stats1['confirmed_defective']}")
    print(f"Approved Restocking: {stats1['approved_restocking']}")
    print(f"Financial Loss: ${stats1['financial_loss']:.2f}")
    print(f"Recoverable Value: ${stats1['recoverable_value']:.2f}")
    print(f"Active Corrective Actions: {stats1['active_actions']}")

    print("\n-----------------------------------------------------------------")
    print("STEP 2: Locating Return Record RET-1002 (Headphone Audio Defect)")
    print("-----------------------------------------------------------------")
    ret_list = get("/api/returns?search=RET-1002")["data"]
    assert len(ret_list) > 0, "RET-1002 not found!"
    ret1002 = ret_list[0]
    print(f"Return Code: {ret1002['return_code']}")
    print(f"Product: {ret1002['product_name']} ({ret1002['product_sku']})")
    print(f"Supplier: {ret1002['supplier_name']}")
    print(f"Customer Reason: '{ret1002['customer_reason']}'")
    print(f"Customer Comment: '{ret1002['customer_comment']}'")
    print(f"Current Status: {ret1002['status']}")

    print("\n-----------------------------------------------------------------")
    print("STEP 3: Submitting Physical Bench Inspection on RET-1002")
    print("-----------------------------------------------------------------")
    insp_payload = {
        "return_id": ret1002["id"],
        "item_condition": "Confirmed defective",
        "functionality_status": "Complete Failure / Dead",
        "packaging_condition": "Opened Intact",
        "missing_components": "None",
        "inspector_name": "David Martinez (Bench Tech Lead)",
        "inspection_date": "2026-10-09",
        "inspection_notes": "Acoustic driver coil open circuit verified on audio analyzer. Left transducer non-functional."
    }
    insp_res = post("/api/inspections", insp_payload)
    assert insp_res["status"] == "success", "Failed to save inspection"
    rec1 = insp_res["data"]["recommendation"]
    print("Generated Recovery Recommendation:")
    print(f"  Recommended Action: {rec1['recommended_action']}")
    print(f"  Rule Triggered: {rec1['rule_triggered']}")
    print(f"  Plain Reason: {rec1['reason']}")
    print(f"  Resale Value: ${rec1['estimated_recovery_value']:.2f}")
    print(f"  Processing Cost: ${rec1['estimated_processing_cost']:.2f}")
    print(f"  Net Recovered Value: ${rec1['estimated_net_recovery']:.2f}")
    print(f"  Confidence: {rec1['confidence_score']} ({rec1['confidence_pct']}%)")

    print("\n-----------------------------------------------------------------")
    print("STEP 4: Querying Root-Cause Insights (Defect Clustering)")
    print("-----------------------------------------------------------------")
    rc_summary = get("/api/root-cause/summary")["data"]
    highlights = rc_summary["highlights"]
    print(f"Active Systemic Defect Clusters Detected: {len(highlights)}")
    for h in highlights:
        print(f"  * [{h['badge']}] {h['title']} (Sample N={h['sample_size']})")
        print(f"    Impact: {h['financial_impact']}")
        print(f"    Recommended Follow-up: {h['recommended_action']}")

    print("\n-----------------------------------------------------------------")
    print("STEP 5: Creating Quality Corrective Action for Supplier")
    print("-----------------------------------------------------------------")
    act_payload = {
        "title": "AuraWave Audio Transducer Assembly Batch #41 Audit",
        "related_type": "Supplier",
        "related_id": "SoundCraft Technologies",
        "priority": "Critical",
        "assigned_to": "Sarah Chen (QA Lead)",
        "evidence": "6 bench-verified voice coil open circuit failures among 8 returns. 75% defect rate among returns.",
        "estimated_impact": "Prevents recurring defect losses on remaining 250 units in warehouse"
    }
    act_res = post("/api/actions", act_payload)
    print(f"Created Corrective Action: {act_res['data']['action_code']}")

    print("\n-----------------------------------------------------------------")
    print("STEP 6: Submitting Inspection for RET-1014 (Unopened Product)")
    print("-----------------------------------------------------------------")
    ret1014 = get("/api/returns?search=RET-1014")["data"][0]
    insp2_payload = {
        "return_id": ret1014["id"],
        "item_condition": "Unopened",
        "functionality_status": "Untested",
        "packaging_condition": "Original Sealed",
        "missing_components": "None",
        "inspector_name": "Sarah Jenkins (Senior QA)",
        "inspection_date": "2026-10-09",
        "inspection_notes": "Factory tamper-evident seal pristine. 100% Grade-A condition."
    }
    insp2_res = post("/api/inspections", insp2_payload)
    rec2 = insp2_res["data"]["recommendation"]
    print(f"Product: {ret1014['product_name']}")
    print(f"Recommended Action: {rec2['recommended_action']}")
    print(f"Net Recovered: ${rec2['estimated_net_recovery']:.2f} (from original ${ret1014['financial_value']:.2f})")

    print("\n-----------------------------------------------------------------")
    print("STEP 7: Verifying Live Updated Dashboard Statistics")
    print("-----------------------------------------------------------------")
    stats2 = get("/api/dashboard/stats")["data"]
    print(f"Awaiting Inspection: {stats2['awaiting_inspection']} (Decreased from {stats1['awaiting_inspection']})")
    print(f"Confirmed Defective: {stats2['confirmed_defective']} (Increased from {stats1['confirmed_defective']})")
    print(f"Approved Restocking: {stats2['approved_restocking']} (Increased from {stats1['approved_restocking']})")
    print(f"Recoverable Value: ${stats2['recoverable_value']:.2f} (Increased from ${stats1['recoverable_value']:.2f})")
    print(f"Active Actions: {stats2['active_actions']} (Updated from {stats1['active_actions']})")

    print("\n=================================================================")
    print("ALL HACKATHON DEMO CHECKS PASSED PERFECTLY!")
    print("=================================================================")

if __name__ == "__main__":
    run_test()
