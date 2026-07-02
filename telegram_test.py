import requests

BOT_TOKEN = "8746011664:AAEJYvYe7euO4_VeqAowfJ_BLCVZ3FokPss"
CHAT_ID = "8152856153"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

data = {
    "chat_id": CHAT_ID,
    "text": "🚀 Your Python Telegram bot is working!"
}

response = requests.post(url, data=data)

print(response.text
