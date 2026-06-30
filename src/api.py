import csv
import os
import shutil
import tempfile
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from src.inspector import inspect_image
from src.llm_insight import generate_factory_insight


load_dotenv()

app = FastAPI(
    title="MiniCorteX Vision LLM API",
    description="AI visual inspection service with factory manager insight.",
    version="1.0.0",
)

latest_result = None
LOG_FILE_PATH = "logs/inspection_logs.csv"


def shorten_text(text: str | None, max_length: int = 120) -> str:
    if not text:
        return "No insight generated."

    cleaned_text = " ".join(text.split())

    if len(cleaned_text) <= max_length:
        return cleaned_text

    return cleaned_text[:max_length] + "..."


def append_inspection_log(inspection_result: dict, insight: str | None) -> None:
    os.makedirs("logs", exist_ok=True)

    file_exists = os.path.exists(LOG_FILE_PATH)

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "image_filename": inspection_result.get("image_filename", "unknown"),
        "defect_status": inspection_result.get("status", "unknown"),
        "confidence_score": inspection_result.get("confidence_score", 0.0),
        "defect_type": inspection_result.get("defect_type", "unknown"),
        "llm_insight_summary": shorten_text(insight),
    }

    fieldnames = [
        "timestamp",
        "image_filename",
        "defect_status",
        "confidence_score",
        "defect_type",
        "llm_insight_summary",
    ]

    with open(LOG_FILE_PATH, mode="a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


@app.get("/")
def health_check():
    return {
        "message": "MiniCorteX API is running",
        "inspect_endpoint": "POST /inspect",
        "latest_result_endpoint": "GET /latest-result",
    }


@app.post("/inspect")
async def inspect_uploaded_image(file: UploadFile = File(...)):
    global latest_result

    supported_extensions = [".jpg", ".jpeg", ".png", ".webp"]

    original_filename = file.filename
    file_extension = os.path.splitext(original_filename)[1].lower()

    if file_extension not in supported_extensions:
        latest_result = {
            "error": "unsupported_format",
            "message": f"Unsupported file format: {file_extension}",
        }

        return JSONResponse(status_code=400, content=latest_result)

    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        inspection_result = inspect_image(temp_file_path)
        inspection_result["image_filename"] = original_filename

        if "error" in inspection_result:
            latest_result = {
                "inspection_result": inspection_result,
                "factory_manager_insight": None,
                "logged": False,
            }

            return JSONResponse(status_code=400, content=latest_result)

        insight = generate_factory_insight(inspection_result)

        append_inspection_log(inspection_result, insight)

        latest_result = {
            "inspection_result": inspection_result,
            "factory_manager_insight": insight,
            "logged": True,
            "log_file": LOG_FILE_PATH,
        }

        return latest_result

    except Exception as error:
        latest_result = {
            "error": "api_error",
            "message": str(error),
            "logged": False,
        }

        return JSONResponse(status_code=500, content=latest_result)

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.get("/latest-result")
def get_latest_result():
    if latest_result is None:
        return {
            "message": "No inspection result available yet. Please upload an image using POST /inspect first."
        }

    return latest_result