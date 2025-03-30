import random

def generate_random_sentence_with_nouns(size=3):
    with open("src/data/english_nouns.txt") as src:
        words = src.read().split("\n")

    return " ".join([random.choice(words).strip() for _ in range(size)])