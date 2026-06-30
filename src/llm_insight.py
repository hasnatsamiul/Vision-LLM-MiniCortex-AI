import json
import os

from dotenv import load_dotenv
from groq import Groq
from groq import APIConnectionError, APITimeoutError, APIStatusError


INSIGHT_PROMPT = """
You are MiniCorteX, an AI assistant for manufacturing quality inspection.

Your task is to explain an inspection result to a non-technical factory floor manager.

Use the inspection JSON as context and write one short plain-English paragraph.

The explanation must include:
- whether a defect was detected
- the defect type
- the confidence score as a percentage
- a likely operational cause
- a practical recommendation for the factory team

Keep the language simple, clear, and useful for a factory floor manager.

Do not use technical AI terms.
Do not mention JSON.
Do not use bullet points.
Do not exaggerate certainty.
"""


FALLBACK_INSIGHT = (
    "The inspection result is available, but the AI insight service is currently "
    "unavailable. Please review the defect status, confidence score, defect type, "
    "and recommendation manually."
)


def format_inspection_context(inspection_result: dict) -> str:
    return json.dumps(inspection_result, indent=2)


def generate_factory_insight(inspection_result: dict, timeout_seconds: int = 30) -> str:
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return FALLBACK_INSIGHT

    client = Groq(api_key=api_key)
    inspection_context = format_inspection_context(inspection_result)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            timeout=timeout_seconds,
            messages=[
                {
                    "role": "system",
                    "content": INSIGHT_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"Inspection result:\n{inspection_context}",
                },
            ],
        )

        insight = response.choices[0].message.content

        if not insight:
            return FALLBACK_INSIGHT

        return insight.strip()

    except (APITimeoutError, APIConnectionError, APIStatusError):
        return FALLBACK_INSIGHT

    except Exception:
        return FALLBACK_INSIGHT