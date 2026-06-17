import json
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.config import POLICY_DIR, CHROMA_DIR


def load_policy_documents():
    """
    Loads all .txt policy files from data/policy.
    """

    policy_path = Path(POLICY_DIR)

    documents = []

    for file_path in policy_path.glob("*.txt"):
        loader = TextLoader(str(file_path), encoding="utf-8")
        docs = loader.load()

        for doc in docs:
            doc.metadata["source"] = file_path.name

        documents.extend(docs)

    return documents


def build_policy_vectorstore():
    """
    Builds or refreshes a ChromaDB vector store from policy documents.
    """

    documents = load_policy_documents()

    if not documents:
        raise ValueError(f"No policy documents found in {POLICY_DIR}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80
    )

    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

    return vectorstore


def get_policy_vectorstore():
    """
    Loads existing ChromaDB vector store if it exists.
    Otherwise builds it from policy files.
    """

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        return Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings
        )

    return build_policy_vectorstore()


def retrieve_policy_evidence(query: str, top_k: int = 3) -> dict:
    """
    Retrieves top relevant policy chunks for a claim-related query.
    """

    vectorstore = get_policy_vectorstore()

    results = vectorstore.similarity_search_with_score(
        query=query,
        k=top_k
    )

    evidence = []

    for doc, score in results:
        evidence.append({
            "source_policy": doc.metadata.get("source", "unknown"),
            "content": doc.page_content,
            "similarity_score": float(score)
        })

    return {
        "query": query,
        "retrieved_evidence": evidence
    }


def build_policy_query(
    complaint_result: dict,
    order_result: dict,
    vision_result: dict
) -> str:
    """
    Converts agent outputs into a search query for policy retrieval.
    """

    issue_type = complaint_result.get("issue_type", "unclear")
    requested_action = complaint_result.get("requested_action", "unclear")
    urgency = complaint_result.get("urgency", "low")

    return_window_status = order_result.get("return_window_status", "unknown")
    customer_claim_risk = order_result.get("customer_claim_risk", "unknown")
    order_value_risk = order_result.get("order_value_risk", "unknown")

    damage_detected = vision_result.get("damage_detected", False)
    damage_type = vision_result.get("damage_type", "unclear")
    damage_severity = vision_result.get("damage_severity", "unknown")

    query = f"""
    Customer claim policy lookup:
    issue_type: {issue_type}
    requested_action: {requested_action}
    urgency: {urgency}
    return_window_status: {return_window_status}
    customer_claim_risk: {customer_claim_risk}
    order_value_risk: {order_value_risk}
    damage_detected: {damage_detected}
    damage_type: {damage_type}
    damage_severity: {damage_severity}

    Find refund, replacement, damaged delivery, return, or escalation policy evidence.
    """

    return query


def retrieve_policy_for_claim(
    complaint_result: dict,
    order_result: dict,
    vision_result: dict,
    top_k: int = 3
) -> dict:
    """
    Main function used by the full pipeline.

    Takes outputs from complaint/order/vision agents and retrieves
    relevant policy evidence.
    """

    query = build_policy_query(
        complaint_result=complaint_result,
        order_result=order_result,
        vision_result=vision_result
    )

    return retrieve_policy_evidence(query=query, top_k=top_k)


if __name__ == "__main__":
    sample_complaint = {
        "issue_type": "damaged_item",
        "requested_action": "replacement",
        "sentiment": "negative",
        "urgency": "high",
        "summary": "Headphones arrived broken and the box was crushed."
    }

    sample_order = {
        "return_window_status": "within_return_window",
        "delivery_issue": "delivered",
        "order_value_risk": "medium",
        "customer_claim_risk": "low",
        "recommended_action_hint": "eligible_for_resolution"
    }

    sample_vision = {
        "damage_detected": True,
        "damage_type": "broken_component",
        "damage_severity": "medium",
        "visible_evidence": "The earbud component appears detached.",
        "confidence": "high"
    }

    result = retrieve_policy_for_claim(
        complaint_result=sample_complaint,
        order_result=sample_order,
        vision_result=sample_vision
    )

    print(json.dumps(result, indent=2))