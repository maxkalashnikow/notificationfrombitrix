import os
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

# Загружаем .env локально (на Render это не обязательно, там через Environment)
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
# Можно жестко указать ID группы, но лучше брать из env
GROUP_CHAT_ID = os.getenv("CHAT_ID")  # -1002399489876

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("=== UPDATE ===")
    print(data)

    message = data.get("message")
    if not message:
        # Ничего интересного, просто вернем ok
        return {"ok": True}

    text = message.get("text", "")
    if not text:
        return {"ok": True}

    # Приводим к нижнему регистру, убираем пробелы
    normalized = text.strip().lower()

    # Реагируем только если сообщение == "test"
    if normalized == "test":
        # Можно отправлять либо в ту же группу:
        # chat_id = message["chat"]["id"]
        # либо в отдельную группу из env:
        chat_id = GROUP_CHAT_ID or message["chat"]["id"]

        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": "Слово 'test' обнаружено! 🟢",
        }

        resp = requests.post(send_url, json=payload)
        print("=== SEND RESPONSE ===")
        print(resp.status_code, resp.text)

    return {"ok": True}
