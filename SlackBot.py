import os
import requests
from flask import Flask, request, jsonify
import Utils
import threading
import LangMinion
app = Flask(__name__)
lang_minion_instance = ''

# Slack Bot Token（在 OAuth & Permissions 页面获取）
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")  # xoxb-xxxx...
SLACK_POST_MESSAGE_URL = "https://slack.com/api/chat.postMessage"

def send_message(channel, text):
    """发送消息到指定 Slack 频道"""
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    text = Utils.markdown_to_slack_mrkdwn(text)
    payload = {
        "channel": channel,
        "text": text,
        "mrkdwn": True
    }
    print(f'send_message(): send {payload} to {channel}')
    response = requests.post(SLACK_POST_MESSAGE_URL, json=payload, headers=headers)
    if not response.json().get("ok"):
        print("发送失败：", response.json())

def process_message(user, text):
    ret = lang_minion_instance.respond('', text)
    return f"{ret}"

def process_command(cmd, data):
    print(f'process_command(): Recieved command {cmd}')
    if data:
        text = data['text']
        text = Utils.get_pure_slack_message(text)
        channel = data['channel_id']
        response = lang_minion_instance.respond_command(cmd, text)
        send_message(channel, f'{response}')
    code = 200
    return "", code

@app.route('/slack/commands/<path:subpath>', methods=['POST'])
def slack_commands(subpath):
    print("Content-Type:", request.content_type)
    data = request.form.to_dict()
    print(f'slack_commands called! subpath = {subpath}, data =\n{data}')
    if lang_minion_instance.can_handle_command(subpath):
        text = data['text']
        text = Utils.get_pure_slack_message(text)
        threading.Thread(target=process_command, args=(subpath, data), daemon=True).start()
        return f"Command [{subpath}]\nArgument [{text}]", 200
    return f"Unsupported command [{subpath}]", 200

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    print(f'message incoming, data = {data}')

    # 1. Slack 第一次会发送 challenge 验证
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    # 2. 处理消息事件
    if "event" in data:
        event = data["event"]

        # 忽略自己发的消息（避免死循环）
        if event.get("bot_id"):
            return "", 200

        # 只处理普通消息（排除 join/leave 等系统消息）
        if (event.get("type") == "message" or event.get("type") == "app_mention")and "subtype" not in event:
            user = event.get("user")
            text = event.get("text")
            channel = event.get("channel")

            # 调用处理函数
            text = Utils.get_pure_slack_message(text)
            def process_message_callback(user, text, channel):
                reply_text = process_message(user, text)
                send_message(channel, reply_text)
            threading.Thread(target=process_message_callback, args=(user, text, channel), daemon=True).start()
    return "", 200

if __name__ == "__main__":
    # 本地运行
    Utils.set_env_from_ini('config.ini')
    api_key = os.environ.get('OPENAI_API_KEY')
    end_point = os.environ.get('OPENAI_AZURE_ENDPOINT')
    lang_minion_instance = LangMinion.OpenAILangMinionBackend("gpt-4.1", api_key, end_point)
    app.run(port=3000, debug=True)
