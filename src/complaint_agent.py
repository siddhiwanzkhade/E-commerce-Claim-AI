import json
from groq import Groq

from src.config import GROQ_API_KEY, GROQ_TEXT_MODEL
from src.prompts import COMPLAINT_ANALYSIS_PROMPT


client = Groq(api_key=GROQ_API_KEY)


def extract_json(text: str) -> dict:
    """
    Safely extracts JSON from LLM output.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1

        if start != -1 and end != 0:
            return json.loads(text[start:end])

        raise ValueError(f"Could not parse JSON from model output: {text}")


def analyze_complaint(complaint: str) -> dict:
    """
    Uses Groq LLM to analyze customer complaint text.
    """

    if not complaint or complaint.strip() == "":
        return {
            "issue_type": "unclear",
            "requested_action": "unclear",
            "sentiment": "neutral",
            "urgency": "low",
            "summary": "No complaint provided."
        }

    prompt = COMPLAINT_ANALYSIS_PROMPT.format(complaint=complaint)

    response = client.chat.completions.create(
        model=GROQ_TEXT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a strict JSON generator for e-commerce complaint analysis. Return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    output_text = response.choices[0].message.content

    return extract_json(output_text)


if __name__ == "__main__":
    print("Complaint agent started...")

    test_complaint = "My headphones arrived broken and the box was crushed. I want a replacement."

    print("Analyzing complaint...")
    result = analyze_complaint(test_complaint)

    print("Result:")
    print(json.dumps(result, indent=2))