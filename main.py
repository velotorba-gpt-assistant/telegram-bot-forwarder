import requests
import time
import threading
import logging
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# === Налаштування ===
TOKEN = "7613552437:AAHz5jBxB6hJ9_-_1VR9ummuhyU_pnDbsqA"
ADMIN_CHAT_ID = 6750366089  # ← Встав свій chat_id сюди
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

last_client_id = None  # зберігає ID останнього клієнта

# === Надсилання повідомлення через Telegram API ===
def send_message(chat_id, text):
    res = requests.post(API_URL + "sendMessage", data={"chat_id": chat_id, "text": text})
    app.logger.info("📤 Telegram API: %s | %s", res.status_code, res.text)

# === Пулінг: ловимо ВСІ повідомлення з Telegram ===
def start_polling():
    global last_client_id
    offset = None
    while True:
        try:
            res = requests.get(API_URL + "getUpdates", params={"timeout": 100, "offset": offset})
            data = res.json()
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                username = msg.get("from", {}).get("username", "невідомо")

                if not text:
                    continue

                # 🔐 Якщо ти пишеш "/start" — бот скаже твій chat_id
                if text == "/start":
                    send_message(chat_id, f"Ваш chat_id: {chat_id}")
                    continue

                # 🧑‍💼 Якщо це адмін → відповідь останньому клієнту
                if chat_id == ADMIN_CHAT_ID and last_client_id:
                    send_message(last_client_id, text)
                    send_message(ADMIN_CHAT_ID, "✅ Відповідь надіслано покупцю")

                # 🧍 Якщо це КЛІЄНТ → повідомлення адміну
                elif chat_id != ADMIN_CHAT_ID:
                    last_client_id = chat_id
                    alert = f"📩 НОВЕ ПОВІДОМЛЕННЯ від @{username}:\n{text}"
                    send_message(ADMIN_CHAT_ID, alert)

        except Exception as e:
            app.logger.error("❌ Polling error: %s", str(e))

        time.sleep(1)

# === Отримання повідомлень із CRM ===
@app.route('/forward', methods=['POST'])
def forward():
    global last_client_id
    data = request.json
    app.logger.info("💬 Отримано повідомлення з CRM: %s", data)

    text = data.get("text", "")
    username = data.get("username", "невідомо")
    client_id = data.get("client_id")
    if client_id:
        last_client_id = client_id

    message = f"✉️ Повідомлення від @{username}:\n{text}"
    send_message(ADMIN_CHAT_ID, message)

    return {"status": "ok"}, 200

# === Тест головної сторінки ===
@app.route('/')
def home():
    return 'Бот працює!'

# === Запуск Flask + Polling ===
def run_all():
    threading.Thread(target=start_polling).start()
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    run_all()
