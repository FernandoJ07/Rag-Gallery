import openai
from app.core import ports
from typing import cast


class OpenAIAdapter(ports.LlmPort):
    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float):
        self._client = openai.OpenAI(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    def generate_text(self, prompt: str, retrieval_context: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": f"The context is: {retrieval_context}, please respond to the following question: ",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=self._max_tokens,
            temperature=self._temperature,
        )
        # Usamos cast para garantizar que el retorno sea una cadena (str)
        return cast(str, response.choices[0].message.content)
