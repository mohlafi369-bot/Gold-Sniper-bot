import os
import sys

# إجبار الطباعة الفورية في اللوجز
def log(message):
    print(message, flush=True)

try:
    import yfinance as yf
    import telebot
    import google.generativeai as genai
    import time
    from flask import Flask
    from waitress import serve
    log("✅ تم تحميل المكتبات بنجاح")
except Exception as e:
    log(f"❌ خطأ في تحميل المكتبات: {e}")
    sys.exit(1)

app = Flask('')

# إعدادات ثابتة مع فحص وجودها
GEMINI_KEY = os.environ.get('GEMINI_KEY')
TELE_TOKEN = os.environ.get('TELE_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

if not all([GEMINI_KEY, TELE_TOKEN, CHAT_ID]):
    log("❌ خطأ: أحد مفاتيح البيئة (Variables) مفقود في إعدادات Render!")

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELE_TOKEN)

@app.route('/')
def home():
    try:
        gold = yf.Ticker("GC=F")
        df = gold.history(period="1d", interval="15m")
        current_price = df['Close'].iloc[-1]
        
        prompt = f"حلل الذهب (SMC) للسعر {current_price:.2f}. أرسل توصية فقط لو كانت قوية."
        response = ai_model.generate_content(prompt)
        
        if any(x in response.text for x in ["دخول", "هدف"]):
            bot.send_message(CHAT_ID, f"🎯 إشارة:\n{response.text}")
            
        return f"Active. Price: {current_price}", 200
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    try:
        log("🚀 بدء تشغيل السيرفر على Port 10000...")
        serve(app, host='0.0.0.0', port=10000)
    except Exception as e:
        log(f"💥 خطأ قاتل عند التشغيل: {e}")
        
