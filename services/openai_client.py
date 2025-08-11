import openai
from app_config import settings

openai.api_key = settings.OPENAI_API_KEY

async def generate_completion(prompt: str) -> str:
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()