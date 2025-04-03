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

                # 📍 Якщо хтось пише "/start" → надіслати йому його chat_id
                if text == "/start":
                    send_message(chat_id, f"Ваш chat_id: {chat_id}")
                    continue

                # 🧑‍💼 Якщо адмін — це відповідь клієнту
                if chat_id == ADMIN_CHAT_ID and last_client_id:
                    send_message(last_client_id, text)
                    send_message(ADMIN_CHAT_ID, "✅ Відповідь надіслано покупцю")

                # 🧍 Якщо пише клієнт — передаємо повідомлення адміну
                elif chat_id != ADMIN_CHAT_ID:
                    last_client_id = chat_id
                    alert = f"📩 НОВЕ ПОВІДОМЛЕННЯ від @{username}:\n{text}"
                    send_message(ADMIN_CHAT_ID, alert)

        except Exception as e:
            app.logger.error("❌ Polling error: %s", str(e))

        time.sleep(1)
