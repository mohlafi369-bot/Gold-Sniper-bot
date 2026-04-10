import os
import yfinance as yf
import telebot
import google.generativeai as genai
import time
from flask import Flask
from threading import Thread

# --- خدعة السيرفر المجاني ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running!"

def run():
    app.run(host='0.0.0.0', port=10000) # بورت ريندر الافتراضي

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت ---
GEMINI_KEY = os.environ.get('GEMINI_KEY')
TELE_TOKEN = os.environ.get('TELE_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELE_TOKEN)

def get_sniper_signal():
    gold = yf.Ticker("GC=F")
    df_15m = gold.history(period="1d", interval="15m")
    current_price = df_15m['Close'].iloc[-1]
    
    prompt = f"حلل سعر الذهب الحالي {current_price:.2f} بنظام SMC وأعطني صفقة (دخول، هدف، وقف خسارة)."
    response = ai_model.generate_content(prompt)
    return response.text

# تشغيل السيرفر الوهمي
keep_alive()

print("🎯 البوت القناص يعمل الآن مجاناً...")
while True:
    try:
        signal = get_sniper_signal()
        bot.send_message(CHAT_ID, f"🎯 إشارة قناص:\n\n{signal}")
        time.sleep(900) # فحص كل 15 دقيقة
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
