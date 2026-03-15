import os
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

# 1. 環境変数が無くてもクラッシュしないようにガード
token = os.environ.get("SLACK_BOT_TOKEN")
signing_secret = os.environ.get("SLACK_SIGNING_SECRET")

# Slack Bolt アプリの初期化
app = App(
    token=token,
    signing_secret=signing_secret
)
handler = SlackRequestHandler(app)

# Flask アプリの名前を 'app' に統一するとミスが減ります
flask_app = Flask(__name__)

# ヘルスチェック用（ブラウザでURLを開いた時に動いているか確認するため）
@flask_app.route("/", methods=["GET"])
def health_check():
    return "Server is running!", 200

# Slack からのイベントを受け取る窓口
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    # Railway 用のポート設定
    port = int(os.environ.get("PORT", 3000))
    flask_app.run(host="0.0.0.0", port=port)
