#
#
#   Anthropic
#
#

from typing import Optional

from .base import LLM

try:
    import anthropic
except ImportError:
    anthropic = None


class Anthropic(LLM):

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307",
                 anthropic_client_kwargs: Optional[dict] = None):
        if anthropic is None:
            raise ImportError("Please install the 'linguista[anthropic]' package to use the Anthropic LLM.")

        if anthropic_client_kwargs is None:
            anthropic_client_kwargs = {}

        self.model = model

        self._client = anthropic.Anthropic(api_key=api_key, **anthropic_client_kwargs)

    def __call__(self, prompt: str):
        message = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return message.content[0].text
