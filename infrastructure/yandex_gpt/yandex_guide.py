import openai
import os
from dotenv import load_dotenv
load_dotenv()

def runYandexGPT(text):
    client = openai.OpenAI(
    api_key=os.getenv("YANDEX_AUTH"),
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
    project="b1guven129cmf8dbhh6e"
    )
    response = client.responses.create(
        prompt={
            "id": "fvt3aaqv5nttshr8gu5i",
        },
        input=text,
    ) 
    return response.output_text