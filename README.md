# E-commerce-Claim-AI
E-commerce Claim AI is an agentic multimodal RAG system designed to improve customer satisfaction in e-commerce issue resolution. By leveraging LLMs, VLMs, policy-grounded retrieval, and risk scoring, it evaluates customer complaints and recommends refund, replacement, manual review, or escalation decisions.

## Features

- **Agentic Claim Processing:** Utilizes an AI agent workflow to assess e-commerce product issues swiftly, reducing manual intervention and improving customer issue resolution.

- **Multimodal Image Analysis:** Employs Vision-Language Models (VLMs) to evaluate uploaded product/package images for damage assessment, ensuring evidence-based claim evaluations.

- **Natural Language Processing:** Analyzes customer-submitted complaints to extract issue type, sentiment, urgency, requested action, and missing information relevant to the claim.

- **Policy-Grounded RAG:** Retrieves relevant refund, return, replacement, and damaged-delivery policies using LangChain, ChromaDB, and vector search to support grounded resolution decisions.

- **Risk Scoring:** Incorporates risk and eligibility logic to identify image-text mismatches, missing proof, policy violations, and claims that require manual review or escalation.

- **Customer Satisfaction-Aware Resolution:** Generates customer-friendly refund, replacement, manual review, or escalation recommendations to improve transparency and support experience.
