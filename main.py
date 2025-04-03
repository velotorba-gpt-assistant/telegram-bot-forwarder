from flask import Flask, request

app = Flask(__name__)

# === Виводимо повідомлення з CRM у лог ===
@app.route('/forward', methods=['POST'])
def forward():
    data = request.json
    print("💬 Отримано повідомлення:", data)
    print("🔍 CHAT ID:", data.get("client_id"))
    return {"status": "ok"}, 200

@app.route('/')
def home():
    return 'Бот працює!'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
