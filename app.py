from flask import Flask, request, jsonify
import os
import threading
from slack_sdk import WebClient
from openai import OpenAI

app = Flask(__name__)

# 環境変数の読み込み
slack = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def process_openai_request(text, channel):
    """OpenAIの処理とSlackへの返信をバックグラウンドで行う関数"""
    try:
        # モデル名はご利用可能なもの（gpt-4oなど）に変更してください
        res = openai.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": text}]
        )

        reply = res.choices[0].message.content

        slack.chat_postMessage(
            channel=channel,
            text=reply
        )
    except Exception as e:
        print(f"Error processing request: {e}")

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json

    # URL確認（Slack App設定時のみ必要）
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    # Slackのリトライ（再送）を無視する設定（3秒ルール対策の補助）
    if request.headers.get("X-Slack-Retry-Num"):
        return {"ok": True}

    if "event" in data:
        event = data["event"]

        # メンションされた場合
        if event.get("type") == "app_mention":
            # 自分の返信には反応しないためのガード
            if event.get("bot_id"):
                return {"ok": True}

            text = event.get("text")
            channel = event.get("channel")

            # OpenAIの処理が重いため、別スレッドで実行して即座に200 OKを返す
            thread = threading.Thread(
                target=process_openai_request, 
                args=(text, channel)
            )
            thread.start()

    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    app.run(port=3000)
