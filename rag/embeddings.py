import time

from google import genai
from google.genai import types

from utils.config import GEMINI_API_KEY


MODEL_NAME = "gemini-embedding-001"

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def create_embeddings(texts):

    if not texts:
        return []

    all_embeddings = []

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
                        output_dimensionality=256
                    )
                )

                batch_embeddings = [
                    embedding.values
                    for embedding in response.embeddings
                ]

                all_embeddings.extend(
                    batch_embeddings
                )

                break

            except Exception as error:

                last_error = error

                error_text = str(error)

                if "503" in error_text or "UNAVAILABLE" in error_text:

                    wait_time = 2 ** attempt

                    time.sleep(
                        wait_time
                    )

                else:

                    raise error

        else:

            raise RuntimeError(
                "Gemini embedding service is temporarily "
                "unavailable after multiple retries. "
                "Please try processing the PDF again later."
            ) from last_error

    return all_embeddings