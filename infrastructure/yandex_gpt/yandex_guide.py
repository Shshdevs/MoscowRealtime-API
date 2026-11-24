import openai
import os
from dotenv import load_dotenv

load_dotenv()


def runYandexGPT(text):
    YANDEX_CLOUD_FOLDER = os.getenv("YANDEX_CLOUD_API_KEY")
    YANDEX_CLOUD_MODEL = os.getenv("YANDEX_CLOUD_MODEL")

    client = openai.OpenAI(
        api_key=os.getenv("YANDEX_CLOUD_API_KEY"),
        base_url="https://ai.api.cloud.yandex.net/v1",
        project=os.getenv("YANDEX_CLOUD_FOLDER"),
    )
    response = client.responses.create(
        model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
        temperature=0.41,
        instructions=
            """Твоя роль это опытный и интересный экскурсовод по городу Москве. 
            Ты будешь получать название памятников культуры (статуи, усадьбы и тому подобное). 
            Расскажи о герое памятника/владельцах зданий самое главное и интересное.  
            Опиши этот памятник культуры. Расскажи, за что он стал известен.\n\n
            Получая объект ты должен внести в рассказ как минимум 3 интересных факта или истории на твое усмотрение, мало кому известных. 
            Не подписывай абзацы как интересный факт 1,2, или интересные детали просто пропустим это.\n\n
            Твой рассказ должен быть интересным, новым и вдохновляющим, чтобы слушателю хотелось дальше продолжить экскурсию.
            """,
        input=text,
        max_output_tokens=2287,
        store=True,
        truncation="disabled",
    )
    return response.output_text
