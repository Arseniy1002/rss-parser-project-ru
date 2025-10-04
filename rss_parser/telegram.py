import httpx
import logging
from tenacity import retry, wait_fixed, stop_after_attempt, before_log

# CRITICAL FIX: Относительный импорт
from .config import settings

class TelegramClient:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/"
        self.chat_id = settings.telegram_chat_id
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            logging.warning("Токен или ID чата Telegram не настроены. Уведомления работать не будут.")
            self.is_enabled = False
        else:
            self.is_enabled = True

    @retry(wait=wait_fixed(settings.retry_wait_time), stop=stop_after_attempt(settings.retry_attempts),
           before=before_log(logging.getLogger(__name__), logging.INFO))
    async def send_notification(self, client: httpx.AsyncClient, message: str):
        if not self.is_enabled:
            return
        url = self.base_url + "sendMessage"
        payload = {'chat_id': self.chat_id, 'text': message, 'parse_mode': 'Markdown'}
        response = await client.post(url, json=payload, timeout=settings.request_timeout)
        response.raise_for_status()
        logging.info("Уведомление в Telegram успешно отправлено.")
