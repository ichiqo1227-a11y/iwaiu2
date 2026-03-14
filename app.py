from flask import Flask, request, jsonify
import os
from slack_sdk import WebClient
from openai import OpenAI

app = Flask(__name__)

slack = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
openai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

@app.route("/slack/events", methods=["POST"])
def slack_events():

    data = request.json

    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    if "event" in data:
        event = data["event"]

        if event["type"] == "app_mention":

            text = event["text"]
            channel = event["channel"]

            res = openai.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "user", "content": text}]
            )

            reply = res.choices[0].message.content

            slack.chat_postMessage(
                channel=channel,
                text=reply
            )

    return {"ok": True}
