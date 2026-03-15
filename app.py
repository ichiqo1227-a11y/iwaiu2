import os
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from openai import OpenAI

app = Flask(__name__)

slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    
    if "event" in data:
        event = data["event"]
        
        if event["type"] == "app_mention":
            text = event["text"]
            channel = event["channel"]
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role":"user","content":text}]
            )
            
            reply = response.choices[0].message.content
            
            slack_client.chat_postMessage(
                channel=channel,
                text=reply
            )
    
    return jsonify({"ok": True}), 200

# --- ここから付け足し ---
@app.route("/slack/events", methods=["POST"])
def slack_events():
    # Slackから届く「challenge」という合図に、そのまま中身を返してあげる処理
    if request.is_json and request.json.get("type") == "url_verification":
        return request.json.get("challenge")
    
    # ここに、後でメッセージを受け取った時の処理などを書けます
    return "OK", 200
# --- ここまで付け足し ---

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
