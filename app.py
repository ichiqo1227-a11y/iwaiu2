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

if __name__ == "__main__":
    app.run(port=3000)
