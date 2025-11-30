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

# 🔹 НОВЫЙ эндпоинт для Битрикс24: исходящий вебхук робота
@app.post("/bitrix")
@app.get("/bitrix")  # на всякий случай, если Битрикс будет дергать GET
async def bitrix_webhook(request: Request):
    print("=== BITRIX WEBHOOK ===")

    # 1) Пробуем взять параметры из query (?deal_id=...&stage_id=...)
    params = dict(request.query_params)
    deal_id = params.get("deal_id")
    stage_id = params.get("stage_id")
    title = params.get("title")

    # 2) Если запрос был POST с JSON — попробуем прочитать тело
    if not (deal_id and stage_id):
        try:
            data = await request.json()
            print("BITRIX JSON:", data)
            deal_id = deal_id or data.get("deal_id") or data.get("ID")
            stage_id = stage_id or data.get("stage_id") or data.get("STAGE_ID")
            title = title or data.get("title") or data.get("TITLE")
        except Exception:
            pass

    # На всякий случай логируем
    print("deal_id:", deal_id, "stage_id:", stage_id, "title:", title)

    # Если вообще ничего не пришло — просто вернём ok
    if not deal_id and not stage_id:
        return {"ok": False, "message": "no deal data"}

    # Формируем текст сообщения для Telegram
    text_lines = [
        "🔔 *Сделка поменяла стадию*",
        f"ID сделки: `{deal_id}`" if deal_id else None,
        f"Стадия (ID): `{stage_id}`" if stage_id else None,
        f"Название: {title}" if title else None,
    ]
    text = "\n".join(line for line in text_lines if line)

    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_CHAT_ID,
        "text": text
    }

    resp = requests.post(send_url, json=payload)
    print("=== SEND RESPONSE (BITRIX) ===")
    print(resp.status_code, resp.text)

    return {"ok": True}