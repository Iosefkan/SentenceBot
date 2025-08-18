from openai import OpenAI
from config import SENTENCE_GENERATION_MODEL, API_KEY
import random

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=API_KEY
)

topics = [
    "nature",
    "technology",
    "science",
    "history",
    "art",
    "music",
    "sports",
    "politics",
    "economy",
    "education",
    "health",
    "travel",
    "food",
    "animals",
    "culture",
    "environment",
    "cosmetics",
    "fashion",
    "beauty",
    "computers"
    "movies",
    "books",
    "literature",
    "games"
]

def generate_base_sentence(language: str) -> str:
    completion = client.chat.completions.create(
    model=SENTENCE_GENERATION_MODEL,
        messages=[
            {
            "role": "user",
            "content": f"Write a short sentence in {language} about the {random.choice(topics)}. Do not follow with suggestions, tranlation or anything else, output just the sentence."
            }
        ]
    )
    result = completion.choices[0].message.content
    return result