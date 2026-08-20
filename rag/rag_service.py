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
        top_k=3
    )

    if not results:

        return (
            "No relevant information was found "
            "in the uploaded financial report."
        )

    context_parts = []

    for result in results:

        text = result["text"]

        # Limit each retrieved chunk
        text = text[:4000]

        context_parts.append(
            f"Page {result['page']}:\n{text}"
        )

    context = "\n\n".join(
        context_parts
    )

    prompt = f"""
Answer the financial question using ONLY
the provided report context.

Do not invent information.

If the answer is not available,
say so clearly.

Question:
{question}

Report context:
{context}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text