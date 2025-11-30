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
    """Отправка сообщения в Telegram с логами ответа."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_CHAT_ID,  # тут можно подставить конкретный ID
        "text": text,
    }
    print("=== SENDING TO TELEGRAM ===")
    print("PAYLOAD:", payload)

    resp = requests.post(url, json=payload)
    print("=== TELEGRAM RESPONSE ===")
    print("STATUS:", resp.status_code)
    print("BODY:", resp.text)


@app.get("/")
async def root():
    return {"status": "ok"}


# ---------- TELEGRAM /webhook (как было) ----------
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

    send_telegram("Слово 'test' обнаружено! 🟢")
    return {"ok": True}


# ---------- BITRIX /bitrix: ТОЛЬКО QUERY ПАРАМЕТРЫ ----------
@app.get("/bitrix")
@app.post("/bitrix")  # на всякий случай, если Битрикс дергает POST
async def bitrix_webhook(request: Request):
    print("=== BITRIX HIT ===")

    # ВСЁ берем только из query string:
    params = dict(request.query_params)
    print("QUERY PARAMS:", params)

    deal_id = params.get("deal_id")
    stage_id = params.get("stage_id")
    title = params.get("title")

    # формируем текст для Telegram
    lines = ["🔔 Сделка поменяла стадию (из Bitrix)"]
    if deal_id:
        lines.append(f"ID сделки: {deal_id}")
    if stage_id:
        lines.append(f"Стадия: {stage_id}")
    if title:
        lines.append(f"Название: {title}")

    text = "\n".join(lines)

    # отправляем сообщение
    send_telegram(text)

    # битриксу можно вернуть просто ok
    return {"ok": True}