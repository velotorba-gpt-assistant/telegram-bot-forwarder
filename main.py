import requests
import time
import threading
from flask import Flask, request

app = Flask(__name__)

# === Конфігурація ===
TOKEN = "7613552437:AAHz5jBxB6hJ9_-_1VR9ummuhyU_pnDbsqA"
ADMIN_CHAT_ID = 6750366089
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

last_client_id = None  # зберігає chat_id останнього клієнта

# === Надіслати повідомлення через API ===
def send_message(chat_id, text):
    requests.post(API_URL + "sendMessage", data={"chat_id": chat_id, "text": text})

# === Polling — ловимо твої відповіді як адміна ===
def start_polling():
    global last_client_id
    offset = None
    while True:
        res = requests.get(API_URL + "getUpdates", params={"timeout": 100, "offset": offset})
        data = res.json()
        for update in data.get("result", []):
            offset = update["update_id"] + 1
            msg = update.get("message", {})
            chat_id = msg.get("chat", {}).get("id")
            text = msg.get("text", "")
            if chat_id == ADMIN_CHAT_ID and last_client_id:
                send_message(last_client_id, f"{text}")
                send_message(ADMIN_CHAT_ID, "✅ Повідомлення надіслано клієнту.")
        time.sleep(1)

# === Flask Webhook для дублювання з SalesDrive ===
@app.route('/forward', methods=['POST'])
def forward():
    global last_client_id
    data = request.json
    text = data.get("text", "")
    username = data.get("username", "невідомо")
    client_id = data.get("client_id")
    if client_id:
        last_client_id = client_id
    full_message = f"✉️ Повідомлення від @{username}:\n{text}"
    send_message(ADMIN_CHAT_ID, full_message)
    return {"status": "ok"}, 200

@app.route('/')
def home():
    return 'Бот працює!'

# === Запуск Flask + Polling ===
def run_all():
    threading.Thread(target=start_polling).start()
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    run_all()
