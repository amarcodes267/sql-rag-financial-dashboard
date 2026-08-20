from google import genai

from utils.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODEL_NAME = "gemini-embedding-001"


def create_embeddings(texts):

    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=texts
    )

    return [
        embedding.values
        for embedding in response.embeddings
    ]