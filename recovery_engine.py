"""
recovery_engine.py - Smart Recovery Recommendation Engine for ReturnWise.
Uses transparent, explainable decision-rule architecture to calculate optimal disposition,
financial recovery estimates, confidence levels, and alternative pathways for inspected items.
"""

from typing import Dict, Any, List
import json


def evaluate_recovery(
    item_condition: str,
    functionality_status: str,
    packaging_condition: str,
    missing_components: str,
    retail_price: float,
    resale_eligible: bool = True,
    processing_cost_base: float = 5.0,
    customer_reason: str = "",
    supplier_name: str = "",
    category: str = ""
) -> Dict[str, Any]:
    """
    Evaluates physical inspection findings against business recovery rules.
    Returns explainable recommendation, financial formula results, confidence score, and alternatives.
    """
    retail_price = float(retail_price)
    processing_base = float(processing_cost_base)
    missing = (missing_components or "").strip().lower()
    has_missing_parts = missing not in ["none", "", "n/a", "no", "nil"]

    # Default containers
    recommended_action = "Hold for further inspection"
    reason = "Initial triage completed. Requires senior technician bench diagnostics before disposition."
    rule_triggered = "RULE_DEFAULT_HOLD_00"
    evidence_items = []
    confidence_score = "Medium"
    confidence_pct = 70
    expected_resale = 0.0
    processing_cost = processing_base
    alternatives = []

    # Evidence collector
    evidence_items.append(f"Inspection condition: {item_condition}")
    evidence_items.append(f"Tested functionality: {functionality_status}")
    evidence_items.append(f"Packaging state: {packaging_condition}")
    if has_missing_parts:
        evidence_items.append(f"Missing parts noted: {missing_components}")
    if customer_reason:
        evidence_items.append(f"Customer reported reason: '{customer_reason}'")

    # RULE 1: Unopened & Resale Eligible
    if item_condition == "Unopened" and packaging_condition in ["Original Sealed", "Opened Intact"]:
        if resale_eligible:
            recommended_action = "Restock after inspection"
            rule_triggered = "RULE_FAST_RESTOCK_UNOPENED_01"
            reason = (
                "Factory seal is intact with flawless packaging. "
                "Product qualifies for immediate Grade-A restock at 100% original value, avoiding markdown."
            )
            # 100% resale recovery value, minimal intake inspection cost ($5-$8)
            expected_resale = round(retail_price, 2)
            processing_cost = round(processing_base + 3.0, 2)
            confidence_score = "High"
            confidence_pct = 96
            alternatives = [
                "Liquidate via B2B lot if inventory sku has reached EOL (End of Life)",
                "Hold if serial barcode verification requires supplier re-authorization"
            ]
        else:
            recommended_action = "Liquidate or sell through an approved secondary channel"
            rule_triggered = "RULE_HYGIENE_RESTOCK_EXCLUSION_02"
            reason = "Item is unopened, but category policy excludes Grade-A return restocking (hygiene or security constraint)."
            expected_resale = round(retail_price * 0.70, 2)
            processing_cost = round(processing_base + 5.0, 2)
            confidence_score = "High"
            confidence_pct = 92
            alternatives = ["Return to supplier for credit agreement"]

    # RULE 2: Opened and Working (Full functionality, no fatal defect)
    elif item_condition == "Opened and working" or (
        functionality_status == "Fully Functional" and item_condition not in ["Confirmed defective", "Damaged"]
    ):
        if not has_missing_parts:
            recommended_action = "Refurbish"
            rule_triggered = "RULE_OPEN_BOX_REFURBISH_03"
            reason = (
                "Hardware fully passes all bench diagnostics. Opened packaging prevents pristine Grade-A restock, "
                "so item is approved for Certified Open-Box / Refurbished channel resale."
            )
            # Typically 80-85% resale value, repackaging cost $12
            expected_resale = round(retail_price * 0.82, 2)
            processing_cost = round(processing_base + 12.0, 2)
            confidence_score = "High"
            confidence_pct = 91
            alternatives = [
                "Restock after inspection if outer seal can be professionally reapplied",
                "Liquidate or sell through an approved secondary channel if overstocked"
            ]
        else:
            recommended_action = "Hold for further inspection"
            rule_triggered = "RULE_MISSING_ACC_WORKING_04"
            reason = (
                f"Core unit operates normally, but missing essential accessories ({missing_components}). "
                "Hold for replenishment kit matching before certifying for open-box resale."
            )
            expected_resale = round(retail_price * 0.70, 2)
            processing_cost = round(processing_base + 18.0, 2)
            confidence_score = "Medium"
            confidence_pct = 82
            alternatives = [
                "Liquidate or sell through an approved secondary channel as bare unit",
                "Salvage working unit for replacement buffer pool"
            ]

    # RULE 3: Confirmed Defective (Hardware failure / bench verified fault)
    elif item_condition == "Confirmed defective" or functionality_status in ["Complete Failure / Dead", "Intermittent Fault"]:
        # Sub-branch: High-value repair / supplier RMA vs Low-value disposal
        if retail_price >= 50.0:
            recommended_action = "Repair"
            rule_triggered = "RULE_BENCH_REPAIR_SUPPLIER_CLAIM_05"
            reason = (
                f"Confirmed hardware malfunction verified by bench technician (contrasted with customer claim). "
                f"Unit value (${retail_price:.2f}) economically justifies OEM warranty return or level-2 repair triage."
            )
            # Recovery through supplier credit or refurbished resale: ~65%
            expected_resale = round(retail_price * 0.65, 2)
            # Diagnostics + component repair cost: ~$22-$30
            processing_cost = round(processing_base + 22.0, 2)
            confidence_score = "High"
            confidence_pct = 89
            alternatives = [
                "Return to supplier for 100% vendor warranty reimbursement credit",
                "Liquidate or sell through an approved secondary channel for component salvage",
                "Dispose of according to applicable policy if circuit board delamination detected"
            ]
        else:
            recommended_action = "Dispose of according to applicable policy"
            rule_triggered = "RULE_UNECONOMIC_REPAIR_DISPOSAL_06"
            reason = (
                f"Defective unit retail value (${retail_price:.2f}) is below economic repair threshold. "
                "Estimated technician triage and freight costs exceed salvage value. Route to WEEE-compliant electronic recycling."
            )
            expected_resale = round(retail_price * 0.05, 2)  # Scrap/salvage value
            processing_cost = round(processing_base + 2.0, 2)
            confidence_score = "High"
            confidence_pct = 95
            alternatives = [
                "Liquidate or sell through an approved secondary channel as bulk scrap lot",
                "Aggregate for quarterly vendor quality penalty credit batch"
            ]

    # RULE 4: Damaged (Cosmetic, Structural, Transit)
    elif item_condition == "Damaged" or functionality_status == "Cosmetic Damage Only":
        recommended_action = "Liquidate or sell through an approved secondary channel"
        rule_triggered = "RULE_SECONDARY_CHANNEL_LIQUIDATION_07"
        reason = (
            "Physical/cosmetic enclosure damage prevents standard customer fulfillment. "
            "Bench test confirms secondary B2B wholesale auction recovery maximizes net return."
        )
        expected_resale = round(retail_price * 0.45, 2)
        processing_cost = round(processing_base + 6.0, 2)
        confidence_score = "Medium"
        confidence_pct = 84
        alternatives = [
            "Repair housing if replacement shell is in stock",
            "File courier freight damage claim if packaging was crushed in transit"
        ]

    # RULE 5: Missing Components (Incomplete item)
    elif item_condition == "Missing components":
        recommended_action = "Hold for further inspection"
        rule_triggered = "RULE_MISSING_PARTS_HOLD_08"
        reason = (
            f"Physical parts checklist failed: {missing_components}. "
            "Hold to verify whether missing components were omitted by customer or packaging error at factory."
        )
        expected_resale = round(retail_price * 0.60, 2)
        processing_cost = round(processing_base + 14.0, 2)
        confidence_score = "Medium"
        confidence_pct = 78
        alternatives = [
            "Refurbish with OEM replacement accessory kit",
            "Liquidate or sell through an approved secondary channel as incomplete lot"
        ]

    # RULE 6: Requires further inspection / Ambiguous
    else:
        recommended_action = "Hold for further inspection"
        rule_triggered = "RULE_AMBIGUOUS_TRIAGE_HOLD_09"
        reason = (
            "Diagnostic telemetry inconclusive. Customer noted intermittent failure requiring 48-hour thermal/stress test "
            "before disposition can be safely authorized."
        )
        expected_resale = round(retail_price * 0.50, 2)
        processing_cost = round(processing_base + 10.0, 2)
        confidence_score = "Low"
        confidence_pct = 58
        alternatives = [
            "Send to OEM factory testing center",
            "Liquidate or sell through an approved secondary channel as 'as-is' return"
        ]

    # Calculate net recovery: Net = expected resale - processing cost
    estimated_net_recovery = round(max(0.0, expected_resale - processing_cost), 2)
    # Edge case: if disposal with zero resale
    if recommended_action == "Dispose of according to applicable policy" and expected_resale < processing_cost:
        estimated_net_recovery = 0.0

    return {
        "recommended_action": recommended_action,
        "reason": reason,
        "rule_triggered": rule_triggered,
        "evidence_summary": " | ".join(evidence_items),
        "estimated_recovery_value": expected_resale,
        "estimated_processing_cost": processing_cost,
        "estimated_net_recovery": estimated_net_recovery,
        "confidence_score": confidence_score,
        "confidence_pct": confidence_pct,
        "alternative_actions": json.dumps(alternatives)
    }
