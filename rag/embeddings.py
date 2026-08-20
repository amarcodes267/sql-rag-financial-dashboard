import time

from google import genai
from google.genai import types

from utils.config import GEMINI_API_KEY


MODEL_NAME = "gemini-embedding-001"

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def create_embeddings(
    texts,
    task_type="RETRIEVAL_DOCUMENT"
):

    if not texts:
        return []

    all_embeddings = []

    # Keep batches safely below the API limit.
    batch_size = 50

    for start in range(
        0,
        len(texts),
        batch_size
    ):

        batch = texts[
            start:start + batch_size
        ]

        last_error = None

        for attempt in range(4):

            try:

                response = client.models.embed_content(
                    model=MODEL_NAME,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type=task_type,
                        output_dimensionality=256,
                        auto_truncate=True
                    )
                )

                embeddings = [
                    embedding.values
                    for embedding in response.embeddings
                ]

                all_embeddings.extend(
                    embeddings
                )

                break

            except Exception as error:

                last_error = error

                error_text = str(error)

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                ):

                    wait_time = 2 ** attempt

                    time.sleep(
                        wait_time
                    )

                else:

                    raise

        else:

            raise RuntimeError(
                "Gemini embedding service is "
                "temporarily unavailable. "
                "Please try again."
            ) from last_error

    return all_embeddings


def create_document_embeddings(texts):

    return create_embeddings(
        texts,
        task_type="RETRIEVAL_DOCUMENT"
    )


def create_query_embedding(text):

    embeddings = create_embeddings(
        [text],
        task_type="RETRIEVAL_QUERY"
    )

    if not embeddings:
        return []

    return embeddings[0]