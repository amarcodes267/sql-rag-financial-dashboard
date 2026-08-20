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

    # Google allows a maximum of 100 requests
    # per embedding batch.
    batch_size = 50

    for start in range(
        0,
        len(texts),
        batch_size
    ):

        batch = texts[
            start:start + batch_size
        ]

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

    return all_embeddings