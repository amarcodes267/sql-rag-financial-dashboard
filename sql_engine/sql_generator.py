from google import genai

from utils.config import GEMINI_API_KEY
from sql_engine.sql_service import execute_query


MODEL_NAME = "gemini-3.6-flash"

client = genai.Client(
    api_key=GEMINI_API_KEY
)


DATABASE_SCHEMA = """
companies(
    id INTEGER,
    name TEXT
)

financial_data(
    id INTEGER,
    company_id INTEGER,
    year INTEGER,
    revenue REAL,
    operating_expense REAL,
    operating_income REAL,
    net_income REAL,
    total_assets REAL,
    total_liabilities REAL,
    total_equity REAL,
    operating_cash_flow REAL
)
"""


def generate_sql(question):

    prompt = f"""
Generate one SQLite SELECT query for this financial question.

Database schema:
{DATABASE_SCHEMA}

Rules:
- Return ONLY SQL.
- Only SELECT is allowed.
- Do not use markdown.
- Do not modify data.
- Use only columns from the schema.

Question:
{question}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    sql = response.text.strip()

    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")

    return sql.strip()


def format_sql_result(question, data):

    if not data:

        return (
            "No matching financial data was found "
            "in the database."
        )

    if len(data) == 1:

        row = data[0]

        parts = []

        for key, value in row.items():

            if value is not None:

                if isinstance(value, (int, float)):

                    parts.append(
                        f"{key.replace('_', ' ').title()}: "
                        f"{value:,.2f}"
                    )

                else:

                    parts.append(
                        f"{key.replace('_', ' ').title()}: "
                        f"{value}"
                    )

        return "\n\n".join(parts)

    return (
        f"I found {len(data)} matching financial records. "
        "The detailed result is shown below."
    )


def answer_with_sql(question):

    sql = generate_sql(
        question
    )

    if not sql.lower().startswith("select"):

        return {
            "sql": sql,
            "data": [],
            "answer": "Only SELECT queries are allowed."
        }

    try:

        data = execute_query(
            sql
        )

        answer = format_sql_result(
            question,
            data
        )

        return {
            "sql": sql,
            "data": data,
            "answer": answer
        }

    except Exception as error:

        return {
            "sql": sql,
            "data": [],
            "answer": (
                f"Unable to retrieve the financial data: "
                f"{error}"
            )
        }