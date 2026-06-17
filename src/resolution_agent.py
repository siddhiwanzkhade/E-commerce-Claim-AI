import json


def resolve_claim(
    complaint_result: dict,
    order_result: dict,
    vision_result: dict
) -> dict:
    """
    Combines complaint analysis, order metadata analysis, and image damage analysis
    to recommend a final claim resolution.

    This is the decision layer of the system.
    """

    # Extract complaint signals
   
    issue_type = complaint_result.get("issue_type", "unclear")
    requested_action = complaint_result.get("requested_action", "unclear")
    sentiment = complaint_result.get("sentiment", "neutral")
    urgency = complaint_result.get("urgency", "low")
    complaint_summary = complaint_result.get("summary", "")

    
    # Extract order signals
    
    return_window_status = order_result.get("return_window_status", "unknown")
    delivery_issue = order_result.get("delivery_issue", "unknown")
    order_value_risk = order_result.get("order_value_risk", "unknown")
    customer_claim_risk = order_result.get("customer_claim_risk", "unknown")
    order_hint = order_result.get("recommended_action_hint", "policy_check_required")

    # -----------------------------
    # Extract vision/image signals
    # -----------------------------
    damage_detected = vision_result.get("damage_detected", False)
    damage_type = vision_result.get("damage_type", "unclear")
    damage_severity = vision_result.get("damage_severity", "unknown")
    visible_evidence = vision_result.get("visible_evidence", "")
    vision_confidence = vision_result.get("confidence", "low")
    vision_backend = vision_result.get("model_backend", "unknown")

    reasons = []

    # Build explanation reasons
    
    if issue_type != "unclear":
        reasons.append(f"Complaint indicates issue type: {issue_type}.")

    if requested_action != "unclear":
        reasons.append(f"Customer requested: {requested_action}.")

    if complaint_summary:
        reasons.append(f"Complaint summary: {complaint_summary}")

    if damage_detected:
        reasons.append(
            f"Image evidence supports damage: {damage_type} with {damage_severity} severity."
        )
    else:
        reasons.append("Image evidence does not clearly confirm visible damage.")

    if visible_evidence:
        reasons.append(f"Visible evidence: {visible_evidence}")

    if return_window_status == "within_return_window":
        reasons.append("Order is within the return/replacement window.")
    elif return_window_status == "outside_return_window":
        reasons.append("Order is outside the return/replacement window.")

    if customer_claim_risk == "high":
        reasons.append("Customer has high previous-claim risk.")
    elif customer_claim_risk == "medium":
        reasons.append("Customer has medium previous-claim risk.")
    elif customer_claim_risk == "low":
        reasons.append("Customer has low previous-claim risk.")

    if order_value_risk == "high":
        reasons.append("Order value is high, so manual review may be required.")

    # Decision rules
   
    # Rule 1: High-risk customer should go to manual review
    if customer_claim_risk == "high":
        final_decision = "manual_review"
        confidence = "medium"

    # Rule 2: High-value orders should be manually reviewed
    elif order_value_risk == "high":
        final_decision = "manual_review"
        confidence = "medium"

    # Rule 3: Damaged item + replacement request + image confirms damage + eligible order
    elif (
        issue_type == "damaged_item"
        and requested_action == "replacement"
        and damage_detected is True
        and return_window_status == "within_return_window"
    ):
        final_decision = "replacement"
        confidence = "high"

    # Rule 4: Damaged item + refund request + image confirms damage + eligible order
    elif (
        issue_type == "damaged_item"
        and requested_action == "refund"
        and damage_detected is True
        and return_window_status == "within_return_window"
    ):
        final_decision = "refund"
        confidence = "high"

    # Rule 5: Missing item or not delivered cases
    elif issue_type == "missing_item" or delivery_issue == "not_delivered":
        final_decision = "manual_review"
        confidence = "medium"

    # Rule 6: Late delivery refund case
    elif (
        issue_type == "late_delivery"
        and requested_action == "refund"
        and return_window_status == "within_return_window"
    ):
        final_decision = "refund"
        confidence = "medium"

    # Rule 7: Outside return window needs policy check/manual review
    elif return_window_status == "outside_return_window":
        final_decision = "manual_review"
        confidence = "medium"

    # Rule 8: If order agent says policy check is required
    elif order_hint == "policy_check_required":
        final_decision = "manual_review"
        confidence = "medium"

    # Default fallback
    else:
        final_decision = "manual_review"
        confidence = "low"

  
    # Escalation logic
    
    escalation_required = False

    if urgency == "high":
        escalation_required = True

    if customer_claim_risk == "high":
        escalation_required = True

    if order_value_risk == "high":
        escalation_required = True

    # Final structured output
    
    return {
        "final_decision": final_decision,
        "confidence": confidence,
        "escalation_required": escalation_required,
        "customer_sentiment": sentiment,
        "urgency": urgency,
        "reason": " ".join(reasons),
        "signals_used": {
            "issue_type": issue_type,
            "requested_action": requested_action,
            "return_window_status": return_window_status,
            "delivery_issue": delivery_issue,
            "order_value_risk": order_value_risk,
            "customer_claim_risk": customer_claim_risk,
            "damage_detected": damage_detected,
            "damage_type": damage_type,
            "damage_severity": damage_severity,
            "vision_confidence": vision_confidence,
            "vision_backend": vision_backend
        }
    }


if __name__ == "__main__":
    sample_complaint_result = {
        "issue_type": "damaged_item",
        "requested_action": "replacement",
        "sentiment": "negative",
        "urgency": "high",
        "summary": "Headphones arrived broken and the box was crushed."
    }

    sample_order_result = {
        "status": "success",
        "order_id": "ORD12345",
        "product_name": "Wireless Headphones",
        "return_window_status": "within_return_window",
        "delivery_issue": "delivered",
        "order_value_risk": "medium",
        "customer_claim_risk": "low",
        "recommended_action_hint": "eligible_for_resolution"
    }

    sample_vision_result = {
        "damage_detected": True,
        "damage_type": "broken_component",
        "damage_severity": "medium",
        "visible_evidence": "The earbud's metal component appears detached.",
        "confidence": "high",
        "model_backend": "groq_vision"
    }

    result = resolve_claim(
        sample_complaint_result,
        sample_order_result,
        sample_vision_result
    )

    print(json.dumps(result, indent=2))