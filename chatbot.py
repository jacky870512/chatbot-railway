from flask import Flask, request, jsonify
from time import time

app = Flask(__name__)

# 記錄使用者的發言時間戳
user_rate_limit = {}

# 設定限制參數
MAX_REQUESTS = 3       # 最多幾次
INTERVAL_SECONDS = 10  # 幾秒內

@app.route("/events", methods=["POST"])
def webhook():
    data = request.json
    print("收到訊息：", data)

    user = data.get("message", {}).get("sender", {}).get("name", "unknown")
    message = data.get("message", {}).get("text", "")

    # DDoS 防護：超過頻率限制就封鎖回應
    if is_spamming(user):
        return jsonify({"text": "⚠️ 訊息過多，請稍後再試。"})

    # 違規判斷
    if has_too_many_repeats(message):
        return jsonify({"text": "❌ 訊息內有重複文字，已禁止發送。"})

    if "giphy.com" in message or ".gif" in message:
        return jsonify({"text": "❌ 不允許傳送 GIF 圖片連結。"})

    # 正常情況不回應
    return "", 204

def is_spamming(user):
    now = time()
    if user not in user_rate_limit:
        user_rate_limit[user] = []

    # 保留這段時間內的紀錄
    recent = [t for t in user_rate_limit[user] if now - t < INTERVAL_SECONDS]
    recent.append(now)
    user_rate_limit[user] = recent

    return len(recent) > MAX_REQUESTS

def has_too_many_repeats(text):
    count = {}
    for word in text.split():
        count[word] = count.get(word, 0) + 1
        if count[word] >= 10:
            return True
    return False

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
