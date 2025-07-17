from openai import AsyncOpenAI
from config import OPENAI_API_KEY
import logging
import os


class OpenAIService:
    def __init__(self):
        # Подробный дамп переменных среды с ключевым словом PROXY
        proxy_vars = {k: v for k, v in os.environ.items() if "PROXY" in k.upper()}
        logging.info(f"[DEBUG] Переменные окружения, связанные с PROXY: {proxy_vars}")

        # Логируем, какой ключ реально используется
        logging.info(
            f"[DEBUG] Используется OPENAI_API_KEY: {'*' * (len(OPENAI_API_KEY) - 4) + OPENAI_API_KEY[-4:] if OPENAI_API_KEY else 'None'}")

        # Логируем тип клиента и параметры
        try:
            logging.info("[DEBUG] Инициализация AsyncOpenAI без параметров прокси.")
            self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        except Exception as e:
            logging.error(f"[DEBUG] Ошибка инициализации OpenAI: {e}")
            raise

    async def get_legal_advice(self, question: str):
        try:
            system_prompt = (
                "Ты - опытный юрист, специализирующийся на похоронном законодательстве и оформлении документов РФ.\n"
                "Отвечай кратко, четко и по существу. Давай практические советы.\n"
                "Если вопрос не связан с юридическими аспектами похорон, вежливо перенаправь к соответствующему специалисту."
            )
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.9
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"[DEBUG] Ошибка OpenAI API: {e}")
            return "Извините, произошла ошибка при обработке вашего вопроса. Попробуйте позже."
