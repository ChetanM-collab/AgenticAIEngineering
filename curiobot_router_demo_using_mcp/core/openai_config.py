import os
from openai import OpenAI

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
DEFAULT_BASE_URL = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY")


def make_openai_client() -> OpenAI:
    return OpenAI(
        api_key=DEFAULT_API_KEY,
        base_url=DEFAULT_BASE_URL,
    )
