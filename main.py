from flask import Flask, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/forward', methods=['POST'])
def forward():
    data = request.json
    app.logger.info("💬 Отримано повідомлення: %s", data)
    app.logger.info("🔍 CHAT ID: %s", data.get("client_id"))
    return {"status": "ok"}, 200

@app.route('/')
def home():
    return 'Бот працює!'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
