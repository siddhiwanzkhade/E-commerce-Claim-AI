import json
import gradio as gr

from src.crew_workflow import run_claim_crew


def run_app(
    complaint_text,
    product_image,
    vision_backend,
    order_id,
    product_name,
    order_value,
    delivery_status,
    delivery_date,
    return_deadline,
    customer_previous_claims
):
    """
    Runs the full E-commerce ClaimAI workflow from the Gradio UI.

    Flow:
    Complaint + Order Metadata + Product Image
        ↓
    crew_workflow.py
        ↓
    Complaint Agent
    Order Agent
    Vision Agent
    Policy RAG Agent
    Resolution Agent
        ↓
    Final claim decision + timing metrics
    """

    try:
        if not complaint_text or complaint_text.strip() == "":
            error = {"error": "Please enter a customer complaint."}
            return (
                json.dumps(error, indent=2),
                "{}",
                "{}",
                "{}",
                "{}",
                "{}",
                product_image
            )

        order_data = {
            "order_id": order_id,
            "product_name": product_name,
            "order_value": order_value,
            "delivery_status": delivery_status,
            "delivery_date": delivery_date,
            "return_deadline": return_deadline,
            "customer_previous_claims": customer_previous_claims
        }

        # Run the complete orchestrated workflow.
        result = run_claim_crew(
            complaint_text=complaint_text,
            order_data=order_data,
            image_path=product_image,
            vision_backend=vision_backend
        )

        complaint_result = result.get("complaint_analysis", {})
        order_result = result.get("order_analysis", {})
        vision_result = result.get("vision_analysis", {})
        policy_result = result.get("policy_rag", {})
        resolution_result = result.get("final_resolution", {})
        timings_result = result.get("timings", {})

        return (
            json.dumps(complaint_result, indent=2),
            json.dumps(order_result, indent=2),
            json.dumps(vision_result, indent=2),
            json.dumps(policy_result, indent=2),
            json.dumps(resolution_result, indent=2),
            json.dumps(timings_result, indent=2),
            product_image
        )

    except Exception as e:
        error = {"error": str(e)}

        return (
            json.dumps(error, indent=2),
            "{}",
            "{}",
            "{}",
            "{}",
            "{}",
            product_image
        )


with gr.Blocks(title="E-commerce ClaimAI") as demo:
    gr.Markdown("# E-commerce ClaimAI")
    gr.Markdown(
        "A multimodal, policy-grounded claim-resolution system using complaint analysis, "
        "order-risk evaluation, VLM-based damage inspection, RAG-based policy retrieval, "
        "and final resolution reasoning."
    )

    with gr.Row():
        with gr.Column():
            gr.Markdown("## Customer Inputs")

            complaint_input = gr.Textbox(
                label="Customer Complaint",
                placeholder="Example: My headphones arrived broken and the box was crushed. I want a replacement.",
                lines=5
            )

            product_image_input = gr.Image(
                label="Upload Damaged Product Image",
                type="filepath"
            )

            vision_backend_input = gr.Dropdown(
                label="Vision Backend",
                choices=["groq", "mlx"],
                value="groq"
            )

        with gr.Column():
            gr.Markdown("## Order Metadata")

            order_id_input = gr.Textbox(
                label="Order ID",
                value="ORD12345"
            )

            product_name_input = gr.Textbox(
                label="Product Name",
                value="Wireless Headphones"
            )

            order_value_input = gr.Number(
                label="Order Value",
                value=149.99
            )

            delivery_status_input = gr.Dropdown(
                label="Delivery Status",
                choices=["delivered", "in_transit", "delayed", "not_delivered"],
                value="delivered"
            )

            delivery_date_input = gr.Textbox(
                label="Delivery Date YYYY-MM-DD",
                value="2026-05-25"
            )

            return_deadline_input = gr.Textbox(
                label="Return Deadline YYYY-MM-DD",
                value="2026-06-24"
            )

            customer_previous_claims_input = gr.Number(
                label="Customer Previous Claims",
                value=1
            )

    analyze_button = gr.Button("Analyze Full Claim")

    gr.Markdown("## Agent Outputs")

    with gr.Row():
        complaint_output = gr.Code(
            label="Complaint Agent Output",
            language="json"
        )

        order_output = gr.Code(
            label="Order Agent Output",
            language="json"
        )

    with gr.Row():
        vision_output = gr.Code(
            label="Vision Agent Output",
            language="json"
        )

        image_preview = gr.Image(
            label="Uploaded Product Image Preview"
        )

    policy_output = gr.Code(
        label="Policy RAG Output",
        language="json"
    )

    resolution_output = gr.Code(
        label="Final Resolution Output",
        language="json"
    )

    timings_output = gr.Code(
        label="Timing Metrics Output",
        language="json"
    )

    analyze_button.click(
        fn=run_app,
        inputs=[
            complaint_input,
            product_image_input,
            vision_backend_input,
            order_id_input,
            product_name_input,
            order_value_input,
            delivery_status_input,
            delivery_date_input,
            return_deadline_input,
            customer_previous_claims_input
        ],
        outputs=[
            complaint_output,
            order_output,
            vision_output,
            policy_output,
            resolution_output,
            timings_output,
            image_preview
        ]
    )


if __name__ == "__main__":
    demo.launch()