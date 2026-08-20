from google import genai

from utils.config import GEMINI_API_KEY
from sql_engine.sql_generator import answer_with_sql
from rag.rag_service import answer_with_rag


MODEL_NAME = "gemini-3.6-flash"

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def classify_question_locally(question):

    q = question.lower().strip()

    sql_keywords = [
        "revenue",
        "sales",
        "profit",
        "net income",
        "income",
        "expense",
        "expenses",
        "assets",
        "liabilities",
        "equity",
        "cash flow",
        "cash",
        "growth",
        "percentage",
        "percent",
        "compare",
        "comparison",
        "total",
        "average",
        "how much",
        "how many",
        "financial",
        "2023",
        "2024",
        "2025",
        "2026"
    ]

    rag_keywords = [
        "why",
        "reason",
        "risk",
        "risks",
        "strategy",
        "management",
        "future",
        "outlook",
        "explain",
        "business",
        "market",
        "competition",
        "products",
        "services",
        "challenge",
        "challenges"
    ]

    has_sql = any(
        keyword in q
        for keyword in sql_keywords
    )

    has_rag = any(
        keyword in q
        for keyword in rag_keywords
    )

    if has_sql and has_rag:
        return "HYBRID"

    if has_sql:
        return "SQL"

    return "RAG"


def answer_hybrid(question):

    sql_result = answer_with_sql(
        question
    )

    rag_result = answer_with_rag(
        question
    )

    prompt = f"""
You are a financial analyst.

Answer the question using the SQL result
and financial report analysis.

Question:
{question}

SQL Result:
{sql_result["data"]}

Report Analysis:
{rag_result}

Rules:
- Do not invent information.
- Use SQL for numerical facts.
- Use report analysis for explanations.
- Give a concise answer.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return {
        "type": "HYBRID",
        "answer": response.text,
        "sql_data": sql_result["data"],
        "rag_answer": rag_result
    }


def process_question(question):

    category = classify_question_locally(
        question
    )

    if category == "SQL":

        result = answer_with_sql(
            question
        )

        return {
            "type": "SQL",
            "answer": result["answer"],
            "data": result["data"]
        }

    if category == "HYBRID":

        return answer_hybrid(
            question
        )

    return {
        "type": "RAG",
        "answer": answer_with_rag(
            question
        )
    }