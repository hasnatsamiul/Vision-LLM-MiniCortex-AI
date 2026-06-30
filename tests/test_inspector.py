from unittest.mock import patch

from src.inspector import inspect_image


@patch("src.inspector.analyze_image_with_llm")
def test_inspect_image_with_mocked_llm(mock_llm, tmp_path):
    image_path = tmp_path / "sample_product.jpg"
    image_path.write_bytes(b"fake image content")

    mock_llm.return_value = {
        "status": "defect_detected",
        "confidence_score": 0.91,
        "defect_type": "scratch",
        "recommendation": "Send the product for manual QA review.",
    }

    result = inspect_image(str(image_path))

    assert result["image_filename"] == "sample_product.jpg"
    assert result["status"] == "defect_detected"
    assert result["confidence_score"] == 0.91
    assert result["defect_type"] == "scratch"
    assert "processing_time_ms" in result


def test_file_not_found():
    result = inspect_image("missing_image.jpg")

    assert result["error"] == "file_not_found"


def test_unsupported_format(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("this is not an image")

    result = inspect_image(str(file_path))

    assert result["error"] == "unsupported_format"