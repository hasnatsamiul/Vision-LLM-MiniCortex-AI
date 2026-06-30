import base64
import json
import os
import time

from dotenv import load_dotenv
from groq import Groq
from groq import APITimeoutError, APIConnectionError


SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".webp"]


class UnsupportedImageFormatError(Exception):
    pass


class VisionAPITimeoutError(Exception):
    pass


INSPECTION_PROMPT = """
You are MiniCorteX, an AI visual inspection assistant for manufacturing.

Inspect the product image and detect visible defects or anomalies.

Return ONLY valid JSON with exactly this structure:
{
  "status": "defect_detected" or "no_defect_detected",
  "confidence_score": number between 0 and 1,
  "defect_type": "scratch" | "crack" | "stain" | "deformation" | "missing_part" | "color_anomaly" | "surface_anomaly" | "none",
  "recommendation": "short practical recommendation"
}

Rules:
- If there is a visible defect, use "defect_detected".
- If no visible defect is found, use "no_defect_detected".
- If the image is unclear, reduce the confidence score.
- If no defect is detected, defect_type must be "none".
- Do not include markdown.
- Do not include explanation outside JSON.
"""


def validate_image_path(image_path: str) -> None:
    if not os.path.exists(image_path):
        raise FileNotFoundError("Image file not found.")

    file_extension = os.path.splitext(image_path)[1].lower()

    if file_extension not in SUPPORTED_FORMATS:
        raise UnsupportedImageFormatError(
            f"Unsupported image format: {file_extension}"
        )


def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_mime_type(image_path: str) -> str:
    extension = os.path.splitext(image_path)[1].lower()

    if extension in [".jpg", ".jpeg"]:
        return "image/jpeg"

    if extension == ".png":
        return "image/png"

    if extension == ".webp":
        return "image/webp"

    return "image/jpeg"


def analyze_image_with_llm(image_path: str, timeout_seconds: int = 30) -> dict:
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Please add it to your .env file.")

    client = Groq(api_key=api_key)

    encoded_image = encode_image_to_base64(image_path)
    mime_type = get_image_mime_type(image_path)

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            timeout=timeout_seconds,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": INSPECTION_PROMPT,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{encoded_image}"
                            },
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        return json.loads(content)

    except (APITimeoutError, APIConnectionError) as error:
        raise VisionAPITimeoutError("Groq Vision API request failed.") from error


def normalize_llm_result(llm_result: dict) -> dict:
    return {
        "status": llm_result.get("status", "unknown"),
        "confidence_score": float(llm_result.get("confidence_score", 0.0)),
        "defect_type": llm_result.get("defect_type", "unknown"),
        "recommendation": llm_result.get(
            "recommendation",
            "Manual review recommended.",
        ),
    }


def inspect_image(image_path: str) -> dict:
    start_time = time.time()

    try:
        validate_image_path(image_path)

        llm_result = analyze_image_with_llm(image_path)
        normalized_result = normalize_llm_result(llm_result)

        processing_time_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "image_filename": os.path.basename(image_path),
            "status": normalized_result["status"],
            "confidence_score": normalized_result["confidence_score"],
            "defect_type": normalized_result["defect_type"],
            "recommendation": normalized_result["recommendation"],
            "processing_time_ms": processing_time_ms,
        }

    except FileNotFoundError as error:
        return {
            "error": "file_not_found",
            "message": str(error),
        }

    except UnsupportedImageFormatError as error:
        return {
            "error": "unsupported_format",
            "message": str(error),
        }

    except VisionAPITimeoutError as error:
        return {
            "error": "api_timeout",
            "message": str(error),
        }

    except Exception as error:
        return {
            "error": "inspection_failed",
            "message": str(error),
        }