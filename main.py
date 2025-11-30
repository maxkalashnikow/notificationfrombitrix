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


def send_telegram(text: str):
    """Простая функция отправки сообщения в Telegram, с логами ответа."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_CHAT_ID,
        "text": text,
        # parse_mode убрал, чтобы точно не ломалось из-за Markdown
    }
    resp = requests.post(url, json=payload)
    print("=== TELEGRAM RESPONSE ===")
    print("STATUS:", resp.status_code)
    print("BODY:", resp.text)


@app.get("/")
def root():
    return {"status": "ok"}


# ------- РУЧКА ДЛЯ TELEGRAM (как была) -------
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("=== TELEGRAM UPDATE ===")
    print(data)

    message = data.get("message")
    if not message:
        return {"ok": True}

    text = (message.get("text") or "").strip().lower()
    if text != "test":
        return {"ok": True}

    # тут можно отправлять в ту же группу
    send_telegram("Слово 'test' обнаружено! 🟢")
    return {"ok": True}


# ------- НОВАЯ РУЧКА ДЛЯ BITRIX -------
@app.get("/bitrix")
@app.post("/bitrix")
async def bitrix_webhook(request: Request):
    print("=== BITRIX HIT ===")

    # ЛОГИРУЕМ query-параметры
    params = dict(request.query_params)
    print("QUERY PARAMS:", params)

    # Пытаемся прочитать тело (если POST с JSON/FORM)
    try:
        body = await request.json()
        print("JSON BODY:", body)
    except Exception:
        body = None
        print("NO JSON BODY OR PARSE ERROR")

    # ДЛЯ ТЕСТА: ВСЕГДА шлём сообщение в телеграм, без условий
    text = "Тест из ручки /bitrix\n"
    if params:
        text += f"query: {params}\n"
    if body:
        text += f"body: {body}\n"

    send_telegram(text)

    return {"ok": True}