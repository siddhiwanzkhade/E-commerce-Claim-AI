import json
import time
from datetime import datetime
from pathlib import Path

from src.complaint_agent import analyze_complaint
from src.order_agent import analyze_order
from src.vision_agent import analyze_product_image
from src.policy_rag_agent import retrieve_policy_for_claim
from src.resolution_agent import resolve_claim


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "claim_runs.jsonl"


def log_claim_run(result: dict) -> None:
    """
    Saves each full pipeline run as one JSON line.

    This gives us basic observability/auditability:
    - agent outputs
    - final decision
    - policy evidence
    - timing metrics
    """

    LOG_DIR.mkdir(exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(result) + "\n")


def run_claim_crew(
    complaint_text: str,
    order_data: dict,
    image_path: str,
    vision_backend: str = "groq",
    enable_logging: bool = True
) -> dict:
    """
    Runs the full claim workflow in a CrewAI-style sequence.

    Workflow:
    1. Complaint Agent analyzes customer complaint.
    2. Order Agent checks order metadata and risk.
    3. Vision Agent inspects product image.
    4. Policy RAG Agent retrieves relevant policy evidence.
    5. Resolution Agent creates final decision.

    Also tracks processing time for each step.
    """

    timings = {}
    pipeline_start = time.perf_counter()

    # -----------------------------
    # 1. Complaint Agent
    # -----------------------------
    start = time.perf_counter()

    complaint_result = analyze_complaint(complaint_text)

    timings["complaint_agent_seconds"] = round(
        time.perf_counter() - start,
        3
    )

    # -----------------------------
    # 2. Order Agent
    # -----------------------------
    start = time.perf_counter()

    order_result = analyze_order(order_data)

    timings["order_agent_seconds"] = round(
        time.perf_counter() - start,
        3
    )

    # -----------------------------
    # 3. Vision Agent
    # -----------------------------
    start = time.perf_counter()

    vision_result = analyze_product_image(
        image_path=image_path,
        backend=vision_backend
    )

    timings["vision_agent_seconds"] = round(
        time.perf_counter() - start,
        3
    )

    # -----------------------------
    # 4. Policy RAG Agent
    # -----------------------------
    start = time.perf_counter()

    policy_result = retrieve_policy_for_claim(
        complaint_result=complaint_result,
        order_result=order_result,
        vision_result=vision_result,
        top_k=3
    )

    timings["policy_rag_seconds"] = round(
        time.perf_counter() - start,
        3
    )

    # -----------------------------
    # 5. Resolution Agent
    # -----------------------------
    start = time.perf_counter()

    resolution_result = resolve_claim(
        complaint_result=complaint_result,
        order_result=order_result,
        vision_result=vision_result
    )

    timings["resolution_agent_seconds"] = round(
        time.perf_counter() - start,
        3
    )

    # Attach retrieved policy evidence to final output.
    resolution_result["policy_evidence"] = policy_result["retrieved_evidence"]

    timings["total_pipeline_seconds"] = round(
        time.perf_counter() - pipeline_start,
        3
    )

    result = {
        "timestamp": datetime.now().isoformat(),
        "vision_backend": vision_backend,
        "complaint_analysis": complaint_result,
        "order_analysis": order_result,
        "vision_analysis": vision_result,
        "policy_rag": policy_result,
        "final_resolution": resolution_result,
        "timings": timings
    }

    if enable_logging:
        log_claim_run(result)

    return result


if __name__ == "__main__":
    sample_complaint = "My headphones arrived broken and the box was crushed. I want a replacement."

    sample_order = {
        "order_id": "ORD12345",
        "product_name": "Wireless Headphones",
        "order_value": 149.99,
        "delivery_status": "delivered",
        "delivery_date": "2026-05-25",
        "return_deadline": "2026-06-24",
        "customer_previous_claims": 1
    }

    sample_image_path = "/Users/siddhiwanzkhade/E-commerce Claim AI/data/policy/images/test_damage.jpg"

    result = run_claim_crew(
        complaint_text=sample_complaint,
        order_data=sample_order,
        image_path=sample_image_path,
        vision_backend="groq"
    )

    print(json.dumps(result, indent=2))
    