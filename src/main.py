import json

from dotenv import load_dotenv

from src.inspector import inspect_image
from src.llm_insight import generate_factory_insight


load_dotenv()


def main():
    image_path = input("Enter image path: ")

    inspection_result = inspect_image(image_path)

    print("\nInspection JSON:")
    print(json.dumps(inspection_result, indent=4))

    if "error" not in inspection_result:
        insight = generate_factory_insight(inspection_result)

        print("\nFactory Manager Insight:")
        print(insight)


if __name__ == "__main__":
    main()