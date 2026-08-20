import time

from google import genai

from utils.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_with_retry(
    model,
    prompt,
    max_retries=4
):

    last_error = None

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            return response

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

    raise RuntimeError(
        "Gemini is temporarily unavailable "
        "after multiple attempts. Please try again."
    ) from last_error
