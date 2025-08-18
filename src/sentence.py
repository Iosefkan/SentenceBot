from transformers import pipeline
import random

generator = pipeline("text-generation", model="bigscience/bloomz-560m")

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
    prompt = f"Write a short sentence in {language} about the {random.choice(topics)}."
    result = generator(prompt, max_length=40, num_return_sequences=1)
    return result[0]['generated_text']