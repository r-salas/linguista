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

    def __init__(self, model: str = "claude-3-haiku-20240307", anthropic_client_kwargs: Optional[dict] = None):
        if anthropic is None:
            raise ImportError("Please install the 'linguista[anthropic]' package to use the Anthropic LLM.")

        self.model = model

        self._client = anthropic.Anthropic(**anthropic_client_kwargs)

    def __call__(self, prompt: str):
        message = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content
