#
#
#   OpenAI
#
#

from typing import Optional

from .base import LLM

try:
    import openai
except ImportError:
    openai = None


class OpenAI(LLM):

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", openai_client_kwargs: Optional[dict] = None):
        if openai is None:
            raise ImportError("Please install the 'linguista[openai]' package to use the OpenAI LLM.")

        if openai_client_kwargs is None:
            openai_client_kwargs = {}

        self.model = model

        self._client = openai.OpenAI(api_key=api_key, **openai_client_kwargs)

    def __call__(self, prompt: str):
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
