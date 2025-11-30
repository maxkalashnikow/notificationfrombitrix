import os
import requests
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("GROUP_CHAT_ID")

text = "Привет, группа! Это тестовое сообщение от бота."

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": text
}

response = requests.post(url, json=payload)

print(response.json())
