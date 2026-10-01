import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured in the .env file."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.7-flash"


def ask_ai(user_message):
    """
    Send a text message to Gemini and return the AI response.
    """

    config = types.GenerateContentConfig(
        automatic_function_calling=(
            types.AutomaticFunctionCallingConfig(
                disable=True
            )
        )
    )

    models_to_try = [
        PRIMARY_MODEL,
        FALLBACK_MODEL,
    ]

    last_error = None

    for model_name in models_to_try:

        for attempt in range(2):

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=user_message,
                    config=config,
                )

                if response.text:
                    return response.text.strip()

                return "I couldn't generate a response."

            except Exception as error:

                last_error = error

                print(
                    f"Gemini error "
                    f"({model_name}, attempt {attempt + 1}): "
                    f"{error}"
                )

                time.sleep(2)

    raise RuntimeError(
        f"Gemini service is temporarily unavailable. "
        f"Last error: {last_error}"
    )