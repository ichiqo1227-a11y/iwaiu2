from flask import Flask, request, jsonify

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    
    if "event" in data:
        event = data["event"]
        
        if event["type"] == "app_mention":
            text = event["text"]
            channel = event["channel"]
            
            response = openai_client.chat.completions.create(
                model="gpt-4",  # gpt-5 は存在しません
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
