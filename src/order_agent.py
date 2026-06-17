from datetime import datetime
import json


def analyze_order(order: dict) -> dict:
    """
    Analyzes order metadata for an e-commerce claim.
    """

    required_fields = [
        "order_id",
        "product_name",
        "order_value",
        "delivery_status",
        "delivery_date",
        "return_deadline",
        "customer_previous_claims"
    ]

    missing_fields = [field for field in required_fields if field not in order]

    if missing_fields:
        return {
            "status": "error",
            "message": f"Missing fields: {missing_fields}"
        }

    today = datetime.today().date()

    return_deadline = datetime.strptime(order["return_deadline"], "%Y-%m-%d").date()

    if today <= return_deadline:
        return_window_status = "within_return_window"
    else:
        return_window_status = "outside_return_window"

    delivery_status = order["delivery_status"].lower()

    if delivery_status == "delivered":
        delivery_issue = "delivered"
    elif delivery_status == "in_transit":
        delivery_issue = "still_in_transit"
    elif delivery_status == "delayed":
        delivery_issue = "delivery_delayed"
    elif delivery_status == "not_delivered":
        delivery_issue = "not_delivered"
    else:
        delivery_issue = "unknown_delivery_status"

    order_value = float(order["order_value"])

    if order_value >= 500:
        order_value_risk = "high"
    elif order_value >= 100:
        order_value_risk = "medium"
    else:
        order_value_risk = "low"

    previous_claims = int(order["customer_previous_claims"])

    if previous_claims >= 5:
        customer_claim_risk = "high"
    elif previous_claims >= 2:
        customer_claim_risk = "medium"
    else:
        customer_claim_risk = "low"

    if return_window_status == "within_return_window" and customer_claim_risk != "high":
        recommended_action_hint = "eligible_for_resolution"
    elif customer_claim_risk == "high":
        recommended_action_hint = "manual_review_recommended"
    else:
        recommended_action_hint = "policy_check_required"

    return {
        "status": "success",
        "order_id": order["order_id"],
        "product_name": order["product_name"],
        "return_window_status": return_window_status,
        "delivery_issue": delivery_issue,
        "order_value_risk": order_value_risk,
        "customer_claim_risk": customer_claim_risk,
        "recommended_action_hint": recommended_action_hint
    }


if __name__ == "__main__":
    sample_order = {
        "order_id": "ORD12345",
        "product_name": "Wireless Headphones",
        "order_value": 149.99,
        "delivery_status": "delivered",
        "delivery_date": "2026-05-25",
        "return_deadline": "2026-06-24",
        "customer_previous_claims": 1
    }

    result = analyze_order(sample_order)

    print(json.dumps(result, indent=2))