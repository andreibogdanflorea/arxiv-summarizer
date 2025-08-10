from google import genai
from google.genai import types

from src.processing.base import AbstractSummarizer


class GeminiSummarizer(AbstractSummarizer):
    def __init__(self):
        self.client = genai.Client()

    def summarize(self, prompt) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )

        return response.text
