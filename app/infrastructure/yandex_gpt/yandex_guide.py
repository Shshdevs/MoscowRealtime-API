import openai


def runYandexGPT(text: str, api_key: str, folder_id: str, model: str) -> str:
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://ai.api.cloud.yandex.net/v1",
        project=folder_id,
    )
    response = client.responses.create(
        model=f"gpt://{folder_id}/{model}",
        temperature=0.41,
        instructions="""Твоя роль это опытный и интересный экскурсовод по городу Москве. 
            Ты будешь получать название памятников культуры (статуи, усадьбы и тому подобное). 
            Расскажи о герое памятника/владельцах зданий самое главное и интересное.  
            Опиши этот памятник культуры. Расскажи, за что он стал известен.\n\n
            Получая объект ты должен внести в рассказ как минимум 3 интересных факта или истории на твое усмотрение, мало кому известных. 
            Не подписывай абзацы как интересный факт 1,2, или интересные детали просто пропустим это.\n\n
            Твой рассказ должен быть интересным, новым и вдохновляющим, чтобы слушателю хотелось дальше продолжить экскурсию.
            """,
        input=text,
        max_output_tokens=837,
        store=False,
        truncation="disabled",
    )
    return response.output_text
