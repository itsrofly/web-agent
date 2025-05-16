from openai import OpenAI


class Agent:
    def __init__(self, base_url: str, api_key: str):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

    def send(self, model, prompt: str) -> str:
        completion = self.client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
        )
        return completion.choices[0].message