import json
import re

from google import genai
from utils.config import GEMINI_API_KEY


MODEL_NAME = "gemini-3.6-flash"

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def clean_json_response(text):

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


def extract_financial_data(text):

    prompt = f"""
You are a financial data extraction system.

Extract structured financial information from
the following financial report.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "company": "company name",
    "financial_data": [
        {{
            "year": 2025,
            "revenue": 0,
            "operating_expense": 0,
            "operating_income": 0,
            "net_income": 0,
            "total_assets": 0,
            "total_liabilities": 0,
            "total_equity": 0,
            "operating_cash_flow": 0
        }}
    ]
}}

Rules:

1. Extract every available financial year.
2. Use numeric values only.
3. Do not include currency symbols.
4. Do not include commas in numbers.
5. Do not invent values.
6. If a value cannot be found, use null.
7. Preserve the actual company name.
8. Return ONLY JSON.
9. Do not return explanations.
10. Do not use markdown.

Financial report:

{text[:120000]}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    response_text = response.text

    cleaned_response = clean_json_response(
        response_text
    )

    try:

        data = json.loads(
            cleaned_response
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "Gemini returned invalid JSON.\n\n"
            f"Response:\n{response_text}\n\n"
            f"Error:\n{error}"
        )

    if "company" not in data:

        data["company"] = "Unknown Company"

    if "financial_data" not in data:

        data["financial_data"] = []

    return data