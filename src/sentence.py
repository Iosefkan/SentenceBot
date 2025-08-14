from faker import Faker


faker = Faker()


def generate_base_sentence() -> str:
    sentence = faker.sentence(nb_words=10)
    if not sentence.endswith((".", "!", "?")):
        sentence += "."
    return sentence


