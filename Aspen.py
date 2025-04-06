import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


while True:
    user_input = input("User: ")

    response = client.responses.create(
    model="gpt-4o-mini",
    tools=[{"type": "web_search_preview"}],
    input=user_input
    )

    print(response.output_text)


