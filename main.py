import os
import yfinance as yf
import telebot
import google.generativeai as genai
import time
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "ONLINE", 200

# إعدادات ثابتة
GEMINI_KEY = os.environ.get('GEMINI_KEY')
TELE_TOKEN = os.environ.get('TELE_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

bot = telebot.TeleBot(TELE_TOKEN)

def start_bot_logic():
    print("🚀 محاولة بدء المحرك...")
    while True:
        try:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            print(f"🕒 نبض حي: {current_time}")
            
            # محاولة بسيطة لإرسال رسالة للتأكد من التوكن
            # bot.send_message(CHAT_ID, f"النبض شغال: {current_time}") 
            
            # فحص الذهب
            gold = yf.Ticker("GC=F")
            data = gold.history(period="1d", interval="15m")
            print(f"📊 جلب البيانات: {'نجح' if not data.empty else 'فشل'}")
            
            # هنا تضع منطق Gemini (get_sniper_signal)
            # ... (سنتركه بسيطاً الآن للتشخيص)
            
        except Exception as e:
            print(f"❌ خطأ داخلي: {e}")
        
        time.sleep(60) # نبض كل دقيقة

if __name__ == "__main__":
    # تشغيل مباشر بدون تعقيدات
    t = Thread(target=start_bot_logic)
    t.daemon = True
    t.start()
    
    print("🌐 السيرفر يبدأ الآن...")
    app.run(host='0.0.0.0', port=10000)
    
