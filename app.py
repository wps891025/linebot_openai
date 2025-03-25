from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

message_counter = 0

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global message_counter
    text1=event.message.text
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "system", "content": "你是一個愛開玩笑的 AI 助手，總是用幽默的方式回答問題，讓使用者開心。"}
            {"role": "user", "content": text1}
        ],
        model="gpt-4o-mini-2024-07-18",
        temperature = 0.5,
    )
    try:
        ret = response['choices'][0]['message']['content'].strip()
        message_counter += 1  # 訊息數量 +1
    except:
        ret = '發生錯誤！'
    # 顯示計數結果
    ret += f"\n\n(📊 OpenAI 已回應 {message_counter} 則訊息)"
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()
