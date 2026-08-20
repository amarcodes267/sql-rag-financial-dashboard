from google import genai

from utils.config import GEMINI_API_KEY
from rag.vector_store import search_documents


MODEL_NAME = "gemini-3.6-flash"

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def answer_with_rag(question):

    results = search_documents(
        question,
        top_k=5
    )

    if not results:

        return (
            "No relevant information was found "
            "in the uploaded financial report."
        )

    context_parts = []

    for result in results:

        page = result.get(
            "page",
            "Unknown"
        )

        text = result.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        context_parts.append(
            f"""
PAGE {page}

{text[:5000]}
"""
        )

    if not context_parts:

        return (
            "No readable information was found "
            "in the retrieved report sections."
        )

    context = "\n\n".join(
        context_parts
    )

    prompt = f"""
You are a financial report analysis assistant.

Answer the user's question using ONLY the
provided financial report context.

IMPORTANT RULES:

1. Do not use outside knowledge.
2. Do not invent facts.
3. If the context contains the answer, explain it clearly.
4. If the answer is not present in the context,
   say that the information was not found.
5. For financial risks, strategies, business information,
   management discussion, and other narrative questions,
   summarize the relevant information from the report.
6. Mention the relevant page number when possible.
7. Keep the answer concise but useful.

USER QUESTION:

{question}

FINANCIAL REPORT CONTEXT:

{context}
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = response.text.strip()

        if not answer:

            return (
                "The AI could not generate an answer "
                "from the retrieved report information."
            )

        return answer

    except Exception as error:

        return (
            f"Unable to analyze the financial report: "
            f"{error}"
        )