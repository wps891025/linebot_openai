from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

# 載入環境變數
openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

if not all([openai.api_key, os.getenv('CHANNEL_ACCESS_TOKEN'), os.getenv('CHANNEL_SECRET')]):
    raise ValueError("環境變數未正確設定！請檢查 .env 檔案或伺服器環境變數。")

# 記錄訊息數量
def load_counter():
    try:
        with open("counter.txt", "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_counter(count):
    with open("counter.txt", "w") as f:
        f.write(str(count))

message_counter = load_counter()

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        abort(400, "Missing X-Line-Signature")

    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400, "Invalid signature")
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global message_counter
    text1 = event.message.text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一個愛開玩笑的 AI 助手，總是用幽默的方式回答問題，讓使用者開心。"},
                {"role": "user", "content": text1}
            ],
            temperature=0.5,
        )
        ret = response['choices'][0]['message']['content'].strip()
        message_counter += 1
        save_counter(message_counter)
    except Exception as e:
        ret = f"發生錯誤！錯誤訊息: {str(e)}"

    ret += f"\n\n(📊 OpenAI 已回應 {message_counter} 則訊息)"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
