import json
from g4f.client import Client


def functional():
    return "Я помогу вам написать сочинение на необходимую тему"


def generate(question):
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content


def operation():
    with open("app9/operations.json", "r", encoding="utf-8") as f:
        operations = json.load(f)
    return list(operations.keys())